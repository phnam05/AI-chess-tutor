import streamlit as st
import chess
import chess.svg
from engine_analysis import analyze_position
from explainer import explain_position, explain_move
from move_review import review_move, review_game, win_chance
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
    "Best":       {"color": "#1a7f5a", "mark": "★",  "badge": "green",  "gloss": "The strongest move available."},
    "Excellent":  {"color": "#4a9d6e", "mark": "!",  "badge": "green",  "gloss": "Nearly the engine's top choice."},
    "Good":       {"color": "#7fae5a", "mark": "✓",  "badge": "green",  "gloss": "A solid, principled move."},
    "Inaccuracy": {"color": "#d8a838", "mark": "?!", "badge": "yellow", "gloss": "Playable, but a better idea was there."},
    "Mistake":    {"color": "#d97742", "mark": "?",  "badge": "orange", "gloss": "Loses meaningful ground."},
    "Blunder":    {"color": "#c0392b", "mark": "??", "badge": "red",    "gloss": "A serious error that changes the game."},
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
    st.session_state.g_selected = None      # move-log pick; None = latest move
    st.session_state.setdefault("g_last_click", None)
    st.session_state.setdefault("g_flip", False)


def _load_reviewed_game(entries):
    """Install a graded game (from review_game) as the live session: the board
    at the final position, every move in the history with its engine review.
    From here it behaves exactly like a game played on the board — click any
    move in the log to rewind to it, per-move verdicts, opt-in explanations."""
    _init_game()
    board = chess.Board(entries[0]["review"]["fen"])
    for e in entries:
        board.push(chess.Move.from_uci(e["review"]["played_move_uci"]))
    st.session_state.g_board = board
    st.session_state.g_history = [dict(e, comment=None) for e in entries]
    st.session_state.g_lastmove = board.move_stack[-1]


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
    st.session_state.g_selected = None       # a new move: coach snaps back to it


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
    """Right-hand column: one move's engine verdict + metrics (free with every
    move), the played-vs-best boards, and an opt-in coach explanation. By
    default that's the latest move; clicking a move in the log (g_selected)
    brings any earlier verdict — and its cached explanation — back. The engine
    grades; the LLM only speaks when the student asks."""
    st.markdown('<div class="eyebrow">The coach</div>', unsafe_allow_html=True)
    history = st.session_state.g_history
    if not history:
        st.markdown(
            '<div class="commentary">Play a move for either side and I&rsquo;ll grade '
            'it &mdash; the verdict, the win-chance swing, and the engine&rsquo;s pick. '
            'Press <em>Explain this move</em> whenever you want it put into words. '
            'Or paste a game&rsquo;s PGN below the board and I&rsquo;ll grade every '
            'move of it.</div>',
            unsafe_allow_html=True,
        )
        return

    # Which move is on the coach's desk: the log's pick, or the latest move.
    sel = st.session_state.get("g_selected")
    idx = sel if sel is not None and 0 <= sel < len(history) else len(history) - 1
    last = history[idx]
    review = last["review"]
    if idx != len(history) - 1:
        st.caption(
            f'Reviewing move {last["move_no"]} ({last["color"]}) — the board '
            f'shows the position after it.'
        )
        if st.button("Back to the latest move", key="g_back_latest"):
            st.session_state.g_selected = None
            st.rerun()
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
    _render_move_boards(review)

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
        if st.button("Explain this move", key=f"g_explain_{idx}"):
            _write_comment()
    elif last["comment"] != "__unavailable__" and last.get("comment_level") != cur_level:
        # Already explained, but the student has since picked a different level.
        if st.button(f"Re-explain for {cur_label}", key=f"g_reexplain_{idx}"):
            _write_comment()

    if last["comment"] == "__unavailable__":
        st.caption("Coach commentary unavailable — check GOOGLE_API_KEY. The engine verdict still stands.")
    elif last["comment"]:
        st.markdown(f'<div class="commentary">{last["comment"]}</div>', unsafe_allow_html=True)


def _render_move_log():
    """The running record of every move — and now the way back to any of them:
    each move is a button, and pressing it puts that move's verdict (and its
    cached explanation, if one was written) back on the coach's desk. Lives in
    its own narrow panel on the far left, beside the board. Streamlit widgets
    can't sit inside custom HTML, so the old styled rows became compact buttons
    (restyled in the CSS block below); the quality mark rides in the label and
    the full label appears on hover."""
    history = st.session_state.g_history
    if not history:
        return
    st.markdown('<div class="eyebrow">Move log</div>', unsafe_allow_html=True)

    # Pair the half-moves into chess.com-style rows: one full-move number with
    # White's and Black's move side by side. A row can be half-filled — Black
    # hasn't replied yet, or (from a FEN that starts on Black's move) there's no
    # White move. White's and Black's plies share the same fullmove number, so we
    # fold a Black ply into the open White row and otherwise start a new row.
    # Each cell keeps its index into g_history — that's what a click selects.
    pairs = []
    for idx, h in enumerate(history):
        open_row = pairs[-1] if pairs else None
        if (h["color"] == "Black" and open_row
                and open_row["no"] == h["move_no"]
                and open_row["white"] is not None and open_row["black"] is None):
            open_row["black"] = (idx, h)
        else:
            side = "white" if h["color"] == "White" else "black"
            pairs.append({"no": h["move_no"], "white": None, "black": None, side: (idx, h)})

    sel = st.session_state.get("g_selected")
    shown = sel if sel is not None and 0 <= sel < len(history) else len(history) - 1

    def _cell(col, entry):
        """One move as a quiet button styled like the old score-sheet row: the
        SAN in serif plus the colored quality chip (a markdown badge — named
        colors only, so the three greens share a hue and the marks ★ ! ✓ keep
        them apart, as before). The move on the coach's desk is highlighted."""
        if entry is None:
            return
        idx, h = entry
        hr = h["review"]
        meta = QUALITY.get(hr["label"], {})
        mark, badge = meta.get("mark", ""), meta.get("badge", "gray")
        label = f'{hr["played_move"]} :{badge}-badge[{mark}]' if mark else hr["played_move"]
        if col.button(
            label,
            key=f"g_log_{idx}",
            type="primary" if idx == shown else "secondary",
            use_container_width=True,
            help=hr["label"],
        ):
            st.session_state.g_selected = idx
            st.rerun()

    # Newest full-move first, so the latest move stays pinned at the top of the
    # scroll panel — no scrolling to see the move you just made. The container
    # only gets a fixed height (and so a scrollbar) once the game is long enough
    # to need one ("content" = grow with the rows; height=None is not accepted).
    with st.container(height=540 if len(pairs) > 10 else "content", key="g_movelog"):
        for p in reversed(pairs):
            # The number column stays skinny so the two move buttons get the
            # width — long SANs like Qxf4 need it to render on one line.
            num, wcol, bcol = st.columns([0.6, 2, 2], gap="small")
            num.markdown(f'<div class="lognum">{p["no"]}.</div>', unsafe_allow_html=True)
            _cell(wcol, p["white"])
            _cell(bcol, p["black"])


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


def _render_move_boards(review):
    """Inside the coach column, under the verdict: one move drawn out — the
    played move with its from/to squares lit and an arrow, and, when it wasn't
    the engine's pick, the engine's best beside it in green. This is the old
    Analyze tab's before/after comparison, kept for game mode. It renders
    straight from the stored review (pre-move FEN + both UCIs), so it's a pure
    redraw — no new engine call. Boards are kept small because the coach column
    is narrow."""
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
            st.session_state.g_selected = None    # the picked move may be gone
            stack = st.session_state.g_board.move_stack
            st.session_state.g_lastmove = stack[-1] if stack else None
        if b3.button("Flip board", use_container_width=True):
            st.session_state.g_flip = not st.session_state.get("g_flip", False)

        board = st.session_state.g_board
        flipped = st.session_state.get("g_flip", False)

        # --- Time travel: a log click rewinds the big board -----------------
        # When an earlier move is picked in the log, the board shows the
        # position right after that move (rebuilt from the review's stored
        # pre-move FEN — a pure redraw, no engine call). Play pauses while
        # browsing: board clicks are ignored until "Back to the latest move"
        # (or the newest log entry) resumes the game. Picking the newest move
        # IS the live position, so that stays playable.
        history = st.session_state.g_history
        sel = st.session_state.get("g_selected")
        browsing = sel is not None and 0 <= sel < len(history) - 1
        if browsing:
            r = history[sel]["review"]
            disp_move = chess.Move.from_uci(r["played_move_uci"])
            disp_board = chess.Board(r["fen"])
            disp_board.push(disp_move)
            disp_last = disp_move
        else:
            disp_board = board
            disp_last = st.session_state.g_lastmove

        # --- Turn / result indicator ---------------------------------------
        if browsing:
            h = history[sel]
            head = (f'Viewing move {h["move_no"]} ({h["color"]}) &mdash; '
                    f'back to the latest move to keep playing')
        elif board.is_game_over():
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
        img = _board_image(
            disp_board.fen(), flipped,
            None if browsing else st.session_state.g_from,
            disp_last.uci() if disp_last else None,
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
        cur_fen = disp_board.fen()      # while browsing, the box shows the viewed position
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

        # --- Review a whole game (PGN) ---------------------------------------
        # The chess.com-style game review: paste a finished game and the engine
        # grades every move of it up front (one progress bar, no LLM calls);
        # the coach's explanations stay opt-in per move, so a 40-move game
        # costs zero API quota until the student asks about a move.
        with st.expander("Review a full game (PGN)"):
            st.caption(
                "Paste a game in PGN format — the standard text export from "
                "chess.com or lichess — and the engine grades every move. "
                "Then click any move in the log to see its verdict."
            )
            pgn_text = st.text_area(
                "PGN", key="g_pgn_box", height=140, label_visibility="collapsed",
                placeholder="1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 ...",
            )
            if st.button("Grade the game", key="g_pgn_grade", use_container_width=True):
                bar = st.progress(0.0, text="Reading the game…")
                try:
                    entries = review_game(
                        pgn_text,
                        progress=lambda done, total: bar.progress(
                            done / total, text=f"Grading move {done} of {total}…"
                        ),
                    )
                except ValueError as err:
                    bar.empty()
                    st.error(str(err))
                else:
                    bar.empty()
                    _load_reviewed_game(entries)
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
                # Watermark the click even while browsing history, so it can't
                # replay as a move the instant the student returns to the game.
                st.session_state.g_last_click = pt
                if not browsing and not board.is_game_over():
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
        # under the button. It reads the DISPLAYED board, so while browsing an
        # earlier move it analyses that position — engine only, still opt-in.
        # The coach's per-move verdict follows below.
        _render_hint(disp_board)
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

      /* The move log — every move is a button now (click = rewind to it), but
         styled to read like the original score sheet: quiet borderless rows,
         serif SAN, a colored chip per move, a thin rule between full moves.
         Scoped to the log container's key so the app's real buttons keep
         their normal look. The move on the coach's desk ("primary") gets a
         soft boxwood fill instead of a loud filled button. */
      .st-key-g_movelog .stButton button {
        min-height: 1.6rem;
        padding: 1px 4px;
        justify-content: flex-start;
        color: var(--ink);
        background: transparent;
        border: none;
        border-radius: 4px;
      }
      /* The label lives in a markdown <p> INSIDE the button, which carries
         Streamlit's own font rules — style it directly or the serif/bold
         never reaches the text (the old .logcell look). Streamlit also sets
         word-break on markdown, which snaps "Qxf4" into "Qxf / 4" when the
         column is tight — a move name must never wrap. */
      .st-key-g_movelog .stButton button p {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: inherit;
        white-space: nowrap;
        word-break: normal;
        overflow-wrap: normal;
      }
      .st-key-g_movelog .stButton button:hover {
        background: rgba(43,38,34,0.05);
        color: var(--ink);
      }
      .st-key-g_movelog .stButton button:focus:not(:focus-visible) {
        color: var(--ink);
      }
      .st-key-g_movelog .stButton button[kind="primary"] {
        background: var(--boxwood);
        color: var(--ink);
      }
      .st-key-g_movelog [data-testid="stHorizontalBlock"] {
        gap: 6px;
        padding: 2px 0;
        border-bottom: 1px solid var(--line);
      }
      .lognum {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: var(--walnut);
        padding-top: 0.3rem;
      }

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