# Chess Tutor — an Explainable AI Coach

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-chess-tutor-phnam05.streamlit.app/)

<p align="center">
  <img src="images/hero.png" width="440" alt="The tutor's chess board, showing an Italian Game position with the last move highlighted">
</p>

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

The app is a single screen: an interactive, click-to-move board you play on — for
both sides — with the coach watching every move, plus a **Show best move** button
that reads whatever position is on the board.

**Play a move.** Click a piece (its legal moves dot the board) and move it, for
either colour. The coach grades the move the instant it's made — a quality label
(*Best* down to *Blunder*), the win-chance swing, and the engine's preferred move
when you missed it. Below the board, your move and the engine's pick are drawn out
side by side. For a weaker move the coaching leads with *why* it fails — walking
through the engine's refutation, the punishing reply you overlooked — before naming
the better move. This turns a mistake into a targeted lesson, the heart of tutoring
rather than mere analysis. A running move log keeps each verdict on screen, and the
written explanation for any move is one click away, at your chosen level.

<p align="center">
  <img src="images/play-game.png" width="360" alt="The interactive game board with the f1 bishop selected, its legal moves marked by dots, and the last move tinted">
</p>

<p align="center"><em>Click a piece and its legal moves dot the board; the last move stays tinted. The coach grades every move, for both sides, as you go.</em></p>

**Show best move.** At any point, ask the engine for the strongest move in the
current position — for whichever side is to move — and its evaluation, then have the
coach put the reasoning into words. It's a hint on demand, not a running spoiler.

<p align="center">
  <img src="images/analyze-position.svg" width="360" alt="A chess position with Black having played e5 and Nc6, White to move">
</p>

<p align="center"><em><strong>Show best move</strong> — for this position the engine's pick is <strong>Bb5</strong> (eval <strong>+0.32</strong>), which the coach then puts into words at your chosen level.</em></p>

**The before/after comparison.** Whenever a move is graded, the two boards beneath
show your move and the engine's best side by side — yours arrowed in the verdict's
colour, the engine's in green — so the difference is visible, not just described.

<table align="center"><tr>
  <td align="center"><img src="images/review-you.svg" width="300" alt="The board after Black plays the knight to f6, with a red arrow marking the move"><br><em>You played <strong>…Nf6</strong></em></td>
  <td align="center"><img src="images/review-best.svg" width="300" alt="The board after Black plays a pawn to g6, with a green arrow marking the engine's preferred move"><br><em>Engine's best, <strong>…g6</strong></em></td>
</tr></table>

<p align="center"><em>The natural-looking <strong>…Nf6</strong> even attacks the queen, yet it's a <strong>Blunder</strong>: it allows Scholar's mate (Qxf7#), and the win chance falls from <strong>54% to 3%</strong>. The coach contrasts it with the engine's <strong>…g6</strong>.</em></p>

**Set up any position.** The live position is shown beneath the board as a copyable
FEN; editing it and pressing *Load* jumps the board there, so you can study a
specific spot or replicate it in any other board or engine.

## How it works

```
Position (FEN)  [+ a played move, when you make one]
      │
      ▼
python-chess ──► Stockfish        →  best move, evaluation (centipawns),
   (rules,         (analysis)          principal variation; and, for a played
    board)                              move, its eval + refutation
      │
      ▼
Explanation layer (Gemini)        →  grounded, level-adapted coaching
      │                                (beginner / intermediate / advanced)
      ▼
Streamlit UI                      →  board + engine verdict + coaching
```

1. The user sets up a position (the live board, or a pasted FEN) and a skill
   level, then either plays a move or asks for the best move.
2. `python-chess` validates the position and queries Stockfish; when a move has
   been played it also evaluates that move and captures the engine's line *after*
   it — the refutation — so the two can be compared and the coach can explain how
   a weak move gets punished.
3. The analysis is packaged into a prompt for Gemini, with a system instruction
   that assigns a focused coach persona, forbids suggesting a different move or
   inventing evaluations, and adapts depth to the chosen level.
4. The board, the engine verdict (plus the move-quality label for a played move),
   and the coaching are shown in a Streamlit page.

## Level adaptation

The same engine facts are explained differently per player:

- **Beginner** — one clear idea in plain words (development, king safety, simple
  threats); no jargon.
- **Intermediate** — plans, why a move creates pressure, typical responses.
- **Advanced** — pawn structure, the bishop pair, tempo, long-term imbalances.


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
├── engine_pool.py           # one shared, persistent Stockfish process + engine discovery
├── board_ui.py              # renders the clickable game board + maps click → square
├── app.py                   # Stage 4: Streamlit interface (analyze + play modes)
├── requirements.txt
├── packages.txt             # apt packages for Streamlit Cloud (Stockfish + a chess font)
├── images/                  # README screenshots, generated from the app's own renderers
├── scripts/
│   └── make_readme_images.py  # regenerates images/ so they always match the live UI
├── .streamlit/secrets.toml  # your API key (not committed)
└── stockfish.exe            # the engine (not committed)
```

The README images are produced by `python scripts/make_readme_images.py` using the
app's actual rendering code — so they stay honest to what the UI shows rather than
being hand-made mock-ups.

## Limitations

- Explanation quality depends on the language model; despite grounding, it can
  phrase an idea loosely. The architecture constrains *what* it can claim, not the
  polish of every sentence.
- The engine searches to a bounded depth (with a short time cap) for
  responsiveness, so evaluations are strong but not exhaustive-depth.
- The board coaches move by move, but the coaching is still per-move: there's
  no conversation across the game and no memory between sessions (see Future
  directions).

## Future directions

- **Conversational dialogue.** Interactive play already exists (the live board),
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
