from hooks import pip_tools_hook
from hooks.pip_tools_hook import main
from pytest_mock import MockerFixture


def mock_run_and_call_main(mocker: MockerFixture, stdout: bytes) -> int:
    mocker.patch.object(pip_tools_hook, "execute_command", autospec=True, return_value=(stdout, "", 0))
    return main()
