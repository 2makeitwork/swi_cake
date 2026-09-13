"""swi_iceberg — a median-centered, MADN-scaled robust band glyph.

Public API:

    from swi_iceberg import build_iceberg, IcebergGlyph, InsufficientDataError
    from swi_iceberg import to_ascii, to_json, to_raster

Statistical semantics are defined by the swi_iceberg specification
(swi_iceberg.md, CC BY 4.0). This code is licensed under the Apache License,
Version 2.0 (LICENSE-CODE).
"""

from __future__ import annotations

from .core import (
    InsufficientDataError,
    IcebergGlyph,
    MADN_CALIBRATION,
    MIN_SAMPLES,
    build_iceberg,
)
from .render import to_ascii, to_json, to_raster

__version__ = "1.0.0"

__all__ = [
    "build_iceberg",
    "IcebergGlyph",
    "InsufficientDataError",
    "MIN_SAMPLES",
    "MADN_CALIBRATION",
    "to_ascii",
    "to_json",
    "to_raster",
    "__version__",
]
