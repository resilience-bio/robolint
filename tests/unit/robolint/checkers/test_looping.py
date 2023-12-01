import os

from pylint.testutils import MessageTest
from pylint.testutils import set_config
from robolint import LoopIndexChecker
from robolint.test_utils import RobolintCheckerTestCase

from ..fixtures import get_parsed_steps
from ..fixtures import get_parsed_xml_module


class TestLoopIndexCheckerSingleSteps(RobolintCheckerTestCase):

    CHECKER_CLASS = LoopIndexChecker
    XML_SUBPATH = "invalid_loop_start_index"

    @set_config(loop_start_index=0)  # type:ignore[misc] # mypy is throwing an error saying this decorator is untyped
    def test_Given_checker_set_for_0__When_Loop_starts_at_0__Then_no_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-starting-at-zero"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[0])

    @set_config(loop_start_index=0)  # type:ignore[misc] # mypy is throwing an error saying this decorator is untyped
    def test_When_Loop_bound_to_variable_and_hardcoded_to_3__Then_no_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-bound-to-variable-but-hardcoded-to-3"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[0])

    @set_config(loop_start_index=0)  # type:ignore[misc] # mypy is throwing an error saying this decorator is untyped
    def test_Given_checker_set_for_0__When_Loop_starts_at_1__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-starting-at-one"))
        step_index_to_test = 0
        with self.assertAddsMessages(
            MessageTest(
                "invalid-loop-start-index",
                args=(1, 0),
                line=step_index_to_test,
            )
        ):
            self.checker.visit_step(steps[step_index_to_test])

    @set_config(loop_start_index=0)  # type:ignore[misc] # mypy is throwing an error saying this decorator is untyped
    def test_Given_checker_set_for_0__When_Loop_starts_at_1_at_2nd_step__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-starting-at-one-at-second-step"))
        step_index_to_test = 1
        with self.assertAddsMessages(
            MessageTest(
                "invalid-loop-start-index",
                args=(1, 0),
                line=step_index_to_test,
            )
        ):
            self.checker.visit_step(steps[step_index_to_test])

    @set_config(loop_start_index=1)  # type:ignore[misc] # mypy is throwing an error saying this decorator is untyped
    def test_Given_checker_set_for_1__When_Loop_starts_at_1__Then_no_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-starting-at-one"))
        step_index_to_test = 0
        with self.assertNoMessages():
            self.checker.visit_step(steps[step_index_to_test])

    @set_config(loop_start_index=1)  # type:ignore[misc] # mypy is throwing an error saying this decorator is untyped
    def test_Given_checker_set_for_1__When_Loop_starts_at_0__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-starting-at-zero"))
        step_index_to_test = 0
        with self.assertAddsMessages(
            MessageTest(
                "invalid-loop-start-index",
                args=(0, 1),
                line=step_index_to_test,
            )
        ):
            self.checker.visit_step(steps[step_index_to_test])


class TestLoopIndexCheckerWholeModule(RobolintCheckerTestCase):

    CHECKER_CLASS = LoopIndexChecker
    XML_SUBPATH = "invalid_loop_start_index"

    @set_config(loop_start_index=0)  # type:ignore[misc] # mypy is throwing an error saying this decorator is untyped
    def test_Given_checker_set_for_0__When_Loop_starts_at_1__Then_error(self) -> None:
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "loop-starting-at-one.xml"))
        with self.assertAddsMessages(
            MessageTest(
                "invalid-loop-start-index",
                args=(1, 0),
                line=0,
            )
        ):
            self.checker.process_module(xml_module)
