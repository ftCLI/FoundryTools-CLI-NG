import json
from pathlib import Path

from pydantic import BaseModel, ValidationError, field_validator


class StylesMapping(BaseModel):
    weights: dict[int, list[str]]
    widths: dict[int, list[str]]
    italics: list[str]
    obliques: list[str]

    @field_validator("weights", mode="before")
    def check_weights_keys(cls, v):
        v = {int(k): val for k, val in v.items()}
        for key in v.keys():
            if not (1 <= key <= 1000):
                raise ValueError(f"Weight key {key} must be an integer between 1 and 1000.")
        return v

    @field_validator("widths", mode="before")
    def check_widths_keys(cls, v):
        v = {int(k): val for k, val in v.items()}
        for key in v.keys():
            if not (1 <= key <= 9):
                raise ValueError(f"Width key {key} must be an integer between 1 and 9.")
        return v

    @field_validator("weights", "widths", mode="before")
    def check_length(cls, v, field):
        for key, value in v.items():
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError(f"Each entry in {field} must have exactly two items.")
        return v

    @field_validator("italics", "obliques", mode="before")
    def check_italics_obliques_length(cls, v, field):
        if not isinstance(v, list) or len(v) != 2:
            raise ValueError(f"{field.name.capitalize()} must have exactly two items.")
        return v


class StylesMappingError(Exception):
    """An exception class for the StylesMapping"""


class StylesMappingHandler:
    """A class to handle the styles mapping file"""

    def __init__(self, input_path: Path):
        self.file = Path.joinpath(input_path, ".ftCLI", "styles_mapping.json")
        if not self.file.exists():
            self.file.parent.mkdir(exist_ok=True, parents=True)
            self.file.touch()
            self.reset_defaults()
        else:
            self.data = self.read_file()

    def read_file(self) -> StylesMapping:
        """Opens the styles mapping file and returns its data as a dictionary"""
        try:
            with self.file.open(encoding="utf-8") as f:
                data = json.load(f)
                return StylesMapping(**data)
        except (ValidationError, ValueError) as e:
            raise StylesMappingError(f"Pydantic validation error: {e}") from e
        except Exception as e:
            raise StylesMappingError(
                f"An error occurred while reading the file: {self.file}: {e}"
            ) from e

    def save_to_file(self, data: StylesMapping) -> None:
        """Saves the styles mapping file"""
        temp_file = self.file.with_suffix(".tmp")
        try:
            json_data = data.model_dump_json()
            formatted_json = json.dumps(json.loads(json_data), indent=4, ensure_ascii=False)
            temp_file.write_text(formatted_json, encoding="utf-8")
            temp_file.rename(self.file)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise StylesMappingError(f"An error occurred while saving the file: {e}") from e

    def reset_defaults(self) -> None:
        """Writes the default values to the styles mapping file"""
        self.data = _DEFAULT_DATA
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

_DEFAULT_ITALICS = ["It", "Italic"]

_DEFAULT_OBLIQUES = ["Obl", "Oblique"]

_DEFAULT_DATA = StylesMapping(
    weights=_DEFAULT_WEIGHTS,
    widths=_DEFAULT_WIDTHS,
    italics=_DEFAULT_ITALICS,
    obliques=_DEFAULT_OBLIQUES,
)
