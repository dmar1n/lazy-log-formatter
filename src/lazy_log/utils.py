"""Utility functions for the lazy_log package."""

import re
import sys
from importlib.metadata import PackageNotFoundError, version

from lazy_log.constants import PROG_NAME

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


def get_version() -> str:
    """Return installed package version, falling back gracefully when not installed."""
    try:
        return version(PROG_NAME)
    except PackageNotFoundError:
        return "unknown"


def print_with_fallback(message: str) -> None:
    """Print text, degrading safely when the console cannot encode the characters."""
    try:
        print(message)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe_bytes = message.encode(encoding, errors="backslashreplace")
        sys.stdout.buffer.write(safe_bytes + b"\n")


def prepare_exclude_patterns(patterns: list[str]) -> list[str]:
    """Normalize user-provided exclude patterns for cross-platform matching."""
    prepared = []
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if normalized.startswith(("**/", "/")) or ":" in normalized:
            prepared.append(normalized)
        else:
            prepared.append(f"**/{normalized}")
    return prepared
