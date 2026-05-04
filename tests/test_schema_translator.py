from __future__ import annotations

import json
from pathlib import Path

import pytest

from mnemos_bridge_core import SchemaTranslator, ToolSchema


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "mnemos_tools.json"


def load_tools() -> list[ToolSchema]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return [ToolSchema.model_validate(item) for item in json.load(handle)]


def assert_key_absent(value: object, key: str) -> None:
    if isinstance(value, dict):
        assert key not in value
        for item in value.values():
            assert_key_absent(item, key)
    elif isinstance(value, list):
        for item in value:
            assert_key_absent(item, key)


@pytest.mark.parametrize("tool", load_tools())
def test_schema_translators_accept_all_mnemos_tools(tool: ToolSchema) -> None:
    openai = SchemaTranslator.to_openai(tool)
    assert set(openai) == {"type", "function"}
    assert openai["type"] == "function"
    assert {"name", "description", "parameters"} <= set(openai["function"])

    gemini = SchemaTranslator.to_gemini(tool)
    assert "functionDeclarations" in gemini
    assert isinstance(gemini["functionDeclarations"], list)
    declaration = gemini["functionDeclarations"][0]
    assert {"name", "description", "parameters"} <= set(declaration)
    assert_key_absent(declaration["parameters"], "additionalProperties")

    anthropic = SchemaTranslator.to_anthropic(tool)
    assert {"name", "description", "input_schema"} <= set(anthropic)
