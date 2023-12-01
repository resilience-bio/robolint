"""Testing helpers."""

import sys
from typing import NoReturn

import pylint
from pylint.testutils import CheckerTestCase
from robolint.run import robolint_prepare_crash_report


# arbitrary exit code that's not 1 (that's reserved in `pre-commit` for modifying files)
INTERNAL_ROBOLINT_ERROR_EXIT_CODE = 3


def prepare_crash_report_and_exit(exception: Exception, filepath: str, crash_file_path: str) -> NoReturn:
    """`Pylint` silences errors but we want test cases to fail."""
    robolint_prepare_crash_report(exception, filepath, crash_file_path)
    sys.exit(INTERNAL_ROBOLINT_ERROR_EXIT_CODE)


class RobolintCheckerTestCase(CheckerTestCase):
    def setup_class(self) -> None:
        pylint.lint.pylinter.prepare_crash_report = prepare_crash_report_and_exit
