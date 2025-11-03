![PyPI - Version](https://img.shields.io/pypi/v/lazy-log-formatter) 
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dmar1n/lazy-log-formatter/.github%2Fworkflows%2Frelease.yaml)
![GitHub License](https://img.shields.io/github/license/dmar1n/lazy-log-formatter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lazy-log-formatter)

# Lazy log formatter

Pre-commit hook to automatically detect and convert f-strings in Python code to 
[printf-style](https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting) logging calls,
following W1203 Pylint rule:

https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/logging-fstring-interpolation.html

## Usage

To use it with pre-commit, add the following lines to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/dmar1n/lazy-log-formatter
  rev: 0.8.2
  hooks:
    - id: lazy-log-formatter
      args: ['--fix']
```

## Options

- `--fix`: Automatically fix f-strings used in log calls to lazy log calls.
- `PATH [PATH ...]`: One or more directories or files to process. If not specified, defaults to the current directory.

## Examples

Check all Python files in the current directory and subdirectories:

```sh
python -m src.cli
```

Check all Python files in two directories:

```sh
python -m src.cli src/ tests/
```

Check specific files:

```sh
python -m src.cli src/cli.py tests/test_cli.py
```

Fix issues in all Python files in a directory:

```sh
python -m src.cli mydir --fix
```

If the `--fix` option is used, the hook will convert f-strings in log calls to lazy log calls, as follows:

```python
# Before
logger.info(f'Hello {name}')

# After
logger.info('Hello %s', name)
```

```python
# Before
logger.info(f'Hello {name} {surname}')

# After
logger.info('Hello %s %s', name, surname)
```

### Example in a Python class

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

```bash
python src\cli.py tests\data
```

The output will be:

```text
F-string in logging call at ...\tests\data\test.py:8: f'Current datetime: {now}'
F-string in logging call at ...\tests\data\test.py:18: f'Current datetime: {now}'
F-strings found and fixed in '...\tests\data\test.py'.
```

After running the formatter, the code will be transformed to:

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

### Important

Only works with the native Python `logging` module. Other libraries, such as `loguru`, do not support lazy calls.

For `loguru`, see [Lazy evaluation of expensive functions](https://loguru.readthedocs.io/en/stable/overview.html#lazy-evaluation-of-expensive-functions):

```python
logger.opt(lazy=True).debug("If sink level <= DEBUG: {x}", x=lambda: expensive_function(2**64))
```
