"""Score the eval-causality checker against the human audit.

The 2026-07-03 human audit (`faithfulness_audit.md`) is the ground truth for the
25 recorded cases: it marked 10 of them as "causal invention (eval attribution)"
— the coach explaining WHY the eval is what it is when the engine gave no reason
— and one (case 24) as a causal explanation that was actually *grounded* in the
engine's line. The old move-token checker said clean on all 25, blind to this by
construction. This script re-runs the extended checker over the same saved prose
and facts and reports how well its new verdicts agree with the human's.

It reads `faithfulness_records_audited.json` — a frozen copy of the exact run
the human judged. (`faithfulness_records.json` is the *latest* eval run and gets
overwritten by evaluate_faithfulness.py; the answer key below is only meaningful
against the audited prose, so the frozen copy keeps this validation reproducible.)

No engine, no API — a pure transform of saved data, like build_audit.py.

Usage:
    python validate_checker.py
"""
import json
from pathlib import Path

from faithfulness import check_faithfulness

# The human's verdict on *eval attribution only* (other audit findings — causal
# drift, the two factual errors, wording — are outside this detector's scope by
# design; see faithfulness.py). Keyed by the audit sheet's 1-based case number,
# which is the order of the records file.
#   invented -> the human flagged an eval-causal claim with no engine backing
#   grounded -> the human judged the eval-causal claim correct (its reason is in
#               the engine's line), so the checker should surface it as
#               "unverified", not fail it
#   none     -> no eval-causal claim was flagged
HUMAN = {i: "none" for i in range(1, 26)}
HUMAN.update({i: "invented" for i in (1, 3, 4, 5, 6, 8, 9, 10, 12, 14)})
HUMAN[24] = "grounded"


def checker_verdict(check):
    if check["causal_invented"]:
        return "invented"
    if check["causal_unverified"]:
        return "unverified"
    return "none"


def main():
    records = json.loads(Path("faithfulness_records_audited.json").read_text(encoding="utf-8"))
    assert len(records) == len(HUMAN), "answer key and records disagree on case count"

    caught, missed, false_hard, ok_count = [], [], [], 0
    print(f"{'#':>2}  {'human':<9} {'checker':<11} case")
    for i, rec in enumerate(records, 1):
        check = check_faithfulness(rec["text"], rec["facts"])
        verdict = checker_verdict(check)
        human = HUMAN[i]
        ok_count += check["ok"]

        if human == "invented":
            # Any surfacing (hard or soft) counts as caught: both put the
            # sentence in front of a human, which is the checker's job.
            (caught if verdict != "none" else missed).append(i)
        elif verdict == "invented":
            false_hard.append(i)  # hard flag on a case the human passed

        mark = "  <-- MISS" if (human == "invented" and verdict == "none") else (
               "  <-- FALSE HARD FLAG" if (human != "invented" and verdict == "invented") else "")
        print(f"{i:>2}  {human:<9} {verdict:<11} {rec['name']}{mark}")
        for s in check["causal_invented"]:
            print(f"      [invented]   {s}")
        for s in check["causal_unverified"]:
            print(f"      [unverified] {s}")

    n_flagged = sum(1 for v in HUMAN.values() if v == "invented")
    print(f"\nHuman flagged eval attribution in {n_flagged}/25 cases.")
    print(f"Checker surfaced {len(caught)}/{n_flagged} of them"
          f"{' (missed: ' + str(missed) + ')' if missed else ''}.")
    print(f"Hard flags on human-clean cases: {len(false_hard)}"
          f"{' ' + str(false_hard) if false_hard else ''}.")
    grounded_ok = checker_verdict(
        check_faithfulness(records[23]["text"], records[23]["facts"])) == "unverified"
    print(f"Case 24 (the grounded causal explanation) surfaced as unverified, "
          f"not failed: {'yes' if grounded_ok else 'NO'}.")
    print(f"\nOverall: {ok_count}/25 pass the extended check "
          f"(was 25/25 under the move-only check) — the before-fix baseline.")


if __name__ == "__main__":
    main()
