from __future__ import annotations

import anyio
import httpx

from .client import McpClient
from .types import ToolResult


_TIMEOUT_ERRORS = tuple(error for error in (TimeoutError, getattr(anyio, "TimeoutError", None)) if error is not None)
_TRANSIENT_ERRORS = (httpx.ConnectError, httpx.ReadError)
_RETRYABLE_ERRORS = _TIMEOUT_ERRORS + _TRANSIENT_ERRORS


async def dispatch(client: McpClient, name: str, args: dict, *, retries: int = 2, timeout: float = 30) -> ToolResult:
    max_retries = max(0, retries)
    for attempt in range(max_retries + 1):
        try:
            with anyio.fail_after(timeout):
                return await client.call_tool(name, args)
        except _RETRYABLE_ERRORS:
            if attempt >= max_retries:
                raise
            await anyio.sleep(1)

    raise RuntimeError("dispatch exhausted retry loop unexpectedly")
