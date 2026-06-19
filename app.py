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
QUALITY = {
    "Best":       {"color": "#1a7f5a", "gloss": "The strongest move available."},
    "Excellent":  {"color": "#4a9d6e", "gloss": "Nearly the engine's top choice."},
    "Good":       {"color": "#7fae5a", "gloss": "A solid, principled move."},
    "Inaccuracy": {"color": "#d8a838", "gloss": "Playable, but a better idea was there."},
    "Mistake":    {"color": "#d97742", "gloss": "Loses meaningful ground."},
    "Blunder":    {"color": "#c0392b", "gloss": "A serious error that changes the game."},
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
# "Play a game" mode — an interactive, click-to-move board where the student
# plays BOTH sides and the coach reviews every move. The chess stays the
# engine's job: every move runs through review_move (the single source of truth
# for quality) and explain_move (which only phrases the verdict), both reused
# untouched. The only new logic here is the board UI + the session-state loop.
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
    every move), an opt-in coach explanation, then the full move log of verdict
    chips. The engine grades; the LLM only speaks when the student asks."""
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

    # The engine facts behind the verdict — the same trio the Analyze tab shows,
    # free with every move. Guarded so a stale review dict degrades gracefully.
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

    # The explanation is opt-in: only call Gemini when the student presses the
    # button, then cache the prose on the move so reruns don't re-call it.
    if not last["comment"]:
        if st.button("Explain this move", key=f"g_explain_{len(history)}"):
            level = LEVELS[st.session_state.get("g_level_label", "Intermediate")]
            with st.spinner("Coach is thinking…"):
                try:
                    last["comment"] = explain_move(review, level=level)
                except Exception:
                    last["comment"] = "__unavailable__"
    if last["comment"] == "__unavailable__":
        st.caption("Coach commentary unavailable — check GOOGLE_API_KEY. The engine verdict still stands.")
    elif last["comment"]:
        st.markdown(f'<div class="commentary">{last["comment"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="eyebrow" style="margin-top:22px;">Move log</div>', unsafe_allow_html=True)
    rows = []
    for h in reversed(history):
        hr = h["review"]
        c = QUALITY.get(hr["label"], {"color": "#888"})["color"]
        num = f'{h["move_no"]}.' if h["color"] == "White" else f'{h["move_no"]}&hellip;'
        rows.append(
            '<div style="display:flex;align-items:center;gap:10px;padding:6px 0;'
            'border-bottom:1px solid var(--line);">'
            f'<span style="font-family:Inter,sans-serif;font-size:0.8rem;color:var(--walnut);width:40px;">{num}</span>'
            f'<span style="font-family:Fraunces,serif;font-weight:600;font-size:0.98rem;color:var(--ink);flex:1;">{hr["played_move"]}</span>'
            f'<span style="font-family:Inter,sans-serif;font-size:0.7rem;font-weight:600;letter-spacing:0.03em;'
            f'color:#fff;background:{c};border-radius:5px;padding:2px 9px;">{hr["label"]}</span>'
            '</div>'
        )
    st.markdown(''.join(rows), unsafe_allow_html=True)


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


def render_game():
    if "g_board" not in st.session_state:
        _init_game()
    # A game already in session state from before this version stored a flatter
    # per-move dict (no "review" key); reset it once so the panel can rely on the
    # new schema instead of crashing on a stale entry.
    stale = st.session_state.g_history
    if stale and "review" not in stale[0]:
        _init_game()

    left, right = st.columns([5, 4], gap="large")

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

        # --- Current position as copyable text -----------------------------
        # The live board's FEN, re-read every rerun so it tracks each move.
        # st.code renders it in monospace with a one-click copy button on
        # hover, so the student can drop the exact position into another board
        # or engine as they play.
        st.caption("Current position (FEN)")
        st.code(board.fen(), language=None)

        # --- Per-move controls ---------------------------------------------
        # The level only matters when the student asks for an explanation; the
        # coach panel reads it from session state (key) at that point.
        st.radio(
            "Explain for", list(LEVELS.keys()), index=1, horizontal=True,
            key="g_level_label",
        )
        st.selectbox("Promote a pawn to", list(PROMO.keys()), key="g_promo")
        with st.expander("Start from a position (FEN)"):
            fen_in = st.text_input(
                "FEN", value=chess.STARTING_FEN, key="g_start_fen",
                label_visibility="collapsed",
            )
            if st.button("Start this position"):
                try:
                    nb = chess.Board(fen_in)
                except ValueError:
                    st.error("That isn't a valid FEN.")
                else:
                    _init_game()
                    st.session_state.g_board = nb
                    st.rerun()

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

      /* Quiet the default Streamlit chrome */
      .block-container { padding-top: 2.2rem; max-width: 1100px; }
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
# Top-level mode: analyse one position, or play a whole game with the coach
# watching every move. "Play a game" short-circuits the single-position UI.
# ----------------------------------------------------------------------------
app_mode = st.radio(
    "What would you like to do?",
    ["Analyze a position", "Play a game"],
    horizontal=True,
)

if app_mode == "Play a game":
    render_game()
    st.stop()

# ----------------------------------------------------------------------------
# Controls + board, side by side
# ----------------------------------------------------------------------------
DEFAULT_FEN = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"

left, right = st.columns([5, 4], gap="large")

with left:
    st.markdown('<div class="eyebrow">The position</div>', unsafe_allow_html=True)
    fen = st.text_input("FEN", value=DEFAULT_FEN, label_visibility="collapsed")

    # Validate once, up front. Keep the board on screen no matter what.
    try:
        board = chess.Board(fen)
    except ValueError:
        st.error("That isn't a valid position. Paste a FEN string, or reset to the starting setup.")
        st.stop()

    level_label = st.radio(
        "Explain for",
        list(LEVELS.keys()),
        index=1,
        horizontal=True,
    )
    level = LEVELS[level_label]

with right:
    # The top board is simply the position you entered. The move you review
    # gets its own dedicated before/after boards in the result, below.
    svg = chess.svg.board(board, size=380, colors=BOARD_COLORS)
    st.image(svg)

st.divider()

# ----------------------------------------------------------------------------
# Mode
# ----------------------------------------------------------------------------
st.markdown('<div class="eyebrow">What do you want?</div>', unsafe_allow_html=True)
mode = st.radio(
    "Mode",
    ["Explain this position", "Review a move"],
    horizontal=True,
    label_visibility="collapsed",
)

# --- Explain the position ---------------------------------------------------
if mode == "Explain this position":
    if st.button("Coach me", type="primary"):
        with st.spinner("Reading the position..."):
            analysis = analyze_position(fen)

        # Engine facts first, so they show even if the explanation call fails.
        st.markdown(
            f'<div class="movepair">Best move &nbsp;'
            f'<span class="best">{analysis["best_move"]}</span></div>',
            unsafe_allow_html=True,
        )

        # The numbers behind the move, like the Review tab — but there's no played
        # move here, so "win chance lost" doesn't apply: we show the current
        # winning chance (with best play) and the eval, not a swing.
        cp = analysis["eval_centipawns"]
        if cp is None:                      # forced mate: 100% unless it's against us
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

        with st.spinner("Writing your explanation..."):
            explanation = explain_position(analysis, level=level)
        st.markdown(f'<div class="commentary">{explanation}</div>', unsafe_allow_html=True)

# --- Review a move ----------------------------------------------------------
else:
    # Friendly dropdown: human notation (SAN) shown, engine notation (UCI) kept.
    legal = {board.san(m): m.uci() for m in board.legal_moves}
    chosen_san = st.selectbox("Which move did you play?", sorted(legal.keys()))

    if st.button("Review my move", type="primary"):
        with st.spinner("Reviewing..."):
            review = review_move(fen, legal[chosen_san])
            comment = explain_move(review, level=level)

        meta = QUALITY.get(review["label"], {"color": "#888", "gloss": ""})
        st.markdown(
            f'<div class="verdict" style="--vc:{meta["color"]}">'
            f'  <div class="label">{review["label"]}</div>'
            f'  <div class="gloss">{meta["gloss"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Show the move on the board: both moves are played out (squares lit,
        # plus an arrow) so the two boards read the same way — yours in the
        # verdict's color, the engine's pick in green. If you found the best
        # move, one board is enough.
        played_uci = legal[chosen_san]
        best_uci = review.get("best_move_uci")
        is_best = bool(best_uci) and best_uci == played_uci

        if best_uci and not is_best:
            you_col, best_col = st.columns(2, gap="medium")
            with you_col:
                st.markdown(
                    f'<div class="boardcap" style="--vc:{meta["color"]}">'
                    f'<div class="role">You played</div>'
                    f'<div class="mv">{review["played_move"]}</div></div>',
                    unsafe_allow_html=True,
                )
                st.image(move_board_svg(
                    fen, played_uci, after=True, arrow_color=meta["color"],
                ))
            with best_col:
                st.markdown(
                    '<div class="boardcap" style="--vc:#1a7f5a">'
                    '<div class="role">Engine&rsquo;s best</div>'
                    f'<div class="mv">{review["best_move"]}</div></div>',
                    unsafe_allow_html=True,
                )
                st.image(move_board_svg(
                    fen, best_uci, after=True, arrow_color="#1a7f5a",
                ))
        else:
            role = "You played &mdash; the engine&rsquo;s top choice" if is_best else "You played"
            st.markdown(
                f'<div class="boardcap" style="--vc:{meta["color"]}">'
                f'<div class="role">{role}</div>'
                f'<div class="mv">{review["played_move"]}</div></div>',
                unsafe_allow_html=True,
            )
            st.image(move_board_svg(
                fen, played_uci, after=True, arrow_color=meta["color"], size=380,
            ))
        # How the verdict was reached: the win-% drop drives the label, with the
        # raw evals and centipawn loss shown for those who want the detail.
        # Guard against an out-of-date review dict (e.g. a stale module cached on
        # Streamlit Cloud after a deploy) so a missing key degrades gracefully
        # instead of hard-crashing the whole app.
        metric_keys = (
            "win_prob_drop", "best_win_pct", "played_win_pct",
            "best_eval", "played_eval", "centipawn_loss",
        )
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
        st.markdown(f'<div class="commentary">{comment}</div>', unsafe_allow_html=True)