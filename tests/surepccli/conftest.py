"""Conftest for CLI tests."""

import inspect
import re
from pathlib import Path

import nest_asyncio
import pytest
from syrupy.assertion import SnapshotAssertion
from typer.testing import CliRunner

from surepccli import app
from surepccli.const import Envs

# Solves "RuntimeError: This event loop is already running"
nest_asyncio.apply()

runner = CliRunner()

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _normalize_output(text: str) -> str:
    """Normalize CLI output for snapshot testing. Otherwise it differs between devices"""
    text = ANSI_RE.sub("", text)
    return "\n".join(line.rstrip() for line in text.splitlines())


async def run_cli(args: list[str], input_text: str | None = None):
    """
    Invoke Typer CLI. If the callback is async (returns coroutine / Task) await it.
    Returns (result, awaited_return_value)
    """
    result = runner.invoke(app, args, input=input_text)
    rv = result.return_value
    if inspect.isawaitable(rv):
        await rv
    return result, rv


@pytest.fixture
def register_mocks(register_device_api_mocks, mock_devices, device_names):
    """
    Fixture to register device API mocks.
    """
    register_device_api_mocks(mock_devices)


@pytest.fixture
def cli_run():
    """
    Run CLI without snapshot. Automatically registers device API mocks.
    """

    async def _run(args: list[str], input_text: str | None = None):
        result, rv = await run_cli(args, input_text)
        return result

    return _run


@pytest.fixture
def cli_capture(snapshot: SnapshotAssertion):
    """
    Same as cli_run but asserts snapshot.
    """

    async def _run(args: list[str], input_text: str | None = None, name: str | None = None):
        result, _ = await run_cli(args, input_text)
        cap = {
            "exit_code": result.exit_code,
            "output": _normalize_output(result.output),
            "exception": repr(result.exception) if result.exception else None,
        }
        assert snapshot(name=name) == cap
        return cap

    return _run


@pytest.fixture(autouse=True)
def test_configuration(monkeypatch, tmp_path):
    monkeypatch.setenv(Envs.TOKEN, "validToken")
    monkeypatch.setenv(Envs.CLIENT_ID, "validClientId")

    test_env = Path(tmp_path / ".surepccli.test.env")
    monkeypatch.setattr("surepccli.session.getEnvFile", lambda: test_env)
    yield test_env
    if test_env.exists():
        test_env.unlink()


def _cmd_id(cmd: list[str]) -> str:
    """Generate a test ID from a CLI command list."""
    parts = []
    it = iter(cmd)
    for token in it:
        if token.startswith("--"):
            next(it, None)
            continue
        parts.append(token.replace("-", "_"))
    return "_".join(parts)


@pytest.fixture
def device_names(request):
    """Return device names from @pytest.mark.devices for the test."""
    mark = request.node.get_closest_marker("devices")
    if mark:
        return list(mark.args)
    else:
        raise ValueError("Missing 'devices' marker on test")


@pytest.fixture
def cli_commands(request):
    """
    Return raw command lists from @pytest.mark.cli_commands for manual looping.
    Not used when test requests 'cli_command' (then pytest_generate_tests handles parametrization).
    """
    mark = request.node.get_closest_marker("cli_commands")
    if not mark:
        raise ValueError("Missing 'cli_commands' marker on test")
    commands: list[list[str]] = []
    for arg in mark.args:
        if not isinstance(arg, (list, tuple)):
            raise TypeError(f"cli_commands marker argument must be list/tuple, got {type(arg)}")
        commands.append([str(x) for x in arg])
    if not commands:
        raise ValueError("cli_commands marker provided no command lists")
    return commands


@pytest.fixture
def cli_inputs(request, cli_command):
    """
    Returns the input string for the current cli_command, based on the cli_inputs marker.
    """
    mark = request.node.get_closest_marker("cli_inputs")
    if not mark:
        return None
    idx = getattr(request, "param_index", None)
    if idx is None:
        # e.g. test_household_connect[household_list]
        for i, arg in enumerate(request.node.callspec.params.get("cli_command", [])):
            if str(arg) == str(cli_command):
                idx = i
                break
        else:
            idx = 0
    try:
        return mark.args[idx]
    except IndexError:
        return None


def pytest_generate_tests(metafunc):
    """
    Auto-parametrize any test function that:
      - requests a fixture named 'cli_command'
      - has a @pytest.mark.cli_commands([...], [...], ...)
    Each list becomes one test case.
    """
    mark = metafunc.definition.get_closest_marker("cli_commands")
    if "cli_command" in metafunc.fixturenames and mark:
        commands: list[list[str]] = []
        for arg in mark.args:
            if not isinstance(arg, (list, tuple)):
                raise TypeError("cli_commands marker arguments must be lists/tuples")
            commands.append([str(x) for x in arg])
        if not commands:
            raise ValueError("cli_commands marker provided no command lists")
        metafunc.parametrize(
            "cli_command",
            commands,
            ids=[_cmd_id(c) for c in commands],
        )


def list_all_typer_commands(obj, prefix=None, filters=None):
    prefix = prefix or []
    commands = []
    # Add the group itself if it has a name (including first-level groups)
    if hasattr(obj, "info") and hasattr(obj.info, "name") and obj.info.name:
        group_name = obj.info.name.replace("_", "-")
        if not prefix or prefix[-1] != group_name:
            commands.append(prefix + [group_name])
        prefix = prefix + [group_name]
    # Add all commands at this level
    if hasattr(obj, "registered_commands"):
        for cmd in getattr(obj, "registered_commands", []):
            name = getattr(cmd, "name", None)
            callback = getattr(cmd, "callback", None)
            callback_name = getattr(callback, "__name__", str(callback))
            cmd_name = (name if name else callback_name).replace("_", "-")
            cmd_path = prefix + [cmd_name]
            commands.append(cmd_path)
            command_obj = getattr(cmd, "command", None)
            if command_obj and (
                hasattr(command_obj, "registered_commands") or hasattr(command_obj, "registered_groups")
            ):
                commands.extend(list_all_typer_commands(command_obj, cmd_path, filters))
    # Add all subgroups at this level
    if hasattr(obj, "registered_groups"):
        for group in getattr(obj, "registered_groups", []):
            group_app = getattr(group, "typer_instance", None)
            group_name = getattr(group, "name", None)
            if group_app and group_name:
                group_name = group_name.replace("_", "-")
                commands.append(prefix + [group_name])
                commands.extend(list_all_typer_commands(group_app, prefix + [group_name], filters))
            elif group_app:
                commands.extend(list_all_typer_commands(group_app, prefix, filters))
    # Handle wrapped Typer instances
    if hasattr(obj, "typer_instance"):
        commands.extend(list_all_typer_commands(obj.typer_instance, prefix, filters))
    # Apply filters if given
    if filters:

        def matches(cmd):
            idx = 0
            for f in filters:
                try:
                    idx = cmd.index(f, idx) + 1
                except ValueError:
                    return False
            return True

        commands = [cmd for cmd in commands if matches(cmd)]
    return commands
