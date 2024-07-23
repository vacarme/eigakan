"""Logger configuration module."""

import logging
import sys
from copy import copy
from enum import StrEnum
from types import MappingProxyType
from typing import Literal

from .env import APP

LOGGING_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

LOGGING_FORMAT = "%(levelprefix)s%(asctime)s - %(message)s"


class Color(StrEnum):
    """Class holding useful values for customising print to CLI line."""

    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RED_ALT = "\033[101m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALIC = "\x1b[3m"
    END = "\033[0m"
    WHITESUB = "\033[7m"


class ColourizedFormatter(logging.Formatter):
    """Logging formatter colorizing the level names in the logs."""

    LVL_NAME_COLORS = MappingProxyType(
        {
            logging.DEBUG: lambda lvl_name: Color.CYAN + lvl_name + Color.END,
            logging.INFO: lambda lvl_name: Color.GREEN + lvl_name + Color.END,
            logging.WARNING: lambda lvl_name: Color.YELLOW
            + lvl_name
            + Color.END,
            logging.ERROR: lambda lvl_name: Color.RED + lvl_name + Color.END,
            logging.CRITICAL: lambda lvl_name: Color.RED_ALT
            + lvl_name
            + Color.END,
        }
    )

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
    ):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format the message with the level name colorized."""
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        seperator = " " * (8 - len(recordcopy.levelname))
        levelname = self.LVL_NAME_COLORS[recordcopy.levelno](levelname)
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(recordcopy)


logger = logging.getLogger(__name__)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = ColourizedFormatter(LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(APP.LOG_LEVEL)
