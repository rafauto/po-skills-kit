"""Command line interface: ``po-kit rice | lint | notes | demo``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from po_skills_kit import __version__, release_notes, rice, story_lint

EXIT_OK = 0
EXIT_CHECK_FAILED = 1
EXIT_INPUT_ERROR = 2


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_rice(args: argparse.Namespace) -> int:
    ranked = rice.rank(rice.read_csv(_read(args.file)))
    if args.json:
        print(json.dumps([row.to_dict() for row in ranked], indent=2))
    else:
        print(rice.to_markdown_table(ranked))
    return EXIT_OK


def _run_lint(args: argparse.Namespace) -> int:
    results = [(path, story_lint.lint_story(_read(path))) for path in args.files]
    if args.json:
        payload = [{"file": str(path), **result.to_dict()} for path, result in results]
        print(json.dumps(payload, indent=2))
    else:
        for path, result in results:
            print(story_lint.format_report(result, source=str(path)))
        passed = sum(result.passed for _, result in results)
        print(f"\n{passed}/{len(results)} stories passed.")
    return EXIT_OK if all(result.passed for _, result in results) else EXIT_CHECK_FAILED


def _run_notes(args: argparse.Namespace) -> int:
    notes = release_notes.build_release_notes(
        _read(args.file), version=args.version, include_internal=args.include_internal
    )
    markdown = notes.to_markdown()
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Release notes written to {args.output}")
    else:
        print(markdown, end="")
    return EXIT_OK


def _run_demo(args: argparse.Namespace) -> int:
    """Run every tool on the bundled examples. Used as the end-to-end smoke test in CI."""
    examples: Path = args.examples
    print("# PO Skills Kit demo\n\n## RICE prioritization\n")
    print(rice.to_markdown_table(rice.rank(rice.read_csv(_read(examples / "backlog.csv")))))

    print("\n## User story checks\n")
    for path in sorted((examples / "stories").glob("*.md")):
        print(story_lint.format_report(story_lint.lint_story(_read(path)), source=path.name))

    print("\n## Release notes\n")
    notes = release_notes.build_release_notes(_read(examples / "commits.txt"), version="v1.4.0")
    print(notes.to_markdown(), end="")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="po-kit", description="Deterministic helpers for Product Owners."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    rice_cmd = commands.add_parser("rice", help="Rank a CSV backlog with RICE.")
    rice_cmd.add_argument(
        "file", type=Path, help="CSV with item, reach, impact, confidence, effort"
    )
    rice_cmd.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    rice_cmd.set_defaults(handler=_run_rice)

    lint_cmd = commands.add_parser("lint", help="Check user stories against quality rules.")
    lint_cmd.add_argument("files", type=Path, nargs="+", help="One or more Markdown stories")
    lint_cmd.add_argument("--json", action="store_true", help="Print JSON instead of text")
    lint_cmd.set_defaults(handler=_run_lint)

    notes_cmd = commands.add_parser("notes", help="Build release notes from commit lines.")
    notes_cmd.add_argument("file", type=Path, help="Text file, e.g. `git log --oneline` output")
    notes_cmd.add_argument("--version", default="Unreleased", help="Release name, e.g. v1.2.0")
    notes_cmd.add_argument("--include-internal", action="store_true", help="Keep chore/ci/test")
    notes_cmd.add_argument("--output", type=Path, help="Write to a file instead of stdout")
    notes_cmd.set_defaults(handler=_run_notes)

    demo_cmd = commands.add_parser("demo", help="Run every tool on the example data.")
    demo_cmd.add_argument("--examples", type=Path, default=Path("examples"), help="Examples folder")
    demo_cmd.set_defaults(handler=_run_demo)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except FileNotFoundError as error:
        print(f"Error: file not found: {error.filename}", file=sys.stderr)
    except rice.RiceInputError as error:
        print("Error: invalid RICE input:", file=sys.stderr)
        for problem in error.problems:
            print(f"  - {problem}", file=sys.stderr)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
    return EXIT_INPUT_ERROR


if __name__ == "__main__":
    sys.exit(main())
