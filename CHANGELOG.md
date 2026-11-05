# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-04

### Added

- Four Claude skills: `write-user-story`, `refine-backlog`, `prioritize-rice`, `release-notes`.
- Core library: RICE scoring, user story linter and release notes from Conventional Commits.
- `po-kit` CLI with `rice`, `lint`, `notes` and `demo` commands.
- `po-kit-mcp` MCP server (stdio) exposing `score_rice`, `lint_story`, `build_release_notes`.
- Streamlit demo app with fictional example data.
- Offline eval: 10 recorded skill drafts and 10 labeled linter cases.
