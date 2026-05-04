from __future__ import annotations

from typing import Any

from .types import ToolResult


class ResultRenderer:
    @staticmethod
    def to_openai_message(r: ToolResult, tool_call_id: str) -> dict[str, Any]:
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": " ".join(block.text for block in r.content if block.text),
        }

    @staticmethod
    def to_gemini_part(r: ToolResult) -> dict[str, Any]:
        return {
            "functionResponse": {
                "response": {
                    "content": [block.text for block in r.content if block.text],
                }
            }
        }

    @staticmethod
    def to_anthropic_message(r: ToolResult, tool_use_id: str) -> dict[str, Any]:
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": [block.model_dump(exclude_none=True) for block in r.content],
                    "is_error": r.is_error,
                }
            ],
        }
