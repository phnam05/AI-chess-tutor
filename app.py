import streamlit as st
import chess
import chess.svg
from engine_analysis import analyze_position
from explainer import explain_position, explain_move
from move_review import review_move, win_chance
from board_ui import render_board, click_to_square, SIZE as BOARD_PX
from streamlit_image_coordinates import streamlit_image_coordinates
from engine_pool import warmup

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Chess Tutor",
    page_icon="♟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Spawn the shared Stockfish now, while the page is loading, so the student's
# first move or analysis doesn't pay the engine's one-time launch cost mid-click.
warmup()

# ----------------------------------------------------------------------------
# Move-quality vocabulary. This is the heart of the tutor: every verdict the
# engine gives a move maps to a color and a short plain-language gloss, so the
# label teaches rather than just scores.
# ----------------------------------------------------------------------------
# `mark` is the move-log badge glyph — a distinct *shape* per tier (not just a
# color), so the three greens are still told apart at a glance, chess.com style.
QUALITY = {
    "Best":       {"color": "#1a7f5a", "mark": "★",  "gloss": "The strongest move available."},
    "Excellent":  {"color": "#4a9d6e", "mark": "!",  "gloss": "Nearly the engine's top choice."},
    "Good":       {"color": "#7fae5a", "mark": "✓",  "gloss": "A solid, principled move."},
    "Inaccuracy": {"color": "#d8a838", "mark": "?!", "gloss": "Playable, but a better idea was there."},
    "Mistake":    {"color": "#d97742", "mark": "?",  "gloss": "Loses meaningful ground."},
    "Blunder":    {"color": "#c0392b", "mark": "??", "gloss": "A serious error that changes the game."},
}

LEVELS = {
    "Beginner":     "beginner",
    "Intermediate": "intermediate",
    "Advanced":     "advanced",
}

# Warm boxwood-and-walnut board, matching the page palette.
BOARD_COLORS = {"square light": "#f0e6d2", "square dark": "#b08d57"}


def move_board_svg(fen, move_uci, *, after, arrow_color, size=320):
    """Render one move on a board.

    `after=True` plays the move first, so you see the resulting position with
    the from/to squares lit — the "here's what the move did" view used for both
    the played move and the engine's pick. `after=False` keeps the starting
    position (no piece moved), for showing a move purely as a suggestion. Either
    way a colored arrow traces the move from origin to target.
    """
    bd = chess.Board(fen)
    move = chess.Move.from_uci(move_uci)
    arrow = chess.svg.Arrow(move.from_square, move.to_square, color=arrow_color)
    lastmove = move if after else None
    if after:
        bd.push(move)
    return chess.svg.board(
        bd, size=size, lastmove=lastmove, arrows=[arrow], colors=BOARD_COLORS,
    )

# ----------------------------------------------------------------------------
# The app's single screen — an interactive, click-to-move board where the
# student plays BOTH sides and the coach reviews every move, plus a "Show best
# move" button that analyses whatever position is on the board (for whichever
# side is to move). The chess stays the engine's job: every move runs through
# review_move (the single source of truth for quality) and explain_move (which
# only phrases the verdict), and the hint runs through analyze_position /
# explain_position — all reused untouched. The only new logic here is the board
# UI + the session-state loop.
# ----------------------------------------------------------------------------
PROMO = {
    "Queen": chess.QUEEN, "Rook": chess.ROOK,
    "Bishop": chess.BISHOP, "Knight": chess.KNIGHT,
}


def _result_text(board):
    """Plain-language game result, for the turn indicator when the game ends."""
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"Checkmate — {winner} wins"
    if board.is_stalemate():
        return "Draw — stalemate"
    if board.is_insufficient_material():
        return "Draw — not enough material to mate"
    if board.is_seventyfive_moves():
        return "Draw — seventy-five-move rule"
    if board.is_fivefold_repetition():
        return "Draw — repetition"
    return "Game over"


def _init_game():
    """Reset to a fresh game. g_last_click is a watermark, not game state, so we
    only seed it (setdefault) — never clear it (see render_game for why)."""
    st.session_state.g_board = chess.Board()
    st.session_state.g_history = []
    st.session_state.g_from = None
    st.session_state.g_lastmove = None
    st.session_state.g_hint = None          # cached "best move here" analysis
    st.session_state.setdefault("g_last_click", None)
    st.session_state.setdefault("g_flip", False)


def _build_move(board, frm, to):
    """frm->to as a Move, promoting (to the selector's piece, default queen)
    when a pawn lands on the back rank."""
    piece = board.piece_at(frm)
    if piece and piece.piece_type == chess.PAWN and chess.square_rank(to) in (0, 7):
        return chess.Move(frm, to, promotion=PROMO[st.session_state.get("g_promo", "Queen")])
    return chess.Move(frm, to)


def _play_and_review(move):
    """Grade the move with the engine — the single source of truth — and push it.
    review_move already scores from board.turn's side, so each colour is judged
    correctly. No LLM here: the coach's prose costs an API call, so it's fetched
    later and only if the student asks for it (see _render_coach_panel)."""
    board = st.session_state.g_board
    fen = board.fen()
    mover = "White" if board.turn == chess.WHITE else "Black"
    move_no = board.fullmove_number
    review = review_move(fen, move.uci())
    board.push(move)
    st.session_state.g_lastmove = move
    st.session_state.g_history.append({
        "move_no": move_no, "color": mover,
        "review": review,     # full engine facts: label + win-chance/eval metrics
        "comment": None,      # LLM explanation, filled in on demand
    })


def _handle_click(sq):
    """Lichess-style selection rules for one click. Cancel-on-misclick: clicking
    anything that isn't a legal target simply puts the piece down."""
    board = st.session_state.g_board
    frm = st.session_state.g_from
    if sq is None:                                   # clicked off the board
        st.session_state.g_from = None
        return
    if frm is None:                                  # nothing picked up yet
        piece = board.piece_at(sq)
        if piece and piece.color == board.turn:
            st.session_state.g_from = sq             # pick up your own piece
        return
    if sq == frm:
        st.session_state.g_from = None               # click it again = put it down
        return
    piece = board.piece_at(sq)
    if piece and piece.color == board.turn:
        st.session_state.g_from = sq                 # switch to a different piece
        return
    move = _build_move(board, frm, sq)
    if move in board.legal_moves:
        with st.spinner("Grading your move…"):
            _play_and_review(move)
    st.session_state.g_from = None                   # moved, or misclick: clear it


def _render_coach_panel():
    """Right-hand column: the latest move's engine verdict + metrics (free with
    every move), the played-vs-best boards, and an opt-in coach explanation. The
    running move log lives in the left column (see _render_move_log). The engine
    grades; the LLM only speaks when the student asks."""
    st.markdown('<div class="eyebrow">The coach</div>', unsafe_allow_html=True)
    history = st.session_state.g_history
    if not history:
        st.markdown(
            '<div class="commentary">Play a move for either side and I&rsquo;ll grade '
            'it &mdash; the verdict, the win-chance swing, and the engine&rsquo;s pick. '
            'Press <em>Explain this move</em> whenever you want it put into words.</div>',
            unsafe_allow_html=True,
        )
        return

    last = history[-1]
    review = last["review"]
    meta = QUALITY.get(review["label"], {"color": "#888", "gloss": ""})
    st.markdown(
        f'<div class="verdict" style="--vc:{meta["color"]}">'
        f'  <div class="label">{review["played_move"]} &mdash; {review["label"]}</div>'
        f'  <div class="gloss">{meta["gloss"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    # Whenever the move wasn't the engine's top pick — even a near-perfect
    # "Excellent" — name the best move beside the verdict.
    if review["best_move"] != review["played_move"]:
        st.markdown(
            f'<div class="movepair">Best move was '
            f'<span class="best">{review["best_move"]}</span></div>',
            unsafe_allow_html=True,
        )

    # The engine facts behind the verdict — the win-% swing, your winning
    # chances, and the eval — free with every move. Guarded so a stale review
    # dict degrades gracefully.
    metric_keys = ("win_prob_drop", "best_win_pct", "played_win_pct",
                   "best_eval", "played_eval", "centipawn_loss")
    if all(k in review for k in metric_keys):
        st.markdown(
            f'<div class="metrics">'
            f'  <div class="metric"><span class="mv">−{review["win_prob_drop"]:.1f}%</span>'
            f'    <span class="ml">win chance lost</span></div>'
            f'  <div class="metric"><span class="mv">{review["best_win_pct"]:.0f}% → {review["played_win_pct"]:.0f}%</span>'
            f'    <span class="ml">your winning chances</span></div>'
            f'  <div class="metric"><span class="mv">{review["best_eval"]} → {review["played_eval"]}</span>'
            f'    <span class="ml">engine eval ({review["centipawn_loss"]} cp lost)</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # The visual proof, right under the numbers: your move and the engine's pick
    # drawn side by side. This sits in the same top-of-column "board slot" the
    # hint uses before you move — the hint clears the moment you play, so only
    # one of the two is ever on screen, and it's visible without scrolling.
    _render_move_boards()

    # The explanation is opt-in: only call Gemini when the student presses the
    # button, then cache the prose on the move so reruns don't re-call it. We
    # also record the level it was written for: if the student changes the level
    # afterwards, the cached prose is stuck at the old level with no button to
    # redo it, so we offer a re-explain whenever the selected level has moved on.
    cur_label = st.session_state.get("g_level_label", "Intermediate")
    cur_level = LEVELS[cur_label]

    def _write_comment():
        with st.spinner("Coach is thinking…"):
            try:
                last["comment"] = explain_move(review, level=cur_level)
            except Exception:
                last["comment"] = "__unavailable__"
            last["comment_level"] = cur_level

    if not last["comment"]:
        if st.button("Explain this move", key=f"g_explain_{len(history)}"):
            _write_comment()
    elif last["comment"] != "__unavailable__" and last.get("comment_level") != cur_level:
        # Already explained, but the student has since picked a different level.
        if st.button(f"Re-explain for {cur_label}", key=f"g_reexplain_{len(history)}"):
            _write_comment()

    if last["comment"] == "__unavailable__":
        st.caption("Coach commentary unavailable — check GOOGLE_API_KEY. The engine verdict still stands.")
    elif last["comment"]:
        st.markdown(f'<div class="commentary">{last["comment"]}</div>', unsafe_allow_html=True)


def _render_move_log():
    """The running record of every move and its verdict chip. Lives in its own
    narrow panel on the far left, beside the board, so the coach column's verdict
    + boards + commentary can't keep pushing it off the bottom of the screen as
    they grow."""
    history = st.session_state.g_history
    if not history:
        return
    st.markdown('<div class="eyebrow">Move log</div>', unsafe_allow_html=True)

    # Pair the half-moves into chess.com-style rows: one full-move number with
    # White's and Black's move side by side. A row can be half-filled — Black
    # hasn't replied yet, or (from a FEN that starts on Black's move) there's no
    # White move. White's and Black's plies share the same fullmove number, so we
    # fold a Black ply into the open White row and otherwise start a new row.
    pairs = []
    for h in history:
        open_row = pairs[-1] if pairs else None
        if (h["color"] == "Black" and open_row
                and open_row["no"] == h["move_no"]
                and open_row["white"] is not None and open_row["black"] is None):
            open_row["black"] = h
        else:
            side = "white" if h["color"] == "White" else "black"
            pairs.append({"no": h["move_no"], "white": None, "black": None, side: h})

    def _cell(entry):
        """One move + a quality badge (full label on hover), or an empty slot."""
        if entry is None:
            return '<span class="logcell"></span>'
        hr = entry["review"]
        meta = QUALITY.get(hr["label"], {"color": "#888", "mark": ""})
        return (
            f'<span class="logcell" title="{hr["label"]}">{hr["played_move"]}'
            f'<span class="qpill" style="background:{meta["color"]}">{meta.get("mark", "")}</span></span>'
        )

    # Newest full-move first, so the latest move stays pinned at the top of the
    # scroll panel — no scrolling to see the move you just made.
    rows = []
    for p in reversed(pairs):
        white = (_cell(p["white"]) if p["white"] is not None
                 else '<span class="logcell muted">&hellip;</span>')
        rows.append(
            f'<div class="logrow"><span class="lognum">{p["no"]}.</span>'
            f'{white}{_cell(p["black"])}</div>'
        )
    # Fixed-height scroll panel so a long game can't run off the page.
    st.markdown(f'<div class="movelog">{"".join(rows)}</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False, max_entries=64)
def _board_image(fen, flipped, selected, lastmove_uci):
    """Render the Play board, cached by everything that affects how it looks.

    The board is redrawn on *every* Streamlit rerun — each click, but also each
    unrelated widget change (the level radio, the promote selectbox, Explain).
    Keying the render on visible state means only a genuinely new position or
    selection pays the ~25ms draw; the rest are instant lookups, so the board
    stays responsive between moves."""
    bd = chess.Board(fen)
    lm = chess.Move.from_uci(lastmove_uci) if lastmove_uci else None
    return render_board(bd, flipped=flipped, selected=selected, lastmove=lm)


def _render_hint(board):
    """The "best move here" coach — the old Analyze tab's single-position read,
    now a button beside the live board. It asks the engine for the strongest
    move in the CURRENT position (whichever side is to move) and shows it with
    the numbers; the written explanation is opt-in, like a move review. The
    result is keyed to the live FEN, so it shows only while the position is
    unchanged and clears itself the moment you play on. The engine supplies the
    move and eval; the LLM only phrases them."""
    if board.is_game_over():
        return
    cur_fen = board.fen()
    if st.button("Show best move", key="g_show_best", use_container_width=True):
        with st.spinner("Reading the position…"):
            st.session_state.g_hint = {
                "fen": cur_fen,
                "analysis": analyze_position(cur_fen),
                "comment": None,
                "comment_level": None,
            }

    hint = st.session_state.get("g_hint")
    if not hint or hint["fen"] != cur_fen:
        return
    analysis = hint["analysis"]

    st.markdown(
        f'<div class="movepair">Best move &nbsp;'
        f'<span class="best">{analysis["best_move"]}</span></div>',
        unsafe_allow_html=True,
    )

    # Draw the best move on the board with a green arrow, the same visual
    # language as the played-vs-best comparison below. after=True plays the move
    # so you see the resulting position with the from/to squares lit and the
    # arrow tracing it. `.get` so a stale analysis without the UCI degrades
    # gracefully.
    best_uci = analysis.get("best_move_uci")
    if best_uci:
        st.image(move_board_svg(analysis["fen"], best_uci, after=True, arrow_color="#1a7f5a"))

    # No played move here, so "win chance lost" doesn't apply: show the current
    # winning chance (with best play) and the eval, not a swing. Forced mate has
    # no centipawn number — it's 100% unless the mate is against the side to move.
    cp = analysis["eval_centipawns"]
    if cp is None:
        win_pct = 0.0 if "-" in analysis["eval_text"] else 100.0
    else:
        win_pct = win_chance(cp)
    st.markdown(
        f'<div class="metrics">'
        f'  <div class="metric"><span class="mv">{win_pct:.0f}%</span>'
        f'    <span class="ml">{analysis["turn"]}&rsquo;s winning chance</span></div>'
        f'  <div class="metric"><span class="mv">{analysis["eval_text"]}</span>'
        f'    <span class="ml">engine evaluation</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # The explanation is opt-in and cached on the hint, mirroring the move panel:
    # only call Gemini when asked, and offer a re-explain if the level has moved
    # on since the prose was written.
    cur_label = st.session_state.get("g_level_label", "Intermediate")
    cur_level = LEVELS[cur_label]

    def _write_comment():
        with st.spinner("Coach is thinking…"):
            try:
                hint["comment"] = explain_position(analysis, level=cur_level)
            except Exception:
                hint["comment"] = "__unavailable__"
            hint["comment_level"] = cur_level

    if not hint["comment"]:
        if st.button("Explain this position", key="g_hint_explain"):
            _write_comment()
    elif hint["comment"] != "__unavailable__" and hint.get("comment_level") != cur_level:
        if st.button(f"Re-explain for {cur_label}", key="g_hint_reexplain"):
            _write_comment()

    if hint["comment"] == "__unavailable__":
        st.caption("Coach commentary unavailable — check GOOGLE_API_KEY. The engine's move still stands.")
    elif hint["comment"]:
        st.markdown(f'<div class="commentary">{hint["comment"]}</div>', unsafe_allow_html=True)


def _render_move_boards():
    """Inside the coach column, under the verdict: the latest move drawn out —
    your move with its from/to squares lit and an arrow, and, when it wasn't the
    engine's pick, the engine's best beside it in green. This is the old Analyze
    tab's before/after comparison, kept for game mode. It renders straight from
    the stored review (pre-move FEN + both UCIs), so it's a pure redraw — no new
    engine call. Boards are kept small because the coach column is narrow."""
    history = st.session_state.g_history
    if not history:
        return
    review = history[-1]["review"]
    fen0 = review.get("fen")
    played_uci = review.get("played_move_uci")
    best_uci = review.get("best_move_uci")
    if not fen0 or not played_uci:        # stale review dict — degrade gracefully
        return
    meta = QUALITY.get(review["label"], {"color": "#888", "gloss": ""})
    is_best = bool(best_uci) and best_uci == played_uci

    st.markdown(
        '<div class="eyebrow" style="margin-top:6px;">The move on the board</div>',
        unsafe_allow_html=True,
    )

    if best_uci and not is_best:
        you_col, best_col = st.columns(2, gap="small")
        with you_col:
            st.markdown(
                f'<div class="boardcap" style="--vc:{meta["color"]}">'
                f'<div class="role">You played</div>'
                f'<div class="mv">{review["played_move"]}</div></div>',
                unsafe_allow_html=True,
            )
            st.image(move_board_svg(fen0, played_uci, after=True, arrow_color=meta["color"], size=210))
        with best_col:
            st.markdown(
                '<div class="boardcap" style="--vc:#1a7f5a">'
                '<div class="role">Engine&rsquo;s best</div>'
                f'<div class="mv">{review["best_move"]}</div></div>',
                unsafe_allow_html=True,
            )
            st.image(move_board_svg(fen0, best_uci, after=True, arrow_color="#1a7f5a", size=210))
    else:
        role = "You played &mdash; the engine&rsquo;s top choice" if is_best else "You played"
        st.markdown(
            f'<div class="boardcap" style="--vc:{meta["color"]}">'
            f'<div class="role">{role}</div>'
            f'<div class="mv">{review["played_move"]}</div></div>',
            unsafe_allow_html=True,
        )
        st.image(move_board_svg(fen0, played_uci, after=True, arrow_color=meta["color"], size=300))


def render_game():
    if "g_board" not in st.session_state:
        _init_game()
    # A game already in session state from before this version stored a flatter
    # per-move dict (no "review" key); reset it once so the panel can rely on the
    # new schema instead of crashing on a stale entry.
    stale = st.session_state.g_history
    if stale and "review" not in stale[0]:
        _init_game()

    # Three columns: the move log gets its own panel on the far left (beside the
    # board, not stacked beneath it), the board in the middle, the coach on the
    # right. Adding the log column necessarily narrows the board a little.
    log_col, left, right = st.columns([2, 5, 4], gap="large")

    with log_col:
        _render_move_log()

    with left:
        # --- Controls -------------------------------------------------------
        b1, b2, b3 = st.columns(3)
        if b1.button("New game", use_container_width=True):
            _init_game()
        if b2.button("Undo", use_container_width=True) and st.session_state.g_history:
            st.session_state.g_board.pop()
            st.session_state.g_history.pop()
            st.session_state.g_from = None
            stack = st.session_state.g_board.move_stack
            st.session_state.g_lastmove = stack[-1] if stack else None
        if b3.button("Flip board", use_container_width=True):
            st.session_state.g_flip = not st.session_state.get("g_flip", False)

        board = st.session_state.g_board
        flipped = st.session_state.get("g_flip", False)

        # --- Turn / result indicator ---------------------------------------
        if board.is_game_over():
            head = _result_text(board)
        else:
            head = f'{"White" if board.turn == chess.WHITE else "Black"} to move'
            if not st.session_state.g_history:
                head += " · click a piece to begin"
        st.markdown(f'<div class="eyebrow">{head}</div>', unsafe_allow_html=True)

        # --- The clickable board -------------------------------------------
        # streamlit_image_coordinates reports the LAST click and keeps reporting
        # it across reruns. We keep a watermark (g_last_click) of the click we
        # already acted on and ignore any rerun that reports that same click, so
        # that pressing a button (or the post-move rerun) can't replay a move.
        lm = st.session_state.g_lastmove
        img = _board_image(
            board.fen(), flipped, st.session_state.g_from,
            lm.uci() if lm else None,
        )
        # use_column_width="always" scales the board to the column width (CSS
        # width:100%) so its right edge — the rank labels and frame — never
        # overflows and gets clipped. ("auto" leaves it at natural 528px, which
        # the narrow column then cuts off.) The click comes back in *displayed*
        # pixels, so we rescale to the board's own pixels below.
        click = streamlit_image_coordinates(img, key="g_click", use_column_width="always")

        # --- Position as FEN: read it, copy it, or edit + Load it ----------
        # One box does both jobs the two old controls did separately: it always
        # shows the live position (refreshed after every move, undo, and new
        # game) so it can be copied as the game goes, and editing it + pressing
        # Load jumps the board to that position. We reseed the box from the board
        # only when the position *actually* changed — never on a plain rerun — so
        # a FEN the student is part-way through typing isn't wiped from under
        # them. (Seeding session state before the widget is the Streamlit-blessed
        # way to set a text_input's value programmatically.)
        cur_fen = board.fen()
        if st.session_state.get("g_fen_synced") != cur_fen:
            st.session_state["g_fen_box"] = cur_fen
            st.session_state["g_fen_synced"] = cur_fen
        st.caption("Position (FEN) — copy the live position, or edit it and press Load")
        fc1, fc2 = st.columns([5, 1])
        fen_text = fc1.text_input(
            "Position (FEN)", key="g_fen_box", label_visibility="collapsed",
        )
        if fc2.button("Load", use_container_width=True):
            try:
                nb = chess.Board(fen_text)
            except ValueError:
                st.error("That isn't a valid FEN.")
            else:
                _init_game()
                st.session_state.g_board = nb
                st.rerun()

        # --- Per-move controls ---------------------------------------------
        # The level only matters when the student asks for an explanation; the
        # coach panel reads it from session state (key) at that point.
        st.radio(
            "Explain for", list(LEVELS.keys()), index=1, horizontal=True,
            key="g_level_label",
        )
        st.selectbox("Promote a pawn to", list(PROMO.keys()), key="g_promo")

        # --- Act on a fresh click ------------------------------------------
        if click is not None:
            pt = (click["x"], click["y"])
            if pt != st.session_state.g_last_click:
                st.session_state.g_last_click = pt
                if not board.is_game_over():
                    # Convert the click from displayed pixels (the image may be
                    # scaled to fit the column) back to the board's own pixels.
                    disp_w = click.get("width") or BOARD_PX
                    disp_h = click.get("height") or BOARD_PX
                    sq = click_to_square(
                        click["x"] * BOARD_PX / disp_w,
                        click["y"] * BOARD_PX / disp_h,
                        flipped,
                    )
                    _handle_click(sq)
                st.rerun()

    with right:
        # "Show best move" lives at the top of the coach column — always on
        # screen (the column is top-aligned with the board), so it's reachable
        # without scrolling past the tall board, and its arrow board sits right
        # under the button. The coach's per-move verdict follows below.
        _render_hint(board)
        _render_coach_panel()

# ----------------------------------------------------------------------------
# Styling. The palette comes from the board itself — aged boxwood and walnut,
# the warm neutrals of a study set — rather than generic dashboard blue.
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

      :root {
        --ink:      #2b2622;
        --walnut:   #5c4733;
        --boxwood:  #e8dcc6;
        --line:     #d9cdb6;
        --paper:    #faf7f0;
      }

      .stApp { background: var(--paper); }

      /* Masthead */
      .masthead {
        border-bottom: 2px solid var(--ink);
        padding-bottom: 14px;
        margin-bottom: 28px;
      }
      .masthead h1 {
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 700;
        font-size: 2.6rem;
        line-height: 1.05;
        color: var(--ink);
        margin: 0;
        letter-spacing: -0.02em;
      }
      .masthead .sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.92rem;
        color: var(--walnut);
        margin-top: 4px;
      }

      /* Section eyebrows */
      .eyebrow {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--walnut);
        margin-bottom: 8px;
      }

      /* The verdict block — the signature element */
      .verdict {
        border-left: 5px solid var(--vc, #888);
        background: #ffffff;
        border-radius: 0 8px 8px 0;
        padding: 18px 22px;
        margin: 6px 0 18px 0;
        box-shadow: 0 1px 3px rgba(43,38,34,0.06);
      }
      .verdict .label {
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 1.5rem;
        color: var(--vc, #2b2622);
        line-height: 1;
      }
      .verdict .gloss {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: var(--walnut);
        margin-top: 4px;
      }

      .movepair {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: var(--ink);
        margin: 10px 0 16px 0;
      }
      .movepair .played { font-weight: 600; }
      .movepair .best   { font-weight: 600; color: var(--walnut); }

      /* The numbers behind the verdict */
      .metrics {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 0 0 16px 0;
      }
      .metric {
        background: #ffffff;
        border: 1px solid rgba(43,38,34,0.10);
        border-radius: 8px;
        padding: 8px 14px;
        display: flex;
        flex-direction: column;
      }
      .metric .mv {
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--ink);
        line-height: 1.1;
      }
      .metric .ml {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--walnut);
        margin-top: 2px;
      }

      /* The move log — a fixed-height scroll panel so a long game can't run off
         the page; newest move is pinned at the top. The scrollbar only appears
         once the rows overflow, which doubles as the "this scrolls" cue. */
      .movelog {
        max-height: 540px;
        overflow-y: auto;
        padding-right: 8px;        /* breathing room for the scrollbar */
      }
      .logrow {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 5px 2px;
        border-bottom: 1px solid var(--line);
        border-radius: 4px;
      }
      .logrow:hover { background: rgba(43,38,34,0.03); }
      .movelog .logrow:last-child { border-bottom: none; }
      .lognum {
        flex: none;
        width: 28px;
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: var(--walnut);
      }
      .logcell {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--ink);
      }
      .logcell.muted { color: var(--walnut); }
      .qpill {
        flex: none;
        min-width: 15px;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 0.62rem;
        font-weight: 700;
        line-height: 1;
        color: #fff;
        border-radius: 4px;
        padding: 2px 4px;
      }
      .movelog::-webkit-scrollbar { width: 8px; }
      .movelog::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; }
      .movelog::-webkit-scrollbar-thumb:hover { background: var(--walnut); }
      .movelog::-webkit-scrollbar-track { background: transparent; }

      /* Quiet the default Streamlit chrome. Wider than the old 1100px because
         the layout is now three columns (log | board | coach); the extra room
         brings the board back up to its pre-log-column size. */
      .block-container { padding-top: 2.2rem; max-width: 1320px; }
      .stRadio > label, .stSelectbox > label, .stTextInput > label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--ink);
      }
      .commentary {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        color: var(--ink);
      }

      /* Caption above each board in the move comparison */
      .boardcap { font-family: 'Inter', sans-serif; margin: 2px 0 6px 0; }
      .boardcap .role {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--walnut);
      }
      .boardcap .mv {
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 1.2rem;
        line-height: 1.1;
        color: var(--vc, #2b2622);
      }

      /* A quiet maker's mark in the bottom corner */
      .credit {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.04em;
        color: var(--walnut);
        opacity: 0.55;
        text-align: right;
        margin: 40px 0 6px 0;
      }
      .credit a { color: inherit; text-decoration: none; border-bottom: 1px dotted currentColor; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Masthead
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="masthead">
      <h1>Chess Tutor</h1>
      <div class="sub">An explainable coach — it shows you the move, then the reasoning.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# One screen: an interactive board you play on (the coach grades every move),
# with a "Show best move" button that analyses whatever position is on the
# board — for whichever side is to move.
# ----------------------------------------------------------------------------
render_game()

# A subtle maker's mark, tucked in the bottom-right corner.
st.markdown(
    '<div class="credit">Developed by Nam Ngo · '
    '<a href="https://github.com/phnam05" target="_blank" rel="noopener">phnam05</a></div>',
    unsafe_allow_html=True,
)