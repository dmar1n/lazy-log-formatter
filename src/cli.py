"""Module for the CLI of the lazylog package.

This file implements the command-line interface (CLI) for the lazylog package, specifically providing a tool to detect
and optionally fix the use of f-strings in Python logging calls. The main goal is to enforce best practices by
converting f-strings in log statements to the percent-format style, which is recommended for logging in Python to avoid
unnecessary string interpolation when the log level is not enabled.

The CLI can be used to scan one or more files, report any found f-strings in logging calls, and optionally rewrite the
files to use percent-format strings instead. It also provides version information and basic error handling.
"""

import argparse
import re
from importlib.metadata import version
from pathlib import Path

F_STRING_PATTERN = re.compile(
    r"""(?:log|logger|logging)\.(?:debug|info|warning|error|critical)\((f[\"'].*[\"'])\)""",
)
VAR_PLACEHOLDERS = re.compile(r"{([^}]*)}")
PROG_NAME = "lazy-log-formatter"


def process_file(file_path: Path | str, fix: bool) -> int:
    """Process a file to find and optionally fix f-strings in log lines.

    Args:
        file_path: The path to the file to be processed.
        fix: If True, converts f-strings to percent format and writes back to the file.
                    If False, only prints the found f-strings.

    Returns:
        Returns 0 if no f-strings are found, 1 if f-strings are found or an error occurs.

    Raises:
        IOError: If an I/O error occurs while reading or writing the file.
        OSError: If an OS-related error occurs while reading or writing the file.
        re.error: If a regex error occurs during the search for f-strings.
    """
    file_path = get_path(file_path)
    try:
        content = file_path.read_text(encoding="utf-8")
        if matches := find_f_strings(content):
            return (
                fix_f_strings(file_path, content, matches)
                if fix
                else print_f_strings(matches, file_path)
            )
        return 0

    except (OSError, re.error) as e:
        print(f"Error: {e}")
        return 1


def get_path(file_path: Path | str) -> Path:
    """Get the absolute path to the file.

    Args:
        file_path: The path to the file.

    Returns:
        The absolute path to the file.
    """
    return Path(file_path).resolve()


def find_f_strings(content: str) -> list[str]:
    """Find f-strings in the content.

    Removes f-strings with backticks to avoid unwanted markdown and documentation changes.

    Args:
        content: The string content to search for f-strings.

    Returns:
        List of f-strings found in the content.
    """
    matches = F_STRING_PATTERN.findall(content)
    return [match for match in matches if "`" not in match]


def print_f_strings(matches: list[str], file_path: Path) -> int:
    """Print found f-strings.

    Args:
        matches: List of f-strings to be printed.
        file_path: The path to the file containing the f-strings.

    Returns:
        Always returns 1 as f-strings are found.
    """
    file_text = file_path.read_text()
    lines = file_text.splitlines()
    for match in matches:
        line = next((i + 1 for i, line in enumerate(lines) if match in line), -1)
        print(f"{file_path}:{line}: found f-string in log call ({match})")

    return 1


def fix_f_strings(file_path: Path, content: str, matches: list[str]) -> int:
    """Fix found f-strings by converting them to percent format and writing back to the file.

    Args:
        file_path: The path to the file to be processed.
        content: The string content containing f-strings to be converted.
        matches: List of f-strings to be converted.

    Returns:
        Always returns 1 as f-strings are found and fixed.
    """
    content = convert_f_strings_to_percent_format(content, matches)
    file_path.write_text(content, encoding="utf-8")
    print(f"💤🐨💤 Converted f-strings to percent format in '{file_path}'.")
    return 1


def convert_f_strings_to_percent_format(content: str, matches: list[str]) -> str:
    """Search for f-strings, and converts them to percent format strings.

    https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/logging-fstring-interpolation.html

    Original: `logging.error(f"Python version: {sys.version}")`
    Converted: `logging.error("Python version: %s", sys.version)`

    Args:
        content: The string content containing f-strings to be converted.
        matches: List of f-strings to be converted.

    Returns:
        The modified content with f-strings converted to percent format strings.
    """
    for match in matches:
        placeholders = VAR_PLACEHOLDERS.findall(match)
        placeholders = [
            placeholder.strip().removesuffix("=") for placeholder in placeholders
        ]
        percent_format = VAR_PLACEHOLDERS.sub("%s", match).removeprefix("f")
        args = ", ".join(placeholders) if placeholders else None
        replacement = f"{percent_format}, {args}" if args else f"{percent_format}"
        content = content.replace(match, replacement)
    return content


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI.

    Args:
        argv: List of command-line arguments.

    Returns:
        Returns 0 if the conversion is successful, otherwise returns 1.
    """
    parser = argparse.ArgumentParser(prog=PROG_NAME)
    parser.add_argument("filenames", nargs="*", help="Filenames to process.")
    parser.add_argument("--fix", help="Fix issues found in file.", action="store_true")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version(PROG_NAME)}",
    )
    args = parser.parse_args(argv)
    results = any(process_file(filename, args.fix) for filename in args.filenames)
    if results:
        print(f"💤🐨💤 {PROG_NAME} completed with issues. 💤🐨💤")

    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main())
