from pytest import mark

from src.cli import convert_f_strings_to_percent_format, find_f_strings

TEST_DATA = [
    (
        'logging.error(f"Python version: {sys.version}")',
        'logging.error("Python version: %s", sys.version)',
    ),
    ('log.info(f"User {user} logged in")', 'log.info("User %s logged in", user)'),
    (
        'log.info(f"User {get_user(1)} logged in")',
        'log.info("User %s logged in", get_user(1))',
    ),
    (
        """log.info(f"User {get_user('1')} logged in")""",
        """log.info("User %s logged in", get_user('1'))""",
    ),
    (
        'log.info(f"User {user} logged in at {time}")',
        'log.info("User %s logged in at %s", user, time)',
    ),
    (
        """log.info(f"User '{user}' logged in at {time}")""",
        """log.info("User '%s' logged in at %s", user, time)""",
    ),
    ('log.info("User logged in")', 'log.info("User logged in")'),
    ('log.info(f"User logged in")', 'log.info("User logged in")'),
    (
        "log.warning(f'User {user} logged in at {time}')",
        "log.warning('User %s logged in at %s', user, time)",
    ),
    (
        'print(f"No f-string here {false_case}.")',
        'print(f"No f-string here {false_case}.")',
    ),
]


class TestConvertFStringsToPercentFormat:
    @mark.parametrize("content, expected", TEST_DATA)
    def test_convert_f_strings_to_percent_format(self, content, expected):
        matches = find_f_strings(content)
        actual = convert_f_strings_to_percent_format(content, matches)
        print(f"Content : {content}")
        print(f"Actual  : {actual}")
        print(f"Expected: {expected}")
        print(f"Matches : {matches}")
        assert actual == expected
