import chess
from engine_pool import analyse, DEFAULT_DEPTH


def render_line(board, moves, length=6):
    """Render an engine line (list of Move objects) as SAN for humans.

    Cut at `length` plies — but never in the middle of a capture exchange: keep
    going while the next move is a capture, so the line ends on a quiet move.
    A line cut one ply before a recapture reads as a piece hung for nothing
    (a real case: a PV shown as "... O-O-O, Qxf4" looked like White losing the
    queen; the very next ply was Bxf4, an even trade). Shared by the position
    line and the refutation so the two renderings can't drift apart.
    """
    board = board.copy()
    san = []
    for i, move in enumerate(moves):
        if i >= length and not board.is_capture(move):
            break
        try:
            san.append(board.san(move))
        except (ValueError, AssertionError):
            break  # a corrupt tail shouldn't kill the whole analysis
        board.push(move)
    return san


def analyze_position(fen, depth=DEFAULT_DEPTH):
    """
    Given a board position (as a FEN string), return the engine's
    key facts: best move, evaluation in centipawns, and the predicted line.
    """
    board = chess.Board(fen)

    # The engine is a shared, persistent process (see engine_pool) — reused
    # across calls instead of spawned per request.
    info = analyse(board, depth=depth)

    # --- 1. The score ---
    # .pov(board.turn) reframes the score from the moving side's perspective.
    score = info["score"].pov(board.turn)

    if score.is_mate():
        # Forced checkmate: report it as text instead of a number.
        eval_text = f"Mate in {score.mate()}"
        eval_centipawns = None
    else:
        eval_centipawns = score.score()          # an integer in centipawns
        eval_text = f"{eval_centipawns / 100:+.2f} pawns"  # e.g. "+0.45 pawns"

    # --- 2. The principal variation (predicted best line) ---
    # NOTE: this line is a *forecast*, not a promise. Deeper moves in it were
    # searched shallower than the first, so re-analysing a position reached by
    # following it can prefer a different, near-equal move. That is inherent to
    # fixed-depth search (every engine does it) — do not "fix" it by caching.
    pv_moves = info.get("pv", [])
    pv_san = render_line(board, pv_moves)   # ~6 plies, never cut mid-exchange

    # --- 3. The best move (first move of the line) ---
    best_move_san = pv_san[0] if pv_san else None
    # UCI too, so the UI can draw an arrow for the move (SAN can't address
    # squares). It's the same engine fact, just in the other notation.
    best_move_uci = pv_moves[0].uci() if pv_moves else None

    return {
        "fen": fen,
        "turn": "White" if board.turn == chess.WHITE else "Black",
        "best_move": best_move_san,
        "best_move_uci": best_move_uci,
        "eval_centipawns": eval_centipawns,
        "eval_text": eval_text,
        "principal_variation": pv_san,
    }


# --- Quick self-test: run this file directly to see it work ---
if __name__ == "__main__":
    # Starting position, written in FEN.
    start_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    result = analyze_position(start_fen)
    for key, value in result.items():
        print(f"{key}: {value}")
