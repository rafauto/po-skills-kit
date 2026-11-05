# ADR 0003: Official MCP Python SDK v2 over stdio

- Status: Accepted
- Date: 2026-11-04

## Context

The server needs to work with Claude Desktop and Claude Code with minimal setup. The official
Python SDK reached version 2, where `FastMCP` became `MCPServer`.

## Decision

Use `mcp>=2.3,<3` with `MCPServer` and the **stdio** transport. Claude starts `po-kit-mcp` as
a local subprocess, so there is no port, no authentication and no hosting. Invalid input is
raised as `ToolError`, whose message reaches the model so Claude can ask the user to fix it.

## Consequences

- Setup is one entry in the Claude Desktop config (`examples/claude_desktop_config.json`).
- Tests use the SDK's in-process `Client` and a real stdio subprocess, so the protocol path
  is covered offline.
- Remote use (Streamable HTTP) is possible later but out of scope for the MVP.
- Projects pinned to `mcp<2` cannot install this package in the same environment.
