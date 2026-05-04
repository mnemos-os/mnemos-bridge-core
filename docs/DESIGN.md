# Design

## Abstraction Rationale

`mnemos-bridge-core` contains the shared mechanics for MNEMOS-to-LLM-consumer bridges: canonical wire types,
MCP client access, tool schema translation, result rendering, auth resolution, and dispatch retries. Per-surface
adapter packages should depend on this core library and only own target-specific packaging, naming, and runtime
integration.

This split keeps MCP behavior and schema policy consistent across OpenAI, Gemini, Anthropic, VS Code extensions,
and future clients without forcing every adapter to duplicate MNEMOS-specific knowledge.

## Wire-Shape Decisions

- `ToolSchema` is MCP-canonical: `name`, `description`, and `input_schema` as JSON Schema.
- `ToolResult` normalizes content into text, image, and resource-link blocks with an `is_error` flag.
- OpenAI tool definitions use the function-tool envelope expected by chat and responses APIs.
- Gemini tool definitions use `functionDeclarations` and proactively strip unsupported JSON Schema keywords.
- Anthropic tool definitions are treated as MCP-passthrough because the shape aligns with `input_schema`.
- Result renderers preserve text for providers that expect string or string-list function responses and keep richer
  content blocks for Anthropic tool-result messages.

## JSON Schema Dialect Mapping

| keyword | OpenAI support | Gemini support | Anthropic support |
| --- | --- | --- | --- |
| `type` | Supported | Supported | Supported |
| `properties` | Supported | Supported | Supported |
| `required` | Supported | Supported | Supported |
| `additionalProperties` | Supported in strict schemas | Stripped by core | Supported |
| `$schema` | Usually ignored | Stripped by core | Usually ignored |
| `$defs` | Limited support | Stripped by core | Limited support |
| `enum` | Supported | Supported | Supported |
| `description` | Supported | Supported | Supported |
| `default` | Accepted as metadata | Accepted as metadata | Accepted as metadata |
| `items` | Supported | Supported | Supported |
| `anyOf`/`oneOf` | Limited support, avoid when possible | Limited support, avoid when possible | Supported with model-dependent behavior |

## Future Work

- Add stdio transport support for local MCP servers.
- Add a JavaScript/TypeScript port for the VS Code extension bridge.
