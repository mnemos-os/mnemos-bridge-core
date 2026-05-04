from __future__ import annotations

from typing import Any

from .types import ToolSchema


_GEMINI_UNSUPPORTED_KEYS = {"additionalProperties", "$schema", "$defs", "definitions"}


class SchemaTranslator:
    @staticmethod
    def to_openai(t: ToolSchema) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.input_schema,
            },
        }

    @staticmethod
    def to_gemini(t: ToolSchema) -> dict[str, Any]:
        # Gemini accepts a JSON Schema subset; unsupported keywords are silently ignored by the API
        # but we strip them proactively to avoid schema validation warnings in strict mode.
        return {
            "functionDeclarations": [
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters": _strip_gemini(t.input_schema),
                }
            ]
        }

    @staticmethod
    def to_anthropic(t: ToolSchema) -> dict[str, Any]:
        # Anthropic's tool shape is essentially MCP-passthrough; no stripping needed.
        return {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema,
        }


def _strip_gemini(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_gemini(item) for key, item in value.items() if key not in _GEMINI_UNSUPPORTED_KEYS}
    if isinstance(value, list):
        return [_strip_gemini(item) for item in value]
    return value
