"""Draw a chess position to a PIL image, and map a pixel click back to a square.

Why Pillow and not SVG: the "Play a game" board has to render a *clickable* image,
and it has to look identical locally and on Streamlit Cloud. SVG->PNG needs cairo
(a system lib that's a headache on Cloud); Pillow is already a dependency, pure
Python, and needs no system libs. Fixed square geometry (SQUARE px per square) also
makes click->square a one-liner — see `click_to_square`.

Pieces are Unicode chess glyphs from whatever chess-capable font the host has, found
the same belt-and-suspenders way the engine is (`find_engine`): try the font that
ships on Streamlit Cloud's Debian first, then the Windows/macOS ones. We always draw
the *solid* (filled) glyph and recolor it — white pieces filled white with a dark
outline, black pieces filled dark with a light outline — because the dedicated
"white" code points are hollow outlines that vanish on a light board.
"""

import os
import chess
from PIL import Image, ImageDraw, ImageFont

# --- Geometry -------------------------------------------------------------
SQUARE = 60                 # one square, in pixels
BOARD = SQUARE * 8          # the 8x8 grid edge (480px)
MARGIN = 24                 # coordinate border around the grid
SIZE = BOARD + 2 * MARGIN   # full image edge (528px)

# --- Palette (matches app.py's boxwood-and-walnut board) ------------------
LIGHT = (240, 230, 210)     # #f0e6d2  light square
DARK = (176, 141, 87)       # #b08d57  dark square
LAST_LIGHT = (226, 221, 150)  # last-move tint on a light square
LAST_DARK = (190, 167, 92)    # last-move tint on a dark square
SEL_LIGHT = (214, 205, 150)   # selected square
SEL_DARK = (170, 150, 95)
DOT = (60, 50, 40, 90)        # legal-target dot (RGBA, semi-transparent)
RING = (60, 50, 40, 150)      # capture-target ring
CHECK = (200, 70, 60)         # king-in-check glow
MARGIN_BG = (250, 247, 240)   # #faf7f0  paper — the coordinate border
LABEL = (92, 71, 51)          # #5c4733  walnut — coordinate text
OUTLINE = (92, 71, 51)        # thin frame between the grid and the border

WHITE_FILL = (250, 247, 240)
WHITE_EDGE = (43, 38, 34)
BLACK_FILL = (43, 38, 34)
BLACK_EDGE = (235, 226, 208)

# The filled silhouette glyphs (the Unicode "black" pieces); we recolor per side.
GLYPHS = {
    chess.KING: "♚",
    chess.QUEEN: "♛",
    chess.ROOK: "♜",
    chess.BISHOP: "♝",
    chess.KNIGHT: "♞",
    chess.PAWN: "♟",
}

# Candidate fonts: Cloud (Debian) first, then Windows, then macOS. Pieces need a
# chess-glyph font; the coordinate labels just need plain letters/digits (some
# symbol fonts lack Latin), so they get their own text-font list.
_PIECE_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "DejaVuSans.ttf",
    "C:/Windows/Fonts/seguisym.ttf",       # Segoe UI Symbol
    "C:/Windows/Fonts/ARIALUNI.TTF",        # Arial Unicode MS
    "/System/Library/Fonts/Apple Symbols.ttf",
)
_LABEL_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arialbd.ttf",         # Arial Bold
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
)


def _load_font(size, candidates):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    # Last resort so we never hard-crash; glyphs fall back to a tiny bitmap.
    return ImageFont.load_default()


_PIECE_FONT = _load_font(int(SQUARE * 0.74), _PIECE_FONT_CANDIDATES)
_LABEL_FONT = _load_font(15, _LABEL_FONT_CANDIDATES)


# --- Screen <-> board square mapping --------------------------------------
# Drawn normally, the top-left square is a8; flipped, it's h1. Geometry is fixed
# (grid offset by MARGIN), so both directions are pure arithmetic.

def _square_to_xy(square, flipped):
    """Top-left pixel of `square`'s cell, inside the coordinate border."""
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    col = 7 - file if flipped else file
    row = rank if flipped else 7 - rank
    return MARGIN + col * SQUARE, MARGIN + row * SQUARE


def click_to_square(x, y, flipped=False):
    """Map a pixel click on the rendered board to a chess square (or None if the
    click landed in the coordinate border / outside the 8x8 grid). Subtract the
    border offset first, so callers can pass raw image coordinates unchanged."""
    bx, by = int(x) - MARGIN, int(y) - MARGIN
    if bx < 0 or by < 0 or bx >= BOARD or by >= BOARD:
        return None
    col, row = bx // SQUARE, by // SQUARE
    file = 7 - col if flipped else col
    rank = row if flipped else 7 - row
    return chess.square(file, rank)


# --- Rendering ------------------------------------------------------------

def render_board(board, *, flipped=False, selected=None, lastmove=None):
    """Return a PIL.Image of `board`.

    selected   square currently picked up — its cell is highlighted and every
               legal target is dotted (captures get a ring instead).
    lastmove   chess.Move just played — both its squares are tinted so the eye
               lands on what changed.
    """
    img = Image.new("RGB", (SIZE, SIZE), MARGIN_BG)
    draw = ImageDraw.Draw(img, "RGBA")

    last_squares = {lastmove.from_square, lastmove.to_square} if lastmove else set()
    targets = []
    if selected is not None:
        targets = [m for m in board.legal_moves if m.from_square == selected]

    # 1. Squares (with selection / last-move tints).
    for square in chess.SQUARES:
        x, y = _square_to_xy(square, flipped)
        is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
        if square == selected:
            color = SEL_LIGHT if is_light else SEL_DARK
        elif square in last_squares:
            color = LAST_LIGHT if is_light else LAST_DARK
        else:
            color = LIGHT if is_light else DARK
        draw.rectangle([x, y, x + SQUARE, y + SQUARE], fill=color)

    # 2. King-in-check glow.
    if board.is_check():
        king_sq = board.king(board.turn)
        if king_sq is not None:
            x, y = _square_to_xy(king_sq, flipped)
            draw.ellipse(
                [x + 4, y + 4, x + SQUARE - 4, y + SQUARE - 4],
                outline=CHECK, width=4,
            )

    # 3. Pieces.
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        x, y = _square_to_xy(square, flipped)
        cx, cy = x + SQUARE / 2, y + SQUARE / 2
        if piece.color == chess.WHITE:
            fill, edge = WHITE_FILL, WHITE_EDGE
        else:
            fill, edge = BLACK_FILL, BLACK_EDGE
        draw.text(
            (cx, cy), GLYPHS[piece.piece_type], font=_PIECE_FONT,
            fill=fill, anchor="mm", stroke_width=2, stroke_fill=edge,
        )

    # 4. Legal-target markers (drawn last, on top of the pieces they'd capture).
    for m in targets:
        x, y = _square_to_xy(m.to_square, flipped)
        cx, cy = x + SQUARE / 2, y + SQUARE / 2
        if board.is_capture(m):
            r = SQUARE / 2 - 4
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RING, width=5)
        else:
            r = SQUARE * 0.16
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DOT)

    # 5. Coordinate border: a thin frame, then files (a–h) on top and bottom and
    # ranks (1–8) down both sides. Labels follow the flip so they always name the
    # square they sit beside.
    draw.rectangle([MARGIN, MARGIN, MARGIN + BOARD, MARGIN + BOARD], outline=OUTLINE, width=1)
    for i in range(8):
        file_letter = chess.FILE_NAMES[7 - i if flipped else i]
        rank_number = str(i + 1 if flipped else 8 - i)
        center = MARGIN + i * SQUARE + SQUARE / 2
        draw.text((center, MARGIN / 2), file_letter, font=_LABEL_FONT, fill=LABEL, anchor="mm")
        draw.text((center, SIZE - MARGIN / 2), file_letter, font=_LABEL_FONT, fill=LABEL, anchor="mm")
        draw.text((MARGIN / 2, center), rank_number, font=_LABEL_FONT, fill=LABEL, anchor="mm")
        draw.text((SIZE - MARGIN / 2, center), rank_number, font=_LABEL_FONT, fill=LABEL, anchor="mm")

    return img


def legal_targets(board, frm):
    """Squares a piece on `frm` can legally move to (for highlight logic)."""
    return {m.to_square for m in board.legal_moves if m.from_square == frm}


# --- Self-test: render a couple of positions to PNGs to eyeball them -------
if __name__ == "__main__":
    b = chess.Board()
    render_board(b).save("_board_start.png")

    b2 = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")
    e2 = chess.E2  # white pawn; show its targets
    render_board(b2, selected=chess.F1, lastmove=chess.Move.from_uci("e7e5")).save("_board_sel.png")
    print("Wrote _board_start.png and _board_sel.png")
    # A click in the border returns None; centres of the corner squares resolve.
    print("click in border (4,4) ->", click_to_square(4, 4), "(expect None)")
    a8 = (MARGIN + SQUARE // 2, MARGIN + SQUARE // 2)
    print("click a8 centre", a8, "->", chess.square_name(click_to_square(*a8)), "(expect a8)")
    print("click a8 centre flipped ->", chess.square_name(click_to_square(*a8, flipped=True)), "(expect h1)")
