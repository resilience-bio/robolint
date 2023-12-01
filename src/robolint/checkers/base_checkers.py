"""Base class for step checkers."""

import abc
from typing import Any
from typing import Optional

from astroid import nodes
from overrides import EnforceOverrides
from overrides import override
from pylint.checkers import BaseRawFileChecker
from pylint.interfaces import Confidence

from ..exceptions import NoStepTypeIdError
from ..robolinter import RoboLinter
from ..utils import MM4Step
from ..utils import parse_steps_from_etree
from ..utils import XmlModule


class StepChecker(BaseRawFileChecker, EnforceOverrides):
    """Checks individual steps."""

    step_type_id: Optional[set[str]] = None  # TODO (Eli 20230222): rename this to `step_type_ids`
    _current_step_index: int

    def __init__(self, linter: RoboLinter) -> None:
        if self.step_type_id is None:
            raise NoStepTypeIdError(self.__class__.__name__)
        super().__init__(linter)

    @abc.abstractmethod
    def check_step(self, step: MM4Step) -> None:
        raise NotImplementedError()

    def visit_step(self, step: MM4Step) -> None:
        self._current_step_index = step.step_index
        self.check_step(step)

    @override(check_signature=False)  # this uses `XmlModule` instead of an `astroid` node
    def process_module(self, node: XmlModule) -> None:
        """Process a module."""
        steps = parse_steps_from_etree(node.tree.getroot())
        if self.step_type_id is None:
            raise NotImplementedError(
                "At this point, step type ID should never be none, it should have been set as a class attribute."
            )

        for step in steps:
            if self.step_type_id and step.step_type_id not in self.step_type_id:
                continue
            self.visit_step(step)

    @override
    def add_message(
        self,
        msgid: str,
        line: Optional[int] = None,
        node: Optional[nodes.NodeNG] = None,
        args: Any = None,
        confidence: Optional[Confidence] = None,
        col_offset: Optional[int] = None,
        end_lineno: Optional[int] = None,
        end_col_offset: Optional[int] = None,
    ) -> None:
        """Override the parent class to automatically set the line number based on the step."""
        super().add_message(msgid=msgid, args=args, confidence=confidence, line=self._current_step_index)
