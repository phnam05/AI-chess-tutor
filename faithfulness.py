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

The 2026-07-03 human audit (`faithfulness_audit.md`) showed the move check alone
is not enough: the dominant real failure was not invented moves but invented
*reasons* — the coach explaining WHY the evaluation is what it is ("the edge
comes from your active pieces") when the engine only ever emitted a number. So a
second, sentence-level check looks for exactly that shape: a sentence that names
the evaluation AND asserts a cause for it (see `check_eval_causality`).

Limitation (honest, by design): both checks are string-based. Moves are matched
as SAN text, not re-derived on the board; causal claims are matched lexically,
so a reason phrased without eval words slips through, and verbal chess claims
("this pins the knight") are still unchecked. That covers the two failure modes
the audit actually found bite — invented moves and invented eval-causes — and
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


# --- Eval-causality check -----------------------------------------------------
# The engine outputs a *number*, never a reason. So any sentence that explains the
# evaluation is, at best, the coach's own story. The human audit found this was
# the dominant failure (10 of 25 cases) and that it comes in two kinds, so the
# check grades rather than shrieks:
#   invented   -> the causal sentence cites NO move the engine produced: the story
#                 has no engine anchor at all. Hard flag (fails `ok`).
#   unverified -> the causal sentence cites a grounded engine move (e.g. "-4.00
#                 because Qxg5 wins the knight", where Qxg5 is the refutation):
#                 the story points at real evidence but only a human can confirm
#                 it. Reported, not failed — the audit saw this kind be right.

_SENTENCE = re.compile(r"(?<=[.!?])\s+")

# A reference to the engine's verdict: a signed eval number, or the small
# vocabulary the coach uses for it. Deliberately tight — words like "better",
# "stronger", "winning" appear in ordinary chess advice and would cry wolf.
# "The edge" is excluded because that phrasing is the board's edge ("play on
# the edge"); the eval sense is "a/slight/your edge".
_EVAL_REF = re.compile(
    r"[+-]\d+(?:\.\d+)?"
    r"|\beval(?:uation)?\b"
    r"|(?<!the )\bedge\b"
    r"|\badvantage\b"
    r"|in your favou?r",
    re.IGNORECASE,
)

# The assertion of a cause. Generic phrases like "by ...ing" only count because
# the caller requires an eval reference in the same sentence.
_CAUSAL = re.compile(
    r"\bbecause\b"
    r"|\bcomes? from\b"
    r"|\bdue to\b"
    r"|\bthanks to\b"
    r"|\bhinges? on\b"
    r"|\bjustif\w*\b"
    r"|\bwhy\b"
    r"|\bby \w+ing\b",
    re.IGNORECASE,
)

# "Gives you an edge" is causal when a chess claim is the giver ("your active
# pieces give you an edge" — an invented reason) but mere translation when the
# eval itself is ("evaluated at +0.20, which gives you a slight edge" — the
# coach restating the number, which is its job). Proxy: an explicit
# engine/evaluation attribution in the sentence marks the giver as the number.
_GIVES_YOU = re.compile(r"\bgiv(?:es?|ing) you\b", re.IGNORECASE)
_ENGINE_SAYS = re.compile(
    r"\b(?:engine|stockfish|computer)\b[^.;]*\b(?:eval\w*|gives?|shows?|says?|rates?)\b"
    r"|\bevaluated at\b",
    re.IGNORECASE,
)


def check_eval_causality(text, allowed):
    """Split the prose into sentences and return (invented, unverified): causal
    claims about the eval with no engine anchor, and ones citing a grounded move."""
    invented, unverified = [], []
    for sentence in _SENTENCE.split(text.strip()):
        if not _EVAL_REF.search(sentence):
            continue
        causal = _CAUSAL.search(sentence) or (
            _GIVES_YOU.search(sentence) and not _ENGINE_SAYS.search(sentence)
        )
        if not causal:
            continue
        cites_engine_move = any(
            _forms(token) & allowed for token in _SAN.findall(sentence)
        )
        (unverified if cites_engine_move else invented).append(sentence.strip())
    return invented, unverified


def check_faithfulness(text, facts):
    """Check the coach's prose against the engine's facts.

    Returns a dict:
      ok                 -> False if an invented *move* or an invented *cause for
                            the eval* was found
      grounded           -> moves named that the engine really produced
      ungrounded_moves   -> moves named that the engine never produced (the flag)
      unverified_squares -> bare squares not in the facts (could be a reference)
      causal_invented    -> sentences explaining the eval with no engine anchor
      causal_unverified  -> eval-causal sentences that at least cite engine moves
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

    causal_invented, causal_unverified = check_eval_causality(text, allowed)

    return {
        "ok": not ungrounded_moves and not causal_invented,
        "grounded": grounded,
        "ungrounded_moves": ungrounded_moves,
        "unverified_squares": unverified_squares,
        "causal_invented": causal_invented,
        "causal_unverified": causal_unverified,
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
        ("eval explained, no engine anchor",
         analysis,
         "You have a clear advantage because your pieces are more active. "
         "Pushing c4 gains more space.",
         False),
        ("eval explained, grounded in the line",
         analysis,
         "Pushing c4 forces the bishop back to Bc2, which is why you keep a "
         "small edge here.",
         True),
        ("eval stated but never explained",
         analysis,
         "The engine gives you a small edge. The move to play is c4.",
         True),
        ("eval translated, not explained",
         analysis,
         "The position is evaluated at +0.20, which gives you a slight edge.",
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
        if r["causal_invented"]:
            print(f"        INVENTED CAUSE: {r['causal_invented']}")
        if r["causal_unverified"]:
            print(f"        unverified cause: {r['causal_unverified']}")
    print("\nself-test:", "all expectations met" if all_good else "MISMATCH — fix the checker")
