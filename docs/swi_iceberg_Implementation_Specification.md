# swi_iceberg — Implementation Specification

**Version:** 1.0 (matches the design boundary)
**Reference stack:** Python 3.10+ · NumPy · Pandas
**Scope:** binding implementation of the *swi_iceberg* design (`../swi_iceberg.md`)

This document is the project-facing implementation of swi_iceberg. It assumes the
statistical semantics defined in [`../swi_iceberg.md`](../swi_iceberg.md) and does
not restate them. Where the two disagree, the design's statistical invariants win.

**Licensing.** Executable code under `src/` (published) and under `private/`
(`private/examples/`, `private/tests/`, `private/verify/` — local tooling, not
published) is licensed under the Apache License, Version 2.0 (`LICENSE-CODE`).
The specification text is CC BY 4.0 (`LICENSE`).

---

## 1. Package overview

`swi_iceberg` separates the **statistical layer** (compute + store) from the
**rendering layer** (encode for display). No renderer mutates the result.

```text
src/swi_iceberg/
  __init__.py     # public API re-exports
  core.py         # IcebergGlyph + build_iceberg()   (statistical layer)
  render.py       # to_ascii(), to_json(), to_raster()   (rendering layer)
```

Public API (`from swi_iceberg import ...`):

| Symbol | Purpose |
|---|---|
| `build_iceberg(values, resolution=1.0, z_min=-3.0, z_max=3.0)` | Compute an `IcebergGlyph`. |
| `IcebergGlyph` | Frozen dataclass holding the canonical result. |
| `InsufficientDataError` | Raised when `n < 100`. |
| `MADN_CALIBRATION` | The 1.4826 factor. |
| `to_ascii / to_json / to_raster` | Rendering-layer encodings. |

---

## 2. Statistical layer

### 2.1 Result model

```python
@dataclass(frozen=True)
class IcebergGlyph:
    mode: str                     # "normal" | "collapsed"
    n: int
    median: float                 # m
    madn: float                   # 1.4826 * MAD  (the robust scale)
    resolution: float             # band width in MADN units (default 1 -> six bands)
    z_min: float; z_max: float    # clipping envelope (default +/-3)
    population: np.ndarray        # uint32 counts, one per MADN band (low -> high)
    edges: np.ndarray             # float64 band edges in MADN units, len+1
    band_lo: np.ndarray           # float64 observed min value per band (NaN if empty)
    band_hi: np.ndarray           # float64 observed max value per band (NaN if empty)
    lower: float; upper: float    # absolute envelope m + z_min*madn .. m + z_max*madn
    topping: int                  # observations with z > z_max (retained, not dropped)
    bottoming: int                # observations with z < z_min
    value: float | None           # collapsed-mode value (== median)
    # .normalized == population / n
```

`population` is the canonical 1D vector: population is stored vertically (per MADN
band) and rendered horizontally (a band's width). `band_lo` / `band_hi` are the
**observed value range inside each band** and drive the band's drawn **height** —
the hybrid encoding (design §6). Both are in absolute value units; an empty band
carries `NaN`.

### 2.2 Construction algorithm

`build_iceberg(values, resolution, z_min, z_max)`:

1. Coerce to a `float64` array; `n = len`. If `n < 100`, raise `InsufficientDataError`.
2. `median = np.median(x)`; `mad = np.median(|x - median|)`; `madn = 1.4826 * mad`;
   `lower = median + z_min*madn`; `upper = median + z_max*madn`.
3. **Zero-MAD collapse:** if `mad == 0` exactly, return `mode="collapsed"` with
   `value = median`, empty `population`/`band_lo`/`band_hi` — no epsilon, no
   artificial spread.
4. `z = (x - median) / madn`.
5. **Clip the body:** bin `z` over float-safe edges `linspace(z_min, z_max, k+1)`
   (k = round((z_max-z_min)/resolution)); `population = histogram(z, edges)`.
6. **Observed range per band:** for each band, take `min`/`max` of the original
   values whose `z` falls in that band (last band closed at the top edge); store in
   `band_lo`/`band_hi` (NaN when the band is empty). Band membership already keeps
   these inside the band's absolute limits.
7. **Retain outliers:** `topping = count(z > z_max)`, `bottoming = count(z < z_min)`.
8. Return `mode="normal"`.

Because the histogram covers only `[z_min, z_max]` and the tails are counted
separately, the conservation invariant holds:
`population.sum() + topping + bottoming == n` (a property test asserts it).

### 2.3 Data types

Counts are `uint32` (never wrap silently); coordinates, statistics, and per-band
observed ranges are `float64`. A glyph carries **no time**: the interval it
summarizes is metadata owned by the caller (§5).

---

## 3. Rendering layer

Rendering is a pure function of an `IcebergGlyph`. Population is rendered as
**horizontal width**; a body band's **vertical extent is its observed range**
(`band_lo`..`band_hi`), clipped by construction to the band.

- **`to_ascii(glyph, width)`** — dependency-free; one line per band (high MADN
  first) with a run proportional to `population / max(population)` and the band's
  observed range printed, plus Topping/Bottoming lines; a single line for
  `collapsed`.
- **`to_json(glyph)`** — the canonical handoff payload (statistics only, no
  pixels): `mode, n, median, madn, resolution, z_min, z_max, lower, upper, edges,
  population, normalized, band_lo, band_hi, topping, bottoming, value, spec_version`
  (`NaN` ranges serialize to `null`).
- **`to_raster(glyph, height_px, width_px)`** — optional 2D bitmap from the 1D
  vector (a rendering artifact, not storage).

### 3.1 Fleet renderer (`private/verify/src/devices-svg.ts`)

The browser harness draws the fleet view (design §4–§10): a shared absolute Y axis;
per category a glyph of six equal MADN bands whose **width = population**
(normalized by the category's N so shapes compare across unequal counts) and whose
**height = the band's observed value range**, colored green→red by band position;
**Topping/Bottoming** as fixed-height caps beyond ±3·MADN; a solid median per glyph;
and a faint **global reference** — the same six-band scheme on the pooled sample at
low opacity, globally clipped to a sky/ground envelope of
`min(10 × global median, pooled max/min)` (the plot border turns red where pooled
samples exceed that clip), with a dashed global-median line. The visible axis is
bounded by the sky/ground clip and the per-glyph envelopes so one
extreme cannot stretch the scale. `private/examples/gen_devices.py` produces
`private/verify/public/devices.json` by calling `build_iceberg` per device and on
the pooled
sample.

---

## 4. Multi-category synchronization (design §4, §10)

Synchronization is a rendering-time concern. To compare categories on a shared
absolute axis, build each glyph with the same `z_min`/`z_max`/`resolution` and plot
them on one value axis; the underlying observations are unchanged.

---

## 5. Integration with SWI Communication Analysis

In the communication-analysis product, one swi_iceberg glyph represents the
response-latency distribution of one device over one defined time interval. The
glyph encodes no time; `device_id` and `start_time_ms`/`end_time_ms` live on the
consuming project's `latency_distribution` table, and the glyph's `median`, `madn`,
`population`, per-band `band_lo`/`band_hi`, and `topping`/`bottoming` are the
statistical payload associated with that record. The visualization semantics are
defined solely by this project.

---

## 6. Running / verification

Environment: conda env **`pktbuild`** (Python 3.12, NumPy 2.5, pandas 3.0, pytest 9).

```bash
conda run -n pktbuild python -m pytest private/tests -q      # statistical invariants
conda run -n pktbuild python private/examples/demo.py        # single-glyph ASCII/JSON
conda run -n pktbuild python private/examples/gen_devices.py # fleet data -> devices.json

cd private/verify && npm install && npm run dev              # browser SVG verification
```

The Python layer proves the statistics; the `private/verify/` harness proves the rendering
contract visually against the same payloads (count conservation, six bands,
normalized widths, band height = observed range inside the envelope,
Topping/Bottoming).
