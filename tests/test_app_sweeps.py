"""Die drei Messreihen-Knöpfe (▶️) lässt der allgemeine Rauchtest aus (er überspringt Auto-Play-Marken): hier wird jeder Knopf einzeln gedrückt und die Seite ohne Ausnahme gerendert."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "600"))


@pytest.mark.parametrize("label, new_charts", [("Messreihe Pivotregeln", 1), ("Messreihe gemeine Familie", 1), ("Messreihe Qualität", 0)])
def test_each_sweep_button_renders(label, new_charts):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception
    before = len(at.get("plotly_chart"))
    next(b for b in at.button if label in b.label).click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("plotly_chart")) == before + new_charts
    assert not at.error, [e.value for e in at.error]                                                                  # kein Verdikt der Art „error“


def test_all_sweeps_together_and_a_preset_afterwards():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    for label in ("Messreihe Pivotregeln", "Messreihe gemeine Familie", "Messreihe Qualität"):
        next(b for b in at.button if label in b.label).click().run(timeout=TIMEOUT)
    assert len(at.get("plotly_chart")) == 1 + 2                                                                      # Verlauf (n = 20 hat keinen Graphen) + zwei Messreihen-Diagramme
    next(b for b in at.button if "Lehrbeispiel" in b.label).click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["n_slider"] == 3 and at.session_state["family_select"] == "ones"
    assert len(at.get("plotly_chart")) == 2 + 2                                                                      # n = 3: der Graph kommt dazu
