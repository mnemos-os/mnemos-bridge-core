> # 📍 Moved to GitLab
> **The canonical, authoritative home of this project is GitLab — always:**
> ## 👉 https://gitlab.com/ncz-os/mnemos-bridge-core
>
> This GitHub repository is a **frozen, read-only mirror**. All development, issues, and releases happen on GitLab. Please open issues and merge requests there. The full history of this stub is preserved on GitLab.

---

# mnemos-bridge-core

Shared core library for MNEMOS-to-LLM-consumer bridges. It keeps MCP wire types, schema translation, auth lookup,
result rendering, and retry dispatch logic in one package so surface-specific adapters can stay small.

## Install

```bash
pip install mnemos-bridge-core
```

## Schema Translation

The same `ToolSchema` can be adapted to each target consumer:

```python
from mnemos_bridge_core import SchemaTranslator, ToolSchema

tool = ToolSchema(
    name="search_memories",
    description="Full-text search across stored MNEMOS memories.",
    input_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}},
        "required": ["query"],
    },
)

openai_tool = SchemaTranslator.to_openai(tool)
gemini_tool = SchemaTranslator.to_gemini(tool)
anthropic_tool = SchemaTranslator.to_anthropic(tool)
```

## MCP Client

```python
import anyio

from mnemos_bridge_core import AuthResolver, McpClient


async def main() -> None:
    token = AuthResolver.resolve()
    async with McpClient.from_url("https://mnemos.example.com/sse", token=token) as client:
        tools = await client.list_tools()
        result = await client.call_tool("search_memories", {"query": "routing notes", "limit": 5})
        print(len(tools), result.is_error)


anyio.run(main)
```

## AuthResolver

```python
from mnemos_bridge_core import AuthResolver

token = AuthResolver.resolve()
explicit = AuthResolver.resolve(api_key="mnemos_sk_test")
```

Lookup order is explicit argument, `MNEMOS_API_KEY`, `~/.mnemos/config.toml`, then
`~/.api_keys_master.json` at `mnemos.bridge.api_key`.

## Dispatcher

```python
from mnemos_bridge_core import dispatch

result = await dispatch(client, "search_memories", {"query": "forecasting"}, retries=2, timeout=30)
```
