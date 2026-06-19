# Chess Tutor — an Explainable AI Coach

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-chess-tutor-phnam05.streamlit.app/)

An explainable-AI prototype that turns a chess engine's cold numbers into clear,
level-adapted coaching. It works three ways: **explain a position** (why the
engine's best move is good), **review a move** (grade a move you played and
explain what it did well or missed), and **play a full game** on a click-to-move
board where the coach reviews every move, for both sides, as you go. All adapt to
the player's level — beginner, intermediate, or advanced.

It's a small prototype of a larger idea: an AI that **explains its reasoning so
people learn from it**, rather than one that simply plays well.

## The core idea

A chess engine knows the best move — but it outputs a *number*, not an
explanation. This project builds the layer that bridges "the machine knows" and
"the human understands" — the subject of Explainable AI (XAI).

The key decision: **the engine decides the chess; the language model only
explains it.**

- **Stockfish** determines the best move, evaluation, and predicted line —
  treated as ground truth.
- **Gemini** is given those facts and asked *only* to explain them in natural
  language, adapted to the player's level. It never evaluates the position itself.

This separation is deliberate: language models are unreliable at actually playing
chess — they hallucinate moves and miscount material. Grounding every explanation
in the engine's verified output keeps the tutor faithful to correct chess while
staying easy to understand. The model is a translator, not a player.

## Ways to use it

The app has two top-level modes: **analyze a single position** or **play a full
game**.

**Analyze a position** offers two actions on a position you enter (as a FEN):

- **Explain this position** — shows the engine's best move and evaluation, and
  explains the reasoning behind it.
- **Review a move** — compares your move to the engine's best, labels its quality
  (*Best* down to *Blunder*), and coaches the difference: affirming a strong move,
  or gently explaining what a weaker one missed and what it cost. This turns a
  mistake into a targeted lesson — the heart of tutoring rather than mere analysis.

**Play a game** is an interactive, click-to-move board where you play both sides
and the coach reviews *every* move as it's made — labelling its quality, naming
the engine's preferred move when you missed it, and explaining the difference at
your chosen level. A running move log keeps each verdict on screen. It reuses the
exact same engine grading and explanation layer as *Review a move*, applied move
after move: a continuous lesson rather than one-shot analysis.

## How it works

```
Position (FEN)  [+ a played move, in Review mode]
      │
      ▼
python-chess ──► Stockfish        →  best move, evaluation (centipawns),
   (rules,         (analysis)          principal variation; and, in Review
    board)                              mode, the eval of the played move
      │
      ▼
Explanation layer (Gemini)        →  grounded, level-adapted coaching
      │                                (beginner / intermediate / advanced)
      ▼
Streamlit UI                      →  board + engine verdict + coaching
```

1. The user supplies a position (FEN) and a skill level, then asks for an
   explanation or selects a move to review.
2. `python-chess` validates the position and queries Stockfish; in Review mode it
   also evaluates the played move, so the two can be compared.
3. The analysis is packaged into a prompt for Gemini, with a system instruction
   that assigns a focused coach persona, forbids suggesting a different move or
   inventing evaluations, and adapts depth to the chosen level.
4. The board, the engine verdict (plus the move-quality label in Review mode),
   and the coaching are shown in a Streamlit page.

## Level adaptation

The same engine facts are explained differently per player:

- **Beginner** — one clear idea in plain words (development, king safety, simple
  threats); no jargon.
- **Intermediate** — plans, why a move creates pressure, typical responses.
- **Advanced** — pawn structure, the bishop pair, tempo, long-term imbalances.

## Tutoring, not lecturing

An early version produced long, encyclopedic answers — accurate, but
pedagogically poor: a wall of text does the learner's thinking for them. The
prompt was redesigned around a coaching persona that says less, targets the one
or two ideas that matter, and leaves room for the student to think. **Good
tutoring withholds and paces; it does not dump everything it knows.**

## Tech stack

- **Python**
- **Stockfish** — chess engine (off-the-shelf; not part of this project's
  contribution)
- **python-chess** — board representation, rules, FEN/PGN parsing, engine
  communication, and SVG board rendering for the analysis view
- **Pillow** — renders the clickable game board to a PNG (no system libraries, so
  it looks identical locally and on Streamlit Cloud); pairs with
  **streamlit-image-coordinates** to turn a click into a square
- **Google Gemini** (`google-genai` SDK) — the explanation layer
- **Streamlit** — web interface

## Running it locally

Requires Python 3.9+ and a free Google AI Studio API key.

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/chess-tutor.git
cd chess-tutor

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add the Stockfish engine — download from
#    https://stockfishchess.org/download/ and place it in this folder
#    as stockfish.exe (Windows)

# 5. Add your Gemini key at .streamlit/secrets.toml:
#    GOOGLE_API_KEY = "your_key_here"

# 6. Run
streamlit run app.py
```

On Streamlit Community Cloud, add the same `GOOGLE_API_KEY = "..."` line via the
app's **Settings → Secrets** panel instead of committing it. Both local and
deployed runs read it through `st.secrets`.

## Project structure

```
chess-tutor/
├── engine_analysis.py       # Stage 1: queries Stockfish → facts (the backbone)
├── move_review.py           # grades a played move against the engine's best
├── explainer.py             # Stage 2–3: grounded, level-adapted explanation layer
├── board_ui.py              # renders the clickable game board + maps click → square
├── app.py                   # Stage 4: Streamlit interface (analyze + play modes)
├── requirements.txt
├── .streamlit/secrets.toml  # your API key (not committed)
└── stockfish.exe            # the engine (not committed)
```

## Limitations

- Explanation quality depends on the language model; despite grounding, it can
  phrase an idea loosely. The architecture constrains *what* it can claim, not the
  polish of every sentence.
- The engine runs at a short think-time for responsiveness, so evaluations are
  strong but not exhaustive-depth.
- *Play a game* coaches move by move, but the coaching is still per-move: there's
  no conversation across the game and no memory between sessions (see Future
  directions).

## Future directions

- **Conversational dialogue.** Interactive play already exists (*Play a game*),
  but the coach speaks one move at a time. The next step is genuine back-and-forth
  — letting the student ask "why?" or "what if?" and having the coach respond in
  context across the whole game, closer to a real tutoring session.
- **A learner model.** Track a player's moves over time to infer *characteristic*
  weaknesses (e.g. missing tactical defenses) and shape explanations around the
  recurring gap. Inferring a learner's hidden understanding from behavior parallels
  inferring an agent's hidden type from its actions — a well-studied multi-agent
  problem, which makes this a principled next step.
- **Beyond board games.** The same architecture — ground an explanation in an
  authoritative source, then adapt it to the learner — transfers to any complex
  decision problem, including domains with *no* clean evaluation function (e.g.
  coaching a physical skill from video, like analysing badminton footage with pose
  estimation). That moves into computer vision while keeping the explainable-tutor
  goal intact.

## Why this project

A demonstration of explainable AI for complex decision-making: an AI that improves
human skill rather than replacing it. Chess was chosen for its clean, verifiable
engine and because the author understands it well enough to judge whether the
explanations are actually good — letting the work focus on the explanation and
adaptation layer, the transferable, research-relevant contribution.
