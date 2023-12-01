"""Checker for looping."""

from overrides import override
from pylint.lint.pylinter import PyLinter

from .base_checkers import StepChecker
from ..constants import BEGIN_LOOP_STEP_ID
from ..utils import MM4Step


class LoopIndexChecker(StepChecker):
    """Checks loop steps for not being indexed at the specified value."""

    name = "invalid_loop_start_index"
    msgs = {
        "C9001": (
            "The loop start index was %s, please replace with %s.",
            "invalid-loop-start-index",
            "Identifies when a loop start index doesn't match convention.",
        ),
    }
    options = (
        (
            "loop-start-index",
            {
                "default": 0,
                "type": "int",
                "metavar": "<int>",
                "help": "Value that loop counters should begin with. Typically 0 or 1.",
            },
        ),
    )

    step_type_id = {BEGIN_LOOP_STEP_ID}

    @override
    def check_step(self, step: MM4Step) -> None:
        """Check if step has invalid loop start index."""
        if step.get_parameter("VariableValueVariable") != "":
            # if the loop start index is bound to a variable, don't check further
            return
        actual_loop_start = int(step.get_parameter("VariableValue"))
        expected_loop_start = self.linter.config.loop_start_index
        if actual_loop_start != expected_loop_start:
            self.add_message("invalid-loop-start-index", args=(actual_loop_start, expected_loop_start))


def register(linter: PyLinter) -> None:
    """Register the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(LoopIndexChecker(linter))
