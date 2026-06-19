# CLAUDE.md

Guidance for AI coding agents (and humans) working in this repo. Read this before
making changes — it captures the *one architectural invariant* that the whole
project depends on, plus the conventions and gotchas that aren't obvious from the
code alone.

## What this is

An explainable-AI chess tutor. It takes a position (and optionally a move the
player made), gets a strong engine's analysis, and turns that analysis into
short, level-adapted coaching. See `README.md` for the full narrative and the
design rationale; this file is the operational map.

## The invariant — do not break this

**The engine decides the chess; the language model only explains it.**

- Stockfish is the *single source of truth* for anything factual: the best move,
  the evaluation, the principal variation, the move's quality label.
- The LLM (Gemini, in `explainer.py`) is a **translator**, never a judge. It is
  given engine facts and asked only to phrase them. It must never evaluate a
  position, pick a move, or invent a tactic/eval that the engine didn't produce.

This separation is the entire point of the project (LLMs hallucinate moves and
miscount material; the architecture routes around that). When adding a feature,
ask: *is this a chess fact?* → it comes from the engine. *Is this phrasing a fact
for a human?* → that's the LLM's job. Never blur the two. The system prompt in
`explainer.py` enforces this at the model level ("do NOT suggest a different
move… do NOT invent tactics or evaluations"); keep those guardrails intact.

## Pipeline / file map

```
app.py              Streamlit UI — the only entry point. Orchestrates the stages.
  │
  ├─ engine_analysis.py   Stage 1: FEN → engine facts (best move, eval, PV).
  ├─ move_review.py       Grades a *played* move vs. the engine's best.
  ├─ explainer.py         Stage 2: engine facts → grounded, level-adapted prose.
  ├─ engine_pool.py       Shared persistent Stockfish handle + engine discovery.
  └─ board_ui.py          Pillow board for the interactive click-to-move UI.
```

Each file is one stage of a pipeline and is meant to stay independently runnable
(each has a `__main__` self-test). Keep that property — it's how you debug a stage
in isolation without the UI or the other stages.

## How move grading works (the non-obvious part)

Moves are graded on **win-probability drop**, not raw centipawn loss
(`move_review.py`). `win_chance()` maps a centipawn eval to a 0–100 win % using
the fitted logistic curve Lichess/chess.com use. Grading on the win-% drop makes
the same eval swing count for *more* in a close game than in a lopsided one — that
is deliberate and correct; don't "simplify" it back to centipawns. `classify_move`
turns the drop into the labels Best / Excellent / Good / Inaccuracy / Mistake /
Blunder, which `app.py`'s `QUALITY` dict maps to colors and one-line glosses.

`review_move` also returns a `refutation`: the engine's PV *after* the played
move (SAN, opponent to move first). For a weak move this is the punishment line —
the concrete *why was my move wrong* — and `explainer.py` leads the coaching with
it instead of just naming the better move. It's an engine fact like any other, so
the explainer narrates it; it must never invent its own refutation. This is the
invariant's textbook shape: a new chess fact comes from the engine first, and only
then does the LLM phrase it.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Requirements (out of the repo's control, intentionally not committed):
- **Stockfish binary.** Locally: put `stockfish.exe` next to the source (Windows)
  or have `stockfish` on PATH. On Streamlit Cloud: `packages.txt` installs it via
  apt. `find_engine()` in `engine_pool.py` resolves all these cases — it's now the
  single source of engine discovery (it used to be copy-pasted into both stage
  files and the copies had drifted: one returned a bare relative `stockfish.exe`
  that won't launch as a subprocess on Windows).
- **Gemini API key** as `GOOGLE_API_KEY`. Read via `st.secrets` first, then the
  environment / `.env` (see the guarded lookup at the top of `explainer.py`).
  Never hardcode or commit it — `.gitignore` already excludes `.env` and
  `.streamlit/secrets.toml`.

Stage self-tests (no UI needed):
```bash
python engine_analysis.py   # prints facts for a sample FEN
python move_review.py        # grades a good move and a bad one
python explainer.py          # explains a sample position at all 3 levels
```

## Conventions & gotchas

- **The LLM model id lives in `explainer.py`** (`gemini-3.1-flash-lite`). That is
  the canonical one used by the app. `test_engine.py` and `test_llm.py` are
  throwaway smoke scripts from early bring-up, *not* a test suite — don't treat
  them as the source of truth (e.g. `test_llm.py` pins an older model).
- **Scores are always taken from the moving side's POV** via `.pov(board.turn)`.
  After a move is pushed it's the opponent's turn, so `move_review.py` flips the
  post-move score back to the mover's perspective. Watch this whenever you touch
  eval math — a sign error here silently corrupts every grade.
- **Mate scores** aren't centipawns. `engine_analysis.py` renders them as text
  ("Mate in N"); `move_review.py` substitutes ±10000 so comparisons still work.
- **Coaching is deliberately short.** The persona in `explainer.py` withholds and
  paces on purpose (good tutoring ≠ an info dump). Don't "improve" it into longer,
  exhaustive, bulleted answers — brevity is a feature, enforced by the prompt.
- **`app.py` renders verdict blocks as raw HTML** (`unsafe_allow_html=True`) for
  styling. The metrics block is guarded against a stale/old `review` dict
  (missing keys degrade gracefully). Preserve that guard when changing the
  review payload — Streamlit Cloud can cache an old module across a deploy.
- **Engine lifecycle:** one persistent `SimpleEngine` is shared across all calls —
  created lazily, reused, lock-guarded, closed at exit (`engine_pool.py`). The old
  design spawned and quit an engine *per request*, which cost a full process launch
  every call (~2.4s to grade one move); reuse drops that to ~0.1s. Analyses are
  **depth-limited** (depth 15, 1s cap), not time-limited: still far stronger than
  any student — so the engine is still the source of truth — but the before/after
  evals are searched to the same depth, which keeps them comparable for grading.

## When extending

- New factual capability → add it to the engine stage and surface it as data;
  only then let the explainer phrase it.
- New explanation behavior → it's a prompt/persona change in `explainer.py`;
  it must not introduce any new chess *claim* the engine didn't supply.
- Keep changes minimal and match the surrounding style: small files, plain
  functions, comments that explain *why* (as the existing code does), no
  framework or abstraction the prototype doesn't need.

## Out of scope (by design, for now)

No multi-turn game state, no learner model, no persistence, no automated test
suite. These are noted as future directions in the README — don't assume they
exist.
