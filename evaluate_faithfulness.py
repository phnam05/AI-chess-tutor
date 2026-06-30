"""Step 2 of the MSc upgrade plan: a small, reproducible faithfulness evaluation.

The project's core promise is "the engine decides the chess; the LLM only explains
it" (see CLAUDE.md). Step 1 turned that promise into a watchdog (`faithfulness.py`)
that checks a single explanation. This script turns it into a *measured number*:
run the real coach over a fixed, curated set of positions and report how many of
its explanations named only moves the engine actually produced — an "X of Y
faithful" table. That is the answer to the question a reviewer will ask: "how do
you know it works?"

It exercises the *shipping* system, not a mock: the same Stockfish engine and the
same Gemini coach the app uses. Positions are built from Standard-Algebraic-Notation
move lists (plus a few endgame FENs), so the whole set is human-readable,
reproducible, and guaranteed legal by python-chess — no hand-copied FEN can be
silently wrong.

Usage:
    python evaluate_faithfulness.py --validate   # check the set is legal (NO API calls)
    python evaluate_faithfulness.py --limit 3    # smoke test: first 3 cases
    python evaluate_faithfulness.py              # full run; writes faithfulness_eval.md

The full run makes one Gemini call per case (~25 total — trivial against the daily
quota), spaced out with --delay to stay under the 15-requests-per-minute ceiling.
"""

import argparse
import json
import time
from pathlib import Path

import chess

from engine_analysis import analyze_position
from move_review import review_move
from explainer import explain_position, explain_move
from faithfulness import check_faithfulness

# --- The curated set -------------------------------------------------------
# Each case is built from a starting point and graded one of two ways:
#   kind="position" -> explain the resulting position (tests explain_position)
#   kind="move"     -> grade `played` from the resulting position (tests explain_move,
#                      which leads with the engine's refutation line)
# `setup` is a list of SAN moves played from the standard start (or from `fen` if
# given). For move cases, `played` is the SAN move we hand to the grader. We mix
# phases (opening / middlegame / endgame) and deliberately include weak moves, so
# the refutation path — where invented tactics are most tempting — is well covered.
CASES = [
    # ---- Opening positions ----
    dict(name="Ruy Lopez (after 3...a6)", phase="opening", level="beginner",
         setup=["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"], kind="position"),
    dict(name="Italian Game (Giuoco Piano)", phase="opening", level="intermediate",
         setup=["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"], kind="position"),
    dict(name="Sicilian Najdorf", phase="opening", level="advanced",
         setup=["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"],
         kind="position"),
    dict(name="Queen's Gambit Declined", phase="opening", level="intermediate",
         setup=["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7"], kind="position"),
    dict(name="French Defence (Winawer)", phase="opening", level="advanced",
         setup=["e4", "e6", "d4", "d5", "Nc3", "Bb4"], kind="position"),
    dict(name="King's Indian Defence", phase="opening", level="intermediate",
         setup=["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6"], kind="position"),
    dict(name="Caro-Kann Defence", phase="opening", level="beginner",
         setup=["e4", "c6", "d4", "d5"], kind="position"),

    # ---- Middlegame positions (FENs the repo/log already exercise) ----
    dict(name="Closed centre, Black to plan", phase="middlegame", level="intermediate",
         fen="r2q1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 b kq - 0 9",
         setup=[], kind="position"),
    dict(name="Queen on f4, White attacking", phase="middlegame", level="advanced",
         fen="r1bq1rk1/pp3pp1/2n1p3/2P1P2p/5Q2/8/PPP2PPP/R1B1KB1R w KQ - 1 13",
         setup=[], kind="position"),
    dict(name="Open game, Black to move", phase="middlegame", level="beginner",
         fen="r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5",
         setup=[], kind="position"),

    # ---- Endgame positions ----
    dict(name="King + pawn vs king", phase="endgame", level="beginner",
         fen="8/8/4k3/8/4K3/8/4P3/8 w - - 0 1", setup=[], kind="position"),
    dict(name="Rook + pawn endgame", phase="endgame", level="intermediate",
         fen="8/8/8/4k3/8/8/4P3/4K2R w K - 0 1", setup=[], kind="position"),
    dict(name="Queen vs lone king (mating)", phase="endgame", level="beginner",
         fen="8/5k2/8/8/8/8/5K2/5Q2 w - - 0 1", setup=[], kind="position"),
    dict(name="Central king & pawn", phase="endgame", level="advanced",
         fen="8/8/8/3k4/8/3K4/3P4/8 w - - 0 1", setup=[], kind="position"),

    # ---- Good moves (explain why the played move is strong) ----
    dict(name="Italian: 3.Bb5 (good)", phase="opening", level="beginner",
         setup=["e4", "e5", "Nf3", "Nc6"], played="Bb5", kind="move"),
    dict(name="Opening move 1.e4 (good)", phase="opening", level="beginner",
         setup=[], played="e4", kind="move"),
    dict(name="Ruy Lopez: 4.Ba4 (good)", phase="opening", level="intermediate",
         setup=["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"], played="Ba4", kind="move"),
    dict(name="Develop with ...Be7 (good)", phase="middlegame", level="intermediate",
         fen="r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5",
         setup=[], played="Be7", kind="move"),
    dict(name="Scotch: ...exd4 (good)", phase="opening", level="intermediate",
         setup=["e4", "e5", "Nf3", "Nc6", "d4"], played="exd4", kind="move"),

    # ---- Weak moves (lead with the engine's refutation line) ----
    dict(name="Scholar's mate trap: ...Nf6?? (blunder)", phase="opening", level="beginner",
         setup=["e4", "e5", "Bc4", "Nc6", "Qh5"], played="Nf6", kind="move"),
    dict(name="...Nxe4?? drops a piece (blunder)", phase="middlegame", level="intermediate",
         fen="r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5",
         setup=[], played="Nxe4", kind="move"),
    dict(name="Wing push 1.a4 (passive)", phase="opening", level="beginner",
         setup=[], played="a4", kind="move"),
    dict(name="Edge push 1.h4 (passive)", phase="opening", level="beginner",
         setup=[], played="h4", kind="move"),
    dict(name="Premature 3.Ng5?! (inaccuracy)", phase="opening", level="advanced",
         setup=["e4", "e5", "Nf3", "Nc6"], played="Ng5", kind="move"),
    dict(name="Passive 2.Na3 (inaccuracy)", phase="opening", level="intermediate",
         setup=["e4", "c5"], played="Na3", kind="move"),
]


def build_board(case):
    """Replay the case's setup moves onto a board. Raises loudly (ValueError) on a
    bad SAN token, which is exactly what we want during --validate."""
    board = chess.Board(case["fen"]) if case.get("fen") else chess.Board()
    for san in case["setup"]:
        board.push_san(san)
    return board


def validate():
    """Check every case is legal without touching the engine or the API."""
    ok = True
    for i, case in enumerate(CASES, 1):
        try:
            board = build_board(case)
            detail = ""
            if case["kind"] == "move":
                # parse_san both validates the move and gives us the UCI the grader needs.
                mv = board.parse_san(case["played"])
                detail = f"played {case['played']} ({mv.uci()})"
            print(f"[ok]  {i:>2}. {case['name']:<40} {case['phase']:<11} {detail}")
        except Exception as e:
            ok = False
            print(f"[BAD] {i:>2}. {case['name']:<40} -> {e!r}")
    n_pos = sum(c["kind"] == "position" for c in CASES)
    n_mv = sum(c["kind"] == "move" for c in CASES)
    print(f"\n{len(CASES)} cases ({n_pos} positions, {n_mv} moves) — "
          f"{'all legal' if ok else 'FIX THE BAD ONES ABOVE'}")
    return ok


def run_case(case):
    """Run one case end to end: engine facts -> coach prose -> faithfulness check.
    Returns a result dict the table is built from."""
    board = build_board(case)
    fen = board.fen()

    if case["kind"] == "position":
        facts = analyze_position(fen)
        text = explain_position(facts, level=case["level"])
        engine_move = facts["best_move"]
    else:
        played_uci = board.parse_san(case["played"]).uci()
        facts = review_move(fen, played_uci)
        text = explain_move(facts, level=case["level"])
        engine_move = f"played {facts['played_move']} / best {facts['best_move']} ({facts['label']})"

    check = check_faithfulness(text, facts)
    return {
        "name": case["name"],
        "phase": case["phase"],
        "kind": case["kind"],
        "level": case["level"],
        "fen": fen,
        "facts": facts,
        "engine_move": engine_move,
        "ok": check["ok"],
        "grounded": check["grounded"],
        "ungrounded_moves": check["ungrounded_moves"],
        "unverified_squares": check["unverified_squares"],
        "text": text,
    }


def write_report(results, path):
    """Write a self-contained markdown report: summary, table, and the full prose
    (so the artifact shows the explanations were real, not asserted)."""
    total = len(results)
    faithful = sum(r["ok"] for r in results)
    rate = 100 * faithful / total if total else 0
    lines = []
    lines.append("# Faithfulness evaluation\n")
    lines.append(f"**{faithful} of {total} explanations ({rate:.0f}%) named only moves "
                 "the engine actually produced.**\n")
    lines.append("Each explanation was produced by the real coach (Stockfish facts → "
                 "Gemini prose) and checked by `faithfulness.check_faithfulness`. A case "
                 "is *faithful* when the prose invents no move the engine never gave.\n")
    lines.append("## What this measures — and what it does not\n")
    lines.append("This is an automatic, string-based check: it reads the moves the coach "
                 "named *in notation* (e.g. `Nf3`, `Bxc3+`, `O-O`) and confirms each was a "
                 "move the engine actually gave — its best move, its principal variation, or "
                 "(for a graded move) its refutation line. Its scope is deliberate:\n")
    lines.append("- **Catches** invented piece moves, captures, checks and mates — the "
                 "attention-grabbing hallucination (\"you can play Nxe5, forking the king\").")
    lines.append("- **Does not hard-flag** a bare pawn push written as a square (e.g. `c3`, "
                 "`h4`): the coach may simply be pointing at a square, so these are reported "
                 "as *unverified* rather than failed, to avoid false alarms.")
    lines.append("- **Does not check** eval numbers or verbal claims (\"this pins the "
                 "knight\") — only moves written in notation.\n")
    lines.append("These limits are validated two ways: a *positive control* (planting fake "
                 "piece-moves in real explanations confirms the check flags them) and a "
                 "*human audit* (how often this automatic verdict agrees with a person's "
                 "judgement).\n")
    lines.append("| # | Position | Phase | Type | Level | Faithful | Grounded moves | Invented |")
    lines.append("|--:|----------|-------|------|-------|:--------:|----------------|----------|")
    for i, r in enumerate(results, 1):
        flag = "yes" if r["ok"] else "**NO**"
        grounded = ", ".join(r["grounded"]) or "—"
        invented = ", ".join(r["ungrounded_moves"]) or "—"
        lines.append(f"| {i} | {r['name']} | {r['phase']} | {r['kind']} | {r['level']} "
                     f"| {flag} | {grounded} | {invented} |")
    lines.append("\n## Explanations\n")
    for i, r in enumerate(results, 1):
        lines.append(f"**{i}. {r['name']}** ({r['kind']}, {r['level']}) — engine: {r['engine_move']}")
        lines.append(f"\n> {r['text'].strip()}\n")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_records(results, path):
    """Save each case's prose AND the exact engine facts behind it, locked together,
    as JSON. This is the canonical record the human-audit sheet reads, so the audit
    judges the coach against the facts it actually saw — no re-deriving, no drift.
    (The engine is deterministic now, so a re-derivation would match anyway; saving
    just makes the artifact self-contained and inspectable without the engine.)"""
    records = []
    for r in results:
        records.append({
            "name": r["name"],
            "phase": r["phase"],
            "kind": r["kind"],
            "level": r["level"],
            "fen": r["fen"],
            "facts": r["facts"],
            "text": r["text"],
            "check": {
                "ok": r["ok"],
                "grounded": r["grounded"],
                "ungrounded_moves": r["ungrounded_moves"],
                "unverified_squares": r["unverified_squares"],
            },
        })
    Path(path).write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Faithfulness evaluation over a curated set.")
    ap.add_argument("--validate", action="store_true", help="check legality only, no API calls")
    ap.add_argument("--limit", type=int, default=0, help="run only the first N cases (smoke test)")
    ap.add_argument("--delay", type=float, default=4.5,
                    help="seconds between API calls (stay under 15/min)")
    ap.add_argument("--out", default="faithfulness_eval.md", help="report path")
    ap.add_argument("--records", default="faithfulness_records.json",
                    help="machine-readable per-case record (prose + engine facts)")
    args = ap.parse_args()

    if args.validate:
        raise SystemExit(0 if validate() else 1)

    cases = CASES[: args.limit] if args.limit else CASES
    results = []
    for i, case in enumerate(cases, 1):
        try:
            r = run_case(case)
        except Exception as e:
            print(f"[ERR ] {i:>2}/{len(cases)} {case['name']}: {e!r}")
            continue
        flag = "PASS" if r["ok"] else "FLAG"
        print(f"[{flag}] {i:>2}/{len(cases)} {r['name']:<40} "
              f"grounded={r['grounded']} invented={r['ungrounded_moves']}")
        results.append(r)
        if i < len(cases):
            time.sleep(args.delay)   # throttle for the 15-requests-per-minute limit

    total = len(results)
    faithful = sum(r["ok"] for r in results)
    rate = 100 * faithful / total if total else 0
    print(f"\n==== {faithful}/{total} faithful ({rate:.0f}%) ====")
    if total:
        write_report(results, args.out)
        print(f"Report written to {args.out}")
        write_records(results, args.records)
        print(f"Records written to {args.records}")


if __name__ == "__main__":
    main()
