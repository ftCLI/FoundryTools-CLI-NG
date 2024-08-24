import typing as t

from foundrytools_cli_2.lib.font.font import Font
from foundrytools_cli_2.lib.font.tables.cff_ import CFFTable


def set_names(font: Font, **kwargs: t.Dict[str, str]) -> None:
    """
    Set the provided values in the CFF table of a font.

    Args:
        font (Font): The font to set the values in.
        kwargs (Dict[str, str]): The values to set in the CFF table.
    """

    cff_table = CFFTable(font.ttfont)
    cff_table.set_names(**kwargs)
    font.modified = cff_table.modified


def del_names(font: Font, **kwargs: t.Dict[str, str]) -> None:
    """
    Delete the provided names from the CFF table of a font.

    Args:
        font (Font): The font to delete the names from.
        kwargs (Dict[str, str]): The names to delete from the CFF table TopDict.
    """

    cff_table = CFFTable(font.ttfont)
    cff_table.del_top_dict_names(**kwargs)
    font.modified = cff_table.modified
