"""Tests for structured stderr logging and --verbose serve wiring.

Verifies:
- Log records are single-line JSON.
- Logging never touches stdout (would corrupt the stdio MCP protocol).
- The log_tool_call decorator records tool name / duration / errors.
- `run_stdio` wires verbosity into the logger level without starting a
  real MCP session (mcp.run is monkeypatched).
"""

from __future__ import annotations

import io
import json
import logging
import sys

import pytest

from ros2_mcp.logging_config import (
    LOGGER_NAME,
    configure_logging,
    log_tool_call,
)


@pytest.fixture(autouse=True)
def _reset_logger():
    logger = logging.getLogger(LOGGER_NAME)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    yield
    for h in list(logger.handlers):
        logger.removeHandler(h)


def test_configure_logging_targets_stderr_only(monkeypatch):
    stdout_writes: list[str] = []
    monkeypatch.setattr("sys.stdout.write", lambda s: stdout_writes.append(s))
    buf = io.StringIO()
    logger = configure_logging(verbose=True, stream=buf)
    logger.debug("hello")
    assert buf.getvalue().strip()
    assert stdout_writes == []


def test_configure_logging_defaults_to_stderr():
    # No explicit stream → handler must target sys.stderr, never sys.stdout.
    logger = configure_logging(verbose=True)
    handler = next(h for h in logger.handlers if getattr(h, "_ros2_mcp", False))
    assert handler.stream is sys.stderr


def test_log_record_is_json_with_expected_fields():
    buf = io.StringIO()
    logger = configure_logging(verbose=True, stream=buf)
    logger.info("something_happened", extra={"extra_fields": {"foo": "bar"}})
    line = buf.getvalue().strip()
    record = json.loads(line)
    assert record["msg"] == "something_happened"
    assert record["level"] == "INFO"
    assert record["logger"] == LOGGER_NAME
    assert record["foo"] == "bar"
    assert "ts" in record


def test_verbose_false_sets_info_level():
    logger = configure_logging(verbose=False)
    assert logger.level == logging.INFO
    assert not logger.isEnabledFor(logging.DEBUG)


def test_verbose_true_sets_debug_level():
    logger = configure_logging(verbose=True)
    assert logger.level == logging.DEBUG
    assert logger.isEnabledFor(logging.DEBUG)


def test_log_tool_call_emits_debug_record_on_success():
    buf = io.StringIO()
    configure_logging(verbose=True, stream=buf)

    @log_tool_call
    def add(a: int, b: int) -> int:
        return a + b

    result = add(1, 2)
    assert result == 3
    lines = [json.loads(x) for x in buf.getvalue().strip().splitlines()]
    tool_calls = [r for r in lines if r["msg"] == "tool_call"]
    assert len(tool_calls) == 1
    assert tool_calls[0]["tool"] == "add"
    assert tool_calls[0]["status"] == "ok"
    assert "duration_ms" in tool_calls[0]


def test_log_tool_call_quiet_when_not_verbose():
    buf = io.StringIO()
    configure_logging(verbose=False, stream=buf)

    @log_tool_call
    def add(a: int, b: int) -> int:
        return a + b

    add(1, 2)
    assert buf.getvalue() == ""  # DEBUG-level tool_call not emitted at INFO


def test_log_tool_call_logs_error_and_reraises():
    buf = io.StringIO()
    configure_logging(verbose=True, stream=buf)

    @log_tool_call
    def boom() -> None:
        raise ValueError("kaboom")

    with pytest.raises(ValueError):
        boom()
    lines = [json.loads(x) for x in buf.getvalue().strip().splitlines()]
    errors = [r for r in lines if r["msg"] == "tool_call_error"]
    assert len(errors) == 1
    assert errors[0]["tool"] == "boom"
    assert errors[0]["level"] == "ERROR"
    assert "exc" in errors[0]


def test_run_stdio_configures_logging_and_instruments_tools(monkeypatch):
    from ros2_mcp import server

    calls: dict[str, object] = {}
    monkeypatch.setattr(server.mcp, "run", lambda transport="stdio": calls.setdefault("ran", transport))

    server.run_stdio(verbose=True)

    assert calls["ran"] == "stdio"
    logger = logging.getLogger(LOGGER_NAME)
    assert logger.level == logging.DEBUG

    # Every registered tool's fn should now be wrapped exactly once.
    manager = server.mcp._tool_manager
    tools = getattr(manager, "_tools", {})
    assert tools, "expected registered tools"
    for tool in tools.values():
        assert getattr(tool.fn, "_ros2_mcp_logged", False) is True

    # Re-running should not double-wrap (idempotent instrumentation).
    fns_before = {name: t.fn for name, t in tools.items()}
    server.run_stdio(verbose=False)
    fns_after = {name: t.fn for name, t in tools.items()}
    assert fns_before == fns_after
