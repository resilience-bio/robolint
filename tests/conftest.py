# -*- coding: utf-8 -*-
"""`Pytest` configuration."""
import os
import sys
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

sys.dont_write_bytecode = True
sys.stdout = (
    sys.stderr
)  # allow printing of `pytest` output when running `pytest-xdist` https://stackoverflow.com/questions/27006884/pytest-xdist-without-capturing-output


@pytest.fixture(scope="function", name="mock_print")
def fixture_mock_print(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("builtins.print", autospec=True)  # don't print all the error messages to console


@pytest.fixture(scope="function", name="aws_credentials", autouse=True)
def fixture_aws_credentials() -> None:
    """Mock AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
