"""Streamlit playground for the PO Skills Kit tools. Runs offline: no API key, no storage."""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from po_skills_kit import __version__, release_notes, rice, story_lint

EXAMPLES = Path(__file__).parent / "examples"
MAX_UPLOAD_BYTES = 200_000
REPO_URL = "https://github.com/rafauto/po-skills-kit"


@st.cache_data
def load_example(name: str) -> str:
    return (EXAMPLES / name).read_text(encoding="utf-8")


def example_stories() -> dict[str, str]:
    return {
        path.stem: load_example(f"stories/{path.name}")
        for path in sorted((EXAMPLES / "stories").glob("*.md"))
    }


def render_rice_tab() -> None:
    st.markdown(
        "Score = **Reach × Impact × Confidence ÷ Effort**. Edit the table or upload a CSV with the "
        "columns `item, reach, impact, confidence, effort`."
    )
    uploaded = st.file_uploader("Upload a CSV (optional)", type="csv")
    if uploaded is not None and uploaded.size > MAX_UPLOAD_BYTES:
        st.error(f"The file is larger than {MAX_UPLOAD_BYTES // 1000} KB.")
        uploaded = None
    source = uploaded if uploaded is not None else EXAMPLES / "backlog.csv"
    try:
        backlog = pd.read_csv(source, dtype=str)
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError):
        st.error("Could not read this CSV. Check that it is comma-separated UTF-8 text.")
        return

    edited = st.data_editor(
        backlog,
        num_rows="dynamic",
        hide_index=True,
        key=f"backlog-{uploaded.name if uploaded is not None else 'example'}",
    )
    try:
        ranked = rice.rank(rice.parse_items(edited.to_dict("records"), first_row_number=1))
    except rice.RiceInputError as error:
        st.error(
            "Fix these values to see the ranking:\n\n" + "\n".join(f"- {p}" for p in error.problems)
        )
        return

    ranking = pd.DataFrame([row.to_dict() for row in ranked])
    chart = (
        alt.Chart(ranking)
        .mark_bar()
        .encode(
            x=alt.X("score:Q", title="RICE score"),
            y=alt.Y("item:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
            tooltip=["rank", "item", "score"],
        )
    )
    table = ranking.assign(confidence=ranking["confidence"].map("{:.0%}".format))
    left, right = st.columns([3, 2])
    left.dataframe(table, hide_index=True)
    right.altair_chart(chart)
    st.download_button(
        "Download ranking (Markdown)", rice.to_markdown_table(ranked), file_name="rice-ranking.md"
    )


def render_story_tab() -> None:
    stories = example_stories()
    choice = st.selectbox(
        "Start from an example",
        list(stories),
        format_func=lambda s: s[3:].replace("-", " ").capitalize(),
    )
    text = st.text_area("User story (Markdown)", stories[choice], height=320, key=f"story-{choice}")
    result = story_lint.lint_story(text)

    status, score, scenarios = st.columns(3)
    status.metric("Status", "✅ Pass" if result.passed else "❌ Fail")
    score.metric("Quality score", f"{result.score}/100")
    scenarios.metric("Scenarios", result.scenario_count)
    if result.findings:
        st.dataframe(pd.DataFrame([vars(finding) for finding in result.findings]), hide_index=True)
    else:
        st.success("No findings: this story is ready for refinement.")


def render_notes_tab() -> None:
    commits = st.text_area(
        "Commit lines (e.g. `git log --oneline`)", load_example("commits.txt"), height=240
    )
    version_col, toggle_col = st.columns(2)
    version = version_col.text_input("Version", "v1.4.0")
    include_internal = toggle_col.toggle("Include internal changes (chore, ci, test...)")
    try:
        notes = release_notes.build_release_notes(
            commits, version=version, include_internal=include_internal
        )
    except ValueError as error:
        st.error(str(error))
        return

    markdown = notes.to_markdown()
    st.markdown(markdown)
    st.caption(
        f"{notes.change_count} change(s) listed · {notes.hidden_internal} internal hidden · "
        f"{len(notes.unparsed)} line(s) not in Conventional Commits format"
    )
    if notes.unparsed:
        with st.expander("Lines that were not parsed"):
            st.code("\n".join(notes.unparsed), language="text")
    st.download_button("Download release notes (Markdown)", markdown, file_name="release-notes.md")


def main() -> None:
    st.set_page_config(page_title="PO Skills Kit", page_icon="🧭", layout="wide")
    st.title("🧭 PO Skills Kit")
    st.caption(
        "The deterministic tools behind the Claude skills: RICE scoring, user story checks and "
        "release notes. All sample data is fictional."
    )
    with st.sidebar:
        st.header("About")
        st.markdown(
            f"Version {__version__}. In Claude these tools run through an MCP server: "
            f"the skills write, the code checks and calculates.\n\n[Source code]({REPO_URL})"
        )
        st.info("Runs without an API key. Nothing you type is stored or sent to third parties.")

    rice_tab, story_tab, notes_tab = st.tabs(
        ["📊 Prioritize (RICE)", "📝 Check a user story", "🚀 Release notes"]
    )
    with rice_tab:
        render_rice_tab()
    with story_tab:
        render_story_tab()
    with notes_tab:
        render_notes_tab()


main()
