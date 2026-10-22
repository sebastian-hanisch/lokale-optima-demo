"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Ergebnis (Flips, Schnitte, Schranken) und die Folge der Flips. Kein Gedankenstrich und kein Euro-Zeichen (Kernschriften)."""

from fpdf import FPDF

import pls_constants as C
import pls_evaluation as ev


def _text(value: str) -> str:
    """Zeichen, die die Kernschriften nicht kennen, ersetzen (Gedankenstrich, Pfeile, Fettdruck-Markierung, mathematische Zeichen)."""
    table = {"–": "-", "—": "-", "→": "->", "**": "", "€": "EUR", "·": "*", "³": "^3", "≤": "<=", "≥": ">=", "−": "-", "×": "x", "„": '"', "“": '"', "⇔": "<=>", "²": "^2", "Σ": "Summe ", "…": "..."}
    for old, new in table.items():
        value = value.replace(old, new)
    return value


def _para(pdf: FPDF, height: float, text: str) -> None:
    """Absatz über die volle Breite; danach steht der Cursor wieder am linken Rand (fpdf2 setzt ihn sonst an den rechten Rand)."""
    pdf.multi_cell(0, height, _text(text), new_x="LMARGIN", new_y="NEXT")


def build_pdf(a: ev.Analysis) -> bytes:
    s = a.settings
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _text("Lokale Optima finden: Max-Cut mit Flip-Nachbarschaft"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _para(pdf, 5.5, f"Knoten: {s.n}   Graph: {C.FAMILIES[s.family]}   Pivotregel: {C.RULE_LABELS[s.rule]}   Zufalls-Seed: {s.seed}")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Ergebnis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _para(pdf, 5.5, ev.verdict_main(a)[1])
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Folge der Flips (Knoten)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "", 8)
    shown = a.search.sequence[:300]
    listing = (" ".join(str(v) for v in shown) + (" ..." if len(a.search.sequence) > len(shown) else "")) if shown else "(keine Flips)"
    _para(pdf, 4.2, listing)
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    _para(pdf, 4.5, "Aufwand in Flips, nicht in Sekunden. Sebastian Hanisch - Operations Research und Machine Learning.")
    return bytes(pdf.output())
