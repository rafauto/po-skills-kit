# ADR 0002: One package, three thin interfaces

- Status: Accepted
- Date: 2026-11-04

## Context

The same logic has to reach three audiences: Claude (MCP server), people who prefer the
terminal or CI (CLI) and recruiters or teammates who just want to try it (web demo).

## Decision

Keep a modular monolith: one installable package, `po_skills_kit`, with three business
modules (`rice`, `story_lint`, `release_notes`) and three thin adapters (`cli`, `mcp_server`,
`app.py`). Adapters only parse input and format output. The core has no runtime dependencies;
`mcp`, `streamlit` and `pandas` are optional extras.

Rejected alternatives:

- **Separate services (an API plus clients):** needless hosting and latency for a local tool.
- **MCP server only:** nobody could try the kit without installing Claude Desktop.

## Consequences

- A bug fixed in the core is fixed everywhere, and one test suite covers all interfaces.
- `pip install po-skills-kit` stays light for CLI users.
- The Streamlit app is a demo of the tools, not of the skills: the skills need Claude.
