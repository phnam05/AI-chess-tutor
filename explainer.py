import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st
load_dotenv()



# Works on Streamlit Cloud (st.secrets) and locally (.streamlit/secrets.toml or env var)
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
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
    facts = f"""The student is playing and just made a move. Here is the engine's review:

Their move: {review['played_move']}
Move quality: {review['label']}
Engine's best move was: {review['best_move']}
Evaluation after their move: {review['played_eval']} (from their perspective)
Evaluation if they had played the best move: {review['best_eval']}

Coach the student on the move they played. If it was strong, affirm why.
If it lost value, gently explain what the better move was and what they missed.
Be encouraging and specific."""

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
    for lvl in ["beginner", "intermediate", "advanced"]:
        print(f"\n========== {lvl.upper()} ==========")
        print(explain_position(midgame, level=lvl))
