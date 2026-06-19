import math
import chess
from engine_pool import analyse, DEFAULT_DEPTH

def _pov_score(info, color):
    """Return the score in centipawns from `color`'s perspective.
    Mate is converted to a large number so comparisons still work."""
    score = info["score"].pov(color)
    if score.is_mate():
        # A forced mate is worth more than any normal material edge.
        return 10000 if score.mate() > 0 else -10000
    return score.score()


def review_move(fen, played_move_uci, depth=DEFAULT_DEPTH):
    """
    Judge a single move. Returns the engine's best move, the move the
    player actually made, how much was lost, and a quality label.
    `played_move_uci` is a move like 'e2e4' or 'g8f6'.

    Both positions are searched to the same depth on the shared, persistent
    engine (see engine_pool), so the two evals are directly comparable and the
    whole review costs ~0.1s instead of a spawn plus two one-second searches.
    """
    board = chess.Board(fen)
    mover_color = board.turn  # whose move we are judging

    # 1. Best available: evaluate the position before the move.
    info_before = analyse(board, depth=depth)
    best_score = _pov_score(info_before, mover_color)          # from mover's POV
    best_move_obj = info_before["pv"][0]                        # the engine's pick
    best_move = board.san(best_move_obj)                       # readable best move

    # 2. The player's actual move: play it, then evaluate the result.
    played_move = chess.Move.from_uci(played_move_uci)
    played_san = board.san(played_move)                        # readable, before pushing
    board.push(played_move)
    info_after = analyse(board, depth=depth)
    # After the move it's the opponent's turn, so the engine reports from THEIR
    # side. Flip it back to the mover's perspective.
    played_score = _pov_score(info_after, mover_color)

    # The engine's line *after* the played move (opponent to move first). For a
    # weak move this IS the refutation: it shows concretely how the opponent
    # punishes it — the reply that was overlooked, the piece or square that
    # falls. That's the "why was my move wrong" the coach needs, and it's an
    # engine fact (we render and narrate it, never invent it). Rendered as SAN
    # from the post-move position; capped at a few plies to stay coachable.
    refutation = []
    line_board = board.copy()
    for mv in info_after.get("pv", [])[:6]:
        try:
            refutation.append(line_board.san(mv))
        except (ValueError, AssertionError):
            break
        line_board.push(mv)

    # 3. The gap = how much the player gave up, in centipawns. Never negative.
    centipawn_loss = max(0, best_score - played_score)

    # Same gap expressed as win chance — this is what the label is based on.
    best_win = win_chance(best_score)
    played_win = win_chance(played_score)
    win_prob_drop = max(0.0, best_win - played_win)

    # 4. Map the move to a label using the win-% the move gave up.
    label = classify_move(best_score, played_score, played_move == best_move_obj)

    return {
        "fen": fen,
        "played_move": played_san,
        "played_move_uci": played_move_uci,
        "best_move": best_move,
        "best_move_uci": best_move_obj.uci(),
        "best_eval": f"{best_score/100:+.2f}",
        "played_eval": f"{played_score/100:+.2f}",
        "centipawn_loss": centipawn_loss,
        "best_win_pct": round(best_win, 1),
        "played_win_pct": round(played_win, 1),
        "win_prob_drop": round(win_prob_drop, 1),
        "label": label,
        "refutation": refutation,
    }


def win_chance(cp):
    """Convert a centipawn eval to a 0-100 win chance for the side to move.

    This is the logistic curve chess.com / Lichess use: equal (0 cp) maps to
    50%, and the curve flattens at the extremes so a swing matters far more in
    a close game than when one side is already winning. The constant was fit to
    real game outcomes. Clamp first so a mate score doesn't overflow exp().
    """
    cp = max(-1000, min(1000, cp))
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * cp)) - 1)


def classify_move(best_score, played_score, is_best):
    """Label a move by how much win chance it gave up, chess.com style.

    Grading on win-% drop (not raw centipawns) makes the same eval swing count
    for more in a tight game than in a lopsided one.
    """
    if is_best:
        return "Best"
    drop = win_chance(best_score) - win_chance(played_score)   # percentage points
    if drop < 1:
        return "Excellent"
    if drop < 3:
        return "Good"
    if drop < 8:
        return "Inaccuracy"
    if drop < 15:
        return "Mistake"
    return "Blunder"


if __name__ == "__main__":
    # Ruy Lopez position, White to move. Try a good move and a bad one.
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    print("Good move (Bb5):", review_move(fen, "f1b5"))
    print("Bad move (a3):  ", review_move(fen, "a2a3"))