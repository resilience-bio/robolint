"""`Robocase` variable name checker.

Pascal case with an optional underscore and numeric suffix.
"""
import re

import humps
from overrides import EnforceOverrides
from overrides import override
from pylint.lint.pylinter import PyLinter
from robolint.checkers.variables import VariableNameChecker


def is_robocase(text: str) -> bool:
    """Test if test is in `Robocase`."""
    name = text
    match = re.search(r"(.+?)(\d+)$", text)
    if match:
        name = match.group(1)
        digits = match.group(2)
        if len(digits) < 2:
            return False
        if name[-1] != "_":
            return False
        name = name[:-1]
    return humps.is_pascalcase(name)


def to_robocase(text: str) -> str:
    """Convert text to `Robocase`."""
    name = text
    numbers = ""
    match = re.search(r"(.+?)(\d+)$", text)
    if match:
        name = match.group(1)
        numbers = match.group(2)
        name = name.replace("-", "_")
        if len(numbers) < 2:
            numbers = f"0{numbers}"
        numbers = f"_{numbers}" if numbers else ""
        if name.endswith("_"):
            name = name[:-1]
    return f"{humps.pascalize(name)}{numbers}"


class RobocaseVariableNameChecker(VariableNameChecker, EnforceOverrides):
    """Adds `Robocase` text case to the `VariableNameChecker` options."""

    @override
    def set_case_functions(self) -> None:
        case_str = self.linter.config.variable_name_case
        if case_str == "robocase":
            self.case_check_function = is_robocase
            self.case_function = to_robocase
        else:
            super().set_case_functions()


def register(linter: PyLinter) -> None:
    """Register the checker during initialization.

    :param `linter`: to register the checker to.
    """
    linter.register_checker(RobocaseVariableNameChecker(linter))
