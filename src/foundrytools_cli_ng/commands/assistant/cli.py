from pathlib import Path

import click

from foundrytools_cli_ng.utils.logger import logger

cli = click.Group(help="Utilities for fixing the ``name`` table.")


@cli.command("init")
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
def init_assistant(input_path: Path) -> None:
    """
    Initialize the name table of a font.
    """

    from foundrytools_cli_ng.commands.assistant.styles_mapping import StylesMappingHandler

    styles_mapping = StylesMappingHandler(input_path)
    print(styles_mapping.file)
    logger.info("Styles mapping file initialized.")
