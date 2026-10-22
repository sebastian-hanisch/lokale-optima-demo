"""Abbildungen: Reihen, Farben, gesperrte Achsen; der PDF-Bau mit Umlauten."""


import pls_algorithm as A
import pls_constants as C
import pls_evaluation as ev
import pls_visualization as V
from pls_pdf_export import build_pdf


def _locked(fig):
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_circle_positions():
    x, y = V.circle_position(0, 4)
    assert (round(x, 9), round(y, 9)) == (0.0, 1.0)
    x, y = V.circle_position(1, 4)
    assert (round(x, 9), round(y, 9)) == (1.0, 0.0)
    x, y = V.circle_position(2, 4)
    assert (round(x, 9), round(y, 9)) == (0.0, -1.0)


def test_graph_chart_splits_edges_and_nodes_by_cut():
    w, side = ((0, 3, 0), (3, 0, 1), (0, 1, 0)), (0, 1, 0)                         # beide Kanten im Schnitt
    fig = V.build_graph(w, side)
    assert [t.name for t in fig.data] == ["Kante im Schnitt", "Kante nicht im Schnitt", "Seite 0", "Seite 1"]
    assert sum(1 for v in fig.data[0].x if v is not None) == 4 and sum(1 for v in fig.data[1].x if v is not None) == 0
    assert list(fig.data[2].text) == ["0", "2"] and list(fig.data[3].text) == ["1"] and fig.data[0].line.color == C.COLOR_BEST
    fig = V.build_graph(w, (0, 0, 0))
    assert sum(1 for v in fig.data[0].x if v is not None) == 0 and sum(1 for v in fig.data[1].x if v is not None) == 4 and len(fig.data[3].x) == 0
    _locked(fig)


def test_progress_chart_shows_the_trace_and_half_of_the_total():
    values = A.cut_trace(((0, 3, 0), (3, 0, 1), (0, 1, 0)), (0, 0, 0), (2, 1, 2))
    assert values == [0, 1, 3, 4]
    fig = V.build_progress(values, 4)
    assert list(fig.data[0].y) == [0, 1, 3, 4] and list(fig.data[0].x) == [0, 1, 2, 3] and fig.data[0].mode == "lines+markers"
    assert fig.layout.shapes[0].y0 == 2.0
    assert V.build_progress(list(range(61)), 100).data[0].mode == "lines"                 # lange Folgen ohne Markierungen
    _locked(fig)


def test_cut_trace_hand_values():
    assert A.cut_trace(((0, 3, 0), (3, 0, 1), (0, 1, 0)), (0, 0, 0), ()) == [0] and A.cut_trace(A.ones(3), (0, 0, 0), (0,)) == [0, 2]


def test_rules_chart_selects_one_weight_bound_and_four_rules():
    rows = ev.sweep_rules(sizes=(6, 8), wmaxes=(1, 5), count=3, seed=1)
    fig = V.build_rules(rows, 5)
    assert [t.name for t in fig.data] == ["Schranke Σw", "beste Regel", "zufällige Regel", "erste Regel", "schlechteste Regel"] and list(fig.data[0].x) == [6, 8]
    assert list(fig.data[0].y) == [float(r["sigma"]) for r in rows if r["wmax"] == 5] and fig.layout.xaxis.type == "log" and fig.layout.yaxis.type == "log"
    assert fig.data[4].line.color == C.COLOR_RULES["worst"]
    _locked(fig)


def test_family_chart_has_bound_exact_rules_and_the_shortest_sequence():
    res = ev.sweep_family(rule_sizes=(6, 8), starts=2, exact_sizes=(4, 5, 6), random_sizes=(5,), graphs=1, seed=2)
    fig = V.build_family(res)
    assert [t.name for t in fig.data] == ["Schranke Σw", "längste mögliche Folge (exakt)", "schlechteste Regel", "erste Regel", "zufällige Regel", "beste Regel",
                                          "kürzeste mögliche Folge (exakt, Maximum über Starts)"]
    assert list(fig.data[1].x) == [4, 5, 6] and list(fig.data[1].y) == [4, res["exact"][1]["longest"], 9] and list(fig.data[2].x) == [6, 8] and fig.layout.yaxis.type == "log"
    _locked(fig)


def test_pdf_builds_for_every_family_and_rule():
    for family in C.FAMILIES:
        for rule in C.RULE_LABELS:
            pdf = build_pdf(ev.analyse(ev.Settings(n=10, family=family, rule=rule)))
            assert pdf[:5] == b"%PDF-" and len(pdf) > 1500
    assert build_pdf(ev.analyse(ev.Settings(n=24, family="expmin")))[:5] == b"%PDF-"       # lange Folge: abgeschnittene Liste
