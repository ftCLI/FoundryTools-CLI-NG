import json
import os
from pathlib import Path
from typing import Union


class StylesMappingHandlerError(Exception):
    """
    An exception class for the StylesMappingHandler
    """


class StylesMappingHandler:
    """
    A class to handle the styles mapping file
    """

    def __init__(self, input_path: Path):
        self.file = Path.joinpath(input_path, ".ftCLI", "styles_mapping.json")
        if not self.file.exists():
            self.file.touch()
            self.reset_defaults()
        self.data = self.get_data()  # Load the data from the file

    def get_data(self) -> dict[str, Union[dict[int, list[str]], list[str]]]:
        """
        Opens the styles mapping file and returns its data as a dictionary

        :return: A dictionary of the styles mapping file.
        """
        try:
            with self.file.open(encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise StylesMappingHandlerError(f"An error occurred while reading the file: {self.file}: {e}")

    def save_to_file(self, data: dict) -> None:
        """
        Saves the styles mapping file

        :param data: The styles mapping dictionary to save
        :type data: dict
        """
        temp_file = self.file.with_suffix(".tmp")
        try:
            self.file.parent.mkdir(exist_ok=True)
            temp_file.touch()
            temp_file.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))
            os.replace(temp_file, self.file)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise StylesMappingHandlerError(f"An error occurred while saving the file: {e}")

    def reset_defaults(self) -> None:
        """
        Writes the default values to the styles mapping file
        """
        self.data = _DEFAULT_DATA
        self.save_to_file(_DEFAULT_DATA)


_DEFAULT_WEIGHTS = {
    250: ["Th", "Thin"],
    275: ["XLt", "ExtraLight"],
    300: ["Lt", "Light"],
    350: ["Bk", "Book"],
    400: ["Rg", "Regular"],
    500: ["Md", "Medium"],
    600: ["SBd", "SemiBold"],
    700: ["Bd", "Bold"],
    800: ["XBd", "ExtraBold"],
    850: ["Hvy", "Heavy"],
    900: ["Blk", "Black"],
    950: ["Ult", "Ultra"],
}

_DEFAULT_WIDTHS = {
    1: ["Cm", "Compressed"],
    2: ["XCn", "ExtraCondensed"],
    3: ["Cn", "Condensed"],
    4: ["Nr", "Narrow"],
    5: ["Nor", "Normal"],
    6: ["Wd", "Wide"],
    7: ["Ext", "Extended"],
    8: ["XExt", "ExtraExtended"],
    9: ["Exp", "Expanded"],
}

_DEFAULT_ITALICS = ["It", "Italic"]

_DEFAULT_OBLIQUES = ["Obl", "Oblique"]

_DEFAULT_DATA = {
    "weights": _DEFAULT_WEIGHTS,
    "widths": _DEFAULT_WIDTHS,
    "italics": _DEFAULT_ITALICS,
    "obliques": _DEFAULT_OBLIQUES,
}
