# chifoumi-arbitre

**Chifoumi (Rock-Paper-Scissors) referee, played with your hand through the webcam.** 😇🤖

Show ✊ (pierre) / ✋ (feuille) / ✌️ (ciseaux) to your webcam. [MediaPipe](https://developers.google.com/mediapipe) Hands reads your gesture, and the computer opponent plays back — sometimes it peeks at your hand and cheats (and admits it with a popup).

## Setup

```bash
pip install -r requirements.txt
```

> **MediaPipe version matters.** This project uses the classic `mp.solutions.hands` API,
> which was **removed in MediaPipe 1.1.0**. `requirements.txt` pins `mediapipe==0.10.14`
> so the code keeps working. If you upgrade MediaPipe later, you must migrate to
> `mediapipe.tasks.python.vision.HandLandmarker`.

## Run

```bash
python chifoumi_arbitre.py
```

| Key | Action |
|---|---|
| `SPACE` | start a round — a 3-2-1-GO countdown plays, your gesture is read at GO |
| `R` | reset the score |
| `Q` | quit |

Requires a working webcam and a graphical desktop (OpenCV windows).

## Test the logic (no webcam)

```bash
python test_chifoumi.py
```

These tests check the referee rules, the gesture classifier (with fake landmarks), and
the computer's cheating behaviour — everything that does not need a camera.

## How it works

1. **Capture** — OpenCV reads the webcam, mirrored so it feels natural.
2. **Detect** — MediaPipe returns 21 hand landmarks (x, y normalized 0–1).
3. **Classify** — for index/middle/ring/pinky, a finger is "raised" when its tip landmark has a smaller `y` than its pip joint (`y` grows downward). The thumb is ignored.
   - 0 fingers up → `pierre` ✊
   - 4 fingers up → `feuille` ✋
   - index + middle only → `ciseaux` ✌️
   - anything else → not recognized
4. **Play** — with probability `proba_triche` the computer plays the move that beats yours (a cheated round is unwinnable, so your win rate at `proba_triche=0.3` is `0.7 × 1/3 = 0.233`, not `0.333`). Otherwise it plays uniformly at random.
5. **Loop** — a small state machine: `ATTENTE → COMPTE_A_REBOURS → RESULTAT → ATTENTE`.

## Files

- `chifoumi_arbitre.py` — the game
- `test_chifoumi.py` — logic tests (no webcam needed)
- `requirements.txt` — pinned dependencies
