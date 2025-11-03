"""Transformer module for rewriting logging calls that use f-strings into printf-style formatting.

This module provides a Transformer class based on libcst.CSTTransformer that traverses Python source code,
identifies logging calls (e.g., log.info, log.debug, etc.) using f-strings, and rewrites them to use
printf-style formatting (e.g., log.info("Value: %s", x)). The transformation ensures compatibility with
logging best practices and can optionally check for the presence of logging imports.

The module also includes a Visitor class for diagnostics, which uses the ast module to identify
potential logging calls with f-strings.

Code formatting is handled using the Black formatter.
"""

import ast
import logging
import re
from pathlib import Path

import black
import libcst as cst

logger = logging.getLogger(__name__)
LOG_CALL_PATTERN = re.compile("^[_]{,2}log", re.IGNORECASE)


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
            and any((alias.name == "logging" for alias in node.names))
        )
        or (isinstance(node, ast.ImportFrom) and node.module == "logging")
        for node in ast.walk(tree)
    )


class Transformer(cst.CSTTransformer):
    """Transformer class that rewrites logging calls using f-strings into printf-style formatting.

    This class extends cst.CSTTransformer to traverse the CST and modify logging calls that use f-strings.
    It specifically targets calls to logging methods (debug, info, warning, error, critical) on variables
    whose names start with 'log', and transforms f-string arguments into format strings with placeholders.

    Attributes:
        __check_import: If `True`, the transformer will check if the logging module is imported in the code.
        __file_path: The path to the file being transformed, used for logging purposes.
        __issues: List of issues found during transformation.
    """

    def __init__(self, file_path: Path, check_import: bool = False) -> None:
        """Initialize the Transformer.

        Args:
            file_path: The path to the file being transformed, used for logging purposes.
            check_import: If `True`, the transformer will check if the logging module is imported in the code.
            Defaults to `False`.
        """
        super().__init__()
        self.__check_import = check_import
        self.__file_path: Path = file_path
        self.__issues: list[str] = []

    @property
    def issues(self) -> list[str]:
        """Get the list of issues found during the transformation.

        Returns:
            A list of strings representing issues found in the code.
        """
        return self.__issues

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        """Transform logging calls using f-strings into printf-style formatting.

        Args:
            original_node: The original CST Call node.
            updated_node: The updated CST Call node.

        Returns:
            The potentially transformed CST Call node.
        """
        func = updated_node.func
        if not (
            isinstance(func, cst.Attribute)
            and (
                (
                    isinstance(func.value, cst.Name)
                    and LOG_CALL_PATTERN.match(func.value.value)
                )
                or (
                    isinstance(func.value, cst.Attribute)
                    and LOG_CALL_PATTERN.match(func.value.attr.value)
                )
            )
            and func.attr.value in {"debug", "info", "warning", "error", "critical"}
            and updated_node.args
            and isinstance(updated_node.args[0].value, cst.FormattedString)
        ):
            return updated_node

        fstring_node = updated_node.args[0].value
        try:
            fstring_code = cst.Module([]).code_for_node(fstring_node)
        except (cst.CSTException, ValueError):
            fstring_code = "<f-string>"
        self.__register_issue(original_node, fstring_code)
        parts = []
        values = []
        for part in fstring_node.parts:
            if isinstance(part, cst.FormattedStringText):
                text = part.value.replace("%", "%%")
                text = text.replace("{{", "{").replace("}}", "}")
                parts.append(text)
            elif isinstance(part, cst.FormattedStringExpression):
                fmt = ""
                if part.equal:
                    expr_code = cst.Module([]).code_for_node(part.expression)
                    parts.append(f"{expr_code}=%s")
                elif part.format_spec:
                    fmt = (
                        "".join(getattr(node, "value", "") for node in part.format_spec)
                        if isinstance(part.format_spec, tuple)
                        else getattr(part.format_spec, "value", "")
                    )
                    fmt = fmt.replace("{", "").replace("}", "")

                    if fmt == ",":
                        parts.append("%s")
                    else:
                        parts.append(f"%{fmt}")
                else:
                    parts.append("%s")
                values.append(part.expression)
        format_str = "".join(parts)
        new_args = [
            cst.Arg(value=cst.SimpleString(f'"{format_str}"')),
            *(cst.Arg(value=val) for val in values),
            *updated_node.args[1:],
        ]
        return updated_node.with_changes(args=new_args)

    def __register_issue(self, node: cst.CSTNode, f_string: str) -> None:
        """Register an issue found during transformation.

        Args:
            node: The CST node where the issue was found.
            f_string: The f-string code found in the logging call.
        """
        issue_message = f"F-string in logging call at '{self.__file_path}:{getattr(node, 'lineno', '?')}': {f_string}"
        self.__issues.append(issue_message)

    def run(self, content: str) -> str:
        """Transform the given Python source code by visiting and potentially modifying its CST.

        Parses the input source code, applies CST transformations, and returns the modified code as a string.

        Args:
            content: The Python source code to transform.

        Returns:
            The transformed Python source code as a string.
        """
        if self.__check_import and (not has_logging_import(content)):
            logger.debug("No logging import found in the content.")
            return content
        try:
            module = cst.parse_module(content)
        except cst.ParserSyntaxError as e:
            logger.debug("Invalid Python syntax: %s", e)
            return content
        wrapper = cst.MetadataWrapper(module)
        tree = wrapper.visit(self)
        result = tree.code
        logger.debug("Transformed code:\n%s", result)
        return self.__format(result)

    def __format(self, content: str) -> str:
        """Format the given Python source code using Black.

        Args:
            content: The Python source code to format.

        Returns:
            str: The formatted Python source code as a string.
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
            or (not node.func.value.id.lower().startswith("log"))
            or (node.func.attr not in {"debug", "info", "warning", "error", "critical"})
            or (not node.args)
            or (not isinstance(node.args[0], ast.JoinedStr))
        ):
            print(f"Found possible f-string in logging call: {ast.dump(node)}")
        self.generic_visit(node)
