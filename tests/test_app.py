"""Smoke test for the Streamlit demo: every tab renders without exceptions."""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = Path(__file__).parents[1] / "app.py"


def test_app_renders_all_tabs_without_errors():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert len(app.tabs) == 3
    assert not app.error  # the example data is valid, so no error boxes
    assert any("Pass" in str(metric.value) for metric in app.metric)
