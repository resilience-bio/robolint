import sys
from typing import Optional
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from .utils import mock_run_and_call_main


@pytest.mark.parametrize(
    ",".join(
        ("test_description", "test_sync_type", "test_stdout", "expected_return_code", "expected_minimum_print_count")
    ),
    [
        (
            "Given pip-sync call is mocked to return no changes, When pip-sync on checkout is called, Then no messages are printed",
            "sync-on-checkout",
            "Everything fine",
            0,
            None,
        ),
        (
            "Given pip-sync call is mocked to return changes, When pip-sync on checkout is called, Then no messages are printed",
            "sync-on-checkout",
            "lots of stuff",
            0,
            None,
        ),
        (
            "Given pip-sync call is mocked to return no changes, When pip-sync on commit is called, Then no messages are printed",
            "sync-on-commit",
            "Everything fine",
            0,
            None,
        ),
        (
            "Given pip-sync call is mocked to return changes, When pip-sync on commit is called, Then messages are printed",
            "sync-on-commit",
            "lots of stuff",
            1,
            2,
        ),
    ],
)
def test_sync(
    test_description: str,
    test_sync_type: str,
    test_stdout: bytes,
    expected_return_code: int,
    expected_minimum_print_count: Optional[int],
    mocker: MockerFixture,
    mock_print: MagicMock,
) -> None:
    argv = ["dummy.py", test_sync_type]
    mocker.patch.object(sys, "argv", argv)
    actual = mock_run_and_call_main(mocker, test_stdout)
    assert actual == expected_return_code
    if expected_minimum_print_count is None:
        mock_print.assert_not_called()
    else:
        assert mock_print.call_count >= expected_minimum_print_count
