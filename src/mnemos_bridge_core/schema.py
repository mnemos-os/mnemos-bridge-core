from __future__ import annotations

from typing import Any

from .types import ToolSchema


# Gemini's Schema proto only accepts a strict subset of JSON Schema keywords.
# Whitelist approach (instead of the original denylist) — anything outside this
# set is silently dropped before the schema reaches the SDK. Source: Gemini
# v1beta API Schema proto.
_GEMINI_SUPPORTED_KEYS = {
    "type",
    "format",
    "description",
    "nullable",
    "enum",
    "properties",
    "required",
    "items",
    # Notes on excluded keys (verified empirically against
    # google-generativeai 0.8.x's protos.Schema 2026-05-04):
    #   "maxItems", "minItems": rejected as 'Unknown field' even though
    #     they're documented in Gemini v1beta. The SDK lags the API.
    #   "title", "default", "minimum", "maximum", "multipleOf",
    #   "exclusiveMinimum", "pattern", "$schema", "$defs",
    #   "additionalProperties": all rejected by the proto validator.
}


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
    """Strip JSON Schema keywords Gemini doesn't support, recursively.

    The whitelist applies at *schema-level* dict positions (where keys are
    keywords like ``type``, ``properties``, ``required``). It does NOT
    apply inside the VALUES of ``properties`` — those keys are user-
    defined property names and must pass through verbatim. The recursion
    into ``properties`` strips per-property schemas individually.
    """
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if key not in _GEMINI_SUPPORTED_KEYS:
                continue
            if key == "properties" and isinstance(item, dict):
                # Property NAMES (the keys here) are user-defined, not JSON
                # Schema keywords. Pass them through; strip each property's
                # schema individually.
                out[key] = {prop_name: _strip_gemini(prop_schema) for prop_name, prop_schema in item.items()}
            elif key == "required" and isinstance(item, list):
                # required is a list of property-name strings; pass through.
                out[key] = list(item)
            else:
                out[key] = _strip_gemini(item)
        return out
    if isinstance(value, list):
        return [_strip_gemini(item) for item in value]
    return value
