"""Overriding `Pylint` Run objects to be able to run `Robolint`."""
from pathlib import Path
import re
import sys
import traceback
from typing import Optional
from typing import Sequence

import pylint.lint.pylinter
from pylint.lint.run import Run
from robolint.robolinter import RoboLinter
from robolint.utils import robolint_overrides


pylint_prepare_crash_report = pylint.lint.pylinter.prepare_crash_report


def robolint_prepare_crash_report(exception: Exception, filepath: str, crash_file_path: str) -> Path:
    # Make errors more visible.  Pylint silently crashes by default...not sure why.
    print(f"There was an error handling '{filepath}'.")  # allow-print
    traceback.print_exc(1)
    error_file_path: Path = pylint_prepare_crash_report(exception, filepath, crash_file_path)
    print(f" A log file of the error is located at: '{error_file_path}'.")  # allow-print
    return error_file_path


pylint.lint.pylinter.prepare_crash_report = robolint_prepare_crash_report

robolint_overrides()


class RobolintRun(Run):
    # pylint:disable=too-few-public-methods # Eli (20230214): this is just overriding to set the linter class
    LinterClass = RoboLinter


# copied from `pylint's` `__init__.py`
def run_pylint(argv: Optional[Sequence[str]] = None) -> int:
    """Run pylint.

    `argv` can be a sequence of strings normally supplied as arguments on the command line
    """
    try:
        RobolintRun(argv or sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(2)
    return 0


# copied from pylint`s `venv/bin/pylint`
if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(run_pylint())
