"""Module for the CLI of the lazylog package.

This file implements the command-line interface (CLI) for the lazylog package, specifically providing a tool to detect
and optionally fix the use of f-strings in Python logging calls. The main goal is to enforce best practices by
converting f-strings in log statements to the percent-format style, which is recommended for logging in Python to avoid
unnecessary string interpolation when the log level is not enabled.

The CLI can be used to scan one or more files, report any found f-strings in logging calls, and optionally rewrite the
files to use percent-format strings instead. It also provides version information and basic error handling.
"""

import argparse
from importlib.metadata import version
from pathlib import Path

from src.transformer import Transformer

PROG_NAME = "lazy-log-formatter"


def process_file(file_path: Path | str, fix: bool, check_import: bool = False) -> int:
    """Process a file to find and optionally fix f-strings in log lines.

    Args:
        file_path: Path to the file to process.
        fix: If True, attempt to fix the f-strings found in the file.
        check_import: If True, check if the logging module is imported in the file.

    Returns:
        Returns 0 if no issues were found or fixed, otherwise returns 1.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        print(f"File {file_path} does not exist or is not a file.")
        return 1

    with file_path.open("r", encoding="utf-8") as file:
        content = file.read()

    transformer = Transformer(file_path, check_import=check_import)
    transformed_content = transformer.run(content)
    if content == transformed_content:
        print(f"No f-strings found in {file_path}.")
        return 0

    if fix:
        with file_path.open("w", encoding="utf-8") as file:
            file.write(transformed_content)
        print(f"Fixed f-strings in {file_path}.")
    else:
        print(f"Found f-strings in {file_path}: {file_path.name}")

    return 1


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

    if not args.filenames:
        print("No filenames provided. Please specify files to process.")
        parser.print_help()
        return 1

    if not all(Path(filename).is_file() for filename in args.filenames):
        print("One or more specified files do not exist or are not files.")
        return 1

    results = any(process_file(filename, args.fix) for filename in args.filenames)
    if results:
        print(f"{PROG_NAME} completed with issues.")

    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main())
