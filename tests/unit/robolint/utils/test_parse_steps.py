import os

from robolint import parse_steps

from ..fixtures import PATH_TO_XMLS


def test__When_single_step__Then_returns_one_step() -> None:
    file = os.path.join(PATH_TO_XMLS, "hardcoded-aspiration-volume", "single-active-channel-with-variable.xml")
    steps = parse_steps(file)
    assert len(steps) == 1


def test__When_multiple_step__Then_returns_multiple_steps() -> None:
    file = os.path.join(PATH_TO_XMLS, "hardcoded-aspiration-volume", "single-active-channel-hardcoded.xml")
    steps = parse_steps(file)
    assert len(steps) == 2
