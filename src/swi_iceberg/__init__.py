"""swi_iceberg — a median-centered, MADN-scaled robust band glyph.

Public API:

    from swi_iceberg import build_iceberg, IcebergGlyph, InsufficientDataError
    from swi_iceberg import to_ascii, to_json, to_raster
    from swi_iceberg import IcebergFeed  # streaming: batch then one-by-one
    from swi_iceberg import IcebergPipeline  # wait-out (2s) time-batched pipeline

Statistical semantics are defined by the swi_iceberg specification
(specification_swi_iceberg.md, CC BY 4.0). This code is licensed under the Apache License,
Version 2.0 (LICENSE-CODE).
"""

from __future__ import annotations

from .core import (
    InsufficientDataError,
    IcebergGlyph,
    MADN_CALIBRATION,
    MIN_SAMPLES,
    build_iceberg,
    global_zone_index,
)
from .render import to_ascii, to_json, to_raster, SPEC_VERSION, DISPLAY_VERSION
from .feed import IcebergFeed, IcebergPipeline

__version__ = "1.1.1"

__all__ = [
    "build_iceberg",
    "global_zone_index",
    "IcebergGlyph",
    "InsufficientDataError",
    "MIN_SAMPLES",
    "MADN_CALIBRATION",
    "to_ascii",
    "to_json",
    "to_raster",
    "SPEC_VERSION",
    "DISPLAY_VERSION",
    "IcebergFeed",
    "IcebergPipeline",
    "__version__",
]
