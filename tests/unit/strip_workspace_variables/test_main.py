from unittest.mock import call

from pytest_mock import MockerFixture
from robolint.hooks import strip_workspace_config_values
from robolint.hooks.strip_workspace_config_values import main

from ..utils import mock_argv_filelist


def test_main_calls_strip_values_from_file_with_passed_filenames(mocker: MockerFixture) -> None:
    mocked_strip_values_from_file = mocker.patch.object(
        strip_workspace_config_values, "strip_values_from_file", return_value=[]
    )
    expected_file_list = ["dummy1.config", "dummy2.config"]
    mock_argv_filelist(mocker, expected_file_list)
    main()
    assert mocked_strip_values_from_file.call_count == 2
    mocked_strip_values_from_file.assert_has_calls(
        [call(expected_file_list[0], None), call(expected_file_list[1], None)], any_order=True
    )


def test_When_strip_values_identifies_problem__Then_main_returns_1(mocker: MockerFixture) -> None:
    mocker.patch.object(strip_workspace_config_values, "strip_values_from_file", return_value=["var1"])
    expected_file_list = ["dummy1.config"]
    mock_argv_filelist(mocker, expected_file_list)
    actual = main()
    assert actual == 1


def test_When_strip_values_identifies_problem__Then_main_logs_the_variable_and_file_name(mocker: MockerFixture) -> None:
    expected_variable_name = "var2"
    mocker.patch.object(strip_workspace_config_values, "strip_values_from_file", return_value=[expected_variable_name])
    mocked_logger = mocker.patch.object(strip_workspace_config_values.logger, "info")
    expected_file_list = ["dummy1.config"]
    mock_argv_filelist(mocker, expected_file_list)
    main()
    assert mocked_logger.call_count == 1
    actual_call_str = str(mocked_logger.call_args_list[0])
    assert expected_file_list[0] in actual_call_str
    assert expected_variable_name in actual_call_str


def test_When_strip_values_identifies_no_problems__Then_main_returns_0(mocker: MockerFixture) -> None:
    mocker.patch.object(strip_workspace_config_values, "strip_values_from_file", return_value=[])
    expected_file_list = ["dummy1.config"]
    mock_argv_filelist(mocker, expected_file_list)
    actual = main()
    assert actual == 0
