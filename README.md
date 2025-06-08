# Lazy log formatter

Pre-commit hook to automatically detect and convert f-strings in Python code used in log calls to lazy log calls, 
following W1203 Pylint rule:

https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/logging-fstring-interpolation.html

## Usage

To use with pre-commit, add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/dmar1n/lazy-log-formatter
  rev: 0.4.6
  hooks:
    - id: lazy-log-formatter
    args: ['--fix']
```

## Options

- `--fix`: Automatically fix f-strings used in log calls to lazy log calls.

## Examples

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

## Current limitations

- Only works with the native Python `logging` module. Other libraries, such as `loguru`, do not support lazy calls.
- Multi-line f-strings in the editor are not supported yet (they are ignored).

For `loguru`, see [Lazy evaluation of expensive functions](https://loguru.readthedocs.io/en/stable/overview.html#lazy-evaluation-of-expensive-functions):

```python
logger.opt(lazy=True).debug("If sink level <= DEBUG: {x}", x=lambda: expensive_function(2**64))
```