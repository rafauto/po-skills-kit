from datetime import date

import pytest

from po_skills_kit.release_notes import MAX_LINES, build_release_notes, parse_commit

COMMITS = """a1b2c3d feat(booking): let owners reschedule
fix: correct slot times
perf(search)!: drop the legacy search endpoint
chore: bump dependencies
Merge pull request #42 from feature/reminders
"""


def test_parse_commit_reads_hash_scope_and_breaking_flag():
    commit = parse_commit("abc1234 feat(api)!: remove v1")
    assert commit is not None
    assert (commit.hash, commit.type, commit.scope, commit.breaking) == (
        "abc1234",
        "feat",
        "api",
        True,
    )


def test_non_conventional_lines_return_none():
    assert parse_commit("Merge branch 'main'") is None


def test_commits_are_grouped_and_internal_work_is_hidden():
    notes = build_release_notes(COMMITS, version="v2.0.0", release_date=date(2026, 11, 4))
    assert list(notes.sections) == ["⚠️ Breaking changes", "✨ Features", "🐛 Bug fixes"]
    assert notes.hidden_internal == 1
    assert notes.unparsed == ["Merge pull request #42 from feature/reminders"]
    assert notes.change_count == 3


def test_markdown_output_matches_the_expected_format():
    notes = build_release_notes(COMMITS, version="v2.0.0", release_date=date(2026, 11, 4))
    assert notes.to_markdown() == (
        "## v2.0.0 — 2026-11-04\n\n"
        "### ⚠️ Breaking changes\n\n- **search:** Drop the legacy search endpoint\n\n"
        "### ✨ Features\n\n- **booking:** Let owners reschedule (a1b2c3d)\n\n"
        "### 🐛 Bug fixes\n\n- Correct slot times\n"
    )


def test_internal_changes_can_be_included():
    notes = build_release_notes(COMMITS, include_internal=True)
    assert "🔧 Internal" in notes.sections
    assert notes.hidden_internal == 0


def test_empty_input_says_there_are_no_user_facing_changes():
    markdown = build_release_notes("chore: tidy up", release_date=date(2026, 1, 1)).to_markdown()
    assert "_No user-facing changes in this release._" in markdown
    assert markdown.startswith("## Unreleased — 2026-01-01")


def test_too_many_lines_are_rejected():
    with pytest.raises(ValueError, match="Too many commit lines"):
        build_release_notes("fix: x\n" * (MAX_LINES + 1))
