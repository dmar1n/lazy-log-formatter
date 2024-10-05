# Lazy log

Pre-commit hook to automatically detect and convert f-strings in Python code used in log calls to lazy log calls, 
following W1203 Pylint rule:

https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/logging-fstring-interpolation.html

## Usage

To use with pre-commit, add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/dmar1n/lazy-log-formatter
  rev: v0.1.0
  hooks:
    - id: lazy-log-formatter
    args: ['--fix']
```

## Options

- `--fix`: Automatically fix f-strings used in log calls to lazy log calls.