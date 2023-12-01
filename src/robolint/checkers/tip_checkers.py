"""Checker for issues with tips."""
import re

from overrides import override
from pylint.lint.pylinter import PyLinter

from .base_checkers import StepChecker
from ..constants import TIP_EJECT_STEP_ID
from ..constants import TIP_LOAD_STEP_ID
from ..utils import MM4Step


def check_tip_checker_step(checker: StepChecker, step: MM4Step, option_name: str) -> None:
    option_name = re.sub(r"^(in)?valid-", "", option_name)
    actual = step.get_parameter("motionProfileName")
    patterns: list[re.Pattern[str]] = getattr(checker.linter.config, option_name.replace("-", "_"))
    if patterns and not any(pattern.match(actual) for pattern in patterns):
        patterns_str = ",".join(pattern.pattern for pattern in patterns)
        checker.add_message(type(checker).name, args=(actual, patterns_str))


class TipLoadChecker(StepChecker):
    """Checks that the Load Tips step has the Tip Load motion profile."""

    name = "invalid-tip-load-profile"
    msgs = {
        "C9002": (
            "The motion profile name was '%s', it must match '%s'.",
            name,
            "Identifies when a tip load step uses an invalid motion profile.",
        ),
    }
    options = (
        (
            "tip-load-profile",
            {
                "default": "Tip Load.*",
                "type": "regexp_csv",
                "metavar": "<pattern>[,<pattern>...]",
                "help": "List of regular expressions for allowed motion profile names for a Tip Load step. Typically 'Tip Load.*'.",
            },
        ),
    )

    step_type_id = {TIP_LOAD_STEP_ID}

    @override
    def check_step(self, step: MM4Step) -> None:
        check_tip_checker_step(self, step, type(self).name)


class TipEjectChecker(StepChecker):
    """Checks that the Eject Tips step has the Tip Eject motion profile."""

    name = "invalid-tip-eject-profile"
    msgs = {
        "C9004": (
            "The motion profile name was '%s', please replace with '%s'.",
            "invalid-tip-eject-profile",
            "Identifies when a tip eject step uses an invalid motion profile.",
        ),
    }
    options = (
        (
            "tip-eject-profile",
            {
                "default": "Tip Eject.*",
                "type": "regexp_csv",
                "metavar": "<pattern>[,<pattern>...]",
                "help": "List of regular expressions for allowed motion profile names for a Tip Load step. Typically 'Tip Eject.*'.",
            },
        ),
    )

    step_type_id = {TIP_EJECT_STEP_ID}

    @override
    def check_step(self, step: MM4Step) -> None:
        check_tip_checker_step(self, step, type(self).name)


class TipWasteEjectHeightChecker(StepChecker):
    """Checks that the Tip height meets requirements."""

    name = "invalid-tip-waste-eject-height"
    msgs = {
        "C9009": (
            "The tip waste eject height was <%s>, please replace with <%s>.",
            "invalid-tip-waste-eject-height",
            "Identifies when a tip waste eject height does not meet requirements.",
        ),
    }
    options = (
        (
            "tip-waste-eject-height",
            {
                "default": 50,
                "type": "int",
                "help": "An integer value for the required tip waste eject height.",
            },
        ),
        (
            "tip-waste-chute-name",
            {
                "default": ".*Waste.*",
                "type": "regexp_csv",
                "metavar": "<pattern>[,<pattern>...]",
                "help": "List of regular expressions for allowed Waste Chute names (displays as 'Tip box' in the UI). Typically '.*Waste.*'.",
            },
        ),
    )

    step_type_id = {TIP_EJECT_STEP_ID}

    @override
    def check_step(self, step: MM4Step) -> None:
        plate = step.get_parameter("plate")
        patterns: list[re.Pattern[str]] = getattr(self.linter.config, "tip_waste_chute_name")
        if patterns and any(pattern.match(plate) for pattern in patterns):
            height = int(step.get_parameter("height"))
            expected_height = self.linter.config.tip_waste_eject_height
            if height != expected_height:
                self.add_message("invalid-tip-waste-eject-height", args=(height, expected_height))


def register(linter: PyLinter) -> None:
    """Register the checker during initialization.

    :param `linter`: to register the checker to.
    """
    linter.register_checker(TipLoadChecker(linter))
    linter.register_checker(TipEjectChecker(linter))
    linter.register_checker(TipWasteEjectHeightChecker(linter))
