"""Define a Python source code transformer that rewrites logging calls using f-strings into equivalent calls
using printf-style formatting. It leverages Python's Abstract Syntax Tree (AST) to parse, analyze, and modify code, and
uses the Black formatter to ensure the output is well-formatted.

Key Components

Transformer (class)
Inherits from ast.NodeTransformer. Its main responsibility is to traverse the AST and transform logging calls (e.g.,
log.info(f"Value: {x}")) that use f-strings into calls using printf-style formatting (e.g., log.info("Value: %s", x)).

visit_Call: Core method that detects relevant logging calls, extracts format strings and values from f-strings, and
rewrites the call arguments.
run: Accepts Python source code as a string, applies the transformation, and returns the reformatted code.

Visitor (class)
Inherits from ast.NodeVisitor. Used for diagnostic or exploratory purposes, it prints out information about logging
calls that might use f-strings.

Use of AST and Black
The file relies on Python's ast module for parsing and transforming code, and on the black library for code formatting.
"""

import ast
import logging

import black

logger = logging.getLogger(__name__)


def has_logging_import(content: str) -> bool:
    """Check if the given content contains an import statement for the logging module.

    Args:
        content: The Python source code as a string.

    Returns:
        True if the content contains an import statement for the logging module, False otherwise.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False
    return any(
        (
            isinstance(node, ast.Import)
            and any(alias.name == "logging" for alias in node.names)
        )
        or (isinstance(node, ast.ImportFrom) and node.module == "logging")
        for node in ast.walk(tree)
    )


class Transformer(ast.NodeTransformer):
    """Transformer class that rewrites logging calls using f-strings into printf-style formatting.
    This class extends ast.NodeTransformer to traverse the AST and modify logging calls that use f-strings.
    It specifically targets calls to logging methods (debug, info, warning, error, critical) on variables
    whose names start with 'log', and transforms f-string arguments into format strings with placeholders.
    """

    def __init__(self, check_import: bool = False) -> None:
        """Initialize the Transformer with an option to check for logging imports.

        Args:
            check_import: If True, the transformer will check if the logging module is imported in the code.
        """
        super().__init__()
        self.__check_import = check_import

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Visit a function call node in the AST and transform logging calls that use f-strings
        into equivalent calls using printf-style formatting.

        Specifically, this method:
        - Checks if the call is to a logging method (debug, info, warning, error, critical) on a variable
          whose name starts with 'log'.
        - Detects if the first argument is an f-string (ast.JoinedStr).
        - Converts the f-string into a format string with placeholders (e.g., "%s") and extracts the
          corresponding values.
        - Replaces the original f-string argument with the new format string and value arguments.

        Args:
            node: The AST node representing the function call.

        Returns:
           The transformed AST node if applicable, otherwise the result of generic_visit.
        """
        if (
            not isinstance(node.func, ast.Attribute)
            or not isinstance(node.func.value, ast.Name)
            or not node.func.value.id.lower().startswith("log")
            or node.func.attr not in {"debug", "info", "warning", "error", "critical"}
            or not node.args
            or not isinstance(node.args[0], ast.JoinedStr)
        ):
            return self.generic_visit(node)

        f_string = node.args[0]
        parts: list[str] = []
        values: list[ast.expr] = []

        for value in f_string.values:
            if isinstance(value, ast.Constant):
                if isinstance(value.value, str):
                    escaped_value = value.value.replace("%", "%%")
                    parts.append(escaped_value)
            elif isinstance(value, ast.FormattedValue):
                if value.format_spec and isinstance(value.format_spec, ast.JoinedStr):
                    fmt = "".join(
                        str(val.value)
                        for val in value.format_spec.values
                        if isinstance(val, ast.Constant)
                    )
                    parts.append(f"%{fmt}")
                else:
                    parts.append("%s")
                values.append(value.value)

        # Preserve the kind from the original node if available (e.g., unicode or bytes)
        kind = getattr(node, "kind", None)
        converted_string = ast.Constant(value="".join(parts), kind=kind)
        new_args = [converted_string, *values]

        # log the file path and line number for debugging
        logger.info(
            "Transforming logging call at %s:%d: %s -> %s",
            node.lineno,
            node.col_offset,
            ast.dump(node),
            new_args,
        )

        return ast.Call(func=node.func, args=new_args, keywords=node.keywords)

    def run(self, content: str) -> str:
        """Transform the given Python source code by visiting and potentially modifying its AST.

        Parses the input source code, applies AST transformations, and returns the modified code as a string.

        Args:
            content: The Python source code to transform.

        Returns:
            The transformed Python source code as a string.
        """
        if self.__check_import and not has_logging_import(content):
            logger.debug("No logging import found in the content.")
            return content

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.debug("Invalid Python syntax: %s", e)
            return content

        tree = self.visit(tree)
        result = ast.unparse(tree)
        logger.debug("Transformed code:\n%s", result)
        return self.__format(result)

    def __format(self, content: str) -> str:
        """Format the given Python source code using Black.

        Args:
            content: The Python source code to format.

        Returns:
            The formatted Python source code as a string.
        """
        try:
            return black.format_str(
                content,
                mode=black.FileMode(line_length=120),
            ).strip()
        except black.InvalidInput as e:
            logger.debug("Error formatting code with Black: %s", e)
            return content


class Visitor(ast.NodeVisitor):
    """Visitor class that traverses the AST and prints out information about logging calls.

    This class extends `ast.NodeVisitor` to inspect function call nodes
    and identify those that match the logging pattern with f-strings.
    It is primarily used for diagnostic purposes, allowing developers to see potential issues
    with logging calls in their codebase.
    """

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call node in the AST and print information about logging calls.

        Args:
            node: The AST node representing the function call.
        """
        if (
            not isinstance(node.func, ast.Attribute)
            or not isinstance(node.func.value, ast.Name)
            or not node.func.value.id.lower().startswith("log")
            or node.func.attr not in {"debug", "info", "warning", "error", "critical"}
            or not node.args
            or not isinstance(node.args[0], ast.JoinedStr)
        ):
            print(f"Found possible f-string in logging call: {ast.dump(node)}")
        self.generic_visit(node)
