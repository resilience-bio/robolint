import os

from defusedxml.ElementTree import parse
from overrides import override
import pytest
from pytest_mock import MockerFixture
from robolint import HardcodedValuesChecker
from robolint import MM4Step
from robolint import NoStepTypeIdError
from robolint import RoboLinter
from robolint import StepChecker
from robolint.test_utils import RobolintCheckerTestCase
from robolint.utils import XmlModule

from ..fixtures import get_parsed_steps
from ..fixtures import PATH_TO_XMLS


def test_Given_no_command_type_provided__When_init__Then_error() -> None:
    class DummyStepChecker(StepChecker):
        @override
        def check_step(self, step: MM4Step) -> None:
            pass

    with pytest.raises(NoStepTypeIdError, match="DummyStepChecker"):
        DummyStepChecker(RoboLinter())


class TestCheckerWholeModule(RobolintCheckerTestCase):
    # this is just using the aspirate values checker as a representative implemented class to check the functions in the base `StepChecker` class
    CHECKER_CLASS = HardcodedValuesChecker

    def test_When_Method_contains_multiple_steps__Then_only_aspirate_steps_are_visited(
        self, mocker: MockerFixture
    ) -> None:
        subpath = os.path.join("hardcoded-aspiration-volume", "rule-disabled-single-active-channel-hardcoded.xml")
        file = os.path.join(PATH_TO_XMLS, subpath)
        steps = get_parsed_steps(subpath)
        xml = XmlModule()
        xml.tree = parse(file)
        xml.file = file
        expected_aspirate_steps_count = 1

        assert len(steps) > expected_aspirate_steps_count
        spied_visit_step = mocker.spy(HardcodedValuesChecker, "visit_step")
        self.checker.process_module(xml)

        assert spied_visit_step.call_count == expected_aspirate_steps_count
