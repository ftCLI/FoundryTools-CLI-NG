import json
import shutil
from pathlib import Path

from pydantic import BaseModel, ValidationError, field_validator


class StylesMapping(BaseModel):
    weights: dict[int, list[str]]
    widths: dict[int, list[str]]
    italics: list[str]
    obliques: list[str]

    @field_validator("weights", "widths", mode="before")
    def check_length(cls, v, field):
        for key, value in v.items():
            if len(value) != 2:
                raise ValueError(f"Each entry in {field.name} must have exactly two items.")
        return v

    @field_validator("italics", "obliques", mode="before")
    def check_italics_obliques_length(cls, v, field):
        if len(v) != 2:
            raise ValueError(f"{field.name.capitalize()} must have exactly two items.")
        return v


class StylesMappingHandlerError(Exception):
    """An exception class for the StylesMappingHandler"""


class StylesMappingHandler:
    """A class to handle the styles mapping file"""

    def __init__(self, input_path: Path):
        self.file = Path.joinpath(input_path, ".ftCLI", "styles_mapping.json")
        if not self.file.exists():
            self.file.parent.mkdir(exist_ok=True, parents=True)
            self.file.touch()
            self.reset_defaults()
        self.data = self.read_file()

    def read_file(self) -> StylesMapping:
        """Opens the styles mapping file and returns its data as a dictionary"""
        try:
            with self.file.open(encoding="utf-8") as f:
                data = json.load(f)
                return StylesMapping(**data)
        except ValidationError as e:
            raise StylesMappingHandlerError(f"Pydantic validation error: {e}") from e
        except Exception as e:
            raise StylesMappingHandlerError(
                f"An error occurred while reading the file: {self.file}: {e}"
            ) from e

    def save_to_file(self, data: StylesMapping) -> None:
        """Saves the styles mapping file"""
        temp_file = self.file.with_suffix(".tmp")
        try:
            with temp_file.open("w", encoding="utf-8") as f:
                json_data = data.model_dump_json()
                formatted_json = json.dumps(json.loads(json_data), indent=4, ensure_ascii=False)
                f.write(formatted_json)
            shutil.move(temp_file, self.file)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise StylesMappingHandlerError(f"An error occurred while saving the file: {e}") from e

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
