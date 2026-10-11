# ======================================================================
# Markdown cell 1
# ======================================================================
# # 🎮 TP — Arbitre de Chifoumi (Pierre-Feuille-Ciseaux) par vision par ordinateur
#
# **Objectif du TP**
#
# Construire pas à pas un programme qui :
# 1. Filme ta main via la webcam
# 2. Reconnaît ton geste (Pierre / Feuille / Ciseaux) grâce à **MediaPipe**
# 3. Fait jouer un adversaire IA — qui, de temps en temps, **triche** (et l'avoue via une popup rigolote que tu personnalises)
# 4. Affiche tout ça dans une interface claire, avec score et compte à rebours
#
# **Format du TP** : chaque étape a un **exercice** (à toi de compléter, avec des `TODO`) suivi d'une **correction**. Tu peux sauter direct à la correction si tu es pressé — l'important est de comprendre chaque brique. À la fin (Étape 6), tout est assemblé dans le jeu complet et jouable.
#
# ---
#
# ## ⚠️ Avant de commencer — spécifique à ton setup
#
# - **Tu es sous WSL2** : WSL2 n'a pas d'accès natif à la webcam ni à l'affichage graphique. Pour ce projet (webcam + fenêtre OpenCV), c'est **beaucoup plus simple d'exécuter ce notebook avec un Python + Jupyter installés côté Windows** (pas dans le terminal WSL2). Si tu tiens à rester sous WSL2, il faudra configurer `usbipd-win` pour la webcam et WSLg pour l'affichage — plus de friction pour le même résultat.
# - **RAM limitée** : ferme les autres applications lourdes avant de lancer la webcam + MediaPipe.
# - **Pas de GPU** : aucun souci, MediaPipe Hands tourne très bien en CPU, c'est fait pour.
#
# ## 0. Installation
#
# Exécute la cellule suivante une seule fois (décommente les lignes).


# ======================================================================
# Code cell 1
# ======================================================================
# !pip install opencv-python mediapipe numpy


# ======================================================================
# Code cell 2
# ======================================================================
%pip install opencv-python


# ======================================================================
# Markdown cell 2
# ======================================================================
# ## Étape 1 — Ouvrir la webcam
#
# Avant de reconnaître quoi que ce soit, il faut afficher le flux vidéo brut.
#
# **Exercice** : complète la fonction pour que la fenêtre s'ouvre, affiche le flux en direct (en miroir, plus naturel), et se ferme proprement quand on appuie sur `q`.


# ======================================================================
# Code cell 3
# ======================================================================
import cv2

def test_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpend():
        print("Impossible d'ouvrir la webcam")
        return 

    while True:
        ret, frame = cap.read()
        # TODO 1 : si ret est False, sors de la boucle (break)
        if not ret:
            break

        # TODO 2 : mets l'image en miroir horizontal (cv2.flip)
        frame = cv2.flip(frame, 1)
        
        # TODO 3 : affiche l'image dans une fenêtre nommée "Webcam Test" (cv2.imshow)
        cv2.imshow("Webcam Test", frame)
        
        # TODO 4 : sors de la boucle si la touche 'q' est pressée (cv2.waitKey)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


    cap.release()
    cv2.destroyAllWindows()

# test_webcam()


# ======================================================================
# Markdown cell 3
# ======================================================================
# ### ✅ Correction — Étape 1


# ======================================================================
# Code cell 4
# ======================================================================
import cv2

def test_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Impossible d'ouvrir la webcam.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        cv2.imshow("Webcam Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Décommente pour tester :
# test_webcam()


# ======================================================================
# Markdown cell 4
# ======================================================================
# ## Étape 2 — Détecter la main avec MediaPipe
#
# MediaPipe Hands renvoie, pour chaque main détectée, **21 points-clés (landmarks)** en coordonnées normalisées (0 à 1). On utilise ici l'API `mp.solutions.hands` (l'API "legacy", plus simple à prendre en main — toujours fonctionnelle, même si Google pousse désormais vers `mediapipe.tasks`, voir la section bonus en fin de notebook).
#
# **Exercice** : initialise `mp_hands.Hands(...)`, convertis chaque frame en RGB, passe-la à `hands.process(...)`, et dessine les landmarks trouvés.


# ======================================================================
# Code cell 5
# ======================================================================
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def test_detection_main():
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        # TODO 1 : convertis frame de BGR (OpenCV) vers RGB (MediaPipe attend du RGB)
        rgb = None

        # TODO 2 : passe rgb à hands.process(...) pour obtenir "results"
        results = None

        # TODO 3 : si results.multi_hand_landmarks n'est pas vide, dessine chaque main
        #          avec mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Detection main", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

# test_detection_main()


# ======================================================================
# Markdown cell 5
# ======================================================================
# ### ✅ Correction — Étape 2


# ======================================================================
# Code cell 6
# ======================================================================
def test_detection_main():
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.imshow("Detection main", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

# test_detection_main()


# ======================================================================
# Markdown cell 6
# ======================================================================
# ## Étape 3 — Reconnaître le geste (Pierre / Feuille / Ciseaux)
#
# **Logique** : pour les 4 doigts index/majeur/annulaire/auriculaire, un doigt est considéré "levé" si le bout du doigt (landmark *tip*) est **au-dessus** de son articulation *pip* (coordonnée `y` plus petite, puisque `y` augmente vers le bas de l'image). On ignore le pouce pour simplifier (son mouvement latéral dépend de la main gauche/droite).
#
# | Geste | Doigts levés (index, majeur, annulaire, auriculaire) |
# |---|---|
# | ✊ Pierre | aucun (poing fermé) |
# | ✋ Feuille | les 4 |
# | ✌️ Ciseaux | index + majeur seulement |
#
# **Exercice** : complète `compter_doigts_leves` puis `reconnaitre_geste`.
#
# *Indices d'index de landmarks : tip = [8, 12, 16, 20], pip = [6, 10, 14, 18].*


# ======================================================================
# Code cell 7
# ======================================================================
def compter_doigts_leves(hand_landmarks):
    # Retourne une liste de 4 booléens : [index, majeur, annulaire, auriculaire] levés ou non.
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    doigts = []
    for tip, pip in zip(tips, pips):
        # TODO : compare hand_landmarks.landmark[tip].y et hand_landmarks.landmark[pip].y
        leve = None
        doigts.append(leve)
    return doigts

def reconnaitre_geste(hand_landmarks):
    doigts = compter_doigts_leves(hand_landmarks)
    nb_leves = sum(doigts)
    # TODO : retourne "pierre" si nb_leves == 0
    # TODO : retourne "feuille" si nb_leves == 4
    # TODO : retourne "ciseaux" si doigts == [True, True, False, False]
    # TODO : sinon, retourne None (geste non reconnu)
    pass


# ======================================================================
# Markdown cell 7
# ======================================================================
# ### ✅ Correction — Étape 3


# ======================================================================
# Code cell 8
# ======================================================================
def compter_doigts_leves(hand_landmarks):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    return [hand_landmarks.landmark[t].y < hand_landmarks.landmark[p].y for t, p in zip(tips, pips)]

def reconnaitre_geste(hand_landmarks):
    doigts = compter_doigts_leves(hand_landmarks)
    n = sum(doigts)
    if n == 0:
        return "pierre"
    if n == 4:
        return "feuille"
    if doigts == [True, True, False, False]:
        return "ciseaux"
    return None


# ======================================================================
# Markdown cell 8
# ======================================================================
# ## Étape 4 — Les règles du jeu
#
# **Exercice** : complète `determiner_gagnant`. Rappel des règles : Pierre bat Ciseaux, Ciseaux bat Feuille, Feuille bat Pierre.


# ======================================================================
# Code cell 9
# ======================================================================
def determiner_gagnant(coup_joueur, coup_ordi):
    if coup_joueur == coup_ordi:
        return "égalité"
    gagne_contre = {"pierre": "ciseaux", "feuille": "pierre", "ciseaux": "feuille"}
    # TODO : si gagne_contre[coup_joueur] == coup_ordi -> le joueur gagne, sinon l'ordi gagne
    pass


# ======================================================================
# Markdown cell 9
# ======================================================================
# ### ✅ Correction — Étape 4


# ======================================================================
# Code cell 10
# ======================================================================
def determiner_gagnant(coup_joueur, coup_ordi):
    if coup_joueur == coup_ordi:
        return "égalité"
    gagne_contre = {"pierre": "ciseaux", "feuille": "pierre", "ciseaux": "feuille"}
    return "joueur" if gagne_contre[coup_joueur] == coup_ordi else "ordi"


# ======================================================================
# Markdown cell 10
# ======================================================================
# ## Étape 5 — Le coup de l'ordinateur, et sa triche 😈
#
# L'ordi joue **aléatoirement** la plupart du temps. Mais avec une probabilité `proba_triche`, il **regarde ton geste et choisit délibérément le coup qui te bat** — et l'avoue via une popup.
#
# **✍️ À toi de jouer** : remplis `MESSAGES_TRICHE` avec tes propres messages rigolos (c'est la partie que tu voulais créer toi-même !).
#
# **Exercice** : complète `generer_coup_ordi`.


# ======================================================================
# Code cell 11
# ======================================================================
import random
import numpy as np

# 👉 Remplis cette liste avec tes propres messages rigolos !
MESSAGES_TRICHE = [
    "Hé, j'ai p'tet regardé ta main avant de jouer... 👀",
    "Oups, l'IA a trouvé une faille dans les regles !",
    # Ajoute les tiens ici...
]

def generer_coup_ordi(coup_joueur, proba_triche=0.3):
    coups = ["pierre", "feuille", "ciseaux"]
    # TODO 1 : avec une probabilité proba_triche (random.random() < proba_triche),
    #          choisis le coup qui bat coup_joueur et retourne (coup, True)
    #          indice : dictionnaire "bat" = {"pierre": "feuille", "feuille": "ciseaux", "ciseaux": "pierre"}
    # TODO 2 : sinon, retourne (random.choice(coups), False)
    pass

def afficher_popup_triche(message, duree_ms=1800):
    # Popup "fait maison" avec une fenêtre OpenCV dédiée (pas de tkinter, pour éviter
    # les conflits de thread avec la fenêtre principale de la webcam).
    popup = np.full((200, 520, 3), (60, 60, 230), dtype="uint8")  # fond BGR
    cv2.putText(popup, "TRICHE DETECTEE !", (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(popup, message[:42], (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    if len(message) > 42:
        cv2.putText(popup, message[42:84], (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    cv2.imshow("Popup Triche", popup)
    cv2.waitKey(duree_ms)
    cv2.destroyWindow("Popup Triche")


# ======================================================================
# Markdown cell 11
# ======================================================================
# ### ✅ Correction — Étape 5


# ======================================================================
# Code cell 12
# ======================================================================
def generer_coup_ordi(coup_joueur, proba_triche=0.3):
    coups = ["pierre", "feuille", "ciseaux"]
    if random.random() < proba_triche:
        bat = {"pierre": "feuille", "feuille": "ciseaux", "ciseaux": "pierre"}
        return bat[coup_joueur], True
    return random.choice(coups), False


# ======================================================================
# Markdown cell 12
# ======================================================================
# ## Étape 6 — Interface & assemblage final
#
# C'est la partie que tu m'as demandé de générer directement. On assemble tout dans une **machine à états** pour une expérience fluide et intuitive :
#
# - **ATTENTE** : la webcam tourne, ton geste est affiché en direct dès qu'il est reconnu. Appuie sur **ESPACE** pour lancer une manche.
# - **COMPTE_A_REBOURS** : 3 secondes de décompte affiché à l'écran (comme un vrai "Pierre... Feuille... Ciseaux... Shoot !"), le geste est capturé à la fin.
# - **RESULTAT** : ton coup, le coup de l'ordi, le résultat, le score — et la popup de triche si besoin.
#
# Touches : **ESPACE** = jouer/rejouer, **R** = réinitialiser le score, **Q** = quitter.


# ======================================================================
# Code cell 13
# ======================================================================
import time

def jouer_chifoumi(proba_triche=0.3):
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)

    etat = "ATTENTE"  # ATTENTE -> COMPTE_A_REBOURS -> RESULTAT -> ATTENTE
    debut_compte = 0
    score_joueur, score_ordi = 0, 0
    dernier_resultat = None
    temps_resultat = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        geste_courant = None
        if results.multi_hand_landmarks:
            for hl in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
                geste_courant = reconnaitre_geste(hl)

        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, 60), (30, 30, 30), -1)
        cv2.putText(frame, f"Toi: {score_joueur}   Ordi: {score_ordi}", (15, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        if etat == "ATTENTE":
            cv2.putText(frame, "ESPACE pour jouer | R: reset | Q: quitter", (15, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
            if geste_courant:
                cv2.putText(frame, f"Geste detecte : {geste_courant}", (15, h - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        elif etat == "COMPTE_A_REBOURS":
            ecoule = time.time() - debut_compte
            restant = 3 - int(ecoule)
            texte = str(restant) if restant > 0 else "GO !"
            cv2.putText(frame, texte, (w // 2 - 40, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 215, 255), 5)
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
                etat = "RESULTAT"
                temps_resultat = time.time()

        elif etat == "RESULTAT":
            gj, go, gagnant, a_triche = dernier_resultat
            if go is None:
                cv2.putText(frame, "Geste non detecte, reessaie (ESPACE)", (15, h // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f"Toi: {gj}   Ordi: {go}", (15, h // 2 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                txt_gagnant = {"joueur": "TU GAGNES !", "ordi": "L'ORDI GAGNE !", "égalité": "EGALITE"}[gagnant]
                cv2.putText(frame, txt_gagnant, (15, h // 2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                if a_triche and time.time() - temps_resultat < 0.3:
                    afficher_popup_triche(random.choice(MESSAGES_TRICHE))
            cv2.putText(frame, "ESPACE: rejouer", (15, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.imshow("Arbitre de Chifoumi", frame)
        touche = cv2.waitKey(1) & 0xFF
        if touche == ord('q'):
            break
        elif touche == ord('r'):
            score_joueur, score_ordi = 0, 0
        elif touche == ord(' ') and etat in ("ATTENTE", "RESULTAT"):
            etat = "COMPTE_A_REBOURS"
            debut_compte = time.time()

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

# 🚀 Lance le jeu complet :
# jouer_chifoumi(proba_triche=0.3)


# ======================================================================
# Markdown cell 13
# ======================================================================
# ## 🎁 Pour aller plus loin
#
# Une fois le jeu de base fonctionnel, quelques pistes pour l'enrichir :
#
# - **Icônes au lieu de texte** : remplace les `cv2.putText("pierre"...)` par des petites images ✊✋✌️ superposées avec `cv2.addWeighted` ou un canal alpha — rendu beaucoup plus visuel.
# - **API moderne** : migrer de `mp.solutions.hands` vers `mediapipe.tasks.python.vision.HandLandmarker`, l'API recommandée par Google pour les nouveaux projets (légèrement plus verbeuse à initialiser, mais plus rapide et plus flexible sur le choix du modèle).
# - **Son** : un petit bruitage avec `playsound` ou `pygame.mixer` quand l'ordi triche.
# - **Historique** : logguer chaque manche (geste joueur, geste ordi, triche ou non, résultat) dans un CSV, pour ensuite tracer des stats (ex. taux de victoire du joueur selon que l'ordi a triché ou non).
# - **Meilleur des 5** : ajouter un mode match en plusieurs manches avec écran de victoire finale.
# - **Interface Tkinter** : envelopper la fenêtre OpenCV dans une vraie appli Tkinter (boutons, réglage du niveau de triche par un slider) — cohérent avec ce que tu as déjà fait sur *Tree Productivity Tracker*.

