import click

from foundrytools_cli_ng.commands.assistant import cli as assistant
from foundrytools_cli_ng.commands.cff import cli as cff
from foundrytools_cli_ng.commands.cmap import cli as cmap
from foundrytools_cli_ng.commands.converter import cli as converter
from foundrytools_cli_ng.commands.fix import cli as fix
from foundrytools_cli_ng.commands.font import cli as font
from foundrytools_cli_ng.commands.gsub import cli as gsub
from foundrytools_cli_ng.commands.hhea import cli as hhea
from foundrytools_cli_ng.commands.name import cli as name
from foundrytools_cli_ng.commands.os_2 import cli as os_2
from foundrytools_cli_ng.commands.otf import cli as otf
from foundrytools_cli_ng.commands.post import cli as post
from foundrytools_cli_ng.commands.print import cli as print_
from foundrytools_cli_ng.commands.ttf import cli as ttf
from foundrytools_cli_ng.commands.utils import cli as utils


@click.group(
    help="A collection of command line tools for working with font files.",
    commands={
        "assistant": assistant,
        "cff": cff,
        "cmap": cmap,
        "converter": converter,
        "fix": fix,
        "font": font,
        "gsub": gsub,
        "hhea": hhea,
        "name": name,
        "os2": os_2,
        "otf": otf,
        "post": post,
        "print": print_,
        "ttf": ttf,
        "utils": utils,
    },
)
@click.version_option()
def cli() -> None:  # pylint: disable=missing-function-docstring
    pass
