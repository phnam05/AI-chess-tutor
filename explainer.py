import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st
load_dotenv()



# Works on Streamlit Cloud (st.secrets) and locally (.env / env var). Touching
# st.secrets when no secrets.toml exists raises StreamlitSecretNotFoundError, so
# guard it and fall back to the environment variable.
try:
    API_KEY = st.secrets.get("GOOGLE_API_KEY")
except Exception:
    API_KEY = None
API_KEY = API_KEY or os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)


LEVEL_INSTRUCTIONS = {
    "beginner": """The player is a BEGINNER. Talk only about concrete, visible things:
what the move attacks or defends, whether pieces are safe, simple threats, and
king safety. Use no complicated chess jargon. Keep it to 2-3 short sentences.""",

    "intermediate": """The player is INTERMEDIATE. Explain the PLAN behind the move,
not just what it does — use the predicted line to show what the player is building
toward over the next few moves. You may use standard terms like space, tempo, and
initiative. Keep it to 3-4 sentences.""",

    "advanced": """The player is ADVANCED. Focus on the underlying imbalances: pawn
structure, long-term weaknesses, and what the evaluation reflects. Be precise about
the eval — do not round a slight edge into "equal." Assume the player knows the
basics and wants the deeper reasoning. Keep it tight, 3-4 sentences.""",
}

SYSTEM_INSTRUCTION = """You are a friendly chess coach sitting next to one
student, looking at their game together. The position and the engine's analysis
(best move, evaluation, predicted line) are given to you and are correct. Treat
them as ground truth.

Your job is to coach this one student. Follow these rules:
- Talk directly to the student as "you." Be warm and concise.
- Write a few plain sentences. NO headings, NO numbered lists, NO bold text,
  NO "Summary" section.
- Mention only the one or two most important ideas. Do not explain everything.
- Explain WHY the engine's best move is good and what the evaluation means, in
  simple language.
- Do NOT suggest a different move than the engine's best move.
- Do NOT invent tactics or evaluations that aren't in the analysis given to you.
- A predicted/refutation line is the engine's EXPECTED best play, not a
  certainty — the opponent may not find it. Phrase it as what would *likely* or
  *probably* follow, or call a reply the *critical* or *main* try. Never state a
  future move as a guaranteed fact ("they will play…", "your opponent is going
  to…").
- End on something that invites the student to think, but never lecture."""

def explain_position(analysis, level="intermediate"):
    """
    Take the fact-dictionary from Stage 1 and return a natural-language
    explanation, grounded strictly in those facts.
    """
    facts = f"""Position (FEN): {analysis['fen']}
Side to move: {analysis['turn']}
Engine's best move: {analysis['best_move']}
Engine's evaluation: {analysis['eval_text']} (from {analysis['turn']}'s perspective)
Engine's predicted line: {', '.join(analysis['principal_variation'])}

Explain this position and why the best move is strong."""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION + "\n\n" + LEVEL_INSTRUCTIONS[level]),
        contents=facts,
    )
    return response.text


def explain_move(review, level="intermediate"):
    """Coach the student on a move they just played, using the review facts."""
    # The engine's continuation after the move the student actually played. For a
    # weak move this is the refutation — concretely how the opponent punishes it.
    # `.get` so a cached/old review without this key degrades gracefully.
    refutation = review.get("refutation") or []
    after_line = ", ".join(refutation) if refutation else "(none — the move ends the game)"

    facts = f"""The student is playing and just made a move. Here is the engine's review:

Position before their move (FEN): {review['fen']}
Their move: {review['played_move']}
Move quality: {review['label']}
Engine's best move was: {review['best_move']}
Evaluation after their move: {review['played_eval']} (from their perspective)
Evaluation if they had played the best move: {review['best_eval']}
What the engine expects to follow their move (opponent moves first): {after_line}

Coach the student on the move THEY played.
- If it was strong, affirm briefly why, and what it builds toward.
- If it lost value, LEAD with what goes wrong with THEIR move: use the line the
  engine expects to follow it to show concretely how the opponent punishes the
  move — the reply they overlooked, the piece or square that falls, why a piece
  can't move. Name the better move only briefly at the end; don't dwell on it.
Read the position from the FEN to ground your explanation, but state only what
the facts and that line show — never invent a threat, tactic, or line that
isn't there. Be encouraging and specific."""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION + "\n\n" + LEVEL_INSTRUCTIONS[level]
        ),
        contents=facts,
    )
    return response.text


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
        "fen": "r2q1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 b kq - 0 9",
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
