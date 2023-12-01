import os
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import MagicMock

from hooks.pip_tools_hook import main
from pytest_mock import MockerFixture
from stdlib_utils import get_current_file_abs_directory


PATH_TO_CURRENT_FILE = get_current_file_abs_directory()
PATH_TO_REQUIREMENTS = os.path.join(PATH_TO_CURRENT_FILE, "requirements_files")


def test_When_requirements_txt_up_to_date__Then_no_printed_message(
    mocker: MockerFixture, mock_print: MagicMock
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        origin = Path().absolute()
        try:
            os.chdir(temp_dir)
            shutil.copy(
                os.path.join(PATH_TO_REQUIREMENTS, f"requirements-clean-{sys.platform}.txt"), "requirements.txt"
            )
            shutil.copy(os.path.join(PATH_TO_REQUIREMENTS, "requirements.in"), "requirements.in")
            argv = ["dummy.py", "compile", "requirements.txt", "requirements.in"]
            mocker.patch.object(sys, "argv", argv)

            actual_exit_code = main()

            mock_print.assert_not_called()
            assert actual_exit_code == 0

        finally:
            os.chdir(origin)


def test_When_requirements_txt_not_up_to_date__Then_message_is_printed(
    mocker: MockerFixture, mock_print: MagicMock
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "requirements.txt")
        shutil.copy(os.path.join(PATH_TO_REQUIREMENTS, "requirements-dirty.txt"), temp_file_path)
        argv = ["dummy.py", "compile", temp_file_path, os.path.join(PATH_TO_REQUIREMENTS, "requirements.in")]
        mocker.patch.object(sys, "argv", argv)
        actual = main()
    assert actual == 1
    assert mock_print.call_count > 2


def test_Given_arg_to_always_exit_zero__When_requirements_txt_not_up_to_date__Then_exit_code_is_zero_after_compile_run(
    mocker: MockerFixture, mock_print: MagicMock
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "requirements.txt")
        shutil.copy(os.path.join(PATH_TO_REQUIREMENTS, "requirements-dirty.txt"), temp_file_path)
        argv = [
            "dummy.py",
            "exit-zero",
            "compile",
            temp_file_path,
            os.path.join(PATH_TO_REQUIREMENTS, "requirements.in"),
        ]
        mocker.patch.object(sys, "argv", argv)
        actual = main()
    assert actual == 0
    compile_notification_print_args = mock_print.call_args_list[2]
    actual_args, _ = compile_notification_print_args
    assert "compiled" in actual_args[0]
