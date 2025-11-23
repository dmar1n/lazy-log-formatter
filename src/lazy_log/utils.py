"""Utility functions for the lazy_log package."""

import re

FLOAT_FMT_PATTERN = re.compile(r"^([+-]?)(\d+)?(\.\d+)?f$")
INT_FMT_PATTERN = re.compile(r"^([+-]?)(\d+)?d$")
GENERIC_FMT_PATTERN = re.compile(r"^([+-]?)(\d+)?(\.\d+)?[fdsxoe]$")


def python_fmt_to_printf(fmt: str) -> str:
    """Convert a Python format specifier to a printf-style format specifier.

    Args:
        fmt: The Python format specifier string.

    Returns:
        The corresponding printf-style format specifier string.
    """
    fmt = fmt.strip()
    result = "%s"  # Default format

    if fmt in {"", ","}:
        result = "%s"
    elif float_match := FLOAT_FMT_PATTERN.match(fmt):
        sign = float_match.group(1) or ""
        width = float_match.group(2) or ""
        precision = float_match.group(3) or ""
        result = f"%{sign}{width}{precision}f"
    elif int_match := INT_FMT_PATTERN.match(fmt):
        sign = int_match.group(1) or ""
        width = int_match.group(2) or ""
        result = f"%{sign}{width}d"
    elif generic_match := GENERIC_FMT_PATTERN.match(fmt):
        sign = generic_match.group(1) or ""
        width = generic_match.group(2) or ""
        precision = generic_match.group(3) or ""
        typechar = fmt[-1]
        result = f"%{sign}{width}{precision}{typechar}"
    elif fmt.endswith(("d", "f", "s", "x", "o", "e")):
        result = f"%{fmt[-1]}"

    return result
