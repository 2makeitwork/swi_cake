"""swi_iceberg statistical layer.

Implements the swi_iceberg glyph (see swi_iceberg.md): a median-centered,
MADN-scaled distribution. MADN = 1.4826 * median(|x - median|) is the normalized
median absolute deviation (the robust scale, historically also called "SWI sigma").

Population is stored per MADN band (default six equal 1-MADN bands over +/-3 MADN)
and rendered horizontally: a band's WIDTH is its population. Each band's drawn
HEIGHT is the OBSERVED value range of the samples inside that band (clipped to the
band by construction), so the vertical silhouette carries the occupied range, not
just the fixed theoretical band. The glyph body is bounded to the +/-3 MADN
envelope; observations beyond it are retained as Topping (above) and Bottoming
(below), never discarded. This module owns statistics only; presentation lives in
swi_iceberg.render.

Code is licensed under the Apache License, Version 2.0 (see LICENSE-CODE); the
specification is CC BY 4.0 (LICENSE).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

__all__ = [
    "InsufficientDataError",
    "IcebergGlyph",
    "build_iceberg",
    "MIN_SAMPLES",
    "MADN_CALIBRATION",
]

#: Minimum observations required (MADN is unstable below this).
MIN_SAMPLES = 100

#: MAD -> standard-deviation calibration factor for a Gaussian reference.
MADN_CALIBRATION = 1.4826


class InsufficientDataError(ValueError):
    """Raised when fewer than ``MIN_SAMPLES`` observations are supplied."""


@dataclass(frozen=True)
class IcebergGlyph:
    """Immutable canonical result for one swi_iceberg glyph.

    ``population`` is the 1D natural-number vector over vertical MADN bands
    (low -> high); a band's WIDTH is this count. ``band_lo`` / ``band_hi`` give
    the OBSERVED value range inside each band (absolute units, NaN when the band
    is empty) and drive the band's drawn HEIGHT. ``topping`` / ``bottoming`` are
    the counts beyond the +/-3 MADN envelope.
    """

    mode: str                       # "normal" | "collapsed"
    n: int
    median: float
    madn: float
    resolution: float               # band width in MADN units
    z_min: float
    z_max: float
    population: np.ndarray          # uint32 counts, len == number of bands
    edges: np.ndarray               # float64 band edges (MADN units), len+1
    band_lo: np.ndarray             # float64 observed min value per band (NaN if empty)
    band_hi: np.ndarray             # float64 observed max value per band (NaN if empty)
    lower: float                    # absolute lower envelope (median + z_min*madn)
    upper: float                    # absolute upper envelope (median + z_max*madn)
    topping: int = 0                # observations with z > z_max
    bottoming: int = 0              # observations with z < z_min
    value: Optional[float] = None   # collapsed-mode value (== median)

    @property
    def normalized(self) -> np.ndarray:
        """``population[r] / n`` as float64."""
        if self.n <= 0:
            return np.zeros_like(self.population, dtype=np.float64)
        return self.population.astype(np.float64) / float(self.n)


def _float_safe_edges(z_min: float, z_max: float, resolution: float) -> np.ndarray:
    span = z_max - z_min
    k = max(1, int(round(span / resolution)))
    return np.linspace(z_min, z_max, k + 1, dtype=np.float64)


def build_iceberg(
    values: Sequence[float] | np.ndarray,
    resolution: float = 1.0,
    z_min: float = -3.0,
    z_max: float = 3.0,
) -> IcebergGlyph:
    """Compute an :class:`IcebergGlyph` from observations.

    Parameters
    ----------
    values: array-like; signed domains allowed.
    resolution: band width in MADN units (default 1 -> six bands over +/-3).
    z_min, z_max: the clipping envelope in MADN units (default +/-3).

    Raises
    ------
    InsufficientDataError if fewer than 100 samples; ValueError for bad params.
    """
    if not (resolution > 0):
        raise ValueError("resolution must be > 0 MADN")
    if not (z_max > z_min):
        raise ValueError("z_max must be > z_min")
    for name, v in (("resolution", resolution), ("z_min", z_min), ("z_max", z_max)):
        if not np.isfinite(v):
            raise ValueError(f"{name} must be finite")

    arr = np.asarray(values, dtype=np.float64).ravel()
    n = int(arr.size)
    if n < MIN_SAMPLES:
        raise InsufficientDataError(f"At least {MIN_SAMPLES} samples are required (got {n}).")

    median = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median)))
    madn = MADN_CALIBRATION * mad
    lower = median + z_min * madn
    upper = median + z_max * madn

    # Zero-MAD collapse: no epsilon, no artificial spread.
    if mad == 0.0:
        return IcebergGlyph(
            mode="collapsed", n=n, median=median, madn=0.0, resolution=float(resolution),
            z_min=float(z_min), z_max=float(z_max),
            population=np.array([], dtype=np.uint32), edges=np.array([], dtype=np.float64),
            band_lo=np.array([], dtype=np.float64), band_hi=np.array([], dtype=np.float64),
            lower=median, upper=median, value=median,
        )

    z = (arr - median) / madn
    edges = _float_safe_edges(float(z_min), float(z_max), float(resolution))
    counts, edges = np.histogram(z, bins=edges)          # body: only |z| within envelope
    population = counts.astype(np.uint32)

    # Per-band OBSERVED value range (drives the band's drawn height). Band
    # membership already keeps these inside the band's absolute limits.
    nb = int(population.size)
    band_lo = np.full(nb, np.nan, dtype=np.float64)
    band_hi = np.full(nb, np.nan, dtype=np.float64)
    for b in range(nb):
        e0, e1 = float(edges[b]), float(edges[b + 1])
        if b == nb - 1:
            mask = (z >= e0) & (z <= e1)
        else:
            mask = (z >= e0) & (z < e1)
        if bool(mask.any()):
            seg = arr[mask]
            band_lo[b] = float(seg.min())
            band_hi[b] = float(seg.max())

    topping = int(np.count_nonzero(z > z_max))           # retained outliers
    bottoming = int(np.count_nonzero(z < z_min))

    return IcebergGlyph(
        mode="normal", n=n, median=median, madn=madn, resolution=float(resolution),
        z_min=float(z_min), z_max=float(z_max),
        population=population, edges=edges.astype(np.float64),
        band_lo=band_lo, band_hi=band_hi,
        lower=lower, upper=upper, topping=topping, bottoming=bottoming, value=None,
    )
