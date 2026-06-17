# Chess Tutor — an Explainable AI Coach
# Quickstart [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-chess-tutor-phnam05.streamlit.app/)

An explainable-AI prototype that turns a chess engine's cold numerical judgments
into clear, level-adapted coaching. It works two ways: **explain a position** —
given a board, it retrieves a strong engine's analysis and explains *why* the
best move is good; and **review a move** — given a move the player actually made,
it grades the move and explains, in plain language, what was good about it or
what it missed. Both are pitched to the player's level (beginner, intermediate,
or advanced).
 
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
 
## Two modes
 
**Explain this position.** The user supplies a position; the tutor shows the
engine's best move and evaluation, and explains the reasoning behind it.
 
**Review a move.** The user picks a move they played from the position. The tutor
compares it to the engine's best, labels its quality (from *Best* down to
*Blunder*), and coaches the player on the difference — affirming a strong move,
or gently explaining what a weaker one missed and what it cost. This turns a
mistake into a targeted lesson, which is the heart of tutoring rather than mere
analysis.
 
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
 
1. The user supplies a position (FEN) and chooses a skill level, then either
   asks for an explanation of the position or selects a move to have reviewed.
2. `python-chess` validates the position and queries Stockfish for the analysis.
   In Review mode it also evaluates the player's chosen move, so the two can be
   compared.
3. The analysis is packaged into a prompt and sent to Gemini, with a system
   instruction that (a) assigns a focused chess-coach persona, (b) forbids the
   model from suggesting a different move or inventing evaluations, and (c)
   adapts depth to the chosen level.
4. The board, the engine verdict (and, in Review mode, the move-quality label),
   and the coaching explanation are shown in a Streamlit page.
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
 
# 5. Add your Gemini API key as a Streamlit secret
# create a file at: .streamlit/secrets.toml  containing:
# GOOGLE_API_KEY = "your_key_here"
 
# 6. Run
streamlit run app.py
```
 
When deployed on Streamlit Community Cloud, the key is not committed to the repo:
it is added through the app's **Settings → Secrets** panel, using the same
`GOOGLE_API_KEY = "..."` line. Both local and deployed runs read it via
`st.secrets`.
 
## Project structure
 
```
chess-tutor/
├── engine_analysis.py       # Stage 1: queries Stockfish → facts (the backbone)
├── move_review.py           # grades a played move against the engine's best
├── explainer.py             # Stage 2–3: grounded, level-adapted explanation layer
├── app.py                   # Stage 4: Streamlit interface
├── requirements.txt
├── .streamlit/secrets.toml  # your API key (not committed)
└── stockfish.exe            # the engine (not committed)
```
 
## Limitations
 
- Explanation quality depends on the language model; despite grounding, it can
  occasionally phrase an idea loosely. The architecture constrains *what* it can
  claim, not the polish of every sentence.
- The engine is run at a short think-time for responsiveness, so evaluations are
  strong but not exhaustive-depth.
- The tutor works one position (or one move) at a time rather than following a
  continuous game move-by-move (see Future directions).
## Future directions
 
- **Interactive play and dialogue.** Let the user make a series of moves and
  have the coach respond across the whole game, building a back-and-forth lesson
  — closer to a real tutoring session — rather than reviewing positions and
  moves in isolation.
- **A learner model.** Track a player's moves over time to infer *characteristic*
  weaknesses (e.g. a tendency to miss tactical defenses), and shape explanations
  around the recurring gap rather than the single move. Inferring a learner's
  hidden understanding from observed behavior is structurally similar to
  inferring an agent's hidden type from its actions — a well-studied problem in
  multi-agent systems — which makes this a principled, not just convenient, next
  step.
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
 
