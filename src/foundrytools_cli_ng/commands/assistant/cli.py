from pathlib import Path

import click

from foundrytools_cli_ng.commands.assistant.styles_mapping import (
    StylesMappingHandler,
)
from foundrytools_cli_ng.utils.logger import logger

cli = click.Group(help="Utilities for fixing the ``name`` table.")


@cli.command("init")
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
def init_mapping(input_path: Path) -> None:
    """
    Initialize the name table of a font.
    """
    styles_mapping_file = StylesMappingHandler.get_file_path(input_path)
    if styles_mapping_file.exists():
        logger.warning(f"Styles mapping file already exists at {styles_mapping_file}")
        click.confirm("Do you want to overwrite the existing styles mapping file?", abort=True)

    styles_mapping_handler = StylesMappingHandler(input_path)
    styles_mapping_handler.reset_defaults()

    logger.info(f"Styles mapping file created at {styles_mapping_file}")
