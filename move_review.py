import io
import math
import chess
import chess.engine
import chess.pgn
from engine_analysis import render_line
from engine_pool import analyse, DEFAULT_DEPTH

def _pov_score(info, color):
    """Return the score in centipawns from `color`'s perspective.
    Mate is converted to a large number so comparisons still work."""
    score = info["score"].pov(color)
    if score.is_mate():
        # A forced mate is worth more than any normal material edge. Test the
        # sign by comparison, not `mate() > 0`: when `color` has just delivered
        # mate the score is MateGiven, whose mate() is 0 — that check read it as
        # being mated, grading a mating move that wasn't the engine's pick
        # (Rb8# when it listed Ra8#) a Blunder.
        return 10000 if score > chess.engine.Cp(0) else -10000
    return score.score()


def _review_from_infos(board, played_move, info_before, info_after):
    """Build the review dict for `played_move` from the two engine analyses:
    `info_before` for `board` (the position the move was played from, left
    untouched) and `info_after` for the position it leads to. Shared by
    review_move (which runs both searches itself) and review_game (where
    consecutive moves share a position, so each analysis is reused as the next
    move's "before" instead of being searched twice)."""
    mover_color = board.turn  # whose move we are judging

    # 1. Best available, from the pre-move analysis.
    best_score = _pov_score(info_before, mover_color)          # from mover's POV
    best_move_obj = info_before["pv"][0]                        # the engine's pick
    best_move = board.san(best_move_obj)                       # readable best move

    # 2. The player's actual move. After it, it's the opponent's turn, so the
    # engine reports from THEIR side; flip back to the mover's perspective.
    played_san = board.san(played_move)
    played_score = _pov_score(info_after, mover_color)

    # The engine's line *after* the played move (opponent to move first). For a
    # weak move this IS the refutation: it shows concretely how the opponent
    # punishes it — the reply that was overlooked, the piece or square that
    # falls. That's the "why was my move wrong" the coach needs, and it's an
    # engine fact (we render and narrate it, never invent it). Rendered as SAN
    # from the post-move position; kept to a few plies to stay coachable, but
    # never cut in the middle of a capture exchange (see render_line).
    line_board = board.copy()
    line_board.push(played_move)
    refutation = render_line(line_board, info_after.get("pv", []))

    # 3. The gap = how much the player gave up, in centipawns. Never negative.
    centipawn_loss = max(0, best_score - played_score)

    # Same gap expressed as win chance — this is what the label is based on.
    best_win = win_chance(best_score)
    played_win = win_chance(played_score)
    win_prob_drop = max(0.0, best_win - played_win)

    # 4. Map the move to a label using the win-% the move gave up.
    label = classify_move(best_score, played_score, played_move == best_move_obj)

    # 5. For a weak move, what KIND of mistake it was — read off the same two
    # engine lines the coach sees. The best line is kept in the review so the
    # kind can be checked by hand against the lines it came from.
    best_line = render_line(board, info_before.get("pv", []))
    mistake_type = classify_mistake(board, played_move, info_before, info_after, label)

    return {
        "fen": board.fen(),
        "played_move": played_san,
        "played_move_uci": played_move.uci(),
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
        "best_line": best_line,
        "mistake_type": mistake_type,
    }


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
    played_move = chess.Move.from_uci(played_move_uci)
    info_before = analyse(board, depth=depth)
    after = board.copy()
    after.push(played_move)
    info_after = analyse(after, depth=depth)
    return _review_from_infos(board, played_move, info_before, info_after)


def review_game(pgn_text, depth=DEFAULT_DEPTH, progress=None):
    """Grade every move of a finished game from its PGN.

    PGN (Portable Game Notation) is the standard text export chess sites use.
    We replay the game's mainline and grade each move with the exact facts
    review_move would produce — same engine, same depth, same labels. The one
    difference is cost: the position after one move IS the position before the
    next, and the engine is deterministic, so each position is searched once
    and reused, not searched twice.

    `progress(done, total)` is called after each graded move so the UI can
    show a bar. Returns a list of {"move_no", "color", "review"} dicts, one
    per half-move, in game order. Raises ValueError on an unusable PGN.
    """
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("That doesn't look like a PGN game.")
    moves = list(game.mainline_moves())
    if not moves:
        raise ValueError("The PGN parsed, but no moves were found in it.")

    board = game.board()          # honours a "FEN" header if the game has one
    entries = []
    info_before = analyse(board, depth=depth)
    for i, move in enumerate(moves):
        move_no = board.fullmove_number
        color = "White" if board.turn == chess.WHITE else "Black"
        after = board.copy()
        after.push(move)
        info_after = analyse(after, depth=depth)
        entries.append({
            "move_no": move_no,
            "color": color,
            "review": _review_from_infos(board, move, info_before, info_after),
        })
        board, info_before = after, info_after
        if progress:
            progress(i + 1, len(moves))
    return entries


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


# The standard teaching count, in pawns. Kings are left out: they're never
# captured, only mated, and mate is checked separately.
PIECE_VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                chess.ROOK: 5, chess.QUEEN: 9}

# Only these labels get a mistake kind; Best/Excellent/Good aren't mistakes.
WEAK_LABELS = ("Inaccuracy", "Mistake", "Blunder")


def material(board, color):
    """`color`'s material balance in pawns: its pieces minus the opponent's."""
    return sum(
        value * (len(board.pieces(pt, color)) - len(board.pieces(pt, not color)))
        for pt, value in PIECE_VALUES.items()
    )


def _material_at_line_end(board, moves, color):
    """`color`'s material where the displayed engine line ends. render_line never
    stops mid-exchange, so the count is taken once a trade is finished — not
    halfway through, where it would show a piece "lost" that the next move wins
    back."""
    end = board.copy()
    for move in moves[:len(render_line(board, moves))]:
        end.push(move)
    return material(end, color)


def classify_mistake(board, played_move, info_before, info_after, label):
    """Name the KIND of mistake a weak move was; None if the move wasn't weak.

    This is a chess fact, so it comes from the engine, not the language model.
    It compares the engine's two lines — its best line from before the move,
    and its line after the move actually played (the refutation) — on mate and
    on a plain material count where each line ends:

      allowed_mate     after your move, the opponent has a forced mate
      missed_mate      you had a forced mate and your move let it go
      lost_material    the line after your move leaves you with less material
                       than you have now (e.g. a piece left hanging)
      missed_material  you lost nothing, but the best line won material you
                       didn't take
      positional       mate and material don't explain the gap: the loss is in
                       the position (activity, pawns, king safety, time). We
                       deliberately don't say which — the engine doesn't tell us.

    Checked in that order: a mate ends the game, and a concrete material loss
    is the first thing a player should fix. Limit: it only sees as far as the
    lines go (~6 plies), so a loss that lands later reads as "positional".
    These kinds are what the learner model counts across a game.
    """
    if label not in WEAK_LABELS:
        return None
    mover = board.turn
    zero = chess.engine.Cp(0)
    best = info_before["score"].pov(mover)
    played = info_after["score"].pov(mover)
    if played.is_mate() and played < zero and not (best.is_mate() and best < zero):
        return "allowed_mate"
    if best.is_mate() and best > zero and not (played.is_mate() and played > zero):
        return "missed_mate"

    now = material(board, mover)
    after_best = _material_at_line_end(board, info_before.get("pv", []), mover)
    played_board = board.copy()
    played_board.push(played_move)
    after_played = _material_at_line_end(played_board, info_after.get("pv", []), mover)
    if after_best - after_played >= 1:           # the two lines differ by a pawn+
        return "lost_material" if after_played < now else "missed_material"
    return "positional"


if __name__ == "__main__":
    # Ruy Lopez position, White to move. Try a good move and a bad one.
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    print("Good move (Bb5):", review_move(fen, "f1b5"))
    print("Bad move (a3):  ", review_move(fen, "a2a3"))

    # One weak move per mistake kind, plus a mating move that isn't the
    # engine's pick (it used to be graded a Blunder — see _pov_score).
    print("\nMistake kinds:")
    kind_cases = [
        ("lost_material", "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2", "d8g5"),
        ("missed_material", "rnb1kbnr/pppp1ppp/8/4p1q1/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", "d2d3"),
        ("allowed_mate", "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3", "g8f6"),
        ("missed_mate", "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4", "h5e2"),
        ("positional", "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2", "e1e2"),
        (None, "7k/6pp/8/8/8/8/8/RR4K1 w - - 0 1", "b1b8"),
    ]
    for expected, kind_fen, uci in kind_cases:
        r = review_move(kind_fen, uci)
        status = "ok" if r["mistake_type"] == expected else "WRONG"
        print(f'  {status:5s} {r["played_move"]:5s} {r["label"]:10s} '
              f'kind={r["mistake_type"]} (expected {expected})')

    # A short miniature (Scholar's Mate) through the full-game path. The last
    # move is checkmate, so this also proves grading survives a terminal
    # position (no legal moves, no refutation line).
    pgn = "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0"
    print("\nFull game review:")
    for e in review_game(pgn, progress=lambda d, t: print(f"  graded {d}/{t}")):
        r = e["review"]
        print(f'  {e["move_no"]}. {e["color"]:5s} {r["played_move"]:6s} '
              f'{r["label"]:10s} (best {r["best_move"]})')