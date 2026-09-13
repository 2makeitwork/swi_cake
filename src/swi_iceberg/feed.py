"""Streaming feed interface for swi_iceberg.

Two ways to feed data:

- **Batch:** :func:`swi_iceberg.build_iceberg` needs at least ``MIN_SAMPLES``
  values at once and recomputes everything from scratch.
- **Streaming:** :class:`IcebergFeed` takes an initial batch (>= ``MIN_SAMPLES``)
  and afterwards accepts new values **one by one** via :meth:`IcebergFeed.feed_one`.

Numerical-stability note. The mean has Welford's algorithm (a stable running
update). The median has no O(1)-memory exact running update, but it does have an
exact, stable incremental form: keep the samples as **order statistics** (a sorted
container). The median is then read off in O(1) with *no floating-point
accumulation at all* — it is an exact order statistic, not a running sum. MADN and
the MADN-band binning depend on the current median, so rather than accumulate them
(which would drift as the median moves) they are recomputed **exactly on demand**
from the sorted samples. Per-update cost is one sorted insert; per-glyph cost is
one O(n) pass, the same as the batch path.
"""

from __future__ import annotations

import bisect
import threading
from typing import Iterable, Union

import numpy as np

from .core import (
    MADN_CALIBRATION,
    MIN_SAMPLES,
    IcebergGlyph,
    InsufficientDataError,
    build_iceberg,
)

__all__ = ["IcebergFeed", "IcebergPipeline"]


class IcebergFeed:
    """Incremental swi_iceberg feeder: initial batch, then single-value updates.

    Examples
    --------
    >>> feed = IcebergFeed()
    >>> feed.feed_batch(first_1500_latencies)   # must reach >= 100 samples
    >>> feed.feed_one(new_latency)              # one by one afterwards
    >>> glyph = feed.glyph()                    # exact, on demand
    """

    def __init__(
        self,
        resolution: float = 1.0,
        z_min: float = -3.0,
        z_max: float = 3.0,
        min_samples: int = MIN_SAMPLES,
    ) -> None:
        if not (resolution > 0):
            raise ValueError("resolution must be > 0 MADN")
        if not (z_max > z_min):
            raise ValueError("z_max must be > z_min")
        self._resolution = float(resolution)
        self._z_min = float(z_min)
        self._z_max = float(z_max)
        self._min = int(min_samples)
        self._xs: list[float] = []  # order statistics (sorted)

    def __len__(self) -> int:
        return len(self._xs)

    @property
    def n(self) -> int:
        """Number of samples fed so far."""
        return len(self._xs)

    @property
    def ready(self) -> bool:
        """True once at least ``min_samples`` values have been fed."""
        return len(self._xs) >= self._min

    def feed_batch(self, values: Iterable[float]) -> None:
        """Feed many values at once (used for the initial >= 100 samples)."""
        arr = np.asarray(values, dtype=np.float64).ravel()
        self._xs.extend(arr.tolist())
        self._xs.sort()

    def feed_one(self, x: float) -> None:
        """Feed a single new value (the incremental update path)."""
        bisect.insort(self._xs, float(x))

    def reset(self) -> None:
        """Drop all fed samples (start a fresh window)."""
        self._xs.clear()

    @property
    def median(self) -> float:
        """Exact median in O(1) from the order statistics."""
        n = len(self._xs)
        if n == 0:
            raise ValueError("no samples fed yet")
        if n % 2:
            return self._xs[n // 2]
        return 0.5 * (self._xs[n // 2 - 1] + self._xs[n // 2])

    @property
    def madn(self) -> float:
        """Exact MADN, recomputed on demand (depends on the current median)."""
        m = self.median
        arr = np.asarray(self._xs, dtype=np.float64)
        return MADN_CALIBRATION * float(np.median(np.abs(arr - m)))

    def glyph(self) -> IcebergGlyph:
        """Current glyph; raises InsufficientDataError below ``min_samples``."""
        if not self.ready:
            raise InsufficientDataError(
                f"At least {self._min} samples are required (got {len(self._xs)})."
            )
        return build_iceberg(
            np.asarray(self._xs, dtype=np.float64),
            resolution=self._resolution,
            z_min=self._z_min,
            z_max=self._z_max,
        )


Values = Union[float, int, Iterable[float]]


class IcebergPipeline:
    """Wait-out (time-batched) incremental feed pipeline.

    Values arrive via :meth:`submit` as a single sample or a batch of any size
    (1..N). They are buffered and then processed **incrementally** — either when
    :meth:`flush` is called, or automatically once every ``flush_interval``
    seconds (default 2.0) by a background thread: wait out 2 seconds, then process
    the batch no matter how many samples it holds.

    :meth:`reset` (or ``submit(..., reset=True)``) starts a fresh window, dropping
    both the buffer and all processed samples.
    """

    def __init__(
        self,
        flush_interval: float = 2.0,
        *,
        resolution: float = 1.0,
        z_min: float = -3.0,
        z_max: float = 3.0,
        min_samples: int = MIN_SAMPLES,
        autostart: bool = False,
    ) -> None:
        if not (flush_interval > 0):
            raise ValueError("flush_interval must be > 0 seconds")
        self._feed = IcebergFeed(
            resolution=resolution, z_min=z_min, z_max=z_max, min_samples=min_samples
        )
        self._flush_interval = float(flush_interval)
        self._buffer: list[float] = []
        self._lock = threading.Lock()
        self._stop_evt = threading.Event()
        self._thread: "threading.Thread | None" = None
        self._batches = 0
        if autostart:
            self.start()

    # -- ingestion ---------------------------------------------------------
    def submit(self, values: Values, reset: bool = False) -> None:
        """Buffer 1..N new samples; ``reset=True`` clears state first."""
        with self._lock:
            if reset:
                self._reset_locked()
            if isinstance(values, (int, float, np.number)):
                self._buffer.append(float(values))
            else:
                self._buffer.extend(np.asarray(values, dtype=np.float64).ravel().tolist())

    def flush(self) -> int:
        """Process everything buffered so far, incrementally. Returns count."""
        with self._lock:
            if not self._buffer:
                return 0
            batch = self._buffer
            self._buffer = []
            self._batches += 1
        self._feed.feed_batch(batch)  # sorted-insert: incremental, not a rebuild
        return len(batch)

    # -- background wait-out flusher ---------------------------------------
    def start(self) -> None:
        """Start the background thread that flushes every ``flush_interval``."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._run, name="swi_iceberg-flush", daemon=True
        )
        self._thread.start()

    def stop(self, join: bool = True) -> None:
        """Stop the background flusher (buffered values stay buffered)."""
        self._stop_evt.set()
        if self._thread is not None and join:
            self._thread.join(timeout=5)
        self._thread = None

    def _run(self) -> None:
        while not self._stop_evt.wait(self._flush_interval):
            self.flush()  # process the batch no matter how many samples it holds

    # -- window reset ------------------------------------------------------
    def reset(self) -> None:
        """Drop buffer and all processed samples (fresh window)."""
        with self._lock:
            self._reset_locked()

    def _reset_locked(self) -> None:
        self._buffer.clear()
        self._feed.reset()
        self._batches = 0

    # -- state -------------------------------------------------------------
    @property
    def n(self) -> int:
        """Processed sample count (buffered values not included)."""
        return self._feed.n

    @property
    def pending(self) -> int:
        """Buffered samples waiting for the next flush."""
        with self._lock:
            return len(self._buffer)

    @property
    def batches_processed(self) -> int:
        return self._batches

    @property
    def ready(self) -> bool:
        return self._feed.ready

    @property
    def median(self) -> float:
        return self._feed.median

    @property
    def madn(self) -> float:
        return self._feed.madn

    def glyph(self) -> IcebergGlyph:
        """Glyph of the processed state; call :meth:`flush` first to include
        anything still buffered. Raises InsufficientDataError below min_samples."""
        return self._feed.glyph()
