import typing as t

import click

from foundrytools_cli_2.cli.options import add_options


def subroutinize_flag() -> t.Callable:
    """
    Add the subroutinize option to a click command.

    :return: a decorator that adds the subroutinize option to a click command
    """
    _subroutinize_flag = [
        click.option(
            "--subroutinize/--no-subroutinize",
            default=True,
            help="Subroutinize the font.",
        )
    ]
    return add_options(_subroutinize_flag)


def min_area_option() -> t.Callable:
    """
    Add the min_area option to a click command.

    :return: a decorator that adds the min_area option to a click command
    """
    _min_area_option = [
        click.option(
            "-ma",
            "--min-area",
            type=click.IntRange(min=0),
            default=25,
            help="Remove tiny paths with area less than the specified value.",
        )
    ]
    return add_options(_min_area_option)


def otf_autohint_options() -> t.Callable:
    """
    Add the autohint options to a click command.

    :return: a decorator that adds the autohint options to a click command
    """
    _autohint_options = [
        allow_changes_flag(),
        allow_no_blues_flag(),
        decimal_flag(),
        no_flex_flag(),
        no_hint_sub_flag(),
    ]
    return add_options(_autohint_options)


def allow_changes_flag() -> t.Callable:
    """
    Add the allow_changes option to a click command.

    :return: a decorator that adds the allow_changes option to a click command
    """
    _allow_changes_flag = [
        click.option(
            "--allow-changes",
            is_flag=True,
            default=False,
            help="""
            Allow changes to the glyphs outlines.
            """,
        )
    ]
    return add_options(_allow_changes_flag)


def allow_no_blues_flag() -> t.Callable:
    """
    Add the allow_no_blues option to a click command.

    :return: a decorator that adds the allow_no_blues option to a click command
    """
    _allow_no_blues_flag = [
        click.option(
            "--allow-no-blues",
            is_flag=True,
            default=False,
            help="""
            Allow the font to have no alignment zones nor stem widths.
            """,
        )
    ]
    return add_options(_allow_no_blues_flag)


def decimal_flag() -> t.Callable:
    """
    Add the decimal option to a click command.

    :return: a decorator that adds the decimal option to a click command
    """
    _decimal_flag = [
        click.option(
            "--decimal",
            is_flag=True,
            default=False,
            help="""
            Use decimal coordinates.
            """,
        )
    ]
    return add_options(_decimal_flag)


def no_flex_flag() -> t.Callable:
    """
    Add the no_flex option to a click command.

    :return: a decorator that adds the no_flex option to a click command
    """
    _no_flex_flag = [
        click.option(
            "--no-flex",
            is_flag=True,
            default=False,
            help="""
            Suppress generation of flex commands.
            """,
        )
    ]
    return add_options(_no_flex_flag)


def no_hint_sub_flag() -> t.Callable:
    """
    Add the no_hint_sub option to a click command.

    :return: a decorator that adds the no_hint_sub option to a click command
    """
    _no_hint_sub_flag = [
        click.option(
            "--no-hint-sub",
            is_flag=True,
            default=False,
            help="""
            Suppress hint substitution.
            """,
        )
    ]
    return add_options(_no_hint_sub_flag)
