"""Gemeinsame Fixtures: Mini-Graphen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Handwerte (Gewinn eines Flips = Gewicht zur eigenen Seite minus Gewicht zur anderen Seite):
* T3 = Dreieck, alle Gewichte 1, Start (0, 0, 0): Schnitt 0, jeder Flip hat Gewinn 2. Nach dem Flip von Knoten 0: Seiten (1, 0, 0), Schnitt 2; Gewinne −2 (Knoten 0), 0, 0: lokales Optimum nach 1 Flip.
* P3 = Pfad 0 —3— 1 —1— 2 (Gewichte 3 und 1), Start (0, 0, 0): Gewinne (3, 4, 1), Σw = 4.
  first: Knoten 0 (Schnitt 3), dann Knoten 2 (Schnitt 4): Folge (0, 2), 2 Flips.
  best: Knoten 1 (Gewinn 4): Schnitt 4 sofort, Folge (1), 1 Flip.
  worst: Knoten 2 (Gewinn 1, Schnitt 1), dann Knoten 1 (Gewinn 2, Schnitt 3), dann Knoten 2 (Gewinn 1, Schnitt 4): Folge (2, 1, 2), 3 Flips.
* K4 mit Gewichten 1, Start (0, 0, 0, 0): Gewinne (3, 3, 3, 3); first flippt Knoten 0 (Schnitt 3), danach haben die Knoten 1 bis 3 Gewinn 2 − 1 = 1; first flippt Knoten 1 (Schnitt 4, 2 + 2): lokales Optimum nach 2 Flips.
* exp-min, n = 4: Gewichte w01 = w02 = w03 = 1, w12 = w13 = 2, w23 = 4, Σw = 11."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

T3 = ((0, 1, 1), (1, 0, 1), (1, 1, 0))
P3 = ((0, 3, 0), (3, 0, 1), (0, 1, 0))
K4 = tuple(tuple(int(i != j) for j in range(4)) for i in range(4))


@pytest.fixture
def mini():
    return {"T3": T3, "P3": P3, "K4": K4}
