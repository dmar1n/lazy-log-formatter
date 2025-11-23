# Lazy log formatter

![PyPI - Version](https://img.shields.io/pypi/v/lazy-log-formatter) 
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dmar1n/lazy-log-formatter/.github%2Fworkflows%2Frelease.yaml)
![GitHub License](https://img.shields.io/github/license/dmar1n/lazy-log-formatter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lazy-log-formatter)
![PyPI - Downloads](https://img.shields.io/pypi/dm/lazy-log-formatter)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)

A tool that automatically converts f-strings in Python logging calls into lazy logging calls (`logger.info("x %s", var)`) 
for consistency with Python documentation, improved performance and linting compliance.

## Why this tool?

In Python, the recommended way to [log variable data](https://docs.python.org/3/howto/logging.html#logging-variable-data) is to use format-string placeholders and pass values separately:

```python
import logging
logging.warning('%s before you %s', 'Look', 'leap!')
```

This approach:
- avoids unnecessary string formatting when a log message is not emitted,
- is compatible with Python’s [logging design](https://docs.python.org/3/howto/logging.html#optimization) and [documentation](https://docs.python.org/3/howto/logging.html#logging-variable-data),
- prevents Pylint’s [W1203](https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/logging-fstring-interpolation.html): logging-fstring-interpolation warning,
- avoids performance overhead from evaluating f-strings when logging is disabled for a certain level.

### Features

- Scans Python files for f-strings used in logging calls.
- Provides an option to automatically convert f-strings in logging calls to lazy logging calls.
- Can be integrated as a pre-commit hook to enforce logging best practices in codebases.

## Installation

Install from PyPI:

```sh
pip install lazy-log-formatter
```

### Pre-commit Integration

Add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/dmar1n/lazy-log-formatter
  rev: 0.10.0
  hooks:
    - id: lazy-log-formatter
      args: ['--fix']
```

## Command-line options

You can run the tool from the command line using the following options:

| Option                   | Description                                               |
| ------------------------ | --------------------------------------------------------- |
| `--fix`                  | Converts f-strings in log calls to lazy logging syntax    |
| `--exclude [PATTERN...]` | Excludes files/directories matching one or more patterns  |
| `PATH [PATH...]`         | One or more paths to scan (defaults to current directory) |


## Examples

Check all Python files in the current directory and subdirectories:

```sh
python -m lazy_log.cli .
```

Fix all Python files in the current directory and subdirectories:

```sh
python -m lazy_log.cli . --fix
```

Check all Python files in two directories:

```sh
python -m lazy_log.cli lazy_log/ tests/
```

Check specific files:

```sh
python -m lazy_log.cli lazy_log/cli.py tests/data/test.py
```

Exclude specific files or directories:

```sh
python -m lazy_log.cli tests/data --exclude "*.pyc" "__pycache__/*" 
```

Fix issues in all Python files in a directory:

```sh
python -m lazy_log.cli mydir --fix
```

## Example transformations

### Simple f-string

```python
# Before
logger.info(f'Hello {name}')

# After
logger.info('Hello %s', name)
```

### Multiple variables

```python
# Before
logger.info(f'Hello {name} {surname}')

# After
logger.info('Hello %s %s', name, surname)
```

### Class-based logging example

```python
import logging
from datetime import datetime


def log_and_return_datetime():
    now = datetime.now()
    logging.info(f"Current datetime: {now}")
    return now


class DateTimeLogger:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def log_datetime(self):
        now = datetime.now()
        self._logger.info(f"Current datetime: {now}")
        return now
```

After running the formatter, the output will be:

```text
F-string in logging call at ...\tests\data\test.py:8: f'Current datetime: {now}'
F-string in logging call at ...\tests\data\test.py:18: f'Current datetime: {now}'
F-strings found and fixed in '...\tests\data\test.py'.
```

And the code will be transformed to:

```python
import logging
from datetime import datetime


def log_and_return_datetime():
    now = datetime.now()
    logging.info("Current datetime: %s", now)
    return now


class DateTimeLogger:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def log_datetime(self):
        now = datetime.now()
        self._logger.info("Current datetime: %s", now)
        return now
```

### Notes

#### Other logging libraries

Only works with the native Python `logging` module. Other libraries, such as `loguru`, do not support lazy calls.

For `loguru`, see [Lazy evaluation of expensive functions](https://loguru.readthedocs.io/en/stable/overview.html#lazy-evaluation-of-expensive-functions):

```python
logger.opt(lazy=True).debug("If sink level <= DEBUG: {x}", x=lambda: expensive_function(2**64))
```

#### Code formatting with Black

When transforming code, the tool uses [Black](https://black.readthedocs.io/en/stable/) to reformat the modified files. 
If you use Black in your project, the changes made by this tool will be consistent with Black's formatting style.

#### Detection of log calls

The tool implements logic to detect calls to a logger in the code assuming your log calls use a logger that is named accordingly (e.g.: `logger.info(...)`, `log.info(...)`). If the logger instance variable is named without "log", it will skip it.
