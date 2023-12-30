# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.click_options import (
    common_options,
    delete_all,
    language_string,
    name_id,
    name_ids,
    name_string,
    new_string,
    old_string,
    platform_id,
    skip_name_ids,
    win_or_mac_platform_id,
)
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Utilities for editing the name table.")


@cli.command("del-names")
@name_ids(required=True)
@platform_id()
@language_string()
@common_options()
def del_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete names from the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import del_names as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("del-empty-names")
@common_options()
def del_empty_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Deletes empty names from the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import del_empty_names as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("del-mac-names")
@delete_all()
@common_options()
def del_mac_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete Macintosh names from the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import del_mac_names as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("del-unused-names")
@common_options()
def del_unused_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete unused names from the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import del_unused_names as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("find-replace")
@old_string()
@new_string()
@name_ids(required=False)
@skip_name_ids()
@platform_id()
@common_options()
def find_replace(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Find and replace text in the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import find_replace as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("set-name")
@name_string()
@name_id()
@win_or_mac_platform_id()
@common_options()
def set_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set the name table of the given font files.
    """
    print(options)
    from foundrytools_cli_2.snippets.name import set_name as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("strip-names")
@common_options()
def strip_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Strip the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import strip_names as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()
