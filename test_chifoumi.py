"""
Tests for the referee logic. No webcam needed: the pure functions
(gesture rules, winner, computer move) are imported and checked.

Run:  python test_chifoumi.py
"""

import random

from chifoumi_arbitre import (
    determiner_gagnant,
    generer_coup_ordi,
    reconnaitre_geste,
)

COUPS = ["pierre", "feuille", "ciseaux"]


# --- the rules -------------------------------------------------------------

def test_neuf_affrontements():
    attendu = {
        ("pierre", "ciseaux"): "joueur",    # ✊ beats ✌️
        ("feuille", "pierre"): "joueur",    # ✋ beats ✊
        ("ciseaux", "feuille"): "joueur",   # ✌️ beats ✋
        ("pierre", "feuille"): "ordi",      # mirror cases: computer wins
        ("feuille", "ciseaux"): "ordi",
        ("ciseaux", "pierre"): "ordi",
    }
    for a in COUPS:
        for b in COUPS:
            if a == b:
                assert determiner_gagnant(a, b) == "egalite", (a, b)
            else:
                assert determiner_gagnant(a, b) == attendu[(a, b)], (a, b)


# --- the computer opponent -------------------------------------------------

def test_triche_totale_fait_toujours_gagner_lordi():
    for a in COUPS:
        for _ in range(300):
            coup_ordi, triche = generer_coup_ordi(a, proba_triche=1.0)
            assert triche is True
            assert determiner_gagnant(a, coup_ordi) == "ordi", (a, coup_ordi)


def test_sans_triche_jamais_signalee():
    for _ in range(1000):
        assert generer_coup_ordi("pierre", proba_triche=0.0)[1] is False


def test_taux_de_victoire_a_30_pourcent():
    # 70% of rounds are random (win 1/3), 30% are cheated (never win)
    # => expected win rate = 0.7 x 1/3 = 0.2333
    N = 60000
    victoires = sum(
        determiner_gagnant((a := random.choice(COUPS)),
                           generer_coup_ordi(a, 0.3)[0]) == "joueur"
        for _ in range(N)
    )
    taux = victoires / N
    assert 0.21 < taux < 0.26, f"win rate {taux:.4f} not near 0.2333"


# --- gesture recognition (fake landmarks) ----------------------------------
#
# MediaPipe landmark indices we use: tip [8, 12, 16, 20], pip [6, 10, 14, 18].
# y grows downward, so a raised finger has tip.y < pip.y.

class Landmark:
    def __init__(self, y):
        self.y = y


class FakeHand:
    """21 landmarks; only the 8 we look at are given meaningful y values."""

    def __init__(self, leves):
        self.landmark = [Landmark(0.5) for _ in range(21)]
        for tip, pip, leve in zip([8, 12, 16, 20], [6, 10, 14, 18], leves):
            self.landmark[tip].y = 0.2 if leve else 0.8   # tip above/below
            self.landmark[pip].y = 0.5


def test_gestures():
    assert reconnaitre_geste(FakeHand([False, False, False, False])) == "pierre"
    assert reconnaitre_geste(FakeHand([True, True, True, True])) == "feuille"
    assert reconnaitre_geste(FakeHand([True, True, False, False])) == "ciseaux"
    assert reconnaitre_geste(FakeHand([True, False, False, False])) is None
    assert reconnaitre_geste(FakeHand([False, False, True, False])) is None


if __name__ == "__main__":
    random.seed(0)
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed.")
