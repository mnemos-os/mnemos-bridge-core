from __future__ import annotations

import base64
import binascii
from contextlib import AsyncExitStack
from datetime import timedelta
from types import TracebackType
from typing import Any, Self

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from .types import ContentBlock, ToolResult, ToolSchema


class McpClient:
    def __init__(self, url: str, *, token: str, timeout: float = 30) -> None:
        self.url = url
        self.token = token
        self.timeout = timeout
        self._exit_stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None

    @classmethod
    def from_url(cls, url: str, *, token: str, timeout: float = 30) -> Self:
        return cls(url, token=token, timeout=timeout)

    async def __aenter__(self) -> Self:
        self._exit_stack = AsyncExitStack()
        headers = {"Authorization": f"Bearer {self.token}"}
        read_stream, write_stream = await self._exit_stack.enter_async_context(
            sse_client(self.url, headers=headers, timeout=self.timeout)
        )
        session = ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=timedelta(seconds=self.timeout),
        )
        self._session = await self._exit_stack.enter_async_context(session)
        await self._session.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._exit_stack is not None:
            await self._exit_stack.aclose()
        self._session = None
        self._exit_stack = None

    async def list_tools(self) -> list[ToolSchema]:
        session = self._require_session()
        result = await session.list_tools()
        return [
            ToolSchema(
                name=tool.name,
                description=tool.description or "",
                input_schema=getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None) or {},
            )
            for tool in result.tools
        ]

    async def call_tool(self, name: str, args: dict) -> ToolResult:
        session = self._require_session()
        result = await session.call_tool(name, arguments=args)
        return ToolResult(
            content=[block for item in result.content if (block := self._map_content(item)) is not None],
            is_error=bool(getattr(result, "isError", False)),
        )

    def _require_session(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError("McpClient session is not open; use 'async with McpClient.from_url(...) as c'.")
        return self._session

    @staticmethod
    def _map_content(item: Any) -> ContentBlock | None:
        item_type = getattr(item, "type", None)
        if item_type == "text":
            return ContentBlock(type="text", text=getattr(item, "text", ""))
        if item_type == "image":
            return ContentBlock(
                type="image",
                data=_decode_image_data(getattr(item, "data", b"")),
                mime_type=getattr(item, "mimeType", None) or getattr(item, "mime_type", None),
            )
        if item_type == "resource_link":
            uri = getattr(item, "uri", None)
            return ContentBlock(type="resource_link", uri=str(uri) if uri is not None else None)
        return None


def _decode_image_data(data: Any) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        try:
            return base64.b64decode(data, validate=True)
        except (binascii.Error, ValueError):
            return data.encode("utf-8")
    return bytes(data)
