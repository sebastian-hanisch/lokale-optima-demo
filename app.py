"""Lokale Optima finden: PLS - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Elftes (optionales) Stück der Komplexitätsklassen-Reihe: eine Lokalsuche (Max-Cut mit Flip-Nachbarschaft) endet immer in einem lokalen Optimum; die Frage ist der Weg. Schranke Σw gegen Praxis, Pivotregeln und eine
Gewichtsfamilie mit exponentiell langen Folgen. Aufwand in Flips, nie in Sekunden.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

from fractions import Fraction

import streamlit as st

import pls_algorithm as A
import pls_constants as C
from pls_evaluation import (
    Settings,
    analyse,
    fmt_int,
    fmt_mean,
    fmt_percent,
    sweep_family,
    sweep_quality,
    sweep_rules,
    validation_errors,
    verdict_family,
    verdict_main,
    verdict_quality,
    verdict_rules,
)
from pls_layout import dunkles_design, kopf_css
from pls_pdf_export import build_pdf
from pls_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from pls_visualization import build_family, build_graph, build_progress, build_rules

st.set_page_config(page_title="Lokale Optima finden – Sebastian Hanisch", layout="wide")

GRAPH_N_MAX = 12                                        # den Graphen zeichnen wir bis hierhin


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _rules():
    return sweep_rules()


@st.cache_data(show_spinner=False)
def _family():
    return sweep_family()


@st.cache_data(show_spinner=False)
def _quality():
    return sweep_quality()


@st.cache_data(show_spinner=False)
def _pdf(settings):
    return build_pdf(analyse(settings))


def _md_table(header, rows):
    lines = ["| " + " | ".join(str(c) for c in header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in pls_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧗 Lokale Optima finden: wie lang ist der Weg?")

st.markdown(
    """
Eine **Lokalsuche** verbessert eine Lösung Schritt für Schritt, bis kein Schritt mehr hilft: ein **lokales Optimum**. Dass es eines gibt, ist klar; die Frage ist, **wie viele Schritte** der Weg braucht. Die Demo zeigt das am **Max-Cut**:
ein Graph mit ganzzahligen Kantengewichten, eine Zweiteilung der Knoten (Schnitt) und als Schritt der **Flip** eines Knotens auf die andere Seite. Jeder verbessernde Flip hebt den Schnitt um mindestens 1, also endet jede Folge nach
höchstens **Σw** Schritten (Summe aller Gewichte; **pseudopolynomial**, vgl. Stück 5). Wie lang der Weg wirklich ist, hängt von der **Pivotregel** (welcher verbessernde Flip) und von den **Gewichten** ab. Das Verfahren auf Touren
steht in [hill-climbing-demo](https://github.com/sebastian-hanisch/hill-climbing-demo). Aufwand wird in **Flips** gezählt, nicht in Sekunden.
Elftes (optionales) Stück der Komplexitätsklassen-Reihe; die Fall-Demos behandeln einzelne Anwendungen, hier steht eine Frage der Komplexitätstheorie im Mittelpunkt.

Weiter unten: die Experimente **🔬 Schranke gegen Praxis**, **🔬 Eine gemeine Familie** und **🔬 Wie gut ist ein lokales Optimum?**, dann **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("Lokale Suche als Suchproblem", expanded=True):
    st.markdown(
        """
1. **Suchen statt entscheiden.** Ein lokales Optimum **existiert immer** (der größte Schnitt ist eines). Gefragt ist nicht „gibt es eines?“, sondern „wie finde ich eines, und wie lange dauert der Weg?“. Solche Probleme heißen
   **Suchprobleme**; die Klasse **PLS** (polynomial local search) fasst die lokale Suche mit polynomiell bewertbaren Schritten zusammen (Johnson, Papadimitriou und Yannakakis, 1988; Literatur). Für Max-Cut mit Flip gilt
   nach der Literatur PLS-Vollständigkeit (Schäffer und Yannakakis, 1991; Literatur, nicht gemessen).
2. **Die Schranke Σw.** Weil jeder Flip den ganzzahligen Schnitt um mindestens 1 erhöht und der Schnitt höchstens Σw beträgt, endet jede Folge nach höchstens Σw Flips. Das ist pseudopolynomiell: es wächst mit der Größe der Gewichte.
3. **Was messen wir?** Wie nahe die Praxis an Σw kommt (auf Zufallsgraphen mit größeren Gewichten weit entfernt), welche Pivotregel kurze Wege liefert, und eine explizite Gewichtsfamilie, auf der natürliche Regeln exponentiell lange Wege gehen.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    n = st.slider("Knoten n", *bounds("n_slider"), key="n_slider", help=f"Die exakte Aufzählung aller 2^n Schnitte läuft nur bis n = {C.EXACT_LIVE_N_MAX}; der Graph wird bis n = {GRAPH_N_MAX} gezeichnet.")
    family = st.selectbox("Graph", list(C.FAMILIES), format_func=C.FAMILIES.get, key="family_select", help="Die Familie „2^min(i, j)“ ist die gemeine: auf ihr wachsen die Flips der ersten und der schlechtesten Regel bei zufälligen Starts im gemessenen Bereich (n ≤ 24) etwa um den Faktor 4 je vier Knoten (2^(n/2)).")
    dens = st.select_slider("Kantendichte in %", options=list(C.DENS_OPTIONS), key="dens_select", help="Nur für den Zufallsgraphen.")
    wmax = st.select_slider("Größtes Gewicht W", options=list(C.WMAX_OPTIONS), format_func=fmt_int, key="wmax_select", help="Nur für den Zufallsgraphen: Gewichte 1 bis W. Σw wächst mit W.")
    rule = st.selectbox("Pivotregel", list(C.RULE_LABELS), format_func=C.RULE_LABELS.get, key="rule_select", help="Welcher verbessernde Flip als nächster genommen wird.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt auf den Zufallsgraphen, den Startschnitt und die zufällige Regel.")
    st.button("🎲 Neuen Graphen generieren", width="stretch", on_click=randomize_seed)

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "family_select": family, "dens_select": int(dens), "wmax_select": int(wmax), "rule_select": rule})

settings = Settings(n=int(n), seed=int(seed), family=family, dens=int(dens), wmax=int(wmax), rule=rule)
with st.spinner("Starte die Lokalsuche …"):
    a = _analysis(settings)
for message in validation_errors(a):
    st.error(message)

# --- Hauptansicht --------------------------------------------------------------------------------------------------------------------------

s = a.search
st.markdown("## 🎯 Wie lang ist der Weg ins lokale Optimum?")
st.markdown(f"{len(a.w)} Knoten, Graph: {C.FAMILIES[settings.family]}; Startschnitt zufällig; Pivotregel: {C.RULE_LABELS[settings.rule]}.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Flips", fmt_int(s.flips), help="Verbessernde Schritte bis zum lokalen Optimum.")
m2.metric("Schnitt", f"{fmt_int(s.cut_start)} → {fmt_int(s.cut_end)}", help="Wert vor dem ersten und nach dem letzten Flip.")
m3.metric("Σw (Schranke)", fmt_int(a.total), help="Jede Folge hat höchstens Σw Flips.")
m4.metric("Schranke ausgeschöpft", fmt_percent(Fraction(s.flips, a.total)) if a.total else "0 %", help="Flips geteilt durch Σw.")
if a.exact is not None:
    e = a.exact
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Kürzeste mögliche Folge", fmt_int(e.shortest), help="Vom Start aus, bei günstigster Wahl der Flips, nicht die Regel „beste“ (alle 2^n Schnitte aufgezählt).")
    k2.metric("Längste mögliche Folge", fmt_int(e.longest), help="Vom Start aus, bei ungünstigster Wahl der Flips.")
    k3.metric("Lokale Optima", fmt_int(e.local_optima), help="Unter allen 2^n Schnitten.")
    k4.metric("Größter Schnitt", fmt_int(e.optimum), help="Das globale Optimum.")
vkind, vtext = verdict_main(a)
getattr(st, vkind)(vtext)

c1, c2 = st.columns([3, 2])
with c1:
    st.markdown("**Der Schnittwert über die Flips**")
    st.plotly_chart(build_progress(A.cut_trace(a.w, a.start, s.sequence), a.total), width="stretch", key="progress_chart")
with c2:
    if len(a.w) <= GRAPH_N_MAX:
        st.markdown("**Der Graph im lokalen Optimum** (Kanten im Schnitt kräftig)")
        st.plotly_chart(build_graph(a.w, s.side), width="stretch", key="graph_chart")
    else:
        st.info(f"Der Graph wird bis n = {GRAPH_N_MAX} gezeichnet; hier ist n = {len(a.w)}.")

if st.button("📄 PDF erstellen"):
    st.session_state["pdf_for"] = settings
if st.session_state.get("pdf_for") == settings:
    st.download_button("⬇️ PDF herunterladen", data=_pdf(settings), file_name="lokale-optima.pdf", mime="application/pdf")

st.markdown("## ❓ Kernfrage: Wie nahe kommt eine Lokalsuche der Schranke, und was entscheidet?")
st.markdown("Die Schranke Σw ist pseudopolynomiell und bleibt auf Zufallsgraphen mit größeren Gewichten weit entfernt; ob die Folge kurz ist, entscheiden die Pivotregel und die Gewichte. Die Experimente messen beides.")

st.markdown("---")

# --- Experimente --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Schranke gegen Praxis")
st.caption(f"Zufallsgraphen G(n, {C.RULES_DENS} %), je Größe und Gewichtsgrenze {C.RULES_COUNT} feste Graphen mit zufälligem Start; mittlere Flips der vier Pivotregeln. Rund 4 Sekunden.")
if st.button("▶️ Messreihe Pivotregeln rechnen"):
    st.session_state["rules_on"] = True
if st.session_state.get("rules_on"):
    with st.spinner("Rechne 1.200 Lokalsuchen je Regel …"):
        rules = _rules()
    st.plotly_chart(build_rules(rules, max(C.RULES_WMAX)), width="stretch", key="rules_chart")
    st.caption(f"Gewichte bis {fmt_int(max(C.RULES_WMAX))}; die Tabelle nennt alle Gewichtsgrenzen.")
    st.markdown(_md_table(
        ["W", "n", "Σw (Mittel)", "beste", "zufällig", "erste", "schlechteste", "schlechteste: größte", "größter Anteil Flips / Σw"],
        [[fmt_int(r["wmax"]), r["n"], fmt_mean(r["sigma"]), fmt_mean(r["flips"]["best"]), fmt_mean(r["flips"]["random"]), fmt_mean(r["flips"]["first"]), fmt_mean(r["flips"]["worst"]), fmt_int(r["worst_max"]),
          fmt_percent(r["share_max"])] for r in rules],
    ))
    vkind, vtext = verdict_rules(rules)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Eine gemeine Familie")
st.caption(f"Vollständiger Graph, Kante {{i, j}} mit Gewicht 2^min(i, j). Pivotregeln von {C.FAMILY_STARTS} festen Zufallsstarts (n = {', '.join(str(x) for x in C.FAMILY_RULE_SIZES)}) und die exakten Folgen aus der Aufzählung aller "
           f"Schnitte (gerade n = {C.FAMILY_EXACT_SIZES[0]} bis {C.FAMILY_EXACT_SIZES[-1]}). Rund 3 Sekunden.")
if st.button("▶️ Messreihe gemeine Familie rechnen"):
    st.session_state["family_on"] = True
if st.session_state.get("family_on"):
    with st.spinner("Zähle alle Schnitte der Familie …"):
        fam = _family()
    st.plotly_chart(build_family(fam), width="stretch", key="family_chart")
    st.markdown("**Pivotregeln** (mittlere Flips)")
    st.markdown(_md_table(
        ["n", "Σw", "beste", "zufällig", "erste", "schlechteste", "schlechteste: größte"],
        [[r["n"], fmt_int(r["sigma"]), fmt_mean(r["flips"]["best"]), fmt_mean(r["flips"]["random"]), fmt_mean(r["flips"]["first"]), fmt_mean(r["flips"]["worst"]), fmt_int(r["worst_max"])] for r in fam["rules"]],
    ))
    st.markdown("**Exakte Folgen** (alle 2^n Schnitte aufgezählt)")
    st.markdown(_md_table(
        ["n", "längste Folge", "2^(n/2) + n/2 − 2", "kürzeste (Maximum über Starts)", "lokale Optima", "2^(n/2)", "Σw"],
        [[r["n"], fmt_int(r["longest"]), fmt_int(r["formula"]) if r["formula"] is not None else "–", r["shortest"], fmt_int(r["local_optima"]), fmt_int(2 ** (r["n"] // 2)) if r["n"] % 2 == 0 else "–", fmt_int(r["sigma"])]
         for r in fam["exact"]],
    ))
    st.markdown(f"**Zum Vergleich: vollständige Graphen mit Zufallsgewichten 1 bis {C.RANDOM_EXACT_WMAX}** (längste Folge, Maximum über {C.RANDOM_EXACT_GRAPHS} Graphen)")
    st.markdown(_md_table(["n", "längste Folge", "geteilt durch n²"], [[r["n"], fmt_int(r["longest"]), f"{float(r['per_n2']):.2f}".replace(".", ",")] for r in fam["random"]]))
    vkind, vtext = verdict_family(fam)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Wie gut ist ein lokales Optimum?")
st.caption(f"{C.QUALITY_COUNT} feste Graphen (n = {C.QUALITY_N}, Gewichte bis {C.QUALITY_WMAX}, erste Regel); das Optimum wird durch Aufzählung aller Schnitte bestimmt. Rund 1 Sekunde.")
if st.button("▶️ Messreihe Qualität rechnen"):
    st.session_state["quality_on"] = True
if st.session_state.get("quality_on"):
    with st.spinner("Zähle die Schnitte von 100 Graphen …"):
        q = _quality()
    q1, q2, q3 = st.columns(3)
    q1.metric("Schnitt ≥ Σw / 2", f"{q['half_ok']} von {q['count']}", help="Jedes lokale Optimum schneidet mindestens die Hälfte von Σw (Beweis: jeder Knoten hat mindestens die Hälfte seines Kantengewichts im Schnitt).")
    q2.metric("Im Mittel vom Optimum", fmt_percent(q["ratio_mean"]))
    q3.metric("Mindestens vom Optimum", fmt_percent(q["ratio_min"]))
    vkind, vtext = verdict_quality(q)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Einordnung: PLS, glatte Analyse und Gleichgewichte")
st.markdown(
    "Die Beobachtung „typisch kurz, im schlimmsten Fall lang“ ist die Frage der **geglätteten Analyse**: unter kleinen zufälligen Störungen der Gewichte ist die Laufzeit der Flip-Lokalsuche für Max-Cut nach Etscheid und Röglin "
    "in beliebigen Graphen quasi-polynomiell (ACM Transactions on Algorithms 13 (2), 2017; Literatur, hier nicht nachgebaut). **Gleichgewichte** (zum Beispiel Nash-Gleichgewichte, vgl. [nash-demo](https://github.com/sebastian-hanisch/nash-demo)) sind ebenfalls Suchprobleme: ihre Existenz ist gesichert, das Finden gilt als schwer (Klasse "
    "**PPAD**; Literatur, nicht gemessen). Für die Rundreise mit 2-opt wird hier **keine** Vollständigkeitsaussage gemacht."
)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **PLS-Vollständigkeit von Max-Cut mit Flip** | Literatur (Schäffer und Yannakakis), die Demo misst sie nicht; sie misst Flips bis n = 80 (Zufallsgraphen) und n = 24 (die Familie). | – |
| **Zufallsgraphen stehen für alle Graphen** | Nein: die Zahlen gelten für G(n, 50 %) mit gleichverteilten Gewichten; strukturierte Graphen verhalten sich anders (zweite Familie). | – |
| **Die Familie 2^min(i, j) ist typisch** | Nein: sie ist eine Konstruktion. Sie zeigt, dass die Schrittzahl bei bestimmten Gewichten und natürlichen Regeln exponentiell sein kann, nicht dass sie es meist ist. | – |
| **Flips sind Zeit** | Ein Flip kostet O(n) (Gewinne fortschreiben); gezählt werden Flips einer einfachen Umsetzung, nicht Rechenzeit. | – |
| **Vier Pivotregeln sind alle** | Es gibt viele weitere (etwa gewichtete Zufallsregeln); die Aussage „die Regel entscheidet“ gilt für diese vier. | – |
| **Die Formel 2^(n/2) + n/2 − 2 ist ein Satz** | Sie ist an den geraden n von 4 bis 18 durch Aufzählung **gemessen**; ein Beweis steht hier nicht. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(r"**Schnitt und Gewinn.** Für einen Graphen mit Gewichten $w_{uv} \ge 0$ und eine Zweiteilung $S \subseteq V$ ist der Schnittwert und der Gewinn des Flips von $v$:")
    st.latex(r"\operatorname{cut}(S) = \sum_{\{u, v\}:\; u \in S,\, v \notin S} w_{uv}, \qquad g(v) = \sum_{u \text{ auf der Seite von } v} w_{uv} \;-\; \sum_{u \text{ auf der anderen Seite}} w_{uv}")
    st.markdown(r"Ein Flip mit $g(v) > 0$ erhöht den Schnitt um genau $g(v) \ge 1$ (ganzzahlige Gewichte). Weil $\operatorname{cut}(S) \le \Sigma w = \sum_{u < v} w_{uv}$, endet jede Folge nach höchstens")
    st.latex(r"\Sigma w \text{ Flips} \qquad \text{(pseudopolynomiell)}")
    st.markdown(r"**Güte.** In einem lokalen Optimum ist $g(v) \le 0$ für jeden Knoten, also liegt mindestens die Hälfte des Kantengewichts an $v$ im Schnitt; Summation über alle Knoten gibt")
    st.latex(r"\operatorname{cut}(S) \;\ge\; \tfrac{1}{2}\, \Sigma w")
    st.markdown(
        r"""
| Annahme | Bedeutung | Wer setzt an |
|---|---|---|
| Ganzzahlige Gewichte | jeder verbessernde Flip erhöht den Schnitt um mindestens 1 | – |
| Nichtnegative Gewichte | die Gütegarantie $\ge \Sigma w / 2$ setzt sie voraus | – |
| Zufall | feste Zufalls-Seeds, damit jede Zahl reproduzierbar ist | – |
| Pivotregeln | vier feste Regeln; Gleichstände entscheidet der kleinste Knotenindex | – |
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
