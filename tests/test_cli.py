import json
from pathlib import Path

from po_skills_kit.cli import EXIT_CHECK_FAILED, EXIT_INPUT_ERROR, EXIT_OK, main

EXAMPLES = Path(__file__).parents[1] / "examples"


def test_rice_prints_a_markdown_ranking(capsys):
    assert main(["rice", str(EXAMPLES / "backlog.csv")]) == EXIT_OK
    output = capsys.readouterr().out
    assert output.splitlines()[2].startswith("| 1 | SMS reminder")


def test_rice_json_output(capsys):
    assert main(["rice", str(EXAMPLES / "backlog.csv"), "--json"]) == EXIT_OK
    ranking = json.loads(capsys.readouterr().out)
    assert ranking[0]["rank"] == 1
    assert len(ranking) == 8


def test_rice_reports_invalid_rows(tmp_path, capsys):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("item,reach,impact,confidence,effort\nA,10,9,50%,1\n", encoding="utf-8")
    assert main(["rice", str(csv_file)]) == EXIT_INPUT_ERROR
    assert "row 2: 'impact'" in capsys.readouterr().err


def test_lint_exit_code_reflects_the_result(capsys):
    stories = EXAMPLES / "stories"
    assert main(["lint", str(stories / "01-ready-story.md")]) == EXIT_OK
    assert main(["lint", *map(str, sorted(stories.glob("*.md")))]) == EXIT_CHECK_FAILED
    assert "1/3 stories passed." in capsys.readouterr().out


def test_notes_can_write_to_a_file(tmp_path):
    output = tmp_path / "notes.md"
    args = ["notes", str(EXAMPLES / "commits.txt"), "--version", "v1.4.0", "--output", str(output)]
    assert main(args) == EXIT_OK
    assert output.read_text(encoding="utf-8").startswith("## v1.4.0")


def test_missing_file_is_a_clear_error(capsys):
    assert main(["rice", "does-not-exist.csv"]) == EXIT_INPUT_ERROR
    assert "file not found" in capsys.readouterr().err


def test_demo_runs_every_tool_end_to_end(capsys):
    assert main(["demo", "--examples", str(EXAMPLES)]) == EXIT_OK
    output = capsys.readouterr().out
    for heading in ("## RICE prioritization", "## User story checks", "## Release notes"):
        assert heading in output
