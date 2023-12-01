import os
from unittest.mock import MagicMock

from defusedxml.ElementTree import parse
import pytest
from pytest import CaptureFixture
from pytest_mock import MockerFixture
from robolint import HardcodedValuesChecker
from robolint import RoboLinter
from robolint.utils import XmlModule

from .fixtures import PATH_TO_XMLS


def test_When_run_on_file_with_error__Then_message_shows_up_in_stdout(capsys: CaptureFixture[str]) -> None:
    # adapted from https://github.com/PyCQA/pylint/blob/main/tests/conftest.py#L31

    linter = RoboLinter()
    linter.register_checker(HardcodedValuesChecker(linter))

    linter.check([os.path.join(PATH_TO_XMLS, "hardcoded-aspiration-volume", "one-variable-one-hardcoded.xml")])

    out, err = capsys.readouterr()
    assert err == ""
    assert "hardcoded-aspirate-volume" in out


def test_When_comment_disables_rule__Then_message_is_locally_disabled_and_suppressed(mock_print: MagicMock) -> None:
    linter = RoboLinter()
    linter.register_checker(HardcodedValuesChecker(linter))

    linter.check(
        [os.path.join(PATH_TO_XMLS, "hardcoded-aspiration-volume", "rule-disabled-single-active-channel-hardcoded.xml")]
    )

    assert linter.stats.by_msg == {"suppressed-message": 1, "locally-disabled": 1}


def test_When_comment_does_not_disable_rule__Then_message_not_supressed(mock_print: MagicMock) -> None:
    linter = RoboLinter()
    linter.register_checker(HardcodedValuesChecker(linter))

    linter.check(
        [
            os.path.join(
                PATH_TO_XMLS,
                "hardcoded-aspiration-volume",
                "comment-not-disabling-rule-and-single-active-channel-hardcoded.xml",
            )
        ]
    )

    assert linter.stats.by_msg == {"hardcoded-aspirate-volume": 1}


def test_When_comment_disabling_rule_is_not_a_valid_rule__Then_unknown_option_value_emitted_with_correct_line(
    capsys: CaptureFixture[str],
) -> None:
    expected_line_number = 1

    linter = RoboLinter()
    linter.register_checker(HardcodedValuesChecker(linter))

    linter.check(
        [
            os.path.join(
                PATH_TO_XMLS,
                "robolinter",
                "invalid-rule-disabled-in-comment.xml",
            )
        ]
    )

    assert linter.stats.by_msg == {"unknown-option-value": 1}
    out, err = capsys.readouterr()
    assert err == ""
    assert "robolint: disable" in out
    assert f"xml:{expected_line_number}:0:" in out


@pytest.mark.parametrize(
    ",".join(("test_file_subpath", "expected_call_args", "test_description")),
    [
        (
            os.path.join("hardcoded-aspiration-volume", "rule-disabled-single-active-channel-hardcoded.xml"),
            (("hardcoded-aspirate-volume", 0),),
            "file with clean comment for single rule",
        ),
        (
            os.path.join(
                "hardcoded-aspiration-volume", "messy-comment-rule-disabled-single-active-channel-hardcoded.xml"
            ),
            (("hardcoded-aspirate-volume", 0),),
            "file with messy comment for single rule",
        ),
        (
            os.path.join("robolinter", "two-rules-disabled-in-one-comment.xml"),
            (("hardcoded-aspirate-volume", 0), ("invalid-variable-name", 0)),
            "file with comment for two rules",
        ),
    ],
)
def test_When_process_tokens_run__Then_rule_disabled(
    test_file_subpath: str,
    expected_call_args: tuple[tuple[str, int], ...],
    test_description: str,
    mocker: MockerFixture,
) -> None:
    linter = RoboLinter()
    mocked_disable_next = mocker.patch.object(linter, "disable_next", autospec=True)
    file = os.path.join(PATH_TO_XMLS, test_file_subpath)
    xml = XmlModule()
    xml.file = file
    xml.tree = parse(file)
    linter.process_tokens(xml)
    assert mocked_disable_next.call_count == len(expected_call_args)
    for rule_name, line_number in expected_call_args:
        mocked_disable_next.assert_any_call(rule_name, line=line_number)
