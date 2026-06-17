import chess
import chess.engine

ENGINE_PATH = "stockfish.exe"

def _pov_score(info, color):
    """Return the score in centipawns from `color`'s perspective.
    Mate is converted to a large number so comparisons still work."""
    score = info["score"].pov(color)
    if score.is_mate():
        # A forced mate is worth more than any normal material edge.
        return 10000 if score.mate() > 0 else -10000
    return score.score()


def review_move(fen, played_move_uci, think_time=1.0):
    """
    Judge a single move. Returns the engine's best move, the move the
    player actually made, how much was lost, and a quality label.
    `played_move_uci` is a move like 'e2e4' or 'g8f6'.
    """
    board = chess.Board(fen)
    mover_color = board.turn  # whose move we are judging

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    # 1. Best available: evaluate the position before the move.
    info_before = engine.analyse(board, chess.engine.Limit(time=think_time))
    best_score = _pov_score(info_before, mover_color)          # from mover's POV
    best_move = board.san(info_before["pv"][0])                # readable best move

    # 2. The player's actual move: play it, then evaluate the result.
    played_move = chess.Move.from_uci(played_move_uci)
    played_san = board.san(played_move)                        # readable, before pushing
    board.push(played_move)
    info_after = engine.analyse(board, chess.engine.Limit(time=think_time))
    # After the move it's the opponent's turn, so the engine reports from THEIR
    # side. Flip it back to the mover's perspective.
    played_score = _pov_score(info_after, mover_color)

    engine.quit()

    # 3. The gap = how much the player gave up, in centipawns. Never negative.
    centipawn_loss = max(0, best_score - played_score)

    # 4. Map the loss to a label.
    label = classify_move(centipawn_loss, played_move == info_before["pv"][0])

    return {
        "fen": fen,
        "played_move": played_san,
        "best_move": best_move,
        "best_eval": f"{best_score/100:+.2f}",
        "played_eval": f"{played_score/100:+.2f}",
        "centipawn_loss": centipawn_loss,
        "label": label,
    }


def classify_move(loss, is_best):
    """Turn centipawn loss into a chess.com-style label."""
    if is_best:
        return "Best"
    if loss <= 20:
        return "Good"
    if loss <= 70:
        return "Inaccurate"
    if loss <= 100:
        return "Mistake"
    return "Blunder"


if __name__ == "__main__":
    # Ruy Lopez position, White to move. Try a good move and a bad one.
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    print("Good move (Bb5):", review_move(fen, "f1b5"))
    print("Bad move (a3):  ", review_move(fen, "a2a3"))