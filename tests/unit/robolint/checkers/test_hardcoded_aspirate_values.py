import os
from unittest.mock import ANY

from pylint.testutils import MessageTest
from robolint import HardcodedValuesChecker
from robolint.test_utils import RobolintCheckerTestCase

from ..fixtures import get_parsed_steps
from ..fixtures import get_parsed_xml_module


class TestHardcodedValuesCheckerSingleSteps(RobolintCheckerTestCase):

    CHECKER_CLASS = HardcodedValuesChecker

    def test_When_Single_Channel_Using_variable__Then_no_error(self) -> None:
        steps = get_parsed_steps(os.path.join("hardcoded-aspiration-volume", "single-active-channel-with-variable"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[0])

    def test_When_Single_Channel_hardcoded__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join("hardcoded-aspiration-volume", "single-active-channel-hardcoded"))
        step_index_to_test = 1
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-aspirate-volume",
                args=("A01: 5 uL",),
                line=step_index_to_test,
            )
        ):
            self.checker.visit_step(steps[step_index_to_test])

    def test_When_Single_Channel_hardcoded_not_A01__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join("hardcoded-aspiration-volume", "single-active-channel-not-a1-hardcoded"))
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-aspirate-volume",
                args=("C05: 8.3 uL",),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])

    def test_When_one_variable_and_one_hardcoded__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join("hardcoded-aspiration-volume", "one-variable-one-hardcoded"))
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-aspirate-volume",
                args=("D08: 4.3 uL",),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])

    def test_When_two_hardcoded__Then_error_shows_both_wells(self) -> None:
        steps = get_parsed_steps(os.path.join("hardcoded-aspiration-volume", "two-active-hardcoded-channels"))
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-aspirate-volume",
                args=("C05: 8.3 uL, D08: 4.3 uL",),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])

    def test_When_Volume_Property_Set_And_Variable_Also_Set__Then_no_error(self) -> None:
        steps = get_parsed_steps(
            os.path.join("hardcoded-aspiration-volume", "volume-property-set-even-though-variable-also-set")
        )
        with self.assertNoMessages():
            self.checker.visit_step(steps[5])


class TestHardcodedValuesCheckerWholeModule(RobolintCheckerTestCase):

    CHECKER_CLASS = HardcodedValuesChecker

    def test_When_Single_Channel_hardcoded__Then_error(self) -> None:
        xml_module = get_parsed_xml_module(
            os.path.join("hardcoded-aspiration-volume", "single-active-channel-hardcoded.xml")
        )
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-aspirate-volume",
                args=("A01: 5 uL",),
                line=1,
            )
        ):
            self.checker.process_module(xml_module)
