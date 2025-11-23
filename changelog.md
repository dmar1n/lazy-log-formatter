# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.4] - 2025-11-23

### Changed

- Updated LICENSE text.

## [0.10.3] - 2025-11-23

### Changed

- Updated `README.md`.
- Changed license to MIT.
- Updated `pyproject.toml` metadata.

## [0.10.2] - 2025-11-23

### Changed

- Updated release workflow.

## [0.10.1] - 2025-11-23

### Fixed

- Fixed `README.md` to improve clarity on code formatting and log call detection.

### Added

- Added a message when no f-strings are found in the scanned files.

## [0.10.0] - 2025-11-23

### Added

- Added support for formatting f-strings with embedded format expressions.
- Added more comprehensive tests for f-string formatting.

### Changed

- Improved `README.md` with more examples and explanations.

## [0.9.0] - 2025-11-18

### Added

- Support for excluding files and directories using glob patterns via the `--exclude` option. 
  Multiple patterns can be specified by separating them with commas.

### Fixed

- Fixed issue when the formatted file does retain the final newline character. Closes #4
- Improved handling of files in virtual environments to avoid processing them. Closes #3
- Minor improvements and code cleanup.

## [0.8.2] - 2025-11-03

### Fixed

- Fixed the case where the f-string contains a format specifier for thousand separator (`,`). 

## [0.8.1] - 2025-11-02

### Fixed

- Fixed and improved file discovery when passing directories as arguments.

## [0.8.0] - 2025-10-20

### Added

- Replace AST with LibCST for code transformation to keep formatting and comments intact.

## [0.7.0] - 2025-07-27

- Several improvements in file discovery and file processing.

## [0.6.0] - 2025-06-29

- Allow to pass a directory to search for Python files.

## [0.5.4] - 2025-06-28

- Fix the output of the transformation log to include the file path.

## [0.5.3] - 2025-06-28

- Improved output of the transformation log to include the file path.

## [0.5.2] - 2025-06-28

- Fix transformation log.

## [0.5.1] - 2025-06-28

- Fix package name.

## [0.5.0] - 2025-06-28

- Refactored the code to improve readability and maintainability.


## [0.4.6] - 2025-06-08

### Fixed

- Bumped version to 0.4.6 to fix the GitHub workflow for publishing to PyPI.

## [0.4.5] - 2025-06-08

### Fixed

- Fixed GitHub workflow to publish the package to PyPI.

## [0.4.4] - 2025-06-08

### Added

- Added documentation and minor improvements.

## [0.4.3] - 2024-11-30

### Fixed

- Handle expressions using the `=` operator in f-strings. Fixes [#1]

## [0.4.2] - 2024-11-01

### Added

- Added current limitation to README.md.

## [0.4.1] - 2024-11-01

### Fixed

- Update README.md.

## [0.4.0] - 2024-11-01

### Added

- Added a new GitHub workflow to automatically publish the package to PyPI.

## [0.3.4] - 2024-10-12

### Fixed

- Update readme.

## [0.3.3] - 2024-10-12

### Fixed

- Update readme.

## [0.3.2] - 2024-10-12

### Fixed

- Renamed program name.

## [0.3.1] - 2024-10-12

### Fixed

- Fixed entry point.

## [0.3.0] - 2024-10-12

### Added

- Initial release.
