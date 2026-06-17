# Chess Tutor — an Explainable AI Coach
# Quickstart [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-chess-tutor-phnam05.streamlit.app/)
An explainable-AI prototype that turns a chess engine's cold numerical judgments
into clear, level-adapted coaching. Given a position, it retrieves a strong
engine's analysis and explains *why* the best move is good — in language pitched
to the player's level (beginner, intermediate, or advanced).

This is a small prototype of a more general idea: an AI that **explains its
reasoning so people learn from it**, rather than one that simply plays well.

## The core idea

A chess engine already knows the best move — but it outputs a *number*, not an
explanation a human can learn from. This project builds the layer that bridges
"the machine knows" and "the human understands." That bridge is the subject of
Explainable AI (XAI).

The key design decision: **the engine decides the chess; the language model only
explains it.**

- **Stockfish** (a strong open-source engine) determines the best move, the
  evaluation, and the predicted line. This is treated as ground truth.
- **A large language model (Gemini)** is given those facts and asked *only* to
  explain them in natural language, adapted to the player's level. It never
  evaluates the position itself.

This separation is deliberate. Language models are unreliable at actually
playing chess — they hallucinate moves and miscount material. By never asking
the model to judge the position, and instead grounding every explanation in the
engine's verified output, the tutor stays faithful to correct chess while
remaining easy to understand. The model is a translator, not a player.

## How it works

```
Position (FEN)
      │
      ▼
python-chess ──► Stockfish        →  best move, evaluation (centipawns),
   (rules,         (analysis)          principal variation
    board)
      │
      ▼
Explanation layer (Gemini)        →  grounded, level-adapted coaching
      │                                (beginner / intermediate / advanced)
      ▼
Streamlit UI                      →  board + engine verdict + coaching
```

1. The user supplies a position (FEN) and chooses a skill level.
2. `python-chess` validates it and queries Stockfish for the analysis.
3. The analysis is packaged into a prompt and sent to Gemini, with a system
   instruction that (a) assigns a focused chess-coach persona, (b) forbids the
   model from suggesting a different move or inventing evaluations, and (c)
   adapts depth to the chosen level.
4. The board and the coaching explanation are shown in a Streamlit page.

## Level adaptation

The same engine facts are explained differently depending on the player:

- **Beginner** — one clear idea in plain words (development, king safety, simple
  threats); no jargon.
- **Intermediate** — plans, why a move creates pressure, typical responses.
- **Advanced** — pawn structure, the bishop pair, tempo, long-term imbalances.

This directly targets the goal of *adapting explanations to the player's
progress level*.

## A note on tutoring, not lecturing

An early version produced long, encyclopedic answers — accurate, but
pedagogically poor: a wall of text does the learner's thinking for them. The
prompt was redesigned around a coaching persona that says less, targets the one
or two ideas that matter, and leaves room for the student to think. **Good
tutoring withholds and paces; it does not dump everything it knows.** This is a
small but real lesson about explanation as a learning aid rather than an
information dump.

## Tech stack

- **Python**
- **Stockfish** — chess engine (off-the-shelf; not part of this project's
  contribution)
- **python-chess** — board representation, rules, FEN/PGN parsing, engine
  communication, board rendering
- **Google Gemini** (`google-genai` SDK) — the explanation layer
- **Streamlit** — web interface

## Running it locally

You will need Python 3.9+ and a free Google AI Studio API key.

```bash
# 1. Clone and enter the project
git clone https://github.com/YOUR_USERNAME/chess-tutor.git
cd chess-tutor

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add the Stockfish engine
# Download from https://stockfishchess.org/download/
# place the executable in this folder, named: stockfish.exe (Windows)

# 5. Add your Gemini API key
# create a file named .env containing:
# GOOGLE_API_KEY=your_key_here

# 6. Run
streamlit run app.py
```

## Project structure

```
chess-tutor/
├── engine_analysis.py   # Stage 1: queries Stockfish → facts (the backbone)
├── explainer.py         # Stage 2–3: grounded, level-adapted explanation layer
├── app.py               # Stage 4: Streamlit interface
├── requirements.txt
├── .env                 # your API key (not committed)
└── stockfish.exe        # the engine (not committed)
```

## Limitations

- Explanation quality depends on the language model; despite grounding, it can
  occasionally phrase an idea loosely. The architecture constrains *what* it can
  claim, not the polish of every sentence.
- The engine is run at a short think-time for responsiveness, so evaluations are
  strong but not exhaustive-depth.
- Currently single-position: the user analyses one position at a time rather
  than playing an interactive game (see Future directions).

## Future directions

- **Interactive play and dialogue.** Let the user make a series of moves and
  have the coach respond move-by-move, building a back-and-forth lesson — closer
  to a real tutoring session.
- **Error identification.** When a player's move differs from the engine's best,
  explain specifically what was missed and what it costs — turning mistakes into
  targeted lessons.
- **Beyond board games, and beyond clean engines.** The same architecture —
  ground an explanation in an authoritative source, then adapt it to the learner
  — transfers to any complex decision problem. A natural and harder next step is
  a domain with *no* clean evaluation function, such as coaching a physical skill
  from video (e.g. analysing badminton footage with pose estimation to identify
  technique errors). That moves the problem into computer vision and video
  analysis while keeping the explainable-tutor goal intact.

## Why this project

Built as a demonstration of explainable AI for complex decision-making: an AI
that improves human skill rather than replacing it. Chess was chosen as the
substrate because it offers a clean, verifiable engine and a domain the author
understands well enough to judge whether the explanations are actually good —
letting the work focus on the explanation and adaptation layer, which is the
transferable, research-relevant contribution.
