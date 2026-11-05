"""Integration tests: an in-process MCP client talks to the server over the real protocol."""

import asyncio
import shutil
import sys

import pytest

pytest.importorskip("mcp")

from mcp import Client, StdioServerParameters  # noqa: E402

from po_skills_kit.mcp_server import server  # noqa: E402

EXPECTED_TOOLS = {"score_rice", "lint_story", "build_release_notes"}


def call(name, arguments):
    async def run():
        async with Client(server) as client:
            return await client.call_tool(name, arguments)

    return asyncio.run(run())


def structured(result):
    assert not result.is_error, result
    return result.structured_content


def test_server_exposes_the_three_tools():
    async def run():
        async with Client(server) as client:
            return await client.list_tools()

    tools = asyncio.run(run()).tools
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
    assert all(tool.description for tool in tools)


def test_score_rice_tool_returns_a_ranking():
    items = [
        {"item": "A", "reach": 100, "impact": 1, "confidence": "50%", "effort": 1},
        {"item": "B", "reach": 100, "impact": "massive", "confidence": 1, "effort": 1},
    ]
    data = structured(call("score_rice", {"items": items}))
    assert [row["item"] for row in data["ranked"]] == ["B", "A"]
    assert data["table"].startswith("| Rank |")


def test_score_rice_tool_reports_invalid_input_to_the_model():
    items = [{"item": "A", "reach": 1, "impact": 7, "confidence": 1, "effort": 1}]
    result = call("score_rice", {"items": items})
    assert result.is_error
    assert "'impact' must be one of" in result.content[0].text


def test_lint_story_tool():
    data = structured(call("lint_story", {"story": "As a user, I want X, so that Y."}))
    assert data["passed"] is False
    assert {f["rule"] for f in data["findings"]} >= {"acceptance-criteria", "specific-role"}


def test_build_release_notes_tool():
    data = structured(
        call("build_release_notes", {"commits": "feat: add waitlist\nci: cache", "version": "v1"})
    )
    assert data["markdown"].startswith("## v1 — ")
    assert (data["change_count"], data["hidden_internal"]) == (1, 1)


def test_console_script_serves_over_stdio():
    """Same launch path as Claude Desktop: a subprocess speaking MCP over stdin/stdout."""
    command = shutil.which("po-kit-mcp")
    params = (
        StdioServerParameters(command=command)
        if command
        else StdioServerParameters(command=sys.executable, args=["-m", "po_skills_kit.mcp_server"])
    )

    async def run():
        async with Client(params) as client:
            return await client.call_tool(
                "lint_story", {"story": "As a user, I want X, so that Y."}
            )

    assert asyncio.run(run()).structured_content["passed"] is False
