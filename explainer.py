import os
import json
import logging
from datetime import datetime
from pathlib import Path
import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types
import chess
import streamlit as st
import board_facts
from faithfulness import check_faithfulness
load_dotenv()



# Works on Streamlit Cloud (st.secrets) and locally (.env / env var). Touching
# st.secrets when no secrets.toml exists raises StreamlitSecretNotFoundError, so
# guard it and fall back to the environment variable.
def _find_api_key():
    secrets_error = None
    try:
        secrets = dict(st.secrets)
    except Exception as err:
        secrets, secrets_error = {}, err
    key = secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        # Say what *was* there (names only, never values) so the Cloud logs show
        # whether the secret is misnamed or the secrets box didn't parse at all.
        print(f"[coach] no API key found; secret names: {sorted(secrets)}; "
              f"secrets error: {secrets_error!r}", flush=True)
    return key


MODEL = "gemini-3.1-flash-lite"

# The SDK never retries unless asked, so one busy moment on Gemini's side (a 503,
# or a 429 from the free tier's ~15 requests/minute) used to fail the explanation
# outright — that is what broke a live demo. Retry those, briefly: 3 attempts
# with ~2s then ~4s waits keeps the student's wait short. The SDK only retries
# transient codes (408/429/5xx), never a bad key or a bad request.
# No key -> no client: newer SDKs raise at construction, which used to crash the
# whole app on import; now only the coach is unavailable and the engine still works.
# Built on first use, not at import: an import-time lookup kept a key added in
# Streamlit's settings unseen until the app was rebooted.
# Each try also has a time limit. The SDK sets none, so one stuck connection
# waited forever (a measurement run froze for minutes on a single request). A
# normal answer takes a few seconds; a timed-out try is retried like a 503, so
# the worst case is ~3 x 20s plus the short waits, about a minute.
_TIMEOUT_S = 20
_client = None


def _get_client():
    global _client
    if _client is None:
        key = _find_api_key()
        if key:
            _client = genai.Client(
                api_key=key,
                http_options=types.HttpOptions(
                    timeout=_TIMEOUT_S * 1000,   # milliseconds, per try
                    retry_options=types.HttpRetryOptions(attempts=3, initial_delay=2, max_delay=8)
                ),
            )
    return _client


def describe_coach_error(err):
    """Why the coach couldn't answer, in plain words for the UI. Every failure
    used to read "check GOOGLE_API_KEY", which sent a quota or overload hiccup
    looking for a key problem that didn't exist."""
    code = getattr(err, "code", None)
    if _client is None:
        return "Coach unavailable: no GOOGLE_API_KEY is set."
    if code == 429:
        return ("The coach hit Gemini's usage limit (the free plan allows about 15 "
                "requests a minute). Wait a minute, then try again.")
    if code in (500, 502, 503, 504):
        return "Gemini is busy right now. Try again in a moment."
    if code in (400, 401, 403):
        return f"Gemini rejected the request (error {code}) — check that GOOGLE_API_KEY is valid."
    if code == 404:
        return f"Gemini doesn't recognise the model '{MODEL}' — it may have been retired."
    if isinstance(err, httpx.TimeoutException):
        return (f"Gemini didn't answer in time ({_TIMEOUT_S} seconds, 3 tries). "
                "Try again in a moment.")
    return f"Coach unavailable ({type(err).__name__}). Try again in a moment."


def _generate(level, facts):
    """One coach call: the fixed persona + the level, then the engine facts."""
    client = _get_client()
    if client is None:
        raise RuntimeError("no GOOGLE_API_KEY set")
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION + "\n\n" + LEVEL_INSTRUCTIONS[level]
        ),
        contents=facts,
    )
    return response.text


# Each level also sets how far down the engine's line the coach goes
# (board_facts.LINE_PLIES): concepts over a short line for weaker players,
# more concrete moves for stronger ones.
LEVEL_INSTRUCTIONS = {
    "beginner": """The player is a BEGINNER. Use plain words and name the pieces
("your knight", "White's bishop"), with the move's notation in brackets after
the words, e.g. "castle (O-O)". Give each idea as a simple, visible thing: a
piece is attacked, a piece can be chased, the king gets safe, a piece comes into
play. No chess jargon. Keep it to 3-4 short sentences.""",

    "intermediate": """The player is INTERMEDIATE. Give each move's idea, then the
move in notation. You may use standard terms like development, tempo and
initiative, but only as a name for what a board fact already says, never as a
new claim. Keep it to 4-5 sentences.""",

    "advanced": """The player is ADVANCED. Be concrete: go through every move of
the given line in notation, each with the board fact behind it, and be precise
about the eval — do not round a slight edge into "equal," and never guess at why
the eval is what it is. Assume the player knows the basics. Keep it tight, 4-5
sentences.""",
}

# The author's rules for walking through a line (CLAUDE.md, 2026-09-24): who
# plays every move, the idea before each recommended move, only the moves given.
# The ideas are the risky part — an idea from Gemini's own chess knowledge is an
# invented reason, the audit's most common failure — so they may come only from
# the board facts (board_facts.py) or from what the line itself shows.
SYSTEM_INSTRUCTION = """You are a friendly chess coach sitting next to one
student, looking at their game together. The engine's analysis (best move,
evaluation, the line it expects) and the board facts listed for each move are
given to you and are correct. Treat them as ground truth, and as your ONLY
source of chess claims: you put them into words, you never add to them.

Your job is to coach this one student. Follow these rules:
- Talk directly to the student as "you." Be warm and concise.
- Write a few plain sentences. NO headings, NO numbered lists, NO bold text,
  NO "Summary" section.
- For each move, use only its one most useful board fact. Do not list them all.
- Do NOT suggest a different move than the engine's.
- Do NOT invent tactics or evaluations that aren't in the analysis given to you.
- The evaluation is a NUMBER the engine computed; it comes with no reason
  attached. State it and say who it favors, but do NOT explain WHY it is what
  it is unless the reason is visible in the facts you were given (the line wins
  material, or forces mate). If you don't know the reason, say what the eval
  means for the player without inventing one.

Walking through the engine's line:
- Go through the moves you are given, in order, and only those.
- Say who plays EVERY move, and change the subject of the sentence whenever the
  side to move changes. Never join two sides' moves with "followed by", "then",
  or "and".
- The opponent's moves are the engine's EXPECTED best play, not a certainty:
  "your opponent's strongest answer is probably ...", "your opponent will likely
  ...". Never state one as a sure thing ("they will play…", "your opponent
  plays…").
- For each of the STUDENT's moves, the idea comes FIRST and the move LAST:
  "<what to notice, from its board fact>, so a natural idea is <the idea>.
  That's why your best reply is <move>." Never name the student's move first and
  explain it afterwards ("You play ...c6 to attack…" is wrong). This pattern is
  only for moves you RECOMMEND: never write "a natural idea is <move>" about a
  move the student already played.
- Write Black's moves with three dots (...c6) and White's without (Nf3).
- A move's idea or purpose may come ONLY from its board facts, or from what the
  line shows happening next. Never from general chess knowledge or rules of
  thumb ("usually", "generally"), and never from your own reading of the board.
  If a move's board facts say "none", name it and give it no reason.
- Keep the evaluation apart from the moves: state it in its own sentence, with
  who it favors exactly as given, and never say a move or a board fact raises,
  drops or causes it.
- Never say a piece or pawn is lost, hanging, or can be won unless the line
  shows it being captured.
- An attack is only an attack: never say a move "forces" a piece away or "wins"
  anything unless the line shows it happening.
- Name pieces and squares only as the facts and moves name them. Name a pawn by
  the square it stands on ("the pawn on c2"), never by a square it could move
  to ("the c3 pawn").
- Never guess what the student wants or wanted ("since you want to...",
  "since you wanted to..."). Say what the move does: "pushing the pawn makes
  room for your queen."
- Say each fact in plain, short words of your own ("you attack the bishop with
  a pawn"), not by copying the fact's wording.
- A move's board facts are listed with the most important first.
- End on something that invites the student to think, but never lecture."""


# --- Output-level faithfulness watchdog --------------------------------------
# The system prompt above keeps Gemini honest at the *prompt* level; faithfulness.py
# checks the prose it actually produced (does it name a move the engine never gave?).
# We run that check on every explanation and append the result to a log, so we can
# later measure how often the coach stays grounded — and keep the outputs without
# re-spending API calls. It is passive by design: it never changes the explanation
# and never raises. A bug in the watchdog must not break the coaching it watches.
_FAITH_LOG = Path(__file__).with_name("faithfulness_log.jsonl")
_faith_logger = logging.getLogger("faithfulness")


def _check_and_log(text, facts, kind, level):
    """Check the coach's prose against the engine facts, then log the result.

    `facts` is the analysis/review dict (not the prompt string); `kind` is
    "position" or "move". Returns the checker's result dict, but callers use it
    only for its side effect — the explanation itself is returned unchanged.
    """
    try:
        result = check_faithfulness(text, facts)
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "kind": kind,
            "level": level,
            "fen": facts.get("fen"),
            "ok": result["ok"],
            "grounded": result["grounded"],
            "ungrounded_moves": result["ungrounded_moves"],
            "unverified_squares": result["unverified_squares"],
            "causal_invented": result["causal_invented"],
            "causal_unverified": result["causal_unverified"],
            "text": text,
        }
        with _FAITH_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        # Always-on console signal: see the watchdog run for every explanation
        # (clean or flagged), so you don't have to open the log to confirm it works.
        print(
            f"[faithfulness] {kind}/{level}: ok={result['ok']} "
            f"grounded={result['grounded']} ungrounded={result['ungrounded_moves']} "
            f"invented_cause={len(result['causal_invented'])}",
            flush=True,
        )
        if result["ungrounded_moves"]:
            _faith_logger.warning(
                "coach named ungrounded move(s) %s [%s/%s]",
                result["ungrounded_moves"], kind, level,
            )
        if result["causal_invented"]:
            _faith_logger.warning(
                "coach invented a cause for the eval: %s [%s/%s]",
                result["causal_invented"], kind, level,
            )
        return result
    except Exception as e:
        # Never break coaching — but surface the error instead of vanishing,
        # so a real bug can't hide behind a silent except again.
        print(f"[faithfulness] check failed: {e!r}", flush=True)
        return None


def _dots(color, san):
    """Black's moves are written with three dots (...c6), White's without, so a
    reader can tell whose move it is from the notation alone."""
    return f"...{san}" if color == "Black" else san


def _facts_text(step):
    if step and step["facts"]:
        return "; ".join(step["facts"])
    return "none (so give this move no reason)"


def _eval_words(value, student):
    """The evaluation with who it favours spelled out, so the coach never has to
    read the sign itself: told "-1.46 (from their perspective)", it once said to
    Black that -1.46 "favors you". `value` is a review eval ("-1.46", a mate
    shown as +/-100.00) or an analysis eval_text ("+0.42 pawns", "Mate in -2")."""
    opponent = "White" if student == "Black" else "Black"
    mate = value.startswith("Mate in")
    v = int(value.split()[-1]) if mate else float(value.split()[0])
    if v == 0:
        return f"{value}: level"
    who = f"{student} (the student)" if v > 0 else f"{opponent} (the opponent)"
    # No number for a mate: given "-100.00: a forced mate", the coach still told
    # a beginner "the evaluation is -100.00" (a stand-in, not a real score).
    if mate:
        return f"a forced checkmate for {who} (mate in {abs(v)}); say it in words, with no number"
    if abs(v) >= 100:
        return f"a forced checkmate for {who}; say it in words, with no number"
    return f"{value} from {student}'s side, so {who} is ahead"


def _walkthrough(steps, student):
    """The engine's line as numbered steps, each labelled with who plays it and
    carrying its board facts. Labelling in code is what stops "O-O, followed by
    a6" from reading as two moves by the same side. The labels say "likely
    reply" / "best move", not "plays": the line is a forecast, not a promise."""
    if not steps:
        return "(none: the game is over)"
    lines = []
    for i, step in enumerate(steps, 1):
        who = (f"Student ({step['color']}), best move:" if step["color"] == student
               else f"Opponent ({step['color']}), likely reply:")
        lines.append(f"{i}. {who} {_dots(step['color'], step['san'])} "
                     f"(the {step['piece']}, {step['from']} to {step['to']}). "
                     f"Board facts: {_facts_text(step)}.")
    return "\n".join(lines)


def _review_facts(review):
    """The board facts of a review: (played move, line steps, best move). A
    review made before board facts existed is rebuilt from its FEN and lines,
    since Streamlit can keep an old review across a deploy."""
    if "line_steps" in review:
        return review["played_facts"], review["line_steps"], review["best_facts"]
    board = chess.Board(review["fen"])
    refutation = review.get("refutation") or []
    played = board_facts.played_facts(board, review["played_move"], refutation)
    after = board.copy()
    after.push_san(review["played_move"])
    steps = board_facts.line_steps(after, refutation)
    best = board_facts.played_facts(board, review["best_move"], (review.get("best_line") or [])[1:])
    return played, steps, best


def explain_position(analysis, level="intermediate"):
    """
    Take the fact-dictionary from Stage 1 and return a natural-language
    explanation, grounded strictly in those facts.
    """
    student = analysis["turn"]
    steps = analysis.get("line_steps")
    if steps is None:                     # an analysis from before board facts
        steps = board_facts.line_steps(chess.Board(analysis["fen"]),
                                       analysis["principal_variation"])
    steps = board_facts.cut_line(steps, board_facts.LINE_PLIES[level], student)

    facts = f"""Position (FEN): {analysis['fen']}
The student plays {student}, and it is their move.
Engine's best move: {_dots(student, analysis['best_move'] or '(none)')}
Engine's evaluation: {_eval_words(analysis['eval_text'], student)}

What the engine expects, one move at a time (the student moves first):
{_walkthrough(steps, student)}

Explain the position through these moves, in order and no further: the
student's best move first, with its idea before the move, then the opponent's
likely reply, and so on."""

    text = _generate(level, facts)
    _check_and_log(text, analysis, "position", level)
    return text


def explain_move(review, level="intermediate"):
    """Coach the student on a move they just played, using the review facts."""
    # The engine's continuation after the move the student actually played. For a
    # weak move this is the refutation — concretely how the opponent punishes it.
    # Cut by level (and before any of the student's moves that no board fact can
    # explain), then labelled move by move.
    student = "White" if chess.Board(review["fen"]).turn == chess.WHITE else "Black"
    played, steps, best = _review_facts(review)
    # After a move that lost material or allowed mate, the rest of the line is
    # damage control: keep it to the punishment and one answer (cut_line).
    damage = review.get("mistake_type") in ("lost_material", "allowed_mate")
    steps = board_facts.cut_line(steps, board_facts.LINE_PLIES[level], student, damage=damage)
    damage_note = ""
    if damage and any(s["color"] == student for s in steps):
        damage_note = ("\n   Their move lost material or allowed mate, so keep this part short:\n"
                       "   say what the opponent's reply does, then give the student's move in\n"
                       "   ONE short clause as the best way to limit the damage, using the problem\n"
                       "   it solves (out of check, out of an attack) if its facts give one.")

    # The move they should have played instead is a different thing from their
    # best reply in the line: keep the two apart for the coach.
    instead = ""
    if review["label"] != "Best":
        instead = (f"\n\nThe move the engine would have played instead: "
                   f"{_dots(student, review['best_move'])}. Board facts: {_facts_text(best)}.")

    facts = f"""The student plays {student} and just made a move. Here is the engine's review:

Position before their move (FEN): {review['fen']}
Their move: {_dots(student, review['played_move'])}
Move quality: {review['label']}
Evaluation after their move: {_eval_words(review['played_eval'], student)}
Evaluation if they had played the best move: {_eval_words(review['best_eval'], student)}
What their move did, from the board: {_facts_text(played)}.

What the engine expects to follow their move, one move at a time:
{_walkthrough(steps, student)}{instead}

Coach the student on the move THEY played, in this order:
1. What their move did, from its board facts: if it lost value, what it
   changed on the board; if it was strong, affirm it briefly. If it has no
   board facts, give no reason and let the line show what follows. Give the
   evaluation in a separate sentence of its own.
2. Walk through the moves above, in order and no further.{damage_note}
3. If it lost value, end with one short clause naming the move the engine
   would have played instead, with its idea first if it has board facts.
Be encouraging and specific."""

    text = _generate(level, facts)
    _check_and_log(text, review, "move", level)
    return text


# --- Self-test on HARDCODED facts (engine not connected yet) ---
if __name__ == "__main__":
    fake_analysis = {
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "turn": "White",
        "best_move": "Bb5",
        "eval_text": "+0.30 pawns",
        "principal_variation": ["Bb5", "a6", "Ba4", "Nf6", "O-O"],
    }
    midgame = {
        "fen": "r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 b - - 0 9",
        "turn": "Black",
        "best_move": "c4",
        "eval_text": "-0.20 pawns",
        "principal_variation": ["c4", "Bc2", "b5", "e4", "b4"],
    }
    # A reviewed *move*: the facts a real review_move() call would hand us,
    # including the refutation line that explains why the move was a blunder.
    # (Hand-written here so this stage stays runnable without the engine.)
    fake_review = {
        "fen": "r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5",
        "played_move": "Nxe4",
        "label": "Blunder",
        "best_move": "Be7",
        "best_eval": "-0.29",
        "played_eval": "-6.70",
        "refutation": ["Rxe4", "dxe4", "Bxc6+", "bxc6", "Qd8+"],
    }
    for lvl in ["beginner", "intermediate", "advanced"]:
        print(f"\n========== POSITION - {lvl.upper()} ==========")
        print(explain_position(midgame, level=lvl))

    for lvl in ["beginner", "intermediate", "advanced"]:
        print(f"\n========== MOVE REVIEW - {lvl.upper()} ==========")
        print(explain_move(fake_review, level=lvl))
