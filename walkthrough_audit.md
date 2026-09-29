# Walkthrough hand check

**Do it here:** https://claude.ai/artifact/RXVx2NjAcuirnqbXqKoqL4 (now showing **round 2**, 26 Sep, 04:09; answered by 29 Sep, 14:05)

13 freshly generated coach answers, shown in full (your ...Nb4 example at all 3
levels + 10 cases), each with a board you can step through move by move, the
engine's facts, and one question: "Any problem in this answer?" (Yes = something
needs fixing). Answers save on the page; Claude reads them and writes them below.

- Fresh run: `walkthrough_eval/v3_fresh_records.json` (25 cases, checker 25/25) and
  `walkthrough_eval/v3_fresh_nb4.json`. Same code as v3; only Gemini's wording is new.
- Claude's own notes (the red underlines on the page): `walkthrough_eval/board_page/notes_fresh.json`.
- Rebuild the page: `PYTHONPATH=. .venv/Scripts/python.exe walkthrough_eval/board_page/build_full_check.py
  walkthrough_eval/v3_fresh_records.json walkthrough_eval/v3_fresh_nb4.json
  walkthrough_eval/board_page/notes_fresh.json <out.html>`
- Older sheets: `walkthrough_eval/audit_full.md` (first run, old vs new) and
  `walkthrough_eval/audit_9_questions_run1.md` (9 questions on the first run).

## Your answers (25 Sep 2026, 15:48, fresh run)

**10 of 13 answers have a problem** (Yes). Fine as they are: 1.h4, Ruy Lopez, Queen's Gambit Declined.

| # | Case | Problem? | Your note |
|---|---|---|---|
| 1 | ...Nb4, beginner | Yes | Where does "c3 or a3" come from? White never plays it in the engine's line (true, though). Should say more about *why* ...a6 (attacking the bishop) is better than the knight move: "that's what the players need." |
| 2 | ...Nb4, intermediate | Yes | Should say the pawns are on c2 and a2 (push c2 to c3), not "the c3 or a3 pawn". Same concern as 1. |
| 3 | ...Nb4, advanced | Yes | Again: "c3 or a3" isn't in the engine's line, so where does it come from? |
| 4 | ...Be7, intermediate | Yes | (no note) |
| 5 | ...Nf6??, beginner | Yes | Should focus on the attack on f7. |
| 6 | ...Nxe4?, intermediate | Yes | "you should aim to capture the pawn on f2 and attack their queen": but why? Doesn't make sense ("hard to come up with a reason, it's just the engine's line"). |
| 7 | 1.a4, beginner | Yes | Should just say e4/e5 are usually played to claim the centre. Otherwise fine. |
| 8 | 1.h4, beginner | No | |
| 9 | 3.Ng5??, advanced | Yes | Simple: the knight went to a square no piece defends and can be taken for free ("hung" it). Don't go deeper after that: when you hang a piece there's not much more to discuss. Then say the good developing move was the bishop. |
| 10 | Ruy Lopez, beginner | No | |
| 11 | Italian, intermediate | Yes | Don't assume ("Since you want to open a line for your queen"): just say pushing the pawn makes room for the queen. "attacking their bishop on c5 with a pawn that is worth less": "you challenge the bishop by pushing the pawn" is enough. |
| 12 | Najdorf, advanced | Yes | "Be3 also opens a line for your queen": not really; it only frees c1 (and b1), useless squares. The queen already had lines. |
| 13 | QGD, intermediate | No | |

## Round 2 (26 Sep 2026, 04:09, after the fixes)

The same 13 cases after the fixes from round 1 (rules in `CLAUDE.md`, "Which facts are worth
saying"). Each answer shows what you said in round 1. Run: `walkthrough_eval/v4b_records_1.json`
+ `v4b_nb4.json` (checker 25/25; misnamed pawns 0/25 in the 25 cases, 1/3 in the ...Nb4 answers).
Claude's notes: `walkthrough_eval/board_page/notes_v4b.json`. Answers save to the page's
`round2` store.

### Your answers (round 2)

Given 28 Sep, 17:36 – 29 Sep, 14:05; read 29 Sep, 14:06.

**9 of 13 answers still have a problem** (round 1: 10 of 13). Fine now: ...Nb4 intermediate,
1.a4, 1.h4, Ruy Lopez. New problem: QGD (one word).

| # | Case | Problem? round 1 → 2 | Your note (round 2) |
|---|---|---|---|
| 1 | ...Nb4, beginner | Yes → Yes | Says very little about how and why ...Nb4 is bad. Maybe base it on development: you lose time ("not sure, but think about it"). The knight can be chased by White's pawns, but in the line White never does it. |
| 2 | ...Nb4, intermediate | Yes → **No** | |
| 3 | ...Nb4, advanced | Yes → Yes | Pushing the pawn doesn't really open much space for the rook. |
| 4 | ...Be7, intermediate | Yes → Yes | Agrees with Claude's note (vague; a guess fills the gap). Should say "could have". Doesn't make clear why ...dxe4 was better and why the played move was worse. |
| 5 | ...Nf6??, beginner | Yes → Yes | Should say the queen and the bishop are targeting f7, leading to mate in 1. |
| 6 | ...Nxe4?, intermediate | Yes → Yes | Still doesn't explain why capturing with the pawn is better than with the knight. |
| 7 | 1.a4, beginner | Yes → **No** | |
| 8 | 1.h4, beginner | No → No | |
| 9 | 3.Ng5??, advanced | Yes → Yes | "and the move opens a line for your queen" is pointless when the knight is lost. "This follows your blunder instead of the suggested Bb5…" is confusing: just say the best move was Bb5, then name its benefits. |
| 10 | Ruy Lopez, beginner | No → No | |
| 11 | Italian, intermediate | Yes → Yes | "By opening a path for your queen and setting up your pawn to control the d4 square, your best reply is c3" is illogical. Say "the best move here is c3, since …". |
| 12 | Najdorf, advanced | Yes → Yes | Not "stuck": say "undeveloped", or "it's time to put your bishop into play". |
| 13 | QGD, intermediate | No → **Yes** | "you retreat" → "should retreat". |

**What's left, grouped** (Claude, 29 Sep, 14:06):
- **Why the better move is better, or the played one worse** (1, 4, 6, 9): the biggest group.
  It isn't a wording slip. It's the "relevant" question of paper 1: our facts don't say *why*.
- **True but useless reasons** (3: a rook "line"; 9: a queen line after losing the knight)
  and one untrue word (12: "stuck"; the bishop could already move).
- **Wording** (4, 9, 11, 13): tense ("could have", "should retreat"), sentence order (move
  first, then "since …"), one garbled sentence.
- **A fact the coach had but didn't use** (5: the queen and bishop on f7, mate next move).
- Case 3 follows your 26 Sep opening rule (a piece gaining a square off its home rank counts);
  your note says that's not worth saying for this rook.
