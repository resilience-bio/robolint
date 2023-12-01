import sys
from typing import Iterable

from pytest_mock import MockerFixture


def mock_argv_filelist(mocker: MockerFixture, file_list: Iterable[str]) -> None:

    argv = ["dummy.py"]
    argv.extend(file_list)
    mocker.patch.object(sys, "argv", argv)
