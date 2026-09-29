"""Build the full old-vs-new sheet (walkthrough_eval/audit_full.md): old vs new coach answers side by side, with the
labelled line + board facts the new coach was given, for the author's hand check.
Usage: build_check.py before.json after.json nb4.json out.md"""
import json
import sys

import chess
import board_facts
import explainer

before_path, after_path, nb4_path, out_path = sys.argv[1:5]
before = {r["name"]: r for r in json.load(open(before_path, encoding="utf-8"))}
after = json.load(open(after_path, encoding="utf-8"))
nb4 = json.load(open(nb4_path, encoding="utf-8"))

# Every weak-move case (where the line is the refutation) plus a spread of
# positions, so all three levels and both kinds are covered: 10 cases.
weak = [r for r in after if r["kind"] == "move"
        and r["facts"]["label"] in ("Inaccuracy", "Mistake", "Blunder")]
positions = [r for r in after if r["kind"] == "position"]
picked = weak[:6]
for level in ("beginner", "intermediate", "advanced"):
    picked += [r for r in positions if r["level"] == level and r not in picked][:1]
picked += [r for r in positions if r not in picked][:10 - len(picked)]

CHECKS = """- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:"""


def given(facts, level, kind):
    """What the new coach was shown: the cut, labelled line with board facts."""
    if kind == "move":
        student = "White" if chess.Board(facts["fen"]).turn == chess.WHITE else "Black"
        played, steps, best = explainer._review_facts(facts)
        steps = board_facts.cut_line(steps, board_facts.LINE_PLIES[level], student)
        head = (f"Your move: {explainer._dots(student, facts['played_move'])} "
                f"({facts['label']}, {facts['best_eval']} → {facts['played_eval']}). "
                f"Board facts: {explainer._facts_text(played)}.\n")
        tail = ""
        if facts["label"] != "Best":
            tail = (f"\nInstead: {explainer._dots(student, facts['best_move'])}. "
                    f"Board facts: {explainer._facts_text(best)}.")
        return head + explainer._walkthrough(steps, student) + tail
    student = facts["turn"]
    steps = board_facts.cut_line(facts["line_steps"], board_facts.LINE_PLIES[level], student)
    return f"Eval: {facts['eval_text']}.\n" + explainer._walkthrough(steps, student)


out = ["# Walkthrough audit: old vs new coach (24 Sep 2026)", "",
       "For each case: what the new coach was given (who plays each move, and the",
       "board facts it may use as reasons), then the old answer and the new one.",
       "Tick the boxes for the **new** answer. A reason that isn't in the board",
       "facts or the line is an invented reason, even if it sounds right.", ""]

out += ["## 0. Your example: ...Nb4 (all three levels)", "",
        "```", given(nb4[0]["facts"], "advanced", "move"), "```", ""]
for r in nb4:
    out += [f"**New, {r['level']}:** {r['text']}", "", CHECKS, ""]

for i, r in enumerate(picked, 1):
    old = before.get(r["name"])
    out += [f"## {i}. {r['name']} ({r['kind']}, {r['level']})", "",
            f"FEN: `{r['fen']}`", "", "```", given(r["facts"], r["level"], r["kind"]), "```", "",
            f"**Old:** {old['text'] if old else '(missing)'}", "",
            f"**New:** {r['text']}", "", CHECKS, ""]

open(out_path, "w", encoding="utf-8").write("\n".join(out))
print(f"wrote {out_path} with {len(picked)} cases + the Nb4 example")
