# ADR 0001: The LLM writes, deterministic code checks and calculates

- Status: Accepted
- Date: 2026-11-04

## Context

A skill could ask Claude to do everything: write the story, judge its quality, compute RICE
scores and group commits. That is the simplest setup, but the results are not reproducible:
the same backlog can get different scores, and the model can report a quality check it never
ran. Product Owners need to defend a ranking in front of stakeholders, so it must be the same
every time.

## Decision

Split the work:

- **Skills (prompts)** handle language: drafting, rewriting, explaining, asking questions.
- **Python tools** handle anything with a right answer: the RICE formula and its validation,
  the user story rules, and commit grouping. Claude reaches them through the MCP server.

Each skill tells Claude to call the tool when available and to say clearly when it was not.

## Consequences

- Scores and checks are reproducible and covered by unit tests that run offline in seconds.
- The eval showed why this matters: in 2 of the 10 recorded drafts, the skill output claimed
  "100/100" while the linter found a warning.
- The linter only checks what rules can check (format, completeness, size, vague words). It
  does not judge whether a story is valuable; that stays with the Product Owner.
- Users without the MCP server still get the skills, with a weaker manual check.
