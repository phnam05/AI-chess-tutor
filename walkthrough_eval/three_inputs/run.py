"""Does each input help? The same move explained three ways (author, 23 Oct):

  A. Gemini alone: only the position and the move the student played.
  B. Gemini + Stockfish: also the engine's review (label, evals, the line,
     the better move), but no board facts.
  C. Gemini + Stockfish + board facts: the coach exactly as the app runs it
     (explainer.explain_move, version 1).

A quick look on 2 hand-picked simple positions (1 opening, 1 middlegame) whose
answer is easy to check by eye: not step 5's experiment, which needs fresh
positions and many more cases. Same model, same level (intermediate) and the
same position text (FEN only, as the app sends) in all three; B shows the same
moves of the engine's line as C, so the board facts are the only thing added.

B's system prompt is version 1's with the board-fact rules taken out (B has no
board facts, so "an idea may come only from its board facts" would leave it
nothing to say). Everything else is word for word the same.

    python walkthrough_eval/three_inputs/run.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import chess

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import board_facts                                    # noqa: E402
import explainer                                      # noqa: E402
from faithfulness import check_faithfulness           # noqa: E402
from move_review import review_move                   # noqa: E402

OUT = Path(__file__).with_name("results.json")
LEVEL = "intermediate"

CASES = [
    {"name": "Opening: Black takes the e4 pawn with the knight",
     "moves": "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 d2d3 g8f6 e1g1",
     "played": "f6e4",
     "truth": "5...Nxe4? The pawn on e4 was defended by the pawn on d3: 6.dxe4 "
              "and Black has given a knight for a pawn. Better was 5...d6."},
    {"name": "Middlegame: Black develops the bishop to f5",
     "moves": ("d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c1g5 f8e7 e2e3 e8g8 g1f3 b8d7 "
               "c4d5 e6d5 f1d3 c7c6 d1c2 f8e8 e1g1 d7f8 a1b1"),
     "played": "c8f5",
     "truth": "11...Bf5? Nothing of Black's defends f5, and White's bishop on d3 "
              "(with the queen on c2 behind it) attacks it: 12.Bxf5 wins a bishop "
              "for nothing. Better was 11...Ne4."},
]

# --- A and B: version 1's prompt, minus what refers to inputs they don't get ---

def _cut(text, old, new=""):
    assert old in text, old
    return text.replace(old, new)


S = explainer.SYSTEM_INSTRUCTION
S = _cut(S, """The engine's analysis (best move,
evaluation, the line it expects) and the board facts listed for each move are
given to you and are correct. Treat them as ground truth, and as your ONLY
source of chess claims: you put them into words, you never add to them.""",
         """The engine's analysis (best move,
evaluation, the line it expects) is given to you and is correct. Treat it as
ground truth.""")
S = _cut(S, "- For each move, use only its one most useful board fact. Do not list them all.\n")
S = _cut(S, "<what to notice, from its board fact>", "<what to notice>")
S = _cut(S, """- A move's idea or purpose may come ONLY from its board facts, or from what the
  line shows happening next. Never from general chess knowledge or rules of
  thumb ("usually", "generally"), and never from your own reading of the board.
  If a move's board facts say "none", name it and give it no reason.
""")
S = _cut(S, "never say a move or a board fact raises", "never say a move raises")
S = _cut(S, "- A move's board facts are listed with the most important first.\n")
ENGINE_SYSTEM = S

# Gemini alone gets the persona and style only: nothing about an engine.
BARE_SYSTEM = """You are a friendly chess coach sitting next to one
student, looking at their game together.

Your job is to coach this one student. Follow these rules:
- Talk directly to the student as "you." Be warm and concise.
- Write a few plain sentences. NO headings, NO numbered lists, NO bold text,
  NO "Summary" section.
- Write Black's moves with three dots (...c6) and White's without (Nf3).
- Never guess what the student wants or wanted ("since you want to...").
  Say what the move does.
- End on something that invites the student to think, but never lecture."""

# Version 1's intermediate line says terms may name "what a board fact already
# says"; A and B have none, so theirs keeps only the length and the terms.
PLAIN_LEVEL = """The player is INTERMEDIATE. Give each move's idea, then the
move in notation. You may use standard terms like development, tempo and
initiative. Keep it to 4-5 sentences."""


def _bare_facts(review, student):
    return f"""The student plays {student} and just made a move.

Position before their move (FEN): {review['fen']}
Their move: {explainer._dots(student, review['played_move'])}

Coach the student on the move THEY played: say what it did and whether it was
good, and if it was not, what they should have played instead and why.
Be encouraging and specific."""


def _engine_facts(review, student, steps):
    """explain_move's message with every board fact taken out; same moves."""
    lines = []
    for i, s in enumerate(steps, 1):
        who = (f"Student ({s['color']}), best move:" if s["color"] == student
               else f"Opponent ({s['color']}), likely reply:")
        lines.append(f"{i}. {who} {explainer._dots(s['color'], s['san'])} "
                     f"(the {s['piece']}, {s['from']} to {s['to']}).")
    walk = "\n".join(lines) or "(none: the game is over)"
    instead = ""
    if review["label"] != "Best":
        instead = (f"\n\nThe move the engine would have played instead: "
                   f"{explainer._dots(student, review['best_move'])}.")
    return f"""The student plays {student} and just made a move. Here is the engine's review:

Position before their move (FEN): {review['fen']}
Their move: {explainer._dots(student, review['played_move'])}
Move quality: {review['label']}
Evaluation after their move: {explainer._eval_words(review['played_eval'], student)}
Evaluation if they had played the best move: {explainer._eval_words(review['best_eval'], student)}

What the engine expects to follow their move, one move at a time:
{walk}{instead}

Coach the student on the move THEY played, in this order:
1. What their move did: if it lost value, what it changed on the board; if it
   was strong, affirm it briefly. Give the evaluation in a separate sentence
   of its own.
2. Walk through the moves above, in order and no further.
3. If it lost value, end with one short clause naming the move the engine
   would have played instead, with its idea first.
Be encouraging and specific."""


def _call(system, contents):
    resp = explainer._get_client().models.generate_content(
        model=explainer.MODEL,
        config=explainer.types.GenerateContentConfig(system_instruction=system),
        contents=contents)
    return resp.text


def main():
    results = []
    for case in CASES:
        board = chess.Board()
        for m in case["moves"].split():
            board.push_uci(m)
        review = review_move(board.fen(), case["played"])
        student = "White" if board.turn == chess.WHITE else "Black"
        # The same moves C will walk through (explain_move's own cut).
        damage = review.get("mistake_type") in ("lost_material", "allowed_mate")
        steps = board_facts.cut_line(review["line_steps"], board_facts.LINE_PLIES[LEVEL],
                                     student, damage=damage)
        arms = {}
        bare = _bare_facts(review, student)
        arms["A. Gemini alone"] = {"system": BARE_SYSTEM + "\n\n" + PLAIN_LEVEL, "contents": bare}
        eng = _engine_facts(review, student, steps)
        arms["B. Gemini + Stockfish"] = {"system": ENGINE_SYSTEM + "\n\n" + PLAIN_LEVEL, "contents": eng}
        for arm in arms.values():
            arm["text"] = _call(arm["system"], arm["contents"])
        po = {}
        text = explainer.explain_move(review, LEVEL, prompt_out=po)
        arms["C. Gemini + Stockfish + board facts"] = {"system": po["system"],
                                                       "contents": po["contents"], "text": text}
        for arm in arms.values():
            r = check_faithfulness(arm["text"], review)
            arm["checker"] = {k: r[k] for k in ("ok", "ungrounded_moves", "causal_invented")}
        results.append({**case, "fen": board.fen(), "student": student,
                        "engine": {k: review[k] for k in ("label", "best_move", "best_eval",
                                                          "played_eval", "refutation",
                                                          "mistake_type", "played_facts")},
                        "arms": arms})
        print(f"\n######## {case['name']}\nTruth: {case['truth']}")
        for name, arm in arms.items():
            print(f"\n--- {name} (checker ok={arm['checker']['ok']}, "
                  f"invented moves={arm['checker']['ungrounded_moves']})\n{arm['text']}")
    OUT.write_text(json.dumps({"generated": datetime.now().isoformat(timespec="minutes"),
                               "model": explainer.MODEL, "level": LEVEL,
                               "cases": results}, indent=2, ensure_ascii=False),
                   encoding="utf-8")


if __name__ == "__main__":
    main()
