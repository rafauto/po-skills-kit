# Contributing

Thanks for your interest in improving the PO Skills Kit! Issues and pull requests are welcome.

## Opening an issue

- **Bug:** use the bug report template and include the command you ran, what you expected and
  what happened.
- **Idea or new skill:** use the feature request template and write it as a user story with
  Given/When/Then criteria. You can check it with `po-kit lint your-story.md`.

> **Privacy:** never paste real backlog items, customer data, personal data, company names or
> API keys into issues or pull requests. Use fictional examples like the ones in `examples/`.

## Setup

```bash
git clone https://github.com/rafauto/po-skills-kit.git
cd po-skills-kit
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,mcp,app]"
```

You can also open the repository in the Dev Container (`.devcontainer/`).

## Pull request flow

1. Create a branch from `main` (`feat/waitlist-skill`, `fix/rice-rounding`).
2. Make small commits with [Conventional Commits](https://www.conventionalcommits.org/):
   `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:`, `style:`, `refactor:`.
3. Run the same checks as the CI before opening the pull request:

   ```bash
   ruff check .
   ruff format --check .
   pytest
   po-kit demo
   ```

4. Open the pull request with the template, link the issue and explain what changed and why.
   Pull requests are merged only with a green CI.

## Guiding principles

- **The LLM writes, the code checks.** Anything that must be reproducible (scores, rules,
  grouping) lives in Python, not in a prompt.
- **Offline first.** Tests and the demo run without network access or API keys.
- **Keep it simple.** One package, three thin interfaces (CLI, MCP server, Streamlit app).
- **Skills never invent facts.** Missing information becomes a question or an assumption.
- **Every bug gets a regression test.**
