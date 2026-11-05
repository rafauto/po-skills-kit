"""Release notes from Conventional Commits (for example the output of ``git log --oneline``).

User-facing types become sections; internal types (chore, ci, test...) are hidden by default
because release notes are written for the people who use the product.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

MAX_LINES = 2_000

_COMMIT = re.compile(
    r"^(?:(?P<hash>[0-9a-f]{7,40})\s+)?"
    r"(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s+(?P<description>.+)$"
)

USER_FACING_SECTIONS = {
    "feat": "✨ Features",
    "fix": "🐛 Bug fixes",
    "perf": "⚡ Improvements",
}
INTERNAL_TYPES = {"build", "chore", "ci", "docs", "refactor", "revert", "style", "test"}
INTERNAL_SECTION = "🔧 Internal"
BREAKING_SECTION = "⚠️ Breaking changes"


@dataclass(frozen=True)
class Commit:
    type: str
    description: str
    scope: str | None = None
    breaking: bool = False
    hash: str | None = None

    def to_markdown(self) -> str:
        text = self.description[:1].upper() + self.description[1:]
        scope = f"**{self.scope}:** " if self.scope else ""
        suffix = f" ({self.hash[:7]})" if self.hash else ""
        return f"- {scope}{text}{suffix}"


@dataclass
class ReleaseNotes:
    version: str
    release_date: date
    sections: dict[str, list[Commit]] = field(default_factory=dict)
    hidden_internal: int = 0
    unparsed: list[str] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return sum(len(commits) for commits in self.sections.values())

    def to_markdown(self) -> str:
        lines = [f"## {self.version} — {self.release_date.isoformat()}", ""]
        if not self.sections:
            lines += ["_No user-facing changes in this release._", ""]
        for title, commits in self.sections.items():
            lines += [f"### {title}", "", *(commit.to_markdown() for commit in commits), ""]
        return "\n".join(lines).rstrip() + "\n"


def parse_commit(line: str) -> Commit | None:
    """Parse one Conventional Commit subject line; return None when it does not match."""
    match = _COMMIT.match(line.strip())
    if not match:
        return None
    return Commit(
        type=match.group("type"),
        description=match.group("description").strip(),
        scope=match.group("scope"),
        breaking=bool(match.group("breaking")) or "BREAKING CHANGE" in match.group("description"),
        hash=match.group("hash"),
    )


def build_release_notes(
    commits_text: str,
    version: str = "Unreleased",
    release_date: date | None = None,
    include_internal: bool = False,
) -> ReleaseNotes:
    lines = [line for line in commits_text.splitlines() if line.strip()]
    if len(lines) > MAX_LINES:
        raise ValueError(f"Too many commit lines: the limit is {MAX_LINES}")

    ordered_titles = [BREAKING_SECTION, *USER_FACING_SECTIONS.values(), INTERNAL_SECTION]
    grouped: dict[str, list[Commit]] = {title: [] for title in ordered_titles}
    notes = ReleaseNotes(
        version=version.strip() or "Unreleased", release_date=release_date or date.today()
    )

    for line in lines:
        commit = parse_commit(line)
        if commit is None:
            notes.unparsed.append(line.strip())
        elif commit.breaking:
            grouped[BREAKING_SECTION].append(commit)
        elif commit.type in USER_FACING_SECTIONS:
            grouped[USER_FACING_SECTIONS[commit.type]].append(commit)
        elif include_internal:
            grouped[INTERNAL_SECTION].append(commit)
        else:
            notes.hidden_internal += 1

    notes.sections = {title: commits for title, commits in grouped.items() if commits}
    return notes
