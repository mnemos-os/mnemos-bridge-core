from __future__ import annotations

import os

import pytest

from mnemos_bridge_core import McpClient


pytestmark = pytest.mark.skipif(
    not os.environ.get("MNEMOS_TEST_BASE"),
    reason="MNEMOS_TEST_BASE is not set",
)


async def test_mcp_client_lists_production_tools() -> None:
    base_url = os.environ["MNEMOS_TEST_BASE"].rstrip("/")
    token = os.environ.get("MNEMOS_API_KEY")
    if not token:
        pytest.skip("MNEMOS_API_KEY is not set")

    async with McpClient.from_url(f"{base_url}/sse", token=token) as client:
        tools = await client.list_tools()

    assert len(tools) >= 20
