import pytest

from lazy_log.utils import python_fmt_to_printf


@pytest.mark.parametrize(
    "input_fmt, expected",
    [
        # Test empty and special cases
        ("", "%s"),
        (",", "%s"),
        # Test float format specifiers
        (".2f", "%.2f"),
        ("10.2f", "%10.2f"),
        ("f", "%f"),
        # Test integer format specifiers
        ("d", "%d"),
        ("5d", "%5d"),
        ("+5d", "%+5d"),
        # Test generic format specifiers
        ("10.2s", "%10.2s"),
        ("5x", "%5x"),
        ("o", "%o"),
        ("e", "%e"),
        # Test edge cases
        ("10.2", "%s"),  # No type character
        ("10.2z", "%s"),  # Unsupported type character
        ("+10.2f", "%+10.2f"),  # Float with sign
        ("-10.2d", "%-10.2d"),  # Integer with sign
    ],
)
def test_python_fmt_to_printf(input_fmt, expected):
    actual = python_fmt_to_printf(input_fmt)
    assert actual == expected
