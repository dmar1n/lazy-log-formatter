"""Module for the CLI of the lazylog package.

This module implements the command-line interface (CLI) for the lazylog package, specifically providing a tool to detect
and optionally fix the use of f-strings in Python logging calls. The main goal is to enforce best practices by
converting f-strings in log statements to the percent-format style, which is recommended for logging in Python to avoid
unnecessary string interpolation when the log level is not enabled.

The CLI can be used to scan one or more files, report any found f-strings in logging calls, and optionally rewrite the
files to use percent-format strings instead. It also provides version information and basic error handling.

Example usage:
    # Check all Python files in the current directory and subdirectories
    python -m lazy_log.cli

    # Check all Python files in two directories
    python -m lazy_log.cli lazy_log/ tests/data/

    # Fix issues in all Python files in a directory
    python -m lazy_log.cli mydir --fix
"""

import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from lazy_log.transformer import Transformer

PROG_NAME = "lazy-log-formatter"
VENV_DIRS = {".venv", ".env"}


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
        return 1
    with file_path.open("r", encoding="utf-8") as file:
        content = file.read()
    transformer = Transformer(file_path, check_import=check_import)
    transformed_content = transformer.run(content)
    if content == transformed_content or not transformer.issues:
        return 0
    if fix:
        with file_path.open("w", encoding="utf-8") as file:
            file.write(transformed_content)
        print(f"F-strings found and fixed in '{file_path}'.")
    elif transformer.issues:
        print(f"F-strings found in '{file_path}':")
        for issue in transformer.issues:
            print(f"  - {issue}")
    return 1


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI.

    Args:
        argv: List of command-line arguments.

    Returns:
        Returns 0 if the conversion is successful, otherwise returns 1.
    """
    parser = argparse.ArgumentParser(prog=PROG_NAME)
    parser.add_argument(
        "paths",
        nargs="+",
        default=["."],
        help="One or more directories or files to process. Defaults to current directory if not specified.",
    )
    parser.add_argument("--fix", help="Fix issues found in file.", action="store_true")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version(PROG_NAME)}",
    )
    args = parser.parse_args(argv)

    all_files: set[Path] = set()

    def is_in_venv(path: Path) -> bool:
        parts = set(path.parts)
        return any(venv in parts for venv in VENV_DIRS)

    for path_str in args.paths:
        input_path = Path(path_str).resolve()
        if input_path.is_file():
            if not is_in_venv(input_path):
                all_files.add(input_path)
        elif input_path.is_dir():
            for file_path in input_path.rglob("*.py"):
                if all(venv not in file_path.parts for venv in VENV_DIRS):
                    all_files.add(file_path.resolve())
        else:
            print(
                f"Warning: '{path_str}' is not a valid file or directory and will be ignored.",
                file=sys.stderr,
            )

    filenames = [str(f) for f in sorted(all_files)]
    results = sum(process_file(filename, fix=args.fix) == 1 for filename in filenames)
    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main())
