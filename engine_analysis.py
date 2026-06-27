import chess
from engine_pool import analyse, DEFAULT_DEPTH

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
    pv_moves = info.get("pv", [])
    # Convert the line to human notation by replaying it on a copy of the board.
    pv_board = board.copy()
    pv_san = []
    for move in pv_moves[:6]:          # first 6 plies is plenty for an explanation
        pv_san.append(pv_board.san(move))
        pv_board.push(move)

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
