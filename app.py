import streamlit as st
import chess
import chess.svg
from engine_analysis import analyze_position
from explainer import explain_position, explain_move
from move_review import review_move

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Chess Tutor",
    page_icon="♟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
            explanation = explain_position(analysis, level=level)

        st.markdown(
            f'<div class="movepair">Best move &nbsp;'
            f'<span class="best">{analysis["best_move"]}</span> &nbsp;·&nbsp; '
            f'{analysis["eval_text"]}</div>',
            unsafe_allow_html=True,
        )
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