from __future__ import annotations

from typing import Any, Literal, Optional

import pydantic


class ToolSchema(pydantic.BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]  # MCP-canonical JSON Schema


class ContentBlock(pydantic.BaseModel):
    type: Literal["text", "image", "resource_link"]
    text: Optional[str] = None
    data: Optional[bytes] = None
    mime_type: Optional[str] = None
    uri: Optional[str] = None


class ToolResult(pydantic.BaseModel):
    content: list[ContentBlock]
    is_error: bool = False
