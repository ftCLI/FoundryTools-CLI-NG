import json
from itertools import product
from pathlib import Path
from typing import Literal

from foundrytools.constants import (
    MAX_US_WEIGHT_CLASS,
    MAX_US_WIDTH_CLASS,
    MIN_US_WEIGHT_CLASS,
    MIN_US_WIDTH_CLASS,
)


def _normalize_style_permutations(
    style_permutations: dict[str, tuple[int, int, str | None]],
) -> dict[str, tuple[int, int, str | None]]:
    """
    Normalize the style permutations by converting all keys to lowercase.
    """
    return {
        style_name.lower(): (weight, width, slope)
        for style_name, (weight, width, slope) in style_permutations.items()
    }


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
        """Adds a weight to the styles mapping file"""
        self._validate_range(weight, MIN_US_WEIGHT_CLASS, MAX_US_WEIGHT_CLASS)
        self._validate_names(names)
        self.data["weights"][weight] = sorted(names, key=len)
        self.save_to_file(self.data)

    def set_width(self, width: int, names: list[str]) -> None:
        """Adds a width to the styles mapping file"""
        self._validate_range(width, MIN_US_WIDTH_CLASS, MAX_US_WIDTH_CLASS)
        self._validate_names(names)
        self.data["widths"][width] = sorted(names, key=len)
        self.save_to_file(self.data)

    def set_slope(self, slope: Literal["italic", "oblique"], names: list[str]) -> None:
        """Adds a slope to the styles mapping file"""
        self._validate_names(names)
        self.data["slopes"][slope] = sorted(names, key=len)
        self.save_to_file(self.data)

    def del_weight(self, weight: int) -> None:
        """Deletes a weight from the styles mapping file"""
        if weight not in self.data["weights"]:
            raise StylesMappingError(f"Weight {weight} not found in the styles mapping file")
        del self.data["weights"][weight]
        self.save_to_file(self.data)

    def del_width(self, width: int) -> None:
        """Deletes a width from the styles mapping file"""
        if width not in self.data["widths"]:
            raise StylesMappingError(f"Width {width} not found in the styles mapping file")
        del self.data["widths"][width]
        self.save_to_file(self.data)

    def generate_style_permutations(self) -> dict[str, tuple[int, int, str | None]]:
        """
        Generate style permutations with flexible naming patterns, including:
        - Mixed short/long forms
        - Different component orderings
        - Implicit Normal width and Regular weight

        Returns a dictionary mapping style names to (weight, width, slope) values.
        """
        result = {}

        # Get component data
        weights = self.data["weights"]
        widths = self.data["widths"]
        slopes = self.data["slopes"]

        # Constants for default/implicit values
        default_weight = 400  # Regular
        default_width = 5  # Normal

        # Add single component names (implicit width and weight)

        # Just weight names (implicit Normal width, no slope)
        for weight_val, weight_names in weights.items():
            for name in weight_names:
                result[name] = (int(weight_val), default_width, None)

        # Just width names (implicit Regular weight, no slope)
        for width_val, width_names in widths.items():
            for name in width_names:
                result[name] = (default_weight, int(width_val), None)

        # Just slope names (implicit Normal width and Regular weight)
        for slope_name, slope_names in slopes.items():
            for name in slope_names:
                result[name] = (default_weight, default_width, slope_name)

        # Two-component combinations

        # Weight-Width combinations
        for (weight_val, weight_names), (width_val, width_names) in product(
            weights.items(), widths.items()
        ):
            w_short, w_long = width_names
            wt_short, wt_long = weight_names

            # All combinations of short/long
            result[w_short + wt_short] = (int(weight_val), int(width_val), None)
            result[w_short + wt_long] = (int(weight_val), int(width_val), None)
            result[w_long + wt_short] = (int(weight_val), int(width_val), None)
            result[w_long + wt_long] = (int(weight_val), int(width_val), None)

            # Reverse order
            result[wt_short + w_short] = (int(weight_val), int(width_val), None)
            result[wt_short + w_long] = (int(weight_val), int(width_val), None)
            result[wt_long + w_short] = (int(weight_val), int(width_val), None)
            result[wt_long + w_long] = (int(weight_val), int(width_val), None)

        # Weight-Slope combinations (implicit Normal width)
        for (weight_val, weight_names), (slope_name, slope_names) in product(
            weights.items(), slopes.items()
        ):
            wt_short, wt_long = weight_names
            s_short, s_long = slope_names

            result[wt_short + s_short] = (int(weight_val), default_width, slope_name)
            result[wt_long + s_long] = (int(weight_val), default_width, slope_name)
            result[s_short + wt_short] = (int(weight_val), default_width, slope_name)
            result[s_long + wt_long] = (int(weight_val), default_width, slope_name)

        # Width-Slope combinations (implicit Regular weight)
        for (width_val, width_names), (slope_name, slope_names) in product(
            widths.items(), slopes.items()
        ):
            w_short, w_long = width_names
            s_short, s_long = slope_names

            result[w_short + s_short] = (default_weight, int(width_val), slope_name)
            result[w_long + s_long] = (default_weight, int(width_val), slope_name)
            result[s_short + w_short] = (default_weight, int(width_val), slope_name)
            result[s_long + w_long] = (default_weight, int(width_val), slope_name)

        # Three-component combinations (all existing implementations)
        for (weight_val, weight_names), (width_val, width_names), (
            slope_name,
            slope_names,
        ) in product(weights.items(), widths.items(), slopes.items()):
            w_short, w_long = width_names
            wt_short, wt_long = weight_names
            s_short, s_long = slope_names

            # Standard order: Width-Weight-Slope
            result[w_short + wt_short + s_short] = (int(weight_val), int(width_val), slope_name)
            result[w_short + wt_long + s_short] = (int(weight_val), int(width_val), slope_name)
            result[w_long + wt_short + s_short] = (int(weight_val), int(width_val), slope_name)
            result[w_long + wt_long + s_long] = (int(weight_val), int(width_val), slope_name)

            # Other common orders
            result[s_short + w_short + wt_short] = (int(weight_val), int(width_val), slope_name)
            result[s_long + w_long + wt_long] = (int(weight_val), int(width_val), slope_name)
            result[w_short + s_short + wt_short] = (int(weight_val), int(width_val), slope_name)
            result[w_long + s_long + wt_long] = (int(weight_val), int(width_val), slope_name)
            result[wt_short + w_short + s_short] = (int(weight_val), int(width_val), slope_name)
            result[wt_long + w_long + s_long] = (int(weight_val), int(width_val), slope_name)

            # Mixed combinations
            result[w_short + wt_long + s_short] = (int(weight_val), int(width_val), slope_name)
            result[wt_short + w_long + s_long] = (int(weight_val), int(width_val), slope_name)
            result[s_short + w_long + wt_short] = (int(weight_val), int(width_val), slope_name)

        return result


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
    "italic": ["It", "Italic"],
    "oblique": ["Ob", "Oblique"],
}

_DEFAULT_DATA = {
    "weights": _DEFAULT_WEIGHTS,
    "widths": _DEFAULT_WIDTHS,
    "slopes": _DEFAULT_SLOPES,
}
