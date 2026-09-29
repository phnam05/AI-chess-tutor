# Walkthrough change: measurements (24 Sep 2026, 15:16)

The author asked the coach to walk through the engine's line differently: say who
plays every move, give the idea before each move recommended to the student, go
only 1–2 moves deep, and adapt to the level (rules in `CLAUDE.md`, "How the coach
walks through a line"). The ideas come from `board_facts.py`, never from Gemini.

Each run is the 25-case set of `evaluate_faithfulness.py`, one Gemini call per case.
Every run below (and every July run) used a mistyped case 8, "Closed centre": Black
had no bishop on c8, so it was a bishop down (−4.79). Fixed 30 Sep 2026, 02:06;
runs from then on aren't comparable with these on that case.

| Version | What changed | Faithful (checker) | "followed by" |
|---|---|---|---|
| before (old coach, last commit 4b46dbb) | — | 23/25, 21/25 | 5, 6 |
| v1 | lines labelled by side, board facts, level cuts, new prompt | 23/25, 22/25 | 0, 0 |
| v2 | eval spelled out in words (v1 told Black −1.46 "favors you"); "likely reply" labels; idea-first and eval-apart rules; "captured next" fact | 25/25, 25/25 | 0, 0 |
| v3 (shipped) | chase fact names both squares ("the pawn on c2 to c3"), since "c3" was read as a pawn on c3 | 25/25, 25/25 | 0, 0 |
| v3 fresh run (25 Sep, 14:19) | no code change; new Gemini wording for the author's hand check | 25/25 | 0 |
| v4 (26 Sep, 03:59) | fixes from the hand check: "opens a line" only when useful (the author's rule), new facts (hanging piece, allows mate, centre, prepares), short damage control, wording rules | 25/25 | 0 |
| v4b (26 Sep, 04:06) | v4 + two fixes found by reading v4: a false "attacks the d2 pawn" fact; the idea-first pattern used on the student's own move | 25/25 | 0 |

Average length (before → v3): beginner 85 → 69 words, intermediate 105 → 87,
advanced 100 → 90. More but shorter sentences (one per move as the side changes).

**Read the 25/25 with care.** v2 and v3 were improved by reading these same 25
answers, so this set is no longer a fair test; and the checker only sees invented
moves and invented reasons for the eval. It cannot see an invented *idea* for a
move, or a misread board fact. Those are what `../walkthrough_audit.md` (the author's hand check: 13 fresh answers in full on a board page; builder in `board_page/`) is for. Known leftovers in v3, found by reading: "forced the
bishop to retreat" / "force the queen away" (the fact only says *attacks*; after
...a6 the bishop may also take on c6); "the c3 or a3 pawn" once at advanced;
"…so your move was a mistake" (a fact linked to the verdict); beginner notation in
square brackets. A clean number needs a fresh set (plan step 6: 100+ positions
from real games).

Files: `before_records_*.json`, `v1/v2/v3_records_*.json` (the 25 cases per run,
with facts and text), `v*_nb4.json` (the author's ...Nb4 example at all three
levels). Scripts: `compare.py` (the table above), `build_check.py` (builds the
hand-check file), `run_with_timeout.py` (runs a script with a 60 s timeout per
Gemini call: one baseline run hung for minutes on a single request), `nb4_run.py`.
Both "before" runs used the last commit's coach (4b46dbb): run 1 before any edits,
run 2 from an exported copy of that commit (a first run 2 had picked up
half-edited code and was thrown away).

v4/v4b also report `misnamed_pawns` ("the c3 pawn" with no pawn on c3), outside the rate: v3 fresh 1/28 answers, v4b 1/28.
