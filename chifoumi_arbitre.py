"""
chifoumi_arbitre.py — Rock-Paper-Scissors referee (Pierre / Feuille / Ciseaux)
played with your hand through the webcam + MediaPipe.

Controls
--------
  SPACE : start a round (a 3-2-1-GO countdown plays, your gesture is read at GO)
  R     : reset the score
  Q     : quit

Requires:  pip install opencv-python mediapipe numpy
"""

import random
import time

import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# ----------------------------------------------------------------------------
# Étape 1 — gesture recognition
# ----------------------------------------------------------------------------

# A finger counts as "raised" when its tip landmark has a SMALLER y than its
# pip joint (y grows downward in the image). The thumb is ignored on purpose:
# its sideways movement depends on whether you use your left or right hand.
TIPS = [8, 12, 16, 20]    # tip    of index / middle / ring / pinky
PIPS = [6, 10, 14, 18]    # pip    of index / middle / ring / pinky


def compter_doigts_leves(hand_landmarks):
    """Return 4 booleans: is index / middle / ring / pinky raised?"""
    lm = hand_landmarks.landmark
    return [lm[t].y < lm[p].y for t, p in zip(TIPS, PIPS)]


def reconnaitre_geste(hand_landmarks):
    """Return 'pierre', 'feuille', 'ciseaux', or None if the gesture is unknown."""
    doigts = compter_doigts_leves(hand_landmarks)
    n = sum(doigts)
    if n == 0:
        return "pierre"                      # ✊ fist, no finger up
    if n == 4:
        return "feuille"                     # ✋ all four fingers up
    if doigts == [True, True, False, False]:
        return "ciseaux"                     # ✌️ index + middle only
    return None


# ----------------------------------------------------------------------------
# Étape 2 — the rules
# ----------------------------------------------------------------------------

# key beats value
GAGNE_CONTRE = {"pierre": "ciseaux", "feuille": "pierre", "ciseaux": "feuille"}


def determiner_gagnant(coup_joueur, coup_ordi):
    """Return 'joueur', 'ordi' or 'egalite'."""
    if coup_joueur == coup_ordi:
        return "egalite"
    return "joueur" if GAGNE_CONTRE[coup_joueur] == coup_ordi else "ordi"


# ----------------------------------------------------------------------------
# Étape 3 — the computer opponent, and its cheating 😈
# ----------------------------------------------------------------------------

# key beats value
BAT = {"pierre": "feuille", "feuille": "ciseaux", "ciseaux": "pierre"}

MESSAGES_TRICHE = [
    "Hé, j'ai p'tet regardé ta main avant de jouer... 👀",
    "Oups, l'IA a trouvé une faille dans les regles !",
    "Triche ? Moi ? Jamais... bon ok, un peu. 😇",
    "J'ai 500 FPS d'avance sur toi, fallait s'y attendre.",
]


def generer_coup_ordi(coup_joueur, proba_triche=0.3):
    """
    Return (coup_ordi, a_triche).

    With probability proba_triche the computer looks at your gesture and plays
    the one that beats it (and admits it). Otherwise it plays uniformly at
    random. Note: a cheated round is unwinnable for the player, so your win
    rate at proba_triche=0.3 is 0.7 x 1/3 = 0.233, not 0.333.
    """
    if random.random() < proba_triche:
        return BAT[coup_joueur], True
    return random.choice(list(BAT)), False


# ----------------------------------------------------------------------------
# Interface helpers
# ----------------------------------------------------------------------------

# Popup drawn with OpenCV only (no tkinter: it clashes with the webcam loop).
def creer_popup_triche(message):
    popup = np.full((200, 520, 3), (60, 60, 230), dtype=np.uint8)  # BGR
    cv2.putText(popup, "TRICHE DETECTEE !", (30, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(popup, message[:42], (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    if len(message) > 42:
        cv2.putText(popup, message[42:84], (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return popup


def afficher_resultat(frame, dernier_resultat, h):
    """Draw the outcome of the round in the middle of the frame."""
    gj, go, gagnant, a_triche = dernier_resultat
    if go is None:
        cv2.putText(frame, "Geste non detecte, reessaie (ESPACE)", (15, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return
    cv2.putText(frame, f"Toi: {gj}   Ordi: {go}", (15, h // 2 - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    txt = {"joueur": "TU GAGNES !", "ordi": "L'ORDI GAGNE !",
           "egalite": "EGALITE"}[gagnant]
    cv2.putText(frame, txt, (15, h // 2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


# ----------------------------------------------------------------------------
# Étape 4 — the game loop (a small state machine)
#
#   ATTENTE -> COMPTE_A_REBOURS -> RESULTAT -> ATTENTE -> ...
#
# One detail worth knowing: cv2.waitKey() BLOCKS. Calling waitKey(1800) for the
# cheat popup used to freeze the whole game for 1.8 s. We instead remember the
# popup and show it for a fixed number of frames, without ever blocking.
# ----------------------------------------------------------------------------

DUREE_POPUP_FRAMES = 55      # ~55 frames ~ 1.8 s at 30 fps


def jouer_chifoumi(proba_triche=0.3):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Impossible d'ouvrir la webcam.")
        return
    hands = mp_hands.Hands(max_num_hands=1,
                           min_detection_confidence=0.7,
                           min_tracking_confidence=0.5)

    etat = "ATTENTE"
    debut_compte = 0
    score_joueur, score_ordi = 0, 0
    dernier_resultat = None
    popup = None
    popup_restant = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)                 # mirror: more natural
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            geste_courant = None
            if results.multi_hand_landmarks:
                for hl in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
                    geste_courant = reconnaitre_geste(hl)

            h, w, _ = frame.shape

            # score bar
            cv2.rectangle(frame, (0, 0), (w, 60), (30, 30, 30), -1)
            cv2.putText(frame, f"Toi: {score_joueur}   Ordi: {score_ordi}", (15, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            if etat == "ATTENTE":
                cv2.putText(frame, "ESPACE pour jouer | R: reset | Q: quitter",
                            (15, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                            (200, 200, 200), 1)
                if geste_courant:
                    cv2.putText(frame, f"Geste detecte : {geste_courant}",
                                (15, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (0, 255, 0), 2)

            elif etat == "COMPTE_A_REBOURS":
                ecoule = time.time() - debut_compte
                restant = 3 - int(ecoule)
                texte = str(restant) if restant > 0 else "GO !"
                cv2.putText(frame, texte, (w // 2 - 40, h // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 215, 255), 5)
                if ecoule >= 3:
                    coup_joueur = geste_courant
                    if coup_joueur is None:
                        dernier_resultat = (None, None, None, False)
                    else:
                        coup_ordi, a_triche = generer_coup_ordi(coup_joueur, proba_triche)
                        gagnant = determiner_gagnant(coup_joueur, coup_ordi)
                        if gagnant == "joueur":
                            score_joueur += 1
                        elif gagnant == "ordi":
                            score_ordi += 1
                        dernier_resultat = (coup_joueur, coup_ordi, gagnant, a_triche)
                        if a_triche:
                            popup = creer_popup_triche(random.choice(MESSAGES_TRICHE))
                            popup_restant = DUREE_POPUP_FRAMES
                    etat = "RESULTAT"

            elif etat == "RESULTAT":
                afficher_resultat(frame, dernier_resultat, h)
                cv2.putText(frame, "ESPACE: rejouer", (15, h - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

            cv2.imshow("Arbitre de Chifoumi", frame)

            # cheat popup, shown for N frames instead of blocking
            if popup is not None and popup_restant > 0:
                cv2.imshow("Popup Triche", popup)
                popup_restant -= 1
                if popup_restant == 0:
                    popup = None
                    cv2.destroyWindow("Popup Triche")

            touche = cv2.waitKey(1) & 0xFF
            if touche == ord('q'):
                break
            elif touche == ord('r'):
                score_joueur, score_ordi = 0, 0
            elif touche == ord(' ') and etat in ("ATTENTE", "RESULTAT"):
                etat = "COMPTE_A_REBOURS"
                debut_compte = time.time()
                dernier_resultat = None
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()


if __name__ == "__main__":
    jouer_chifoumi(proba_triche=0.3)
