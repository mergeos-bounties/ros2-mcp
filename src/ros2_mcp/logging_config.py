"""Structured logging for ros2-mcp.

Logs go to **stderr only**. This is critical: the MCP stdio transport uses
**stdout** for the JSON-RPC protocol stream, so writing logs to stdout would
corrupt the protocol and break the connection. All handlers here target
``sys.stderr``.

Records are emitted as single-line JSON so hosts / log collectors can parse
tool-call telemetry without scraping free text.
"""

from __future__ import annotations

import functools
import json
import logging
import sys
import time
from typing import Any, Callable, TypeVar

LOGGER_NAME = "ros2_mcp"

F = TypeVar("F", bound=Callable[..., Any])


class JsonStderrFormatter(logging.Formatter):
    """Format log records as compact single-line JSON on stderr."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": round(record.created, 3),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Attach any structured extras stashed on the record.
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(verbose: bool = False, stream: Any = None) -> logging.Logger:
    """Configure the ros2_mcp logger to emit JSON to stderr.

    Args:
        verbose: When True, level is DEBUG (every tool call logged with args
            and durations). When False, level is INFO (only lifecycle events
            like server start, not per-call detail).
        stream: Optional target stream (defaults to ``sys.stderr``). Never
            pass ``sys.stdout`` — stdout is reserved for the MCP JSON-RPC
            protocol. Exposed mainly for testing.

    Returns:
        The configured ``ros2_mcp`` logger.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Replace any handlers we previously attached so repeat calls are idempotent.
    for handler in list(logger.handlers):
        if getattr(handler, "_ros2_mcp", False):
            logger.removeHandler(handler)

    handler = logging.StreamHandler(stream=stream if stream is not None else sys.stderr)
    handler.setFormatter(JsonStderrFormatter())
    handler._ros2_mcp = True  # type: ignore[attr-defined]
    logger.addHandler(handler)

    # Never propagate to the root logger (which may target stdout).
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def _preview(value: Any, limit: int = 300) -> str:
    text = repr(value)
    return text if len(text) <= limit else text[:limit] + "…"


def log_tool_call(func: F) -> F:
    """Decorator that logs an MCP tool call (name, args, duration, status).

    Emits a DEBUG ``tool_call`` record on success and an ERROR record if the
    wrapped tool raises. Logging failures never mask the tool result. All
    output is on stderr via the ros2_mcp logger.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger()
        start = time.perf_counter()
        # Only build arg previews when the log level would emit them.
        if logger.isEnabledFor(logging.DEBUG):
            arg_fields = {
                "tool": func.__name__,
                "args": [_preview(a) for a in args],
                "kwargs": {k: _preview(v) for k, v in kwargs.items()},
            }
            logger.debug("tool_call_start", extra={"extra_fields": arg_fields})
        try:
            result = func(*args, **kwargs)
        except Exception:
            dur_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                "tool_call_error",
                extra={"extra_fields": {"tool": func.__name__, "duration_ms": dur_ms}},
                exc_info=True,
            )
            raise
        dur_ms = round((time.perf_counter() - start) * 1000, 2)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "tool_call",
                extra={
                    "extra_fields": {
                        "tool": func.__name__,
                        "duration_ms": dur_ms,
                        "status": "ok",
                    }
                },
            )
        return result

    return wrapper  # type: ignore[return-value]
