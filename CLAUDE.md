# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

Claude skills for Product Owners (`skills/`) backed by a small Python library
(`src/po_skills_kit/`) that is exposed three ways: a CLI (`po-kit`), an MCP server
(`po-kit-mcp`) and a Streamlit demo (`app.py`).

## Commands

```bash
pip install -e ".[dev,mcp,app]"   # install everything
pytest                           # all tests, offline, a few seconds
ruff check . && ruff format .    # lint and format
po-kit demo                      # end-to-end smoke test
streamlit run app.py             # demo app on http://localhost:8501
```

## Rules

- Everything in the repository is in English: code, comments, docs and commit messages.
- Business logic lives in `rice.py`, `story_lint.py` and `release_notes.py`. The CLI, the MCP
  server and the app only parse input and format output; do not duplicate logic there.
- The core library has no runtime dependencies. `mcp`, `streamlit` and `pandas` are extras.
- Tests must run offline without API keys. Add a regression test for every bug fix.
- Use only fictional data. No real company, customer or personal data.
- When a skill changes, update the recorded drafts in `tests/fixtures/eval/` only with new
  output actually produced by the skill, and keep the eval target (>= 8 of 10 pass).
- Keep the architecture diagram in `README.md` in sync with the structure.
