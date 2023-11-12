from pathlib import Path
from typing import Optional

import click

from foundrytools_cli_2.lib.click.click_options import (
    input_path_argument,
    recursive_flag,
    recalc_timestamp_flag,
    overwrite_flag,
    output_dir_option,
    debug_flag,
    subroutinize_flag,
    min_area_option,
)
from foundrytools_cli_2.lib.constants import TTFontOptions
from foundrytools_cli_2.lib.font_finder import FontFinder, FontFinderError, FontFinderFilter
from foundrytools_cli_2.lib.logger import logger, logger_filter
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.snippets.ps_correct_contours import correct_otf_contours

cli = click.Group()


@cli.command("fix-contours")
@input_path_argument()
@recursive_flag()
@min_area_option()
@subroutinize_flag()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@debug_flag()
@Timer(logger=logger.info)
def fix_contours(
    input_path: Path,
    recursive: bool = False,
    min_area: int = 25,
    subroutinize: bool = True,
    debug: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Fix the contours of OpenType-PS fonts by removing overlaps, correcting contours direction, and
    removing tiny paths.
    """

    if debug:
        logger_filter.level = "DEBUG"

    filters = FontFinderFilter(filter_out_tt=True, filter_out_variable=True)
    options = TTFontOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.generate_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort(e)

    for font in fonts:
        with font:
            try:
                print()
                logger.info(f"Checking file {font.file}")
                logger.info("Correcting contours...")
                correct_otf_contours(font, min_area=min_area)
                if subroutinize:
                    logger.info("Subroutinizing...")
                    font.ps_subroutinize()
                output_file = font.get_output_file(output_dir=output_dir, overwrite=overwrite)
                font.ttfont.save(output_file)
                logger.success(f"File saved to {output_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)


@cli.command("subr")
@input_path_argument()
@recursive_flag()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@debug_flag()
@Timer(logger=logger.info)
def subr(
    input_path: Path,
    recursive: bool = False,
    debug: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    if debug:
        logger_filter.level = "DEBUG"

    filters = FontFinderFilter(filter_out_tt=True, filter_out_variable=True)
    options = TTFontOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.find_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort(e)

    for font in fonts:
        with font:
            try:
                print()
                logger.info(f"Checking file {font.file}")
                logger.info("Subroutinizing...")
                font.ps_subroutinize()
                out_file = font.get_output_file(output_dir=output_dir, overwrite=overwrite)
                font.save(out_file)
                logger.success(f"File saved to {out_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)


@cli.command("desubr")
@input_path_argument()
@recursive_flag()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@debug_flag()
@Timer(logger=logger.info)
def desubr(
    input_path: Path,
    recursive: bool = False,
    debug: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    if debug:
        logger_filter.level = "DEBUG"

    filters = FontFinderFilter(filter_out_tt=True, filter_out_variable=True)
    options = TTFontOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.generate_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort(e)

    for font in fonts:
        with font:
            try:
                print()
                logger.info(f"Checking file {font.file}")
                logger.info("Desubroutinizing...")
                font.ps_desubroutinize()
                out_file = font.get_output_file(output_dir=output_dir, overwrite=overwrite)
                font.save(out_file)
                logger.success(f"File saved to {out_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)
