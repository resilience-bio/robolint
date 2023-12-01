import os
from unittest.mock import ANY

from pylint.testutils import MessageTest
from robolint import HardcodedValuesChecker
from robolint.test_utils import RobolintCheckerTestCase

from ..fixtures import get_parsed_steps
from ..fixtures import get_parsed_xml_module


class TestHardcodedValuesCheckerSingleSteps(RobolintCheckerTestCase):

    CHECKER_CLASS = HardcodedValuesChecker
    XML_SUBPATH = "hardcoded_mix_volume"

    def test_When_one_variable_and_one_hardcoded__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "one-channel-variable-other-hardcoded"))
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-mix-volume",
                args=("D05: 2.3 uL",),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])

    def test_When_one_variable__Then_no_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "one-channel-variable"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[0])

    def test_When_two_hardcoded__Then_error_shows_both_wells(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "two-channels-hardcoded"))
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-mix-volume",
                args=("G04: 12.8 uL, B10: 9.3 uL",),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])


class TestHardcodedValuesCheckerWholeModule(RobolintCheckerTestCase):

    CHECKER_CLASS = HardcodedValuesChecker
    XML_SUBPATH = "hardcoded_mix_volume"

    def test_When_one_variable_and_one_hardcoded__Then_error(self) -> None:
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "one-channel-variable-other-hardcoded.xml"))
        with self.assertAddsMessages(
            MessageTest(
                "hardcoded-mix-volume",
                args=("D05: 2.3 uL",),
                line=ANY,
            )
        ):
            self.checker.process_module(xml_module)
