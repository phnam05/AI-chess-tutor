"""Step 3d: can the learner model find a weakness we planted on purpose?

A real player's weaknesses are unknown, so a learner model can't be checked
against them directly. Instead we build simulated players whose weakness we
choose, let them play, and see whether the model names it. (This is also how
teammate-type estimators are evaluated in ad-hoc teamwork research: agents of
known type, and the question is how fast and how reliably the estimator finds it.)

Each bot plays the engine's best move, except that on some share of its moves
it makes its one planted kind of mistake:

  hangs    leaves a piece where it can be taken       -> should be found as lost_material
  misses   passes up a chance to win material         -> should be found as missed_material
  drifts   plays a random quiet move instead of best  -> should be found as positional
  solid    never plants anything (the control)        -> should get no pattern at all

Bots play against Stockfish from a rotating set of openings, alternating
colours. Every bot move runs through the real pipeline — engine review ->
mistake kind -> learner model — exactly as a student's move would. A game stops
once it's decided (either side up 5+ pawns, or a forced mate): after that the
win-chance curve is flat, so grading is lenient and says little about habits.

One "trial" = one simulated player's session of MOVES_PER_TRIAL moves. For
each bot we run several trials (different random seeds) and report:
  * found      — trials where the planted kind is a pattern at the end
  * first seen — median number of moves until it first became a pattern
  * false      — trials where some OTHER kind was called a pattern at the end
  * agreement  — of the moves where the bot planted its mistake, how many the
                 detector (move_review.classify_mistake) labelled as that kind

The engine is deterministic and the bots use seeded randomness, so a run is
reproducible. No language model is involved.

Usage:
    python simulate_learners.py            # full run, writes learner_eval.md
    python simulate_learners.py --quick    # small smoke run, prints only
    python simulate_learners.py --rescore  # re-score the saved games after a
                                           # learner-model change (no engine)
"""
import json
import random
import statistics
import sys
from pathlib import Path

import chess

from engine_pool import analyse
from move_review import PIECE_VALUES, _review_from_infos, position_chances
from learner_model import KINDS, new_model, summary, update

OPENINGS = [
    "e4 e5 Nf3 Nc6 Bb5",                     # Ruy Lopez
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3",     # Sicilian
    "d4 d5 c4 e6 Nc3 Nf6",                   # Queen's Gambit Declined
    "e4 e6 d4 d5 Nc3",                       # French
    "e4 c6 d4 d5",                           # Caro-Kann
    "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6",            # King's Indian
    "c4 e5 Nc3 Nf6",                         # English
    "e4 e5 Nf3 Nc6 Bc4 Bc5",                 # Italian
]

# bot -> (how often it plants its mistake when it can, the kind we expect found)
BOTS = {
    "hangs":  (0.3, "lost_material"),
    "misses": (0.7, "missed_material"),
    "drifts": (0.4, "positional"),
    "solid":  (0.0, None),
}

MOVES_PER_TRIAL = 40
TRIALS = 5
DECIDED_CP = 500


def _value(piece):
    return PIECE_VALUES.get(piece.piece_type, 0)


def hanging(board, color):
    """Squares of `color`'s pieces (pawns included, king not) that can be taken
    for profit: attacked and undefended, or attacked by something cheaper."""
    out = set()
    for sq, piece in board.piece_map().items():
        if piece.color != color or piece.piece_type == chess.KING:
            continue
        attackers = board.attackers(not color, sq)
        if not attackers:
            continue
        cheapest = min(_value(board.piece_at(a)) or 100 for a in attackers)  # king -> 100
        if not board.attackers(color, sq) or cheapest < _value(board.piece_at(sq)):
            out.add(sq)
    return out


def newly_hanging(board, move):
    """What `move` leaves hanging that wasn't hanging before — checked for every
    piece, not just the one that moved (moving a defender away hangs another).
    A cheap rule of thumb for steering the bot; the engine, not this rule,
    decides what each move really was."""
    after = board.copy()
    after.push(move)
    return {sq: after.piece_at(sq) for sq in hanging(after, board.turn) - hanging(board, board.turn)}


def _hangs_a_piece(board, move):
    return any(_value(p) >= 3 for p in newly_hanging(board, move).values())


def _quiet_safe(board, move, best):
    return (move != best and not board.is_capture(move) and not move.promotion
            and not newly_hanging(board, move))


def bot_move(bot, board, info, rng):
    """The bot's move and whether it planted its mistake on this move."""
    best = info["pv"][0]
    share, _ = BOTS[bot]
    legal = list(board.legal_moves)
    candidates = []
    if bot == "hangs" and rng.random() < share:
        candidates = [m for m in legal if not board.is_capture(m) and not m.promotion
                      and _hangs_a_piece(board, m)]
    elif bot == "misses" and position_chances(board, info)["material"] and rng.random() < share:
        candidates = [m for m in legal if _quiet_safe(board, m, best)]
    elif bot == "drifts" and rng.random() < share:
        candidates = [m for m in legal if _quiet_safe(board, m, best)]
    if candidates:
        return rng.choice(candidates), True
    return best, False


def _decided(info):
    score = info["score"].pov(chess.WHITE)
    return score.is_mate() or abs(score.score()) >= DECIDED_CP


def run_trial(bot, seed, moves=MOVES_PER_TRIAL):
    """One simulated player's session: games until `moves` bot moves are graded.
    Returns the model's history and the planted-vs-detected log."""
    rng = random.Random(seed)
    moves_log = []         # every graded bot move: what the learner model needs
    game = 0
    while len(moves_log) < moves:
        board = chess.Board()
        for san in OPENINGS[(seed + game) % len(OPENINGS)].split():
            board.push_san(san)
        bot_color = chess.WHITE if (seed + game) % 2 == 0 else chess.BLACK
        info = analyse(board)
        while len(moves_log) < moves and not board.is_game_over() and not _decided(info):
            if board.turn != bot_color:                 # Stockfish replies
                board.push(info["pv"][0])
                info = analyse(board)
                continue
            move, planted = bot_move(bot, board, info, rng)
            after = board.copy()
            after.push(move)
            info_after = analyse(after)
            review = _review_from_infos(board, move, info, info_after)
            moves_log.append({
                "where": f'game {game + 1}, move {board.fullmove_number} {review["played_move"]}',
                "label": review["label"], "mistake_type": review["mistake_type"],
                "chances": review["chances"], "planted": planted,
            })
            board, info = after, info_after
        game += 1
    return score_trial({"bot": bot, "seed": seed, "games": game, "moves": moves_log})


def score_trial(trial):
    """Replay a trial's graded moves through the learner model. Kept separate from
    playing, so a change to the model is re-scored from the saved moves in
    seconds (`--rescore`) instead of replaying every game."""
    model = new_model()
    history = []           # per bot move: set of kinds called a pattern after it
    for m in trial["moves"]:
        update(model, {"played_move": m["where"], "mistake_type": m["mistake_type"],
                       "chances": m["chances"]}, where=m["where"])
        history.append({r["kind"] for r in summary(model) if r["status"] == "pattern"})
    planted = [m["mistake_type"] for m in trial["moves"] if m["planted"]]
    return trial | {"history": history, "planted": planted, "final": summary(model)}


def score_bot(bot, trials):
    """The four numbers per bot described in the module docstring."""
    _, expected = BOTS[bot]
    found = sum(expected in t["history"][-1] for t in trials) if expected else None
    firsts = [next((i + 1 for i, pats in enumerate(t["history"]) if expected in pats), None)
              for t in trials] if expected else []
    firsts = [f for f in firsts if f is not None]
    false = sum(bool(t["history"][-1] - {expected}) for t in trials)
    planted = [k for t in trials for k in t["planted"]]
    agree = sum(k == expected for k in planted) if expected else None
    return {
        "bot": bot, "expected": expected, "trials": len(trials),
        "found": found, "first_seen_median": statistics.median(firsts) if firsts else None,
        "false": false, "planted": len(planted), "agree": agree,
        "detected_as": {k: planted.count(k) for k in sorted(set(planted), key=str)},
        "games": sum(t["games"] for t in trials),
    }


def write_report(scores, trials_by_bot, path):
    lines = [
        "# Step 3d — Can the learner model find a planted weakness?",
        "",
        "Generated by `simulate_learners.py` (deterministic: fixed engine depth, seeded bots).",
        f"Each trial is one simulated player's session of {MOVES_PER_TRIAL} graded moves against "
        f"Stockfish, over several games from rotating openings; {TRIALS} trials per bot.",
        "",
        "| Bot | Planted weakness | Found by the end | First flagged at move (median) "
        "| Other kinds flagged | Detector agreed on planted moves |",
        "|---|---|---|---|---|---|",
    ]
    for s in scores:
        found = f'{s["found"]}/{s["trials"]}' if s["expected"] else "—"
        first = s["first_seen_median"] if s["first_seen_median"] is not None else "—"
        agree = f'{s["agree"]}/{s["planted"]}' if s["expected"] else "—"
        lines.append(f'| {s["bot"]} | {s["expected"] or "none (control)"} | {found} | {first} '
                     f'| {s["false"]}/{s["trials"]} | {agree} |')
    lines += [
        "",
        "**How to read this.** \"Planted\" is what the bot *tried* to do, not what its move "
        "really was: a crude \"quiet\" move can still lose material to a pin or fork, and "
        "skipping a recapture can let the opponent take more. The engine judges each move "
        "as it really is, so the last column shows how often the plan and the engine "
        "agree — and \"other kinds flagged\" can be a real weakness the bot showed, not a "
        "false alarm. Check the per-trial counts below before reading a miss as a failure "
        "of the learner model.",
        "",
        "## What the detector called the planted moves",
        "",
    ]
    for s in scores:
        if s["expected"]:
            lines.append(f'- **{s["bot"]}** ({s["planted"]} planted): {s["detected_as"]}')
    lines += ["", "## Final learner model, trial by trial", ""]
    for bot, trials in trials_by_bot.items():
        lines.append(f"**{bot}**")
        lines.append("")
        lines.append("| Trial | Games | " + " | ".join(KINDS) + " |")
        lines.append("|---|---|" + "---|" * len(KINDS))
        for t in trials:
            cells = [f'{r["misses"]}/{r["chances"]} {r["status"]}' for r in t["final"]]
            lines.append(f'| seed {t["seed"]} | {t["games"]} | ' + " | ".join(cells) + " |")
        lines.append("")
    lines += [
        "Cells read `misses/chances status`. *pattern* = at least 80% sure the rate is above the "
        "kind's bar; *fine* = at least 80% sure it's below; *unsure* = not enough evidence yet.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


RECORDS = Path("learner_eval_records.json")


def main():
    quick = "--quick" in sys.argv
    trials_n, moves = (2, 15) if quick else (TRIALS, MOVES_PER_TRIAL)
    trials_by_bot, scores = {}, []
    if "--rescore" in sys.argv:            # re-score saved games; no engine needed
        saved = json.loads(RECORDS.read_text(encoding="utf-8"))
        trials_by_bot = {bot: [score_trial(t) for t in ts] for bot, ts in saved.items()}
    for bot in BOTS:
        if bot not in trials_by_bot:
            trials_by_bot[bot] = [run_trial(bot, seed, moves=moves) for seed in range(trials_n)]
        for t in trials_by_bot[bot]:
            print(f"{bot:7s} seed {t['seed']}: {t['games']} games, planted {len(t['planted'])}, "
                  f"patterns at end {sorted(t['history'][-1]) or '-'}", flush=True)
        scores.append(score_bot(bot, trials_by_bot[bot]))
    print()
    for s in scores:
        print(s)
    if not quick:
        write_report(scores, trials_by_bot, Path("learner_eval.md"))
        # Save only the raw graded moves: everything else is re-derived by score_trial.
        RECORDS.write_text(json.dumps(
            {bot: [{k: t[k] for k in ("bot", "seed", "games", "moves")} for t in ts]
             for bot, ts in trials_by_bot.items()}, indent=1), encoding="utf-8")
        print(f"\nwrote learner_eval.md and {RECORDS}")


if __name__ == "__main__":
    main()
