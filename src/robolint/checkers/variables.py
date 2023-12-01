"""Checker for variable names."""
from typing import Callable

import humps
from overrides import override
from pylint.lint.pylinter import PyLinter
from robolint.robolinter import RoboLinter

from .base_checkers import StepChecker
from ..utils import MM4Step


class VariableNameChecker(StepChecker):
    """Checks that variable names follow convention.

    Variable Naming Conventions
    - Configurable text case: pascal, camel, kebab or snake
    - Abbreviations
    """

    name = "variable-name-checker"
    msgs = {
        "C9007": (
            "The variable name was '%s', it must match '%s'.",
            "invalid-variable-case",
            "Identifies when a variable name isn't in the specified case.",
        ),
        "C9008": (
            "The variable name '%s' contained '%s', it should be abbreviated to '%s'.",
            "non-abbreviated-variable",
            "Checks for preferred abbreviations of specified names.",
        ),
    }
    options = (
        (
            "variable-name-abbreviations",
            {
                "default": "",
                "type": "csv",
                "metavar": "Name,Abbreviation[,Name,Abbreviation,...]",
                "help": "Comma delimited list of names and abbreviations that can be substituted for them. E.g Destination,Dest,Source,Src,Volume,Vol,Cycles,Cyc",
            },
        ),
        (
            "variable-name-case",
            {
                "default": "camel",
                "type": "string",
                "metavar": "camel|pascal|",
                "help": "Variable name case, one of camel, kebab, pascal, snake.",
            },
        ),
    )
    step_type_id = set()
    abbreviations: dict[str, str] = {}
    case_check_function: Callable[[str], bool]
    case_function: Callable[[str], str]
    variable_xpaths: list[str] = [
        r"Items/Item/Simple[@value='VariableName']/../Simple[2]",
        r"Items/Item/Simple[@value='VariableValueVariable']/../Simple[2]",
        r"Items/Item/Simple[@value='ValueVariable']/../Simple[2]",
        r"Items/Item/Simple[@value='AssignToVariable']/../Simple[2]",
        r"Items/Item/Simple[@value='plateVariable']/../Simple[2]",
        r"Items/Item/Simple[re:match(@value, '^[A-Z]{1,2}\d{2}\.volumeVariable$')]/../Simple[2]",
    ]

    def __init__(self, linter: RoboLinter) -> None:
        super().__init__(linter)
        self.variables_observed: set[str] = set()
        self._variables_observed_in_step: set[str] = set()
        self._initialized: bool = False

    def set_abbreviations(self) -> None:
        items = self.linter.config.variable_name_abbreviations
        if len(items) % 2 != 0:
            raise ValueError("Odd number of variable names / abbreviations provided: " + ",".join(items))
        self.abbreviations: dict[str, str] = {items[counter]: items[counter + 1] for counter in range(0, len(items), 2)}

    def set_case_functions(self) -> None:
        """Set the functions that will test and transform the text case."""
        case_str = self.linter.config.variable_name_case
        if case_str == "pascal":
            self.case_check_function = humps.is_pascalcase
            self.case_function = humps.pascalize
        elif case_str == "camel":
            self.case_check_function = humps.is_camelcase
            self.case_function = humps.camelize
        elif case_str == "kebab":
            self.case_check_function = humps.is_kebabcase
            self.case_function = humps.kebabize
        elif case_str == "snake":
            self.case_check_function = humps.is_snakecase
            self.case_function = humps.decamelize
        else:
            raise ValueError(f"Could not determine variable case. Input was '{case_str}'")

    @override
    def check_step(self, step: MM4Step) -> None:
        if not self._initialized:
            self.set_abbreviations()
            self.set_case_functions()
            self._initialized = True

        self._variables_observed_in_step = set()
        for xpath in type(self).variable_xpaths:
            for node in step.parameters_node.xpath(xpath, namespaces={"re": "http://exslt.org/regular-expressions"}):  # type: ignore[union-attr]
                name = node.get("value", default="")  # type: ignore[union-attr]
                self.variables_observed.add(name)
                self._run_checks(name)

    def _run_checks(self, name: str) -> None:
        if name not in self._variables_observed_in_step:
            self._variables_observed_in_step.add(name)
            if not self.case_check_function(name):
                new_name = self.case_function(name)
                self.add_message("invalid-variable-case", args=(name, new_name))

            self._check_abbreviations(name)

    def _check_abbreviations(self, name: str) -> None:
        name_cmp = name.casefold()
        for token in humps.main.SPLIT_RE.split(name):  # type: ignore[attr-defined] # it's there but not in the `pyi` file.
            if not token:
                continue
            token_cmp = token.casefold()
            for key, value in self.abbreviations.items():
                key_cmp = key.casefold()
                if key_cmp != name_cmp and key_cmp == token_cmp:
                    self.add_message("non-abbreviated-variable", args=(name, key, value))


def register(linter: PyLinter) -> None:
    """Register the checker during initialization.

    :param `linter`: to register the checker to.
    """
    linter.register_checker(VariableNameChecker(linter))
