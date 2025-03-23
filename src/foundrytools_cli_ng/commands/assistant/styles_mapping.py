import json
import os
from pathlib import Path
from typing import Union

from foundrytools_cli_ng.utils.logger import logger


class StylesMappingHandler:
    """
    A class to handle the styles mapping file
    """

    def __init__(self, input_path: Path):
        self.file = Path.joinpath(input_path, ".ftCLI", "styles_mapping.json")
        if not self.file.exists():
            self.reset_defaults()

    def get_data(self) -> dict[str, Union[dict[int, list[str]], list[str]]]:
        """
        Opens the styles mapping file and returns its data as a dictionary

        :return: A dictionary of the styles mapping file.
        """
        try:
            with self.file.open(encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"An error occurred while reading the file: {self.file}: {e}")
            return {}
        except RuntimeError as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {}

    def save(self, data: dict) -> None:
        """
        Saves the styles mapping file

        :param data: The styles mapping dictionary to save
        :type data: dict
        """
        temp_file = self.file.with_suffix(".tmp")
        try:
            self.file.parent.mkdir(exist_ok=True)
            temp_file.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))
            os.replace(self.file, temp_file)
        except OSError as e:
            print(f"An error occurred while saving the file: {e}")
            if temp_file.exists():
                temp_file.unlink()

    def reset_defaults(self) -> None:
        """
        Writes the default values to the styles mapping file
        """
        default_data = {
            "weights": _DEFAULT_WEIGHTS,
            "widths": _DEFAULT_WIDTHS,
            "italics": _DEFAULT_ITALICS,
            "obliques": _DEFAULT_OBLIQUES,
        }
        self.save(default_data)


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
