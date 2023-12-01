import os
import shutil
from tempfile import TemporaryDirectory

import pytest
from robolint.hooks.enforce_workspace_settings import enforce_values
from stdlib_utils import get_current_file_abs_directory

PATH_TO_CURRENT_FILE = get_current_file_abs_directory()
PATH_TO_CONFIGS = os.path.join(PATH_TO_CURRENT_FILE, "workspace_settings_configs")


def test_When_file_is_clean__Then_returns_falsey() -> None:
    actual = enforce_values(os.path.join(PATH_TO_CONFIGS, "clean.xml"))
    assert not actual


def test_When_one_value_is_wrong__Then_problem_identified_and_new_file_is_clean() -> None:
    original_file_path = os.path.join(PATH_TO_CONFIGS, "always_reconnect_false.xml")
    with TemporaryDirectory() as temp_dir:
        new_file_path = os.path.join(temp_dir, "blah.xml")
        shutil.copy(original_file_path, new_file_path)
        initial_result = enforce_values(new_file_path)
        assert len(initial_result) == 1

        actual = enforce_values(new_file_path)
        assert not actual


@pytest.mark.parametrize(
    ",".join(("test_filename", "expected_message", "test_description")),
    [
        (
            "always_reconnect_false.xml",
            "InitWorkspaceHardwareOptions/AlwaysReConnect changed from 'false' to 'true'",
            "Always Reconnect value should be true",
        ),
        (
            "close_on_success_false.xml",
            "InitWorkspaceHardwareOptions/CloseOnSuccess changed from 'false' to 'true'",
            "Close on Success value should be true",
        ),
        (
            "try_connect_all_false.xml",
            "InitWorkspaceHardwareOptions/TryToConnectAll changed from 'false' to 'true'",
            "Try to Connect All value should be true",
        ),
        (
            "create_new_log_missing.xml",
            "CreateNewLogWhenStartingMethod added and set to 'false'",
            "Create new Log should be present",
        ),
        (
            "create_new_log_in_wrong_position.xml",
            "CreateNewLogWhenStartingMethod was moved to correct position and set to 'false'",
            "Create new Log should be in the position that MM4 automatically puts it, to avoid git conflicts",
        ),
    ],
)
def test_When_single_error_is_present__Then_problem_identified_and_new_file_is_clean(
    test_filename: str, expected_message: str, test_description: str
) -> None:
    original_file_path = os.path.join(PATH_TO_CONFIGS, test_filename)
    with TemporaryDirectory() as temp_dir:
        new_file_path = os.path.join(temp_dir, "blah.xml")
        shutil.copy(original_file_path, new_file_path)
        initial_result = enforce_values(new_file_path)
        assert initial_result == [expected_message]

        actual = enforce_values(new_file_path)
        assert not actual


def test_When_multiple_errors_are_present__Then_problems_identified_and_new_file_is_clean() -> None:
    original_file_path = os.path.join(PATH_TO_CONFIGS, "multiple_errors.xml")
    with TemporaryDirectory() as temp_dir:
        new_file_path = os.path.join(temp_dir, "blah.xml")
        shutil.copy(original_file_path, new_file_path)
        initial_result = enforce_values(new_file_path)
        assert len(initial_result) > 1

        actual = enforce_values(new_file_path)
        assert not actual
