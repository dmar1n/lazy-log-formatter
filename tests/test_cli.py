import tempfile
from pathlib import Path

from hypothesis import assume, given
from hypothesis import strategies as st
from pytest import fixture, mark

from lazy_log.cli import process_file
from lazy_log.transformer import Transformer

TEST_DATA = [
    (
        'logging.error(f"Python version: {sys.version}")',
        'logging.error("Python version: %s", sys.version)',
    ),
    ('call.warning(f"Value is {value}")', 'call.warning(f"Value is {value}")'),
    (
        'logging.info(f"User {user.username} logged in")',
        'logging.info("User %s logged in", user.username)',
    ),
    ('logger.warning(f"Value is {value}")', 'logger.warning("Value is %s", value)'),
    (
        'logger.debug(f"Current time: {datetime.now()}")',
        'logger.debug("Current time: %s", datetime.now())',
    ),
    (
        'logger.critical(f"Error occurred: {error_message}")',
        'logger.critical("Error occurred: %s", error_message)',
    ),
    (
        'logger.info(f"Sum of {a} and {b} is {a + b}")',
        'logger.info("Sum of %s and %s is %s", a, b, a + b)',
    ),
    (
        'logger.info(f"Pi rounded to 2 decimals: {pi:.2f}")',
        'logger.info("Pi rounded to 2 decimals: %.2f", pi)',
    ),
    (
        'logger.info(f"Multiple values: {a}, {b}, and {c}")',
        'logger.info("Multiple values: %s, %s, and %s", a, b, c)',
    ),
    (
        'logger.info(f"Escape percent: {value} %")',
        'logger.info("Escape percent: %s %%", value)',
    ),
    ('logger.info(f"User debug: {info=}")', 'logger.info("User debug: info=%s", info)'),
    ('logger.info("No f-string here")', 'logger.info("No f-string here")'),
    (
        """logger.info(f'Nested f-string: {f"{a} + {b} = {a + b}"}')""",
        """logger.info("Nested f-string: %s", f"{a} + {b} = {a + b}")""",
    ),
    (
        'logger.info(f"Formatted value: {value:.3f}")',
        'logger.info("Formatted value: %.3f", value)',
    ),
    (
        """logger.info(f"List items: {', '.join(items)}")""",
        'logger.info("List items: %s", ", ".join(items))',
    ),
    (
        """logger.info(f"Dict value: {my_dict.get(key, 'default')}")""",
        """logger.info("Dict value: %s", my_dict.get(key, "default"))""",
    ),
    (
        'logger.info(f"Complex expression: {a * b + c}")',
        'logger.info("Complex expression: %s", a * b + c)',
    ),
    (
        'logger.info(f"Function result: {my_function()}")',
        'logger.info("Function result: %s", my_function())',
    ),
    (
        'logger.info(f"With percent: {value} %")',
        'logger.info("With percent: %s %%", value)',
    ),
    ('logger.info(f"Escape brace: {{value}}")', 'logger.info("Escape brace: {value}")'),
    (
        'logger.info(f"Escape brace with percent: {{value}} %")',
        'logger.info("Escape brace with percent: {value} %%")',
    ),
    (
        'logger.info(f"Literal string with percent: %")',
        'logger.info("Literal string with percent: %%")',
    ),
    (
        'logger.info(f"Literal string with braces: {{}}")',
        'logger.info("Literal string with braces: {}")',
    ),
    (
        'logger.info(f"With braces and percent: {{}} %")',
        'logger.info("With braces and percent: {} %%")',
    ),
    ('logger.info(f"Empty f-string: {{}}")', 'logger.info("Empty f-string: {}")'),
    (
        'logger.info(f"Empty f-string with percent: {{}} %")',
        'logger.info("Empty f-string with percent: {} %%")',
    ),
    (
        'self._logger.info(f"Empty f-string with braces: {{}}")',
        'self._logger.info("Empty f-string with braces: {}")',
    ),
    (
        '__logger.info(f"{value} created with specs: {self.__specs}")',
        '__logger.info("%s created with specs: %s", value, self.__specs)',
    ),
    (
        "# Logger usage without f-string remains unchanged",
        "# Logger usage without f-string remains unchanged",
    ),
    (
        'logger.info(f"Reading {len(paths):,} files for {name1} - {name2} - {service}...")',
        'logger.info("Reading %s files for %s - %s - %s...", len(paths), name1, name2, service)',
    ),
    (
        'logger.info(f"Value with sign: {value:+d}")',
        'logger.info("Value with sign: %+d", value)',
    ),
]

STANDARD_LOGGING_IMPORT = (
    'import logging\nname = "pytest"\nlogging.info(f"Hello, {name}!")\n'
)
NON_STANDARD_LOGGING_IMPORT = (
    'from loguru import logger\nname = "pytest"\nlogger.info(f"Hello, {name}!")\n'
)


@fixture(scope="function", params=["standard", "non_standard"])
def temp_logging_fstring_file(request):
    """Fixture to create a temporary file with logging f-strings."""
    content = (
        STANDARD_LOGGING_IMPORT
        if request.param == "standard"
        else NON_STANDARD_LOGGING_IMPORT
    )
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".py", mode="w", encoding="utf-8"
    ) as temp_file:
        temp_file.write(content)
        temp_file_path = Path(temp_file.name)
    yield temp_file_path
    temp_file_path.unlink(missing_ok=True)


class TestDataForSanity:
    @mark.parametrize("content, expected", TEST_DATA)
    def test_sanity(self, content, expected):
        assert isinstance(content, str)
        assert isinstance(expected, str)

    def test_valid_py_syntax(self):
        for content, expected in TEST_DATA:
            try:
                compile(content, "<string>", "exec")
                compile(expected, "<string>", "exec")
            except SyntaxError as e:
                assert False, f"Syntax error in test data: {e}"


class TestConvertFStringsToPercentFormat:
    @mark.parametrize("content, expected", TEST_DATA)
    def test_transform(self, content, expected):
        transformer = Transformer(Path(), check_import=False)
        result = transformer.run(content)

        normalized_result = result.strip()
        normalized_expected = expected.strip()

        assert normalized_result == normalized_expected, (
            f"Expected {normalized_expected}, but got {normalized_result}"
        )


class TestTransformerHypothesis:
    @given(st.from_regex(r'f["\'][^\n]+["\']', fullmatch=True))
    def test_fstring_transformation_does_not_crash(self, text):
        assume("\x00" not in text)
        # The transformer should not raise exceptions on any f-string
        transformer = Transformer(Path(), check_import=False)
        try:
            transformer.run(text)
        except (ValueError, SyntaxError, TypeError) as e:
            assert False, f"Transformer crashed on input: {text} with error: {e}"


class TestTransformerWithFiles:
    def test_transform_file(self, tmp_path):
        temp_file = tmp_path / "temp_test_file.py"
        temp_file.write_text(
            'import logging\nname = "world"\nlogging.info(f"Hello, {name}!")',
            encoding="utf-8",
        )

        process_file(temp_file, fix=True, check_import=True)
        with open(temp_file, "r", encoding="utf-8") as file:
            content = file.read()
        if "import logging" in content:
            assert 'logging.info("Hello, %s!", name)' in content
        else:
            assert NON_STANDARD_LOGGING_IMPORT in content
