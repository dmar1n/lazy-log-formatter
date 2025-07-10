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
  rev: 0.6.1
  hooks:
    - id: lazy-log-formatter
      args: ['--fix']
```

## Options

- `--fix`: Automatically fix f-strings used in log calls to lazy log calls.
- `DIR [DIR ...]`: One or more directories to search for Python files. If not specified, defaults to the current directory.

## Examples

Check all Python files in the current directory and subdirectories:

```sh
python -m src.cli
```

Check all Python files in two directories:

```sh
python -m src.cli src/ tests/
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

### Important

Only works with the native Python `logging` module. Other libraries, such as `loguru`, do not support lazy calls.

For `loguru`, see [Lazy evaluation of expensive functions](https://loguru.readthedocs.io/en/stable/overview.html#lazy-evaluation-of-expensive-functions):

```python
logger.opt(lazy=True).debug("If sink level <= DEBUG: {x}", x=lambda: expensive_function(2**64))
```
