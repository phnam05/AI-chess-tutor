"""Generate the board images used in README.md, straight from the app's own
rendering code so they match the live UI exactly — no hand-drawn mock-ups.

  python scripts/make_readme_images.py     # writes into ./images, prints the facts

The Analyze/Review tabs render python-chess SVG; the Play tab renders the Pillow
board (board_ui). We reuse each, with the same colours/sizes app.py uses, so the
README shows the actual renderers. The Review example runs Stockfish, so the
verdict and the "engine's best" arrow are the engine's real output, not invented
(needs stockfish.exe locally / stockfish on PATH).
"""
import os
import sys
import chess
import chess.svg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from board_ui import render_board                 # the Pillow board (Play a game)
from move_review import review_move               # real engine verdict for Review

# Mirror app.py exactly.
BOARD_COLORS = {"square light": "#f0e6d2", "square dark": "#b08d57"}
DEFAULT_FEN = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
# QUALITY colours from app.py, for the played-move arrow.
VERDICT = {"Best": "#1a7f5a", "Excellent": "#4a9d6e", "Good": "#7fae5a",
           "Inaccuracy": "#d8a838", "Mistake": "#d97742", "Blunder": "#c0392b"}
BEST_GREEN = "#1a7f5a"

IMG = os.path.join(ROOT, "images")
os.makedirs(IMG, exist_ok=True)


def _write_svg(name, svg):
    path = os.path.join(IMG, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.relpath(path, ROOT))


def _move_board_svg(fen, uci, *, arrow_color, size=320):
    """One move played out, from/to squares lit and a coloured arrow — exactly
    app.py's move_board_svg(after=True)."""
    bd = chess.Board(fen)
    mv = chess.Move.from_uci(uci)
    bd.push(mv)
    arrow = chess.svg.Arrow(mv.from_square, mv.to_square, color=arrow_color)
    return chess.svg.board(bd, size=size, lastmove=mv, arrows=[arrow], colors=BOARD_COLORS)


# 1. Analyze a position — the exact board the Analyze tab shows.
_write_svg("analyze-position.svg",
           chess.svg.board(chess.Board(DEFAULT_FEN), size=380, colors=BOARD_COLORS))

# 2. Review a move — a natural developing move (...Nf6, which even attacks the
#    queen) that walks into Scholar's mate. The engine grades it and names its
#    own best reply; we render both boards the way the Review result does.
b = chess.Board()
for mv in ["e4", "e5", "Bc4", "Nc6", "Qh5"]:
    b.push_san(mv)
review_fen = b.fen()
played_uci = b.parse_san("Nf6").uci()
rv = review_move(review_fen, played_uci)
_write_svg("review-you.svg",
           _move_board_svg(review_fen, rv["played_move_uci"],
                           arrow_color=VERDICT.get(rv["label"], "#888")))
_write_svg("review-best.svg",
           _move_board_svg(review_fen, rv["best_move_uci"], arrow_color=BEST_GREEN))

# 3. Play a game — the Pillow board with a piece picked up (legal-target dots)
#    and the last move tinted, exactly what a click shows mid-game.
play = chess.Board(DEFAULT_FEN)
render_board(play, selected=chess.F1,
             lastmove=chess.Move.from_uci("e7e5")).save(os.path.join(IMG, "play-game.png"))
print("wrote", os.path.relpath(os.path.join(IMG, "play-game.png"), ROOT))

# 4. Hero banner — a clean Italian-game tabiya, last move tinted (no selection).
hero = chess.Board()
for mv in ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "c3", "Nf6", "d4"]:
    hero.push_san(mv)
render_board(hero, lastmove=hero.move_stack[-1]).save(os.path.join(IMG, "hero.png"))
print("wrote", os.path.relpath(os.path.join(IMG, "hero.png"), ROOT))

# Print the real facts so the README captions stay faithful to the engine.
# (We read the engine's best move via review_move; analyze_position would work
# too — both now share the one engine in engine_pool.)
an = review_move(DEFAULT_FEN, "a2a3")   # any legal move; we only read the engine's best
print("\n--- faithful facts for captions ---")
print(f"Analyze: best {an['best_move']}, eval {an['best_eval']} (White POV)")
print(f"Review FEN: {review_fen}")
print(f"Played {rv['played_move']} -> {rv['label']}: "
      f"win {rv['best_win_pct']}% -> {rv['played_win_pct']}% "
      f"(drop {rv['win_prob_drop']} pts), eval {rv['best_eval']} -> {rv['played_eval']}")
print(f"Engine best: {rv['best_move']} ({rv['best_move_uci']})")
