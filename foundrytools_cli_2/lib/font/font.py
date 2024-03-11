import typing as t
from io import BytesIO
from pathlib import Path

from dehinter.font import dehint
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.ttLib.tables._f_v_a_r import Axis, NamedInstance

from foundrytools_cli_2.lib.constants import (
    FVAR_TABLE_TAG,
    HEAD_TABLE_TAG,
    MAX_UPM,
    MIN_UPM,
    OTF_EXTENSION,
    PS_SFNT_VERSION,
    TT_SFNT_VERSION,
    TTF_EXTENSION,
    WOFF2_EXTENSION,
    WOFF2_FLAVOR,
    WOFF_EXTENSION,
    WOFF_FLAVOR,
)
from foundrytools_cli_2.lib.font.tables import HeadTable, OS2Table
from foundrytools_cli_2.lib.otf.cffsubr import cff_desubr, cff_subr
from foundrytools_cli_2.lib.otf.otf_builder import build_otf
from foundrytools_cli_2.lib.otf.t2_charstrings import fix_charstrings, quadratics_to_cubics
from foundrytools_cli_2.lib.ttf.decomponentize import decomponentize
from foundrytools_cli_2.lib.ttf.ttf_builder import build_ttf
from foundrytools_cli_2.lib.utils.path_tools import get_temp_file_path


class Font:  # pylint: disable=too-many-public-methods
    """
    The ``Font`` class adds additional properties and methods to the ``fontTools.ttLib.TTFont``
    class.
    """

    def __init__(
        self,
        source: t.Union[str, Path, BytesIO, TTFont],
        lazy: t.Optional[bool] = None,
        recalc_bboxes: bool = True,
        recalc_timestamp: bool = False,
        modified: bool = False,
    ) -> None:
        """
        Initialize a Font object.

        Args:
            source: A path to a font file, a BytesIO object or a TTFont object.
            lazy (bool): If lazy is set to True, many data structures are loaded lazily, upon access
                only. If it is set to False, many data structures are loaded immediately. The
                default is ``lazy=None`` which is somewhere in between.
            recalc_bboxes (bool): If true (the default), recalculates ``glyf``, ``CFF ``, ``head``
                bounding box values and ``hhea``/``vhea`` min/max values on save. Also compiles the
                glyphs on importing, which saves memory consumption and time.
            recalc_timestamp (bool): If true, sets the ``modified`` timestamp in the ``head`` table
                on save. Default is False.
        """

        self._file: t.Optional[Path] = None
        self._bytesio: t.Optional[BytesIO] = None
        self._ttfont: t.Optional[TTFont] = None
        self._temp_file: Path = get_temp_file_path()
        self.modified = modified

        if isinstance(source, (str, Path)):
            self._init_from_file(source, lazy, recalc_bboxes, recalc_timestamp)
        elif isinstance(source, BytesIO):
            self._init_from_bytesio(source, lazy, recalc_bboxes, recalc_timestamp)
        elif isinstance(source, TTFont):
            self._init_from_ttfont(source, lazy, recalc_bboxes, recalc_timestamp)
        else:
            raise ValueError(
                f"Invalid source type {type(source)}. Expected str, Path, BytesIO, or TTFont."
            )

    def _init_from_file(
        self,
        path: t.Union[str, Path],
        lazy: t.Optional[bool],
        recalc_bboxes: bool,
        recalc_timestamp: bool,
    ) -> None:
        self._file = Path(path).resolve()
        self._ttfont = TTFont(
            path, lazy=lazy, recalcBBoxes=recalc_bboxes, recalcTimestamp=recalc_timestamp
        )

    def _init_from_bytesio(
        self, bytesio: BytesIO, lazy: t.Optional[bool], recalc_bboxes: bool, recalc_timestamp: bool
    ) -> None:
        self._bytesio = bytesio
        self._ttfont = TTFont(
            bytesio, lazy=lazy, recalcBBoxes=recalc_bboxes, recalcTimestamp=recalc_timestamp
        )
        bytesio.close()

    def _init_from_ttfont(
        self, ttfont: TTFont, lazy: t.Optional[bool], recalc_bboxes: bool, recalc_timestamp: bool
    ) -> None:
        self._bytesio = BytesIO()
        ttfont.save(self._bytesio, reorderTables=False)
        self._bytesio.seek(0)
        self._ttfont = TTFont(
            self._bytesio, lazy=lazy, recalcBBoxes=recalc_bboxes, recalcTimestamp=recalc_timestamp
        )

    def __enter__(self) -> "Font":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self.close()

    def __repr__(self) -> str:
        return f"<Font file={self.file}, bytesio={self.bytesio}, ttfont={self.ttfont}>"

    @property
    def file(self) -> t.Optional[Path]:
        """
        Get the file path of the font.

        :return: The file path of the font.
        """
        return self._file

    @property
    def bytesio(self) -> t.Optional[BytesIO]:
        """
        Get the BytesIO object of the font.

        :return: The BytesIO object of the font.
        """
        return self._bytesio

    @property
    def ttfont(self) -> TTFont:
        """
        Get the underlying TTFont object.
        """
        return self._ttfont

    @property
    def temp_file(self) -> Path:
        """
        Get the temporary file path of the font.

        :return: The temporary file path of the font.
        """
        return self._temp_file

    @property
    def is_ps(self) -> bool:
        """
        Check if the font has PostScript outlines font.

        :return: True if the font is a PostScript font, False otherwise.
        """
        return self.ttfont.sfntVersion == PS_SFNT_VERSION

    @property
    def is_tt(self) -> bool:
        """
        Check if the font has TrueType outlines.

        :return: True if the font is a TrueType font, False otherwise.
        """
        return self.ttfont.sfntVersion == TT_SFNT_VERSION

    @property
    def is_woff(self) -> bool:
        """
        Check if the font is a WOFF font.

        :return: True if the font is a WOFF font, False otherwise.
        """
        return self.ttfont.flavor == WOFF_FLAVOR

    @property
    def is_woff2(self) -> bool:
        """
        Check if the font is a WOFF2 font.

        :return: True if the font is a WOFF2 font, False otherwise.
        """
        return self.ttfont.flavor == WOFF2_FLAVOR

    @property
    def is_sfnt(self) -> bool:
        """
        Check if the font is a SFNT font.

        :return: True if the font is a SFNT font, False otherwise.
        """
        return self.ttfont.flavor is None

    @property
    def is_static(self) -> bool:
        """
        Check if the font is a static font.

        :return: True if the font is a static font, False otherwise.
        """
        return self.ttfont.get(FVAR_TABLE_TAG) is None

    @property
    def is_variable(self) -> bool:
        """
        Check if the font is a variable font.

        :return: True if the font is a variable font, False otherwise.
        """
        return self.ttfont.get(FVAR_TABLE_TAG) is not None

    @property
    def is_italic(self) -> bool:
        """
        Check if the font is italic.

        :return: True if the font is italic, False otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)
        return os_2.is_italic and head.is_italic

    @property
    def is_oblique(self) -> bool:
        """
        Check if the font is oblique.

        :return: True if the font is oblique, False otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        return os_2.is_oblique

    @property
    def is_bold(self) -> bool:
        """
        Check if the font is bold.

        :return: True if the font is bold, False otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)
        return os_2.is_bold and head.is_bold

    @property
    def is_regular(self) -> bool:
        """
        Check if the font is regular.

        :return: True if the font is regular, False otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        return os_2.is_regular

    def set_italic(self, value: bool) -> None:
        """
        Set the italic bit in the macStyle field of the 'head' table.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)

        if value:
            os_2.is_italic = True
            head.is_italic = True
            os_2.is_regular = False
        else:
            os_2.is_italic = False
            head.is_italic = False
            if not self.is_bold:
                os_2.is_regular = True

    def set_bold(self, value: bool) -> None:
        """
        Set the bold bit in the macStyle field of the 'head' table.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)

        if value:
            os_2.is_bold = True
            head.is_bold = True
            os_2.is_regular = False
        else:
            os_2.is_bold = False
            head.is_bold = False
            if not self.is_italic:
                os_2.is_regular = True

    def set_regular(self, value: bool) -> None:
        """
        Set the regular bit in the macStyle field of the 'head' table.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)

        if value:
            os_2.is_bold = False
            os_2.is_italic = False
            head.is_bold = False
            head.is_italic = False
            os_2.is_regular = True
        else:
            if self.is_bold or self.is_italic:
                os_2.is_regular = False

    def set_oblique(self, value: bool) -> None:
        """
        Set the oblique bit in the macStyle field of the 'head' table.
        """
        os_2 = OS2Table(self.ttfont)
        os_2.is_oblique = value

    def save(
        self,
        file: t.Union[str, Path, BytesIO],
        reorder_tables: t.Optional[bool] = True,
    ) -> None:
        """
        Save the font to a file.

        Args:
            file: The file path to save the font to.
            reorder_tables: If true (the default), reorder the tables, sorting them by tag
                (recommended by the OpenType specification). If false, retain the original font
                order. If None, reorder by table dependency (fastest).
        """
        self.ttfont.save(file, reorderTables=reorder_tables)

    def save_to_temp_file(self, reorder_tables: t.Optional[bool] = True) -> None:
        """
        Save the font to a temporary file.

        Args:
            reorder_tables: If true (the default), reorder the tables, sorting them by tag
                (recommended by the OpenType specification). If false, retain the original font
                order. If None, reorder by table dependency (fastest).
        """
        self.save(self._temp_file, reorder_tables=reorder_tables)

    def close(self) -> None:
        """
        Close the underlying TTFont object.
        """
        self.ttfont.close()
        self._temp_file.unlink(missing_ok=True)

    def get_real_extension(self) -> str:
        """
        Get the real extension of the font. If the font is a web font, the extension will be
        determined by the font flavor. If the font is a SFNT font, the extension will be determined
        by the sfntVersion attribute.

        Returns:
            The extension of the font.
        """

        # Order of the if statements is important. WOFF and WOFF2 must be checked before OTF and
        # TTF.
        if self.is_woff:
            return WOFF_EXTENSION
        if self.is_woff2:
            return WOFF2_EXTENSION
        if self.is_ps:
            return OTF_EXTENSION
        if self.is_tt:
            return TTF_EXTENSION
        return self.ttfont.sfntVersion

    def make_out_file_name(
        self,
        file: t.Optional[Path] = None,
        output_dir: t.Optional[Path] = None,
        overwrite: bool = True,
        extension: t.Optional[str] = None,
        suffix: str = "",
    ) -> Path:
        """
        Get output file for a Font object. If ``output_dir`` is not specified, the output file will
        be saved in the same directory as the input file. It the output file already exists and
        ``overwrite`` is False, file name will be incremented by adding a number preceded by '#'
        before the extension until a non-existing file name is found. If ``suffix`` is specified,
        it will be appended to the file name. If the suffix is already present, it will be removed
        before adding it again.

        Args:
            file: The file name to use for the output file. If not specified, the file name will be
                determined by the input file.
            output_dir: Path to the output directory.
            overwrite: A boolean indicating whether to overwrite existing files.
            extension: An optional extension to use for the output file. If not specified, the
                extension will be determined by the font type.
            suffix: An optional suffix to append to the file name.

        Returns:
            A Path object pointing to the output file.
        """

        if file is None and self.file is None:
            raise ValueError(
                "Cannot get output file for a BytesIO object without providing a file name."
            )

        file = file or self.file
        if not isinstance(file, Path):
            raise ValueError("File must be a Path object.")

        out_dir = output_dir or file.parent
        extension = extension or self.get_real_extension()
        file_name = file.stem + extension

        # Clean up the file name by removing the extensions used as file name suffix as added by
        # possible previous conversions.
        if suffix != "":
            for ext in [OTF_EXTENSION, TTF_EXTENSION, WOFF2_EXTENSION, WOFF_EXTENSION]:
                file_name = file_name.replace(ext, "")

        out_file = Path(
            makeOutputFileName(
                input=file_name,
                outputDir=out_dir,
                extension=extension,
                overWrite=overwrite,
                suffix=suffix,
            )
        )
        return out_file

    def get_axes(self) -> t.List[Axis]:
        """
        Get axes from a variable font.

        :return: Axes.
        """
        if not self.is_variable:
            raise NotImplementedError("Not a variable font.")

        return [axis for axis in self.ttfont[FVAR_TABLE_TAG].axes if axis.flags == 0]

    def get_instances(self) -> t.List[NamedInstance]:
        """
        Get named instances from a variable font.

        :return: Named instances.
        """
        if not self.is_variable:
            raise NotImplementedError("Not a variable font.")

        return self.ttfont[FVAR_TABLE_TAG].instances

    def to_woff(self) -> None:
        """
        Convert a font to WOFF.
        """
        if self.is_woff:
            raise NotImplementedError("Font is already a WOFF font.")

        self.ttfont.flavor = WOFF_FLAVOR
        self.modified = True

    def to_woff2(self) -> None:
        """
        Convert a font to WOFF2.
        """
        if self.is_woff2:
            raise NotImplementedError("Font is already a WOFF2 font.")

        self.ttfont.flavor = WOFF2_FLAVOR
        self.modified = True

    def to_ttf(self, max_err: float = 1.0, reverse_direction: bool = True) -> None:
        """
        Convert a font to TrueType.
        """
        if self.is_tt:
            raise ValueError("Font is already a TrueType font.")
        if self.is_variable:
            raise NotImplementedError("Conversion to TrueType is not supported for variable fonts.")

        build_ttf(font=self.ttfont, max_err=max_err, reverse_direction=reverse_direction)
        self.modified = True

    def to_otf(self, tolerance: float = 1.0) -> None:
        """
        Convert a font to PostScript.
        """
        if self.is_ps:
            raise ValueError("Font is already a PostScript font.")
        if self.is_variable:
            raise NotImplementedError(
                "Conversion to PostScript is not supported for variable fonts."
            )

        charstrings = quadratics_to_cubics(font=self.ttfont, tolerance=tolerance)
        build_otf(font=self.ttfont, charstrings_dict=charstrings)
        self.modified = True

    def to_sfnt(self) -> None:
        """
        Convert a font to SFNT.
        """
        if self.is_sfnt:
            raise NotImplementedError("Font is already a SFNT font.")

        self.ttfont.flavor = None
        self.modified = True

    def tt_decomponentize(self) -> None:
        """
        Decomponentize a TrueType font.
        """
        if not self.is_tt:
            raise NotImplementedError("Decomponentization is only supported for TrueType fonts.")

        decomponentize(self.ttfont)
        self.modified = True

    def tt_remove_hints(self) -> None:
        """
        Remove hints from a TrueType font.
        """
        if not self.is_tt:
            raise NotImplementedError("Only TrueType fonts are supported.")

        dehint(self.ttfont)
        self.modified = True

    def tt_scale_upem(self, new_upem: int) -> None:
        """
        Scale the font's unitsPerEm value to the given value.

        Args:
            new_upem (int): The new unitsPerEm value.
        """
        if not self.is_tt:
            raise NotImplementedError("Scaling upem is only supported for TrueType fonts.")

        if new_upem < MIN_UPM or new_upem > MAX_UPM:
            raise ValueError(f"units_per_em must be in the range {MAX_UPM} to {MAX_UPM}.")

        if self.ttfont[HEAD_TABLE_TAG].unitsPerEm == new_upem:
            raise ValueError(f"Font already has {new_upem} units per em. No need to scale upem.")

        scale_upem(self.ttfont, new_upem=new_upem)
        self.modified = True

    def ps_correct_contours(self, min_area: int = 25) -> t.List[str]:
        """
        Correct the contours of a PostScript font by removing tiny paths and correcting the
        direction of paths.

        :param min_area: The minimum area of a path to be retained.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "PS Contour correction is only supported for PostScript flavored fonts."
            )

        charstrings, modified_glyphs = fix_charstrings(font=self.ttfont, min_area=min_area)
        if not modified_glyphs:
            return []
        build_otf(font=self.ttfont, charstrings_dict=charstrings)
        self.modified = True
        return modified_glyphs

    def ps_subroutinize(self) -> None:
        """
        Subroutinize a PostScript font.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "Subroutinization is only supported for PostScript flavored fonts."
            )
        cff_subr(font=self.ttfont)
        self.modified = True

    def ps_desubroutinize(self) -> None:
        """
        Desubroutinize a PostScript font.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "Desubroutinization is only supported for PostScript flavored fonts."
            )
        cff_desubr(font=self.ttfont)
        self.modified = True
