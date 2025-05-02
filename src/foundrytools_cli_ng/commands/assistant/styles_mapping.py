import json
from pathlib import Path
from typing import Literal

from foundrytools.constants import (
    MAX_US_WEIGHT_CLASS,
    MAX_US_WIDTH_CLASS,
    MIN_US_WEIGHT_CLASS,
    MIN_US_WIDTH_CLASS,
)


class StylesMappingError(Exception):
    """An exception class for the StylesMapping"""


class StylesMappingHandler:
    """A class to handle the styles mapping file"""

    def __init__(self, input_path: Path):
        self.file = self.get_file_path(input_path)
        try:
            self.data = self.read_file()
        except StylesMappingError:
            self.reset_defaults()

    @classmethod
    def get_file_path(cls, input_path: Path) -> Path:
        """Returns the path to the styles mapping file"""
        return input_path / ".ftCLI" / "styles_mapping.json"

    def read_file(self) -> dict:
        """Opens the styles mapping file and returns its data as a dictionary"""
        try:
            with self.file.open(encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            raise StylesMappingError(f"Error reading the file {self.file}: {e}") from e

    def save_to_file(self, data: dict) -> None:
        """Saves the styles mapping file"""
        temp_file = self.file.with_suffix(".tmp")
        try:
            self.file.parent.mkdir(exist_ok=True, parents=True)
            self.file.touch(exist_ok=True)
            temp_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
            temp_file.replace(self.file)
        except Exception as e:
            temp_file.unlink(missing_ok=True)
            raise StylesMappingError(f"An error occurred while saving the file: {e}") from e

    def reset_defaults(self) -> None:
        """Writes the default values to the styles mapping file"""
        self.data = _DEFAULT_DATA
        self.save_to_file(self.data)

    @staticmethod
    def _validate_names(names: list[str]) -> None:
        """Validates the names list"""
        if len(names) != 2:
            raise StylesMappingError("Names list must contain exactly 2 names")

    @staticmethod
    def _validate_range(value: int, min_value: int, max_value: int) -> None:
        """Validates the range of a value"""
        if not min_value <= value <= max_value:
            raise StylesMappingError(f"Value {value} is out of range ({min_value}, {max_value})")

    def set_weight(self, weight: int, names: list[str]) -> None:
        """
        Adds a 'weight' entry to the styles mapping file.

        Validates the provided weight value and names list, then associates the names
        with the specified weight in the styles mapping data. The names are sorted by
        length before being saved.

        Args:
            weight (int): The weight value to add.
            names (list[str]): A list of two names associated with the weight.

        Raises:
            StylesMappingError: If the weight is out of range or the names list does
            not contain exactly two names.
        """
        self._validate_range(weight, MIN_US_WEIGHT_CLASS, MAX_US_WEIGHT_CLASS)
        self._validate_names(names)
        self.data["weights"][weight] = sorted(names, key=len)
        self.save_to_file(self.data)

    def del_weight(self, weight: int) -> None:
        """
        Removes a 'weight' entry from the styles mapping data.

        Checks if the specified weight exists in the current styles mapping data. If found,
        deletes the entry and saves the updated data back to the file.

        Args:
            weight (int): The weight value to be removed.

        Raises:
            StylesMappingError: If the weight is not found in the styles mapping file.
        """
        if weight not in self.data["weights"]:
            raise StylesMappingError(f"Weight {weight} not found in the styles mapping file")
        del self.data["weights"][weight]
        self.save_to_file(self.data)

    def set_width(self, width: int, names: list[str]) -> None:
        """
        Sets a 'width' entry in the styles mapping file.

        Validates the provided width value and names list, then associates the names
        with the specified width in the styles mapping data. The names are sorted by
        length before being saved.

        Args:
            width (int): The width value to add.
            names (list[str]): A list of two names associated with the width.

        Raises:
            StylesMappingError: If the width is out of range or the names list does
            not contain exactly two names.
        """
        self._validate_range(width, MIN_US_WIDTH_CLASS, MAX_US_WIDTH_CLASS)
        self._validate_names(names)
        self.data["widths"][width] = sorted(names, key=len)
        self.save_to_file(self.data)

    def del_width(self, width: int) -> None:
        """
        Removes a 'width' entry from the styles mapping file.

        Checks if the specified width exists in the current styles mapping data. If found, deletes
        the entry and saves the updated data back to the file.

        Args:
            width (int): The width value to be removed.
        Raises:
            StylesMappingError: If the width is not found in the styles mapping file.
        """
        if width not in self.data["widths"]:
            raise StylesMappingError(f"Width {width} not found in the styles mapping file")
        del self.data["widths"][width]
        self.save_to_file(self.data)

    def set_slope(self, slope: Literal["upright", "italic", "oblique"], names: list[str]) -> None:
        """
        Sets a 'slope' entry to the styles mapping file.

        Validates the provided names list and associates it with the specified slope type
        ('upright', 'italic', or 'oblique') in the styles mapping data. The names are sorted by
        length before being saved.

        Args:
            slope (Literal["upright", "italic", "oblique"]): The slope type to add.
            names (list[str]): A list of two names associated with the slope.
        Raises:
            StylesMappingError: If the names list does not contain exactly two names.
        """
        self._validate_names(names)
        self.data["slopes"][slope] = sorted(names, key=len)
        self.save_to_file(self.data)


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

_DEFAULT_SLOPES = {
    "upright": ["", ""],
    "italic": ["It", "Italic"],
    "oblique": ["Ob", "Oblique"],
}

_DEFAULT_DATA = {
    "weights": _DEFAULT_WEIGHTS,
    "widths": _DEFAULT_WIDTHS,
    "slopes": _DEFAULT_SLOPES,
}
