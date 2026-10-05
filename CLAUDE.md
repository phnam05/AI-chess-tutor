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

## Research focus (the author, 2026-10-01 21:55)

Only paper 1's question: is an explanation **correct and relevant**. Paper
2's, meaningful at the player's level (level guessing, Maia, a model of the
player), gets no work until the author says so. **The player model is
removed** (the author, 2026-10-05 16:22: "remove anything that's related to the
player model. Right now only focus on explanation"): the learner model, the
"Your patterns" panel, saved games and the simulations are gone from `main`.
They are kept on the local branch `paper2-player-model`, with the old to-do
list. Still in the app: the bot opponent (a way to get positions to explain)
and the 3 explanation levels (part of the frozen version 1 coach). Before
proposing anything, ask whether it helps measure or improve correct +
relevant. The plan is `TODO.md`, section 1.

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
  ├─ board_facts.py       What a human would *notice* about each move (attacks,
  │                       chases, castling…), computed with python-chess: the
  │                       coach's only source for the idea behind a move.
  ├─ engine_pool.py       Shared persistent Stockfish handle + engine discovery,
  │                       and a separate weak Stockfish that plays the bot.
  └─ board_ui.py          Pillow board for the interactive click-to-move UI.

Research scripts (run by hand, not imported by the app):
  faithfulness.py / evaluate_faithfulness.py / validate_checker.py / build_audit.py
                          Steps 1–2: check, measure and audit the coach's faithfulness.
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

For a weak move (Inaccuracy / Mistake / Blunder), `classify_mistake` also names
its **kind** — `allowed_mate`, `missed_mate`, `lost_material`, `missed_material`,
or `positional` — by comparing the engine's best line (`best_line`, kept in the
review) with the line after the played move, on mate and a plain 1/3/3/5/9
material count. It's the same kind of fact as the label: read off engine output,
never guessed. `positional` deliberately doesn't say *which* positional thing
went wrong, because the engine doesn't say. The coach uses the kind to keep
its walk-through short after a move that lost material or allowed mate (see
`cut_line`'s `damage` below).

**Every number needs a source** (the author, 2026-09-30 10:52, about the
since-removed learner model: "where does the numbers like 10 moves, 80%, 3
times come from? … You cant just pull up those numbers"). Never present a
hand-picked constant as settled or research-backed: cite it, measure it, or say
"hand-picked for now" wherever it's explained.

## How the coach walks through a line (author's rules, 2026-09-24 14:27)

The author's requirements for every explanation that narrates an engine line
(`explain_move` *and* `explain_position`). The target style, in the author's
words: "Moving your knight to b4… on b4 it can easily be chased away with c3 or
a3. Your opponent's strongest answer is to castle (O-O), getting their king
safe. Now look at White's bishop on b5… a natural idea is to challenge it
directly. That's why your best reply is ...a6, asking the bishop to decide
where it wants to go."

1. Every move says **who plays it** ("your opponent plays…", "your best reply
   is…"). Switch the subject whenever the side to move switches; never chain two
   sides' moves with "followed by".
2. For a weak move, first say what it **changed in the position** (what it gave
   up or allowed), not only that the evaluation dropped.
3. For every move recommended to the player, give the **idea before the move**:
   the problem it solves, or the feature a human would notice that points to it.
4. Go only **1–2 moves deep** unless each further move has a human-understandable
   reason; stop there instead of listing more moves.
5. **Adapt to the level:** concepts for weaker players, concrete lines for
   stronger ones.

How this must respect the invariant: the *reasons* in rules 2–3 are chess facts,
so they come from code (board facts computed with python-chess, or the engine's
own line), never from the LLM's chess knowledge. A board fact can be true and
still be the wrong reason: after ...Nb4 in
`r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3` the knight
no longer defends e5, but 4.Nxe5? Qg5 leaves White worse. So "you can lose X" is
stated only when the engine's line actually takes X. The engine gives no plans,
so "stop at the plan" means: stop at the last move that has a reason.

How it's built — each rule is enforced in code where it can be, not left to the
prompt:
- `board_facts.py` computes each move's facts (captures / takes back, checks,
  castling, bringing a piece out, stepping out of a chase (by a cheaper piece,
  or by any piece when nothing defended it), new attacks on
  something worth more or undefended, "a pawn can chase it next move" — naming
  both squares, "the pawn on c2 to c3", since "c3" alone was read as a pawn on
  c3 — "the very next move in the line captures it", opening a line for another
  piece, and "no longer defends X" *only* if the line then captures X). `move_review` stores them as `played_facts`, `line_steps`,
  `best_facts`; `analyze_position` as `line_steps`. An attack is stated, never
  that it *wins* something — that's only said when the line shows the capture.
- `explainer.py` labels every step in code ("Opponent (White), likely reply:
  O-O", "Student (Black), best move: ...c6" — "likely", because the line is a
  forecast), writes Black's moves with "...", and hands Gemini the facts per
  move. It also spells out who each eval favours (`_eval_words`): given "-1.46
  (from their perspective)", Gemini told Black it "favors you". The prompt says
  a move's idea may come *only* from its facts or from what the line shows next
  (no rules of thumb); a move with no facts gets no reason; the student's moves
  are written idea-first, move-last; the eval stays in its own sentence, never
  linked to a move or fact.
- `board_facts.cut_line` decides depth by level (`LINE_PLIES`: beginner 2
  half-moves, intermediate 3, advanced 4), finishes a same-square exchange but
  never starts a new one past the cut, and stops before any of the student's
  moves that has no fact (no honest idea to give it). After a move that lost
  material or allowed mate (`damage=True`), it keeps only the opponent's reply
  and the student's one answer, which the coach gives in one clause as damage
  control (author, 2026-09-26 00:44: "could just be shorter on how to minimize the
  damage").
- **Which facts are worth saying (author's hand check, 2026-09-25 15:48 and 2026-09-26 00:44).** A true
  fact can still be useless: 6.Be3 frees c1 and b1 for the queen. "Opens a line
  for X" is stated only if (1) through the opened line X now attacks something
  worth more or undefended, or (2) *in the opening* (that side still has a
  knight or bishop on its starting square) X gains a square off its home rank,
  a way into the game (nobody can say yet when that line will be used), or
  (3) the engine's line later moves X along it. The author rejected both a fixed
  "ignore the back rank" rule and a "now or later only" rule; don't bring either
  back. Other facts added from that check: a piece left where nothing defends
  it and the next move takes it ("hanging", not said for a trade); "allows
  checkmate next move", naming the pieces that hit the mating square; "puts a
  pawn in the centre"; "prepares d4" (a pawn move covering the square of the
  side's next, non-capturing move); an attack on an equal, defended piece only
  when the line's next move steps it away (7...Ng4 8.Bd2). Attack facts no
  longer say "which is worth less" (the coach copied it word for word).
- The move the student *should have played instead* (engine best) is passed
  separately from their *best reply now* (in the line), so the two aren't mixed.
- `faithfulness.py` counts squares/moves named in the facts as grounded mentions
  (`board_fact_tokens`), but the eval-cause check still accepts only engine moves
  as an anchor, so its strictness is unchanged.

Measured (`walkthrough_eval/README.md`): checker 44/50 before → 50/50 after,
"followed by" 11 → 0. But the 25 cases were used to develop the change, and the
checker can't see an invented *idea* or a misread fact, so the author's hand
check (`walkthrough_audit.md`, done on a board page: full answers, a board you
can step through, one Yes/No each) is the real test. The prompt now also says:
an attack is only an attack (no "forces"), name a pawn by the square it stands
on, never guess what the student "wants", say facts in plain words. The checker
reports `misnamed_pawns` ("the c3 pawn" with no pawn on c3) separately, outside
`ok`, so the faithful rate stays comparable.

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
  `.streamlit/secrets.toml`. With no key the app still runs (engine, grading,
  board); only the coach reports that the key is missing.

`requirements.txt` is **pinned** to the versions the app is run and tested with.
Streamlit Cloud reinstalls dependencies on every deploy, so unpinned it silently
picked up whatever was newest (by 2026-09 the Gemini SDK had started refusing a
missing key at import, which would crash the whole app). Upgrade deliberately:
bump a pin, run the app, then push.

Stage self-tests (no UI needed):
```bash
python engine_analysis.py   # prints facts for a sample FEN
python move_review.py        # grades a good move and a bad one
python board_facts.py        # board facts + level cuts for the ...Nb4 example (no engine)
python explainer.py          # explains a sample position at all 3 levels
```

## Conventions & gotchas

- **The LLM model id lives in `explainer.py`** (`MODEL = "gemini-3.1-flash-lite"`).
  That is the canonical one used by the app. `test_engine.py` and `test_llm.py` are
  throwaway smoke scripts from early bring-up, *not* a test suite — don't treat
  them as the source of truth (e.g. `test_llm.py` pins an older model).
- **Gemini calls retry, and failures say why.** The client retries transient
  errors (429 quota, 5xx overload) 3 times with short waits — the SDK does *not*
  retry by default, and one blip once broke a live demo. Each try also has a
  20 s limit (`_TIMEOUT_S`): the SDK sets none, and one stuck request froze a
  measurement run for minutes. The SDK retries a timed-out try too, so the
  worst wait is ~1 minute. `describe_coach_error`
  turns a failure into a plain reason (quota / busy / timeout / bad key / retired model);
  the app shows it and keeps a "Try again" button. Never go back to one
  catch-all "check GOOGLE_API_KEY" message — it hid the real cause.
- **The exact prompt is visible in the app** (the author, 2026-10-03 01:52,
  for research and debugging): `explain_move` / `explain_position` take an
  optional `prompt_out` dict, filled with the model, level, system instruction
  and facts message *before* the call (so a failed call still shows it);
  `app.py`'s `_render_prompt` shows it in a collapsed "Prompt sent to Gemini"
  box. Keep it a caller-owned dict, not a module global: the online app is one
  process shared by all visitors. Build the system instruction only through
  `_system(level)`, so what's shown is what's sent.
- **Scores are always taken from the moving side's POV** via `.pov(board.turn)`.
  After a move is pushed it's the opponent's turn, so `move_review.py` flips the
  post-move score back to the mover's perspective. Watch this whenever you touch
  eval math — a sign error here silently corrupts every grade.
- **Mate scores** aren't centipawns. `engine_analysis.py` renders them as text
  ("Mate in N"); `move_review.py` substitutes ±10000 so comparisons still work.
  Take a mate's sign by comparing with `Cp(0)`, never `mate() > 0`: the side that
  just delivered mate gets `MateGiven`, whose `mate()` is 0 (that bug once graded
  a mating move that wasn't the engine's pick a Blunder).
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
  **depth-limited** (depth 15, no time cap), not time-limited: still far stronger
  than any student — so the engine is still the source of truth — but the
  before/after evals are searched to the same depth, which keeps them comparable
  for grading. There is deliberately no time cap: with one, a busier laptop
  searched shallower and gave a different answer for the same position. Together
  with one thread and a fresh hash per call, depth-only makes the engine
  deterministic (`engine_pool.analyse`).
- **The bot opponent is a second Stockfish process** (`engine_pool.bot_move`,
  2026-09-30 11:38). Never set `Skill Level` on the shared grading engine: it
  would weaken every verdict. The bot is time-limited (0.3 s, hand-picked) and
  random on purpose (below Skill 20 Stockfish picks among its top few moves);
  none of the grader's determinism rules apply to it. Its moves are graded like
  any other (marked `bot=True`), and the coach's desk keeps the student's own
  move when the bot has just replied.
  Undo takes back the bot's reply and the student's move together.
- **The engine's line (PV) is a forecast, not a promise.** In a fixed-depth
  search only the first move gets the full depth; each later move in the line was
  effectively searched shallower. So re-analysing a position you reached *by
  following the line* can prefer a different, near-equal move (observed: a PV
  said the reply to Be3 is Qd5, but a fresh search after playing Be3 picks Qa5+ —
  the two are ~0.2 pawns apart, and both answers are individually deterministic).
  Every engine and analysis site behaves this way. Do **not** "fix" it with a PV
  cache — that would serve staler, shallower answers than a fresh search.
  Relatedly, `render_line` (`engine_analysis.py`) never cuts a displayed line in
  the middle of a capture exchange: a line truncated at "…Qxf4" looked like a
  hung queen when the very next ply was the Bxf4 recapture.

## Development diary

`DEV_DIARY.md` is the project's running story, written for the author: plain
words, no unexplained jargon. At the end of **every** working session, add an
entry at the end of Part 3 and refresh "Where the project stands".
Record honest results, including what failed or was reverted.

**Date and time on everything** (the author, 2026-09-26 04:03: "i want a clear
timestamp too, not just the date"). Every diary heading, both "Where the
project stands" blocks, `TODO.md`'s "Last updated" and "(Done …)" notes,
`lab_notes.md` entries, dated notes in this file and the "Generated on" line
of reports carry the date *and* the time: 24-hour clock, Vietnam time (UTC+7),
e.g. "26 Sep, 04:06". Read the time off the clock as you write (`Get-Date` /
`date`); never guess it, and don't write "(later)" or "(night)" instead.
Older entries from 23 Sep on got their times from the session logs (when
each was written); the June–July ones keep only their dates (no logs left).

**Keep it short** (the author asked, 2026-09-24 15:20: the 1,050-line version was a
hassle to read). An entry is a few bullets: **Did** → **Problems → fixes** →
**End state** (or the result). Only what the author needs to follow the story,
not every detail. To-dos live in `TODO.md` only; don't copy them into either
diary.

**`DEV_DIARY_full.md` is the long version, and it is kept up to date too**
(the author, 2026-09-26 03:55: "so in case I want to read deeper"). Every session
adds its entry to both: a few bullets in `DEV_DIARY.md`, the full story in
`DEV_DIARY_full.md` (what was done and why → difficulties and how they were
solved → state at end of day, with the numbers and file names). Refresh both
"Where the project stands" blocks. Same story in both: the long one only adds
detail, never a different claim.

**The GitHub repo is public.** Notes from the lab's private chat (the
supervisor's remarks, labmates' unpublished work) go in `lab_notes.md`, never
in the diary or `TODO.md`; point to it instead. `lab_notes.md`,
`DEV_DIARY_full.md` and `PROJECT_STORY.md`/`.html` (they quote the chat) are
git-ignored, and so is the chat export itself (`NESPeD-Lab*.html`, it holds
personal data). `PROJECT_STORY.md` is the whole project told as one story
(written 2026-09-29 17:08, for when the author feels lost), and
`PROJECT_STORY.html` the same story with step-through boards (2026-09-30
01:17). Since 2026-09-30 02:30 both are kept up to date along with the
diaries (the author: "dont forget the story and diary too so i can keep
track"): each session that changes the story adds to its timeline, the
matching chapter and "Where you are right now", in both files. When the
author asks a question about the project, it goes in the story's "Your
questions, answered" part (since 2026-09-30 14:47: "make a part where i asked
a question and you provide the explanation"): the question in their own
words with its time, then the answer that made sense to them, kept short.

## When extending

- New factual capability → add it to the engine stage and surface it as data;
  only then let the explainer phrase it.
- New explanation behavior → it's a prompt/persona change in `explainer.py`;
  it must not introduce any new chess *claim* the engine didn't supply.
- Keep changes minimal and match the surrounding style: small files, plain
  functions, comments that explain *why* (as the existing code does), no
  framework or abstraction the prototype doesn't need.

## Out of scope (by design, for now)

No conversation with the coach across moves, no persistence between sessions,
no model of the player (removed 2026-10-05; see "Research focus"), no
automated test suite (only the per-stage self-tests).
