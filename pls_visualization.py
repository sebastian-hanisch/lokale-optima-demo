"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import pls_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def circle_position(i: int, n: int) -> tuple:
    """Lage von Knoten i auf dem Kreis (Knoten 0 oben, im Uhrzeigersinn)."""
    angle = 2 * math.pi * i / n
    return math.sin(angle), math.cos(angle)


def build_graph(w, side):
    """Der Graph (kleines n) auf einem Kreis: Knoten nach Seite gefärbt, Kanten zwischen den Seiten (im Schnitt) kräftig, die übrigen blass."""
    n = len(w)
    fig = go.Figure()
    for name, cut, color, width in (("Kante im Schnitt", True, C.COLOR_BEST, 3), ("Kante nicht im Schnitt", False, "rgba(150,150,150,0.35)", 1)):
        xs, ys = [], []
        for i in range(n):
            for j in range(i + 1, n):
                if w[i][j] and (side[i] != side[j]) == cut:
                    (x0, y0), (x1, y1) = circle_position(i, n), circle_position(j, n)
                    xs += [x0, x1, None]
                    ys += [y0, y1, None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=name, line=dict(color=color, width=width), hoverinfo="skip"))
    for s, name, color in ((0, "Seite 0", C.COLOR_FIRST), (1, "Seite 1", C.COLOR_RANDOM)):
        nodes = [i for i in range(n) if side[i] == s]
        fig.add_trace(go.Scatter(x=[circle_position(i, n)[0] for i in nodes], y=[circle_position(i, n)[1] for i in nodes], mode="markers+text", name=name, text=[str(i) for i in nodes],
                                 textposition="middle center", marker=dict(size=24, color=color), textfont=dict(color="white")))
    fig.update_xaxes(visible=False, range=[-1.25, 1.25])
    fig.update_yaxes(visible=False, range=[-1.25, 1.25], scaleanchor="x")
    return _base(fig, 360)


def build_progress(values, total):
    """Der Schnittwert vor dem ersten und nach jedem Flip; gestrichelt die Hälfte von Σw (jedes lokale Optimum liegt darüber)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(values))), y=values, mode="lines+markers" if len(values) <= 60 else "lines", name="Schnittwert", line=dict(color=C.COLOR_BEST)))
    fig.add_hline(y=total / 2, line=dict(color=C.COLOR_BOUND, dash="dash"), annotation_text="Σw / 2", annotation_position="bottom right")
    fig.update_xaxes(title="Flips")
    fig.update_yaxes(title="Schnittwert")
    return _base(fig, 300)


def build_rules(rows, wmax):
    """Mittlere Flips über n (logarithmisch) für die vier Pivotregeln bei der Gewichtsgrenze `wmax`, dazu Σw (gestrichelt)."""
    sel = sorted((r for r in rows if r["wmax"] == wmax), key=lambda r: r["n"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["n"] for r in sel], y=[float(r["sigma"]) for r in sel], mode="lines+markers", name="Schranke Σw", line=dict(color=C.COLOR_BOUND, dash="dash")))
    for rule, label in (("best", "beste"), ("random", "zufällige"), ("first", "erste"), ("worst", "schlechteste")):
        fig.add_trace(go.Scatter(x=[r["n"] for r in sel], y=[float(r["flips"][rule]) for r in sel], mode="lines+markers", name=f"{label} Regel", line=dict(color=C.COLOR_RULES[rule])))
    fig.update_xaxes(title="Knoten n", type="log")
    fig.update_yaxes(type="log", title="Flips (Mittel)")
    return _base(fig, 380)


def build_family(res):
    """Die Familie exp-min über n (logarithmisch): Flips der Regeln, die längste und die kürzeste mögliche Folge (exakt) und Σw."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["n"] for r in res["exact"]], y=[r["sigma"] for r in res["exact"]], mode="lines", name="Schranke Σw", line=dict(color=C.COLOR_BOUND, dash="dash")))
    fig.add_trace(go.Scatter(x=[r["n"] for r in res["exact"]], y=[r["longest"] for r in res["exact"]], mode="lines+markers", name="längste mögliche Folge (exakt)", line=dict(color=C.COLOR_WORST, dash="dot")))
    for rule, label in (("worst", "schlechteste"), ("first", "erste"), ("random", "zufällige"), ("best", "beste")):
        fig.add_trace(go.Scatter(x=[r["n"] for r in res["rules"]], y=[float(r["flips"][rule]) for r in res["rules"]], mode="lines+markers", name=f"{label} Regel", line=dict(color=C.COLOR_RULES[rule])))
    fig.add_trace(go.Scatter(x=[r["n"] for r in res["exact"]], y=[r["shortest"] for r in res["exact"]], mode="lines+markers", name="kürzeste mögliche Folge (exakt, Maximum über Starts)", line=dict(color=C.COLOR_BEST, dash="dot")))
    fig.update_xaxes(title="Knoten n", dtick=2)
    fig.update_yaxes(type="log", title="Flips")
    return _base(fig, 420)
