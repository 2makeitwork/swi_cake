"""swi_iceberg rendering layer.

Pure functions that turn a :class:`~swi_iceberg.core.IcebergGlyph` into a display
form. Population is rendered as horizontal width; each band's drawn height is its
observed value range; the glyph body spans the six MADN bands within +/-3, with
Topping/Bottoming as the retained out-of-envelope counts. Nothing here mutates the
statistical result.

Code is licensed under the Apache License, Version 2.0 (see LICENSE-CODE).
"""

from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np

from .core import IcebergGlyph

__all__ = ["to_ascii", "to_json", "to_raster"]


def _json_float(x: float) -> Any:
    """Return the float, or None for NaN (empty band has no observed extent)."""
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)


def to_ascii(glyph: IcebergGlyph, width: int = 40) -> str:
    """Dependency-free textual rendering, for tests and quick eyeballs."""
    lines = [
        f"swi_iceberg  mode={glyph.mode}  N={glyph.n}  median={glyph.median:g}  "
        f"madn={glyph.madn:g}  res={glyph.resolution:g}",
    ]
    if glyph.mode == "collapsed":
        lines.append("  (zero-MAD collapse: a single line at the median)")
        lines.append(f"{glyph.value:>8} |{'█' * width}")
        return "\n".join(lines)

    max_pop = int(glyph.population.max()) if glyph.population.size else 0
    scale = width / max_pop if max_pop > 0 else 0
    lines.append(f"  TOPPING    {glyph.topping}")
    for idx in range(len(glyph.population) - 1, -1, -1):  # high MADN at top
        count = int(glyph.population[idx])
        run = int(round(count * scale))
        lo, hi = glyph.edges[idx], glyph.edges[idx + 1]
        olo, ohi = glyph.band_lo[idx], glyph.band_hi[idx]
        obs = "-" if math.isnan(olo) else f"{olo:g}..{ohi:g}"
        lines.append(f"  [{lo:+g},{hi:+g}) |{'█' * run} ({count}) obs={obs}")
    lines.append(f"  BOTTOMING  {glyph.bottoming}")
    return "\n".join(lines)


def to_raster(glyph: IcebergGlyph, height_px: int, width_px: int, min_visible_px: int = 1) -> np.ndarray:
    """Constant-height-band bitmap from the population vector (a render artifact)."""
    if height_px <= 0 or width_px <= 0:
        raise ValueError("height_px and width_px must be positive")
    raster = np.zeros((height_px, width_px), dtype=np.uint8)
    if glyph.mode == "collapsed":
        raster[:] = 255
        return raster
    rows = int(glyph.population.size)
    if rows == 0:
        return raster
    max_pop = int(glyph.population.max())
    for idx in range(rows):
        count = int(glyph.population[idx])
        if count == 0:
            continue
        y0 = max(0, min(height_px, int(np.floor(idx * height_px / rows))))
        y1 = max(y0 + 1, min(height_px, int(np.floor((idx + 1) * height_px / rows))))
        fill = min(width_px, max(min_visible_px, int(round(count / max_pop * width_px))))
        raster[y0:y1, :fill] = 255
    return raster


def to_json(glyph: IcebergGlyph) -> Dict[str, Any]:
    """Canonical JSON payload (statistics only; no pixels)."""
    population = [int(c) for c in glyph.population.tolist()]
    n = int(glyph.n)
    normalized = [pop / n if n else 0.0 for pop in population]
    return {
        "mode": glyph.mode,
        "n": n,
        "median": glyph.median,
        "madn": glyph.madn,
        "resolution": glyph.resolution,
        "z_min": glyph.z_min,
        "z_max": glyph.z_max,
        "lower": glyph.lower,
        "upper": glyph.upper,
        "edges": [float(e) for e in glyph.edges.tolist()],
        "population": population,
        "normalized": normalized,
        # Observed value range per band (drives the band's drawn height).
        "band_lo": [_json_float(float(v)) for v in glyph.band_lo.tolist()],
        "band_hi": [_json_float(float(v)) for v in glyph.band_hi.tolist()],
        "topping": int(glyph.topping),
        "bottoming": int(glyph.bottoming),
        "value": glyph.value,
        "spec_version": "1.0",
    }
