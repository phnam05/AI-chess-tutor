"""Turn the saved faithfulness records into the human-audit sheet.

Reads `faithfulness_records.json` (each case's coach prose plus the exact engine
facts behind it, written by evaluate_faithfulness.py) and writes
`faithfulness_audit.md`: a summary table, then one block per case with the engine
facts, the automatic checker's verdict, and blank A/B/C/D slots for a human to fill.

No engine, no API — a pure transform of saved data, so the audit always lines up
with the facts the coach actually used (no re-derivation, no drift).

Usage:
    python build_audit.py            # records -> audit sheet
"""
import argparse
import json
from pathlib import Path


def facts_line(rec):
    """One-line summary of what the engine produced for this case."""
    f = rec["facts"]
    if rec["kind"] == "position":
        pv = ", ".join(f.get("principal_variation", [])) or "—"
        return f"best: `{f['best_move']}` · eval: `{f['eval_text']}` · PV: `{pv}`"
    ref = ", ".join(f.get("refutation", [])) or "—"
    return (f"played: `{f['played_move']}` · best: `{f['best_move']}` · grade: "
            f"`{f['label']}` · evals: played `{f['played_eval']}` / best `{f['best_eval']}` "
            f"· refutation: `{ref}`")


def build(records):
    out = []
    out.append("# Faithfulness — human audit\n")
    out.append("**You are the ground truth.** For each explanation judge ONLY whether the "
               "coach stuck to the engine's facts or invented something — *fidelity to the "
               "engine*, not whether it is the best chess. Then, separately, note anything "
               "you would reword even when it is faithful.\n")
    out.append("Per case, fill:\n")
    out.append("- **A. Faithful to the engine?** — `Yes` / `No`")
    out.append("- **B. If No, what did it invent?** — the move or claim, else `—`")
    out.append("- **C. What I'd change (even if faithful)** — free text, else `nothing`")
    out.append("- **D. (optional) Change type** — `wording` / `too long` / `too short` / "
               "`too vague` / `missed teaching point` / `level off` / `other`\n")

    out.append("## Summary\n")
    out.append("| # | Case | Phase | Type | Checker | A. Faithful? | Agree w/ checker? | D. Change type |")
    out.append("|--:|------|-------|------|:-------:|:------------:|:-----------------:|----------------|")
    for i, rec in enumerate(records, 1):
        verdict = "clean" if rec["check"]["ok"] else "flagged"
        out.append(f"| {i} | {rec['name']} | {rec['phase']} | {rec['kind']} | {verdict} | "
                   f"____ | ____ | ____ |")

    out.append("\n## Cases\n")
    for i, rec in enumerate(records, 1):
        verdict = "clean" if rec["check"]["ok"] else "flagged"
        grounded = ", ".join(rec["check"]["grounded"]) or "—"
        out.append(f"### {i}. {rec['name']}  ({rec['kind']}, {rec['level']})\n")
        fen_note = " (the position *before* the played move)" if rec["kind"] == "move" else ""
        out.append(f"**Board (FEN)** — `{rec['fen']}`{fen_note}")
        out.append(f"**Engine facts** — {facts_line(rec)}")
        out.append(f"**Checker** — {verdict} (grounded: {grounded})")
        out.append(f"\n**Coach said:**\n> {rec['text'].strip()}\n")
        out.append("- **A. Faithful?** ")
        out.append("- **B. Invented?** ")
        out.append("- **C. What I'd change:** ")
        out.append("- **D. Type:** ")
        out.append("\n---\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Build the human-audit sheet from saved records.")
    ap.add_argument("--records", default="faithfulness_records.json", help="input JSON")
    ap.add_argument("--out", default="faithfulness_audit.md", help="output markdown")
    args = ap.parse_args()

    records = json.loads(Path(args.records).read_text(encoding="utf-8"))
    Path(args.out).write_text(build(records), encoding="utf-8")
    print(f"Wrote {args.out} with {len(records)} cases from {args.records}")


if __name__ == "__main__":
    main()
