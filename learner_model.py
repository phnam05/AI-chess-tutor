"""Stage 3: a running model of ONE learner — which kinds of mistake they repeat.

The invariant still holds: every input here is an engine fact. The kind of each
mistake (`mistake_type`) and the chances the position offered (`chances`) come
from move_review; nothing is read from the language model. This module only
counts them — carefully.

Why not just count? Because one slip must not label a player, and "3 hung
pieces" means something different after 10 moves than after 60. So each kind
keeps a *rate* estimate that starts from a sensible guess and is updated with
every move (Bayesian updating, Beta-Binomial):

  * a CHANCE is a move where the mistake was possible: every move, for a mistake
    you can always make (hanging material); only the moves where the engine's
    best line won material / forced mate, for a "missed" mistake;
  * a MISS is a chance where it actually happened (the engine's verdict);
  * the belief about the rate is Beta(a + misses, b + chances - misses), where
    the starting guess Beta(a, b) sits at the kind's `bar` — the rate we'd call
    worth coaching — and counts as PRIOR_STRENGTH moves of evidence.

A kind is a PATTERN once we're CONFIDENT the player's rate is above its bar
AND it has happened at least MIN_MISSES times; FINE once we're that confident
the rate is below; "unsure" in between. The floor matters early on: with a weak
starting guess, 2 slips in the first 2 moves already look "80% certain", and the
first simulation run showed exactly that — a pattern flagged at move 2 that
vanished later. Two slips are an accident, not a habit. The bars are set by
hand for now; calibrating them from real games is future work.

This is the same shape of problem as estimating a teammate's hidden type and
parameters from its actions in ad-hoc teamwork (Marcolino's line of work): the
player's mistake rates are hidden parameters, estimated online from observed
moves, with the uncertainty kept in view.
"""
import math

# kind -> (which moves count as a chance, the bar, plain words for the student)
KINDS = {
    "lost_material":   ("every",    0.1, "leaving material to be taken"),
    "allowed_mate":    ("every",    0.1, "allowing a forced checkmate"),
    "positional":      ("every",    0.2, "positional slips (nothing lost at once)"),
    "missed_material": ("material", 0.5, "missing a chance to win material"),
    "missed_mate":     ("mate",     0.5, "missing a forced checkmate"),
}

PRIOR_STRENGTH = 10   # the starting guess weighs as much as 10 moves
CONFIDENT = 0.8       # how sure we must be before calling something a pattern
MIN_MISSES = 3        # ...and it must have happened at least this often

# The exact tail formula below needs whole-number Beta parameters.
assert all((bar * PRIOR_STRENGTH).is_integer() for _, bar, _ in KINDS.values())


def new_model():
    """An empty model: no moves seen yet, so every kind is at its starting guess."""
    return {kind: {"chances": 0, "misses": 0, "examples": []} for kind in KINDS}


def update(model, review, where=None):
    """Fold one reviewed move into the model. `where` (e.g. "12. Qg5") is kept
    with each miss so the student can see the evidence behind a pattern.
    Reviews made before mistake kinds existed are skipped, not miscounted."""
    if "mistake_type" not in review or "chances" not in review:
        return model
    for kind, (chance, _, _) in KINDS.items():
        if chance != "every" and not review["chances"].get(chance):
            continue                      # this mistake wasn't possible here
        entry = model[kind]
        entry["chances"] += 1
        if review["mistake_type"] == kind:
            entry["misses"] += 1
            entry["examples"].append(where or review["played_move"])
    return model


def _prob_above(a, b, bar):
    """P(rate > bar) under a Beta(a, b) belief. For whole-number a, b this is
    exactly P(Binomial(a + b - 1, bar) <= a - 1) — no sampling, no SciPy."""
    n = a + b - 1
    return sum(math.comb(n, j) * bar**j * (1 - bar)**(n - j) for j in range(a))


def summary(model):
    """One row per kind: the counts, the estimated rate, how sure we are that
    it's above the bar, and the verdict (pattern / fine / unsure)."""
    rows = []
    for kind, (_, bar, words) in KINDS.items():
        e = model[kind]
        a0 = round(bar * PRIOR_STRENGTH)
        a = a0 + e["misses"]
        b = (PRIOR_STRENGTH - a0) + (e["chances"] - e["misses"])
        p_above = _prob_above(a, b, bar)
        if p_above >= CONFIDENT and e["misses"] >= MIN_MISSES:
            status = "pattern"
        elif p_above <= 1 - CONFIDENT:
            status = "fine"
        else:
            status = "unsure"
        rows.append({
            "kind": kind, "words": words, "bar": bar,
            "chances": e["chances"], "misses": e["misses"],
            "estimate": a / (a + b), "p_above": p_above, "status": status,
            "examples": list(e["examples"]),
        })
    return rows


def patterns(model):
    """Just the kinds we're confident are a recurring weakness."""
    return [r for r in summary(model) if r["status"] == "pattern"]


# --- Self-test on hand-made reviews (no engine, no API) -----------------------
if __name__ == "__main__":
    def review(kind=None, material=False, mate=False, san="x"):
        return {"played_move": san, "mistake_type": kind,
                "chances": {"material": material, "mate": mate}}

    def show(title, model):
        print(f"\n{title}")
        for r in summary(model):
            print(f'  {r["kind"]:16s} {r["misses"]:>2}/{r["chances"]:<2} chances  '
                  f'est {r["estimate"]:.2f} (bar {r["bar"]})  '
                  f'P(above bar) {r["p_above"]:.2f}  -> {r["status"]}')

    expectations = []

    # One hung piece in 5 moves: a slip, not yet a pattern.
    m = new_model()
    for k in (None, "lost_material", None, None, None):
        update(m, review(k))
    show("1 hung piece in 5 moves", m)
    expectations.append(("one slip is not a pattern", not patterns(m)))

    # 2 positional slips in the first 2 moves: the odds say 84%, but two
    # slips are an accident, not a habit (the floor of MIN_MISSES).
    m = new_model()
    for _ in range(2):
        update(m, review("positional"))
    show("2 positional slips in the first 2 moves", m)
    expectations.append(("two early slips are not a pattern", not patterns(m)))

    # 4 hung pieces in 12 moves: now a pattern.
    m = new_model()
    for i in range(12):
        update(m, review("lost_material" if i % 3 == 0 else None), where=f"move {i + 1}")
    show("4 hung pieces in 12 moves", m)
    expectations.append(("repeated hanging is a pattern",
                         [r["kind"] for r in patterns(m)] == ["lost_material"]))
    expectations.append(("evidence is kept",
                         summary(m)[0]["examples"] == ["move 1", "move 4", "move 7", "move 10"]))

    # Missed 3 of 3 free-material chances in 10 moves.
    m = new_model()
    for i in range(10):
        chance = i in (2, 5, 8)
        update(m, review("missed_material" if chance else None, material=chance))
    show("missed 3 of 3 chances to win material", m)
    row = {r["kind"]: r for r in summary(m)}["missed_material"]
    expectations.append(("missed chances are counted per chance, not per move",
                         row["chances"] == 3 and row["status"] == "pattern"))

    # 20 clean moves: confident the player doesn't hang pieces.
    m = new_model()
    for _ in range(20):
        update(m, review())
    show("20 clean moves", m)
    expectations.append(("clean play reads as fine",
                         {r["kind"]: r["status"] for r in summary(m)}["lost_material"] == "fine"))

    # An old review without the new fields is skipped, not miscounted.
    m = new_model()
    update(m, {"played_move": "e4", "label": "Best"})
    expectations.append(("old reviews are skipped", all(r["chances"] == 0 for r in summary(m))))

    print()
    for name, ok in expectations:
        print(f'  [{"ok" if ok else "WRONG"}] {name}')
    print("\nself-test:", "all expectations met" if all(ok for _, ok in expectations) else "MISMATCH")
