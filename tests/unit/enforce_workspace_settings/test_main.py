from unittest.mock import call

from pytest_mock import MockerFixture
from robolint.hooks import enforce_workspace_settings
from robolint.hooks.enforce_workspace_settings import main

from ..utils import mock_argv_filelist


def test_main_calls_enforce_values_with_passed_filenames(mocker: MockerFixture) -> None:
    mocked_function = mocker.patch.object(enforce_workspace_settings, "enforce_values", return_value=[])
    expected_file_list = ["dummy4.config", "dummy2.config"]
    mock_argv_filelist(mocker, expected_file_list)
    main()
    assert mocked_function.call_count == 2
    mocked_function.assert_has_calls([call(expected_file_list[0]), call(expected_file_list[1])], any_order=True)


def test_When_enforce_values_identifies_problem__Then_main_returns_1(mocker: MockerFixture) -> None:
    mocker.patch.object(enforce_workspace_settings, "enforce_values", return_value=["var1"])
    expected_file_list = ["dummy3.config"]
    mock_argv_filelist(mocker, expected_file_list)
    actual = main()
    assert actual == 1


def test_When_enforce_values_identifies_problem__Then_main_logs_the_variable_and_file_name(
    mocker: MockerFixture,
) -> None:
    expected_variable_name = "var2"
    mocker.patch.object(enforce_workspace_settings, "enforce_values", return_value=[expected_variable_name])
    mocked_logger = mocker.patch.object(enforce_workspace_settings.logger, "info")
    expected_file_list = ["dummy2.config"]
    mock_argv_filelist(mocker, expected_file_list)
    main()
    assert mocked_logger.call_count == 1
    actual_call_str = str(mocked_logger.call_args_list[0])
    assert expected_variable_name in actual_call_str
    assert expected_file_list[0] in actual_call_str


def test_When_enforce_values_identifies_no_problems__Then_main_returns_0(mocker: MockerFixture) -> None:
    mocker.patch.object(enforce_workspace_settings, "enforce_values", return_value=[])
    expected_file_list = ["dummy1.config"]
    mock_argv_filelist(mocker, expected_file_list)
    actual = main()
    assert actual == 0
