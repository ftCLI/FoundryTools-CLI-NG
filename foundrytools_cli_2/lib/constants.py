from dataclasses import dataclass
import typing as t
from pathlib import Path


@dataclass
class TTFontInitOptions:
    """
    A class that specifies how to initialize the font.
    """

    lazy: t.Optional[bool] = None
    recalc_timestamp: bool = False
    recalc_bboxes: bool = True


@dataclass
class TTFontSaveOptions:
    """
    A class that specifies how to save the font.
    """

    output_dir: t.Optional[Path] = None
    overwrite: bool = False
    reorder_tables: bool = True
