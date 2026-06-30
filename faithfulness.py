"""Does the coach's prose stay grounded in the engine's facts?

The invariant of the whole project is "the engine decides the chess; the LLM only
explains it" (see CLAUDE.md). `explainer.py` enforces that at the *prompt* level —
it tells Gemini not to invent moves. This module enforces it at the *output* level:
it reads the prose Gemini actually produced and checks that every chess move it
names was the one the engine really gave us. A move the engine never mentioned is the
classic LLM failure ("you could play Nxe5, forking the king and queen" — for a
fork that doesn't exist), and this is the cheap, deterministic check that catches
it after the fact.

It is intentionally *string-based and high-precision*: we compare the moves named
in the prose against the exact SAN strings the engine emitted (best move, principal
variation, refutation, the played move). That is a tighter guarantee than "is this
a legal move" — the LLM must echo a move the engine literally produced, not merely
one that happens to be legal. We err toward NOT crying wolf: a bare square like
"e5" can be the coach pointing at a square rather than claiming a move, so an
ungrounded *piece/capture/castle/promotion* move is a hard flag, while a bare,
ungrounded square is only reported as "unverified".

Limitation (honest, by design): this checks *moves*, not eval numbers or verbal
claims, and it matches SAN text rather than re-deriving legality on the board.
That covers the failure mode that actually bites — invented moves/tactics — and
leaves the rest as a clear extension point.
"""

import re

# A token shaped like Standard Algebraic Notation. Castling first (so "O-O-O"
# isn't truncated to "O-O"), then piece moves, pawn captures, and finally a bare
# pawn push / square. The lookarounds keep us from matching inside a word.
_SAN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?:O-O-O|O-O"
    r"|[KQRBN][a-h]?[1-8]?x?[a-h][1-8]"      # piece move, optional disambiguation/capture
    r"|[a-h]x[a-h][1-8](?:=[KQRBN])?"        # pawn capture, optional promotion
    r"|[a-h][1-8](?:=[KQRBN])?"              # pawn push or a bare square
    r")"
    r"[+#]?[!?]{0,2}"                        # optional check/mate + annotation marks
    r"(?![A-Za-z0-9])"
)


def _clean(san):
    """Strip the cosmetic marks so two ways of writing the same move compare equal."""
    san = san.strip().replace("0-0-0", "O-O-O").replace("0-0", "O-O")
    return re.sub(r"[+#!?]+$", "", san)


def _forms(san):
    """The set of spellings we'll accept as 'the same move'. We also add the
    capture-free form so the coach writing 'Bc6' still matches the engine's
    'Bxc6' (and vice-versa) instead of being flagged as invented."""
    c = _clean(san)
    return {c, c.replace("x", "")}


def _is_move(token):
    """True if the token is unambiguously a *move* (not just a square reference).
    Castling, any piece move, any capture, any promotion — but a bare 'e5' is
    ambiguous, so it returns False and is treated more leniently."""
    t = _clean(token)
    return (
        t.startswith("O-O")
        or t[0] in "KQRBN"
        or "x" in t
        or "=" in t
    )


def build_allowed(facts):
    """Every move the engine actually produced, as a set of accepted spellings.

    Works on either dict the pipeline makes: the analysis dict from
    `engine_analysis.analyze_position` (best_move + principal_variation) or the
    review dict from `move_review.review_move` (best_move + played_move +
    refutation). Missing keys are simply skipped, so it's safe on both.
    """
    moves = []
    for key in ("best_move", "played_move"):
        if facts.get(key):
            moves.append(facts[key])
    for key in ("principal_variation", "refutation"):
        moves.extend(facts.get(key) or [])

    allowed = set()
    for m in moves:
        allowed |= _forms(m)
    return allowed


def check_faithfulness(text, facts):
    """Check the coach's prose against the engine's facts.

    Returns a dict:
      ok                 -> False if any invented *move* was found
      grounded           -> moves named that the engine really produced
      ungrounded_moves   -> moves named that the engine never produced (the flag)
      unverified_squares -> bare squares not in the facts (could be a reference)
      allowed            -> the engine moves we checked against (for debugging)
    """
    allowed = build_allowed(facts)

    grounded, ungrounded_moves, unverified_squares = [], [], []
    seen = set()
    for token in _SAN.findall(text):
        if token in seen:          # report each distinct mention once
            continue
        seen.add(token)
        if _forms(token) & allowed:
            grounded.append(token)
        elif _is_move(token):
            ungrounded_moves.append(token)
        else:
            unverified_squares.append(token)

    return {
        "ok": not ungrounded_moves,
        "grounded": grounded,
        "ungrounded_moves": ungrounded_moves,
        "unverified_squares": unverified_squares,
        "allowed": sorted(allowed),
    }


# --- Self-test on hardcoded facts + prose (no engine, no API needed) ----------
if __name__ == "__main__":
    # The same sample facts explainer.py uses, so the two stages line up.
    analysis = {
        "fen": "r2q1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 b kq - 0 9",
        "best_move": "c4",
        "principal_variation": ["c4", "Bc2", "b5", "e4", "b4"],
    }
    review = {
        "fen": "r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5",
        "played_move": "Nxe4",
        "best_move": "Be7",
        "refutation": ["Rxe4", "dxe4", "Bxc6+", "bxc6", "Qd8+"],
    }

    cases = [
        # (label, facts, prose, should_pass)
        ("position / clean",
         analysis,
         "Pushing c4 grabs space and gains a tempo on the bishop, which likely "
         "drops back to c2. You can then expand with b5 and b4.",
         True),
        ("position / invented move",
         analysis,
         "Instead of c4, consider Nxe5 — it wins a pawn and forks the king.",
         False),
        ("review / clean refutation",
         review,
         "Nxe4 looks tempting, but after Rxe4 dxe4 the follow-up Bxc6+ wins a "
         "piece — Be7 was the calm move.",
         True),
        ("review / invented tactic",
         review,
         "After Nxe4 you should be fine; in fact Qh4 would threaten mate.",
         False),
        ("square reference, not a move",
         analysis,
         "Your pawn on e5 is well defended, so c4 is safe to play.",
         True),
    ]

    all_good = True
    for label, facts, prose, should_pass in cases:
        r = check_faithfulness(prose, facts)
        verdict = "PASS" if r["ok"] else "FLAG"
        correct = "ok" if r["ok"] == should_pass else "!! WRONG !!"
        if r["ok"] != should_pass:
            all_good = False
        print(f"[{verdict}] {label}  ({correct})")
        print(f"        grounded:   {r['grounded']}")
        if r["ungrounded_moves"]:
            print(f"        INVENTED:   {r['ungrounded_moves']}")
        if r["unverified_squares"]:
            print(f"        unverified: {r['unverified_squares']}")
    print("\nself-test:", "all expectations met" if all_good else "MISMATCH — fix the checker")
