import os

from lxml.etree import _Element
import pytest
from pytest_mock import MockerFixture
from robolint import MM4Step
from robolint import parse_steps
from robolint import utils

from ..fixtures import PATH_TO_XMLS


@pytest.fixture(scope="function", name="basic_step")
def fixture_basic_step() -> MM4Step:
    file = os.path.join(PATH_TO_XMLS, "hardcoded-aspiration-volume", "single-active-channel-with-variable.xml")
    steps = parse_steps(file)
    return steps[0]


def test__When_parameters_node_accessed__Then_parameters_node_available(basic_step: MM4Step) -> None:

    parameters_node = basic_step.parameters_node

    assert isinstance(parameters_node, _Element)
    assert parameters_node.attrib["name"] == "Parameters"


def test__Given_parameters_node_already_accessed__When_parameters_node_accessed_again__Then_cached_value_used(
    mocker: MockerFixture, basic_step: MM4Step
) -> None:
    spied_parse = mocker.spy(basic_step, "parse")
    assert isinstance(basic_step.parameters_node, _Element)
    original_call_count = spied_parse.call_count
    assert original_call_count > 0

    basic_step.parameters_node  # pylint:disable=pointless-statement # this is the actual action of the test

    assert spied_parse.call_count == original_call_count


def test_When_get_parameter_called__Then_value_returned(basic_step: MM4Step) -> None:
    assert basic_step.get_parameter("A01.enable") == "True"


def test_Given_parameter_already_obtained__When_get_parameter_called__Then_cached_value_used(
    basic_step: MM4Step, mocker: MockerFixture
) -> None:
    spied_find_element = mocker.spy(utils, "find_exactly_one_xml_element")
    basic_step.get_parameter("A01.enable")
    original_call_count = spied_find_element.call_count
    assert original_call_count > 0

    basic_step.get_parameter("A01.enable")

    assert spied_find_element.call_count == original_call_count
