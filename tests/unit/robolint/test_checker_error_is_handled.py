import os

from overrides import override
from pylint.testutils import CheckerTestCase
import pytest
from pytest_mock import MockerFixture
from robolint.checkers.base_checkers import StepChecker
from robolint.run import RobolintRun
from robolint.test_utils import INTERNAL_ROBOLINT_ERROR_EXIT_CODE
from robolint.test_utils import RobolintCheckerTestCase
from robolint.utils import MM4Step
from stdlib_utils import get_current_file_abs_directory

PATH_TO_CURRENT_FILE = get_current_file_abs_directory()
PATH_TO_XMLS = os.path.join(PATH_TO_CURRENT_FILE, "xml")


class DummyChecker(StepChecker):
    step_type_id: set[str] = set()

    @override
    def check_step(self, step: MM4Step) -> None:
        raise Exception(  # pylint:disable=broad-exception-raised # Eli (20230714) deliberately raising a general exception
            "Dummy Checker threw an Exception"
        )


class TestHandledByRobolintCheckerTestCase(RobolintCheckerTestCase):
    CHECKER_CLASS = DummyChecker

    def test_When_using_RobolintCheckerTestCase_and_StepChecker_raises_Exception_Then_exit_3(
        self, mocker: MockerFixture
    ) -> None:
        spied_checker = mocker.spy(DummyChecker, "check_step")
        with pytest.raises(SystemExit) as err:
            RobolintRun(
                args=[
                    "--disable=all",
                    os.path.join(
                        PATH_TO_XMLS, "hardcoded-aspiration-volume", "single-active-channel-with-variable.xml"
                    ),
                ]
            )
            assert err.exception_code == INTERNAL_ROBOLINT_ERROR_EXIT_CODE, f"System exited with code {err.exception_code}"  # type: ignore[attr-defined]
            assert spied_checker.call_count == 1, f"DummyChecker.check_step was called {spied_checker.call_count} times"


class TestNotHandledByCheckerTestCase(CheckerTestCase):
    CHECKER_CLASS = DummyChecker

    def test_When_using_CheckerTestCase_and_StepChecker_raises_Exception_Then_exit_0(
        self, mocker: MockerFixture
    ) -> None:
        spied_checker = mocker.spy(DummyChecker, "check_step")
        with pytest.raises(SystemExit) as err:
            RobolintRun(
                args=[
                    "--disable=all",
                    os.path.join(
                        PATH_TO_XMLS, "hardcoded-aspiration-volume", "single-active-channel-with-variable.xml"
                    ),
                ]
            )
            assert (
                err.exception_code == 0  # type: ignore[attr-defined]
            ), "When utilizing robolint_prepare_crash_report, we should exit(0) with no SystemExit exception"
            assert spied_checker.call_count == 1, f"DummyChecker.check_step was called {spied_checker.call_count} times"
