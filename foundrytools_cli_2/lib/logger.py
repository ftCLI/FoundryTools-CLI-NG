import sys

from functools import partialmethod

from loguru import logger


class LoggerFilter:  # pylint: disable=too-few-public-methods
    """
    A custom logger filter that filters out log records below the given level.
    """

    def __init__(self, level: str) -> None:
        self.level = level

    def __call__(self, record) -> bool:  # type: ignore
        level_no = logger.level(self.level).no
        return record["level"].no >= level_no


logger_filter = LoggerFilter("INFO")

# Remove the default logger
logger.remove()

# Add a sink to the logger to print to stdout
logger.add(
    sys.stderr,
    filter=logger_filter,
    backtrace=True,
    colorize=True,
    format="[ <level>{level: <8}</level> ] " "<level>{message}</level>",
)

# Add a custom level to the logger
logger.level("SKIP", no=27, color="<light-black><bold>", icon="⏭️")
logger.__class__.skip = partialmethod(logger.__class__.log, "SKIP")  # type: ignore


__all__ = ["logger", "logger_filter"]
