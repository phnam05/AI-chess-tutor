# Faithfulness — human audit

**You are the ground truth.** For each explanation judge ONLY whether the coach stuck to the engine's facts or invented something — *fidelity to the engine*, not whether it is the best chess. Then, separately, note anything you would reword even when it is faithful.

Per case, fill:

- **A. Faithful to the engine?** — `Yes` / `No`
- **B. If No, what did it invent?** — the move or claim, else `—`
- **C. What I'd change (even if faithful)** — free text, else `nothing`
- **D. (optional) Change type** — `wording` / `too long` / `too short` / `too vague` / `missed teaching point` / `level off` / `other`

*Filled 2026-07-03 from the auditor's verdict (verbatim source: `human response.txt` at the repo root). The auditor used a four-level scale for A — Yes / Mostly yes / Partially / No — which is preserved here because it carries more information than the planned Yes/No.*

## Summary

| # | Case | Phase | Type | Checker | A. Faithful? | Agree w/ checker? | D. Change type |
|--:|------|-------|------|:-------:|:------------:|:-----------------:|----------------|
| 1 | Ruy Lopez (after 3...a6) | opening | position | clean | Partially | partly | causal invention |
| 2 | Italian Game (Giuoco Piano) | opening | position | clean | Partially | partly | clarity + causal drift |
| 3 | Sicilian Najdorf | opening | position | clean | Partially | partly | causal invention + drift |
| 4 | Queen's Gambit Declined | opening | position | clean | **No** | **no** | **factual error** + causal invention |
| 5 | French Defence (Winawer) | opening | position | clean | Partially | partly | causal invention |
| 6 | King's Indian Defence | opening | position | clean | Mostly yes | mostly | causal invention |
| 7 | Caro-Kann Defence | opening | position | clean | Yes | yes | wording |
| 8 | Closed centre, Black to plan | middlegame | position | clean | Partially | partly | causal invention (high-risk) |
| 9 | Queen on f4, White attacking | middlegame | position | clean | Partially | partly | causal invention + drift |
| 10 | Open game, Black to move | middlegame | position | clean | Mostly yes | mostly | causal invention |
| 11 | King + pawn vs king | endgame | position | clean | **No** | **no** | **factual error** |
| 12 | Rook + pawn endgame | endgame | position | clean | Mostly yes | mostly | causal invention |
| 13 | Queen vs lone king (mating) | endgame | position | clean | Partially | partly | missed teaching point |
| 14 | Central king & pawn | endgame | position | clean | Mostly yes | mostly | causal invention |
| 15 | Italian: 3.Bb5 (good) | opening | move | clean | Yes | yes | clean |
| 16 | Opening move 1.e4 (good) | opening | move | clean | Yes | yes | clean |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | clean | Mostly yes | mostly | causal drift |
| 18 | Develop with ...Be7 (good) | middlegame | move | clean | Yes | yes | clean (label bug) |
| 19 | Scotch: ...exd4 (good) | opening | move | clean | Yes | yes | clean (checker gap) |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | clean | Yes | yes | clean |
| 21 | ...Nxe4?? drops a piece (blunder) | middlegame | move | clean | Yes | yes | clean (label bug) |
| 22 | Wing push 1.a4 (passive) | opening | move | clean | Yes | yes | wording |
| 23 | Edge push 1.h4 (passive) | opening | move | clean | Yes | yes | clean (repetition) |
| 24 | Premature 3.Ng5?! (inaccuracy) | opening | move | clean | Yes | yes | clean (label bug) |
| 25 | Passive 2.Na3 (inaccuracy) | opening | move | clean | Yes | yes | clean (label bug) |

## Audit result (2026-07-03)

Human verdict across the 25 cases: **11 Yes / 5 Mostly yes / 7 Partially / 2 No.**
The automatic checker had said *clean* on all 25, so it fully agrees with the
human on 16/25 — and the gap **is** the finding: everything the human caught
lies outside what a move-token checker can see, by construction.

Cross-cutting patterns (the auditor's, verified where mechanically checkable):

1. **Causal invention (eval attribution) — ~13/25, the dominant issue.** The
   coach explains *why* the eval is what it is when Stockfish gave no reason.
   Sometimes harmless (small evals, plausible story), sometimes risky — worst is
   case 8, where −4.79 is "explained" by open files when the real cause is
   unknown and likely tactical.
2. **Causal drift (cases 2, 3, 9, 17).** The move is real and grounded, but the
   stated purpose isn't what the engine's line actually shows. Different from
   invention: nothing false is asserted about *moves*, only about *intent*.
3. **Two genuine factual errors.** Case 4 calls the g5 bishop "light-squared"
   (it came from c1 and is dark-squared); case 11 inverts the king/pawn roles in
   a king-and-pawn endgame. Rarer but more serious than unverified filler.
4. **Four dataset label mismatches (18, 21, 24, 25).** The hand-written case
   *titles* contradicted the engine's grade field. Verified: the titles are
   display-only guesses in `evaluate_faithfulness.py`, never fed to the engine
   or the coach — and the coach followed the real grade every time, so this is a
   metadata bug, not a coach failure. Titles corrected in the source 2026-07-03
   (this sheet keeps the original titles as the audited record).
5. **Checker under-coverage (cases 7, 17, 19).** Some claims match the engine's
   line but aren't credited in "grounded", so "clean (grounded: X)" understates
   how much of a response was actually checkable.

Data integrity, re-verified 2026-07-03: all 25 recorded fact sets reproduce
byte-for-byte on the deterministic engine. Two audit puzzles resolved along the
way: case 9's PV ending "…Qxf4" is a queen trade truncated one ply before the
Bxf4 recapture (engine lines are now rendered to a quiet move — see
`render_line` in `engine_analysis.py`); case 15's played-eval > best-eval is the
inherent before/after search-root asymmetry, which the grader already clamps.
Related observation: a PV is a *forecast* — a fresh search of a position reached
by following it can prefer a different near-equal move (after case 9's Be3, the
PV said Qd5 but a fresh search says Qa5+; both individually deterministic). See
the CLAUDE.md gotcha before "fixing" that.

## Cases

### 1. Ruy Lopez (after 3...a6)  (position, beginner)

**Board (FEN)** — `r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4`
**Engine facts** — best: `Ba4` · eval: `+0.42 pawns` · PV: `Ba4, Nf6, O-O, Nxe4, d4, b5`
**Checker** — clean (grounded: —)

**Coach said:**
> Pulling your bishop back to a4 keeps it safe while maintaining pressure on the knight that is protecting the center pawn. The slight edge for you comes from keeping your pieces active and ready to castle your king to safety soon. If your opponent tries to chase the bishop away, how do you think your center pawns might help you control more of the board?

- **A. Faithful?** Partially — chess claims are fine, but nothing is engine-grounded (grounded: —).
- **B. Invented?** Yes — "The slight edge for you comes from keeping your pieces active…" fabricates a reason for +0.42 that Stockfish never gave.
- **C. What I'd change:** Cut the eval-justification sentence, or replace it with a grounded fact. Rewrite the closing question — it's redundant and teaches nothing.
- **D. Type:** causal invention (eval attribution) + weak pedagogical follow-up

---

### 2. Italian Game (Giuoco Piano)  (position, intermediate)

**Board (FEN)** — `r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4`
**Engine facts** — best: `c3` · eval: `+0.20 pawns` · PV: `c3, Nf6, d4, exd4, e5, d5`
**Checker** — clean (grounded: c3, d4, Nf6)

**Coach said:**
> It is great to see you developing your pieces so well, and playing c3 here is a smart way to prepare for a central push. By supporting a future d4 move, you are aiming to claim more space in the center and challenge their control of the board. If black responds with Nf6, you can follow through with d4 to open lines for your pieces and fight for the initiative. If you were sitting at the board, where do you think your pieces would be most active once that central pawn tension is resolved?

- **A. Faithful?** Partially — the move sequence matches the PV (c3, Nf6, d4 all grounded); the stated purpose of d4 drifts.
- **B. Invented?** Mild — "open lines for your pieces" isn't the PV's point; the real idea is e5 hitting the f6-knight for a tempo.
- **C. What I'd change:** Name c3's subject explicitly ("c3 sets up d4 next move"). Cut the redundancy with sentence 1. Ground the "why" in e5 hitting the knight.
- **D. Type:** pedagogical clarity (ambiguous referent, redundancy) + mild causal drift (purpose ≠ PV mechanism)

---

### 3. Sicilian Najdorf  (position, advanced)

**Board (FEN)** — `rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6`
**Engine facts** — best: `Be3` · eval: `+0.51 pawns` · PV: `Be3, e5, Nb3, Ng4, Bd2, Nf6`
**Checker** — clean (grounded: Be3, e5)

**Coach said:**
> By playing Be3, you are cementing your control over the d4-square and preparing for a solid Sicilian setup that balances space with flexibility. This move secures a slight edge of +0.51 because it anticipates the common e5 push, allowing you to reposition your knight to b3 to maintain central tension while preparing to challenge the kingside knight. Think about how this development choice dictates the flow of the game compared to a more aggressive or immediate pawn expansion; how would you plan to maneuver your pieces if your opponent chooses a more restrained development instead?

- **A. Faithful?** Partially.
- **B. Invented?** Yes — the eval attribution ("+0.51 because it anticipates e5") is unverified. Also "preparing to challenge the kingside knight" misdescribes Nb3 — the PV shows Black's Ng4 attacking the bishop, not White challenging a knight.
- **C. What I'd change:** Cut the eval-causal sentence. Fix the Nb3 description to match what the PV actually shows.
- **D. Type:** causal invention + causal drift

---

### 4. Queen's Gambit Declined  (position, intermediate)

**Board (FEN)** — `rnbqk2r/ppp1bppp/4pn2/3p2B1/2PP4/2N5/PP2PPPP/R2QKBNR w KQkq - 4 5`
**Engine facts** — best: `e3` · eval: `+0.31 pawns` · PV: `e3, h6, Bh4, O-O, Nf3, Ne4`
**Checker** — clean (grounded: e3, h6)

**Coach said:**
> Playing e3 is a solid choice here because it secures your central pawn structure and opens the path for your light-squared bishop to retreat safely if challenged. By tucking the bishop away to h4 after black plays h6, you maintain long-term pressure on the board and keep your pieces flexible for the upcoming middlegame. This move keeps the evaluation slightly in your favor by ensuring your development remains harmonious while you wait to see how black chooses to challenge your center. Given how you want to deploy your knights and complete your kingside development, where do you think your pieces will have the most influence once you castle?

- **A. Faithful?** No.
- **B. Invented?** Yes — and this one's a real error, not just unverified filler: the bishop on g5 is dark-squared (it came from c1), not "light-squared" as stated. Plus the usual eval-causal invention.
- **C. What I'd change:** Fix the bishop colour. This is a factual chess error, not a phrasing issue — higher severity than the other cases.
- **D. Type:** factual error + causal invention

---

### 5. French Defence (Winawer)  (position, advanced)

**Board (FEN)** — `rnbqk1nr/ppp2ppp/4p3/3p4/1b1PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 2 4`
**Engine facts** — best: `e5` · eval: `+0.64 pawns` · PV: `e5, c5, a3, Bxc3+, bxc3, Qc7`
**Checker** — clean (grounded: e5, c5)

**Coach said:**
> By playing e5, you immediately claim central space and force the black knight to relocate to a less ideal square, which justifies your +0.64 advantage. This push creates a clear strategic imbalance where you accept a slightly compromised pawn structure in exchange for superior control of the center and long-term attacking potential. If black continues with the critical line of c5 and an exchange on c3, you are left with the bishop pair and a solid space advantage to work with in the resulting middlegame. How would you plan to utilize your extra space to restrict black's pieces once the minor pieces start coming off the board?

- **A. Faithful?** Partially.
- **B. Invented?** Mild — the eval-causal claim again. "Forces the black knight to relocate" is imprecise: the knight hasn't moved yet, e5 just denies it the f6 square.
- **C. What I'd change:** Say "denies Nf6" instead of "forces relocation". Drop the eval justification or ground it in the PV's actual bxc3 doubled-pawn outcome.
- **D. Type:** causal invention + minor imprecision

---

### 6. King's Indian Defence  (position, intermediate)

**Board (FEN)** — `rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N5/PP3PPP/R1BQKBNR w KQkq - 0 5`
**Engine facts** — best: `Nf3` · eval: `+0.65 pawns` · PV: `Nf3, O-O, Be2, e5, Be3, Qe8`
**Checker** — clean (grounded: e5)

**Coach said:**
> It is time to develop your knight to f3 to support your center and prepare for kingside castling. By doing this, you are solidifying your control over the d4 and e5 squares, which gives you a slight edge in space and long-term stability. Your opponent will likely look to challenge your control of the center with e5, but by following up with your bishop, you maintain a strong setup that keeps your pieces coordinated. How would you plan to react if black continues to pressure your center after you castle?

- **A. Faithful?** Mostly yes.
- **B. Invented?** Mild — only the eval-causal line ("gives you a slight edge in space").
- **C. What I'd change:** Cut/soften that one sentence. The rest is well grounded (the Be3 follow-up matches the PV).
- **D. Type:** causal invention (isolated)

---

### 7. Caro-Kann Defence  (position, beginner)

**Board (FEN)** — `rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3`
**Engine facts** — best: `e5` · eval: `+0.30 pawns` · PV: `e5, Bf5, c4, e6, Nc3, Ne7`
**Checker** — clean (grounded: e5)

**Coach said:**
> Pushing your pawn to e5 is a great way to grab extra space in the center and cramp your opponent's pieces. This move forces their bishop to move again and sets you up to control more of the board. Since the game is still very even, how would you decide where to develop your knights next to support this space advantage?

- **A. Faithful?** Yes.
- **B. Invented?** No major issue — "forces their bishop to move" is a bit strong (it's best practice, not forced) but low risk.
- **C. What I'd change:** Soften "forces" to "encourages" or "invites".
- **D. Type:** wording

---

### 8. Closed centre, Black to plan  (position, intermediate)

**Board (FEN)** — `r2q1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 b - - 0 9`
**Engine facts** — best: `Qc7` · eval: `-4.79 pawns` · PV: `Qc7, Bc2, Rad8, a4, Rfe8, Qe2`
**Checker** — clean (grounded: Qc7)

**Coach said:**
> You are in a very solid position here, and playing Qc7 is a great way to centralize your queen while keeping your options flexible. By stepping off the d-file, you clear the way for your rook to join the fight, setting you up to control the center and put pressure on their d4 pawn. The evaluation is heavily in your favor because your pieces are poised to dominate the open files, making it hard for White to find any counterplay. How do you think your rook on d8 will change the way White has to defend their central pawns?

- **A. Faithful?** Partially.
- **B. Invented?** Yes, and worth flagging harder than most: −4.79 is a huge eval, and "your pieces dominate open files" is a speculative story for a swing that size. Large evals like this often hide a concrete tactic/material point the coach doesn't actually know about — this is the risk pattern the checker should probably catch.
- **C. What I'd change:** Either don't explain large evals causally at all, or explicitly hedge ("the engine sees a big advantage here, likely from more than just piece activity").
- **D. Type:** causal invention (high-risk instance)

---

### 9. Queen on f4, White attacking  (position, advanced)

**Board (FEN)** — `r1bq1rk1/pp3pp1/2n1p3/2P1P2p/5Q2/8/PPP2PPP/R1B1KB1R w KQ - 1 13`
**Engine facts** — best: `Be3` · eval: `+2.68 pawns` · PV: `Be3, Qd5, Bc4, Qxe5, O-O-O, Qxf4`
**Checker** — clean (grounded: Be3)

**Coach said:**
> With an evaluation of +2.68, you have a commanding advantage here because your space advantage and central control severely cramp Black’s development. Playing Be3 is the strongest continuation because it brings your final minor piece into the game while reinforcing the critical d4 square and preparing to link your rooks. By solidifying the center, you effectively neutralize Black's attempts to challenge your advanced e5 pawn, allowing you to transition into a long-term squeeze. How would you plan to coordinate your rooks once you complete your development?

- **A. Faithful?** Partially.
- **B. Invented?** Yes — the eval-causal claim again. Also the stated purpose ("reinforcing d4, linking rooks") doesn't match the PV, which is actually a sharp tactical queen-chase line (Qd5, Bc4, Qxe5…). *The PV's odd ending Qxf4 was investigated and resolved: it is a legal queen trade truncated one ply before the Bxf4 recapture — a display artifact, now fixed by `render_line`, not a data error.*
- **C. What I'd change:** Rewrite Be3's purpose to reflect the tactical PV, not generic development language.
- **D. Type:** causal invention + causal drift

---

### 10. Open game, Black to move  (position, beginner)

**Board (FEN)** — `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5`
**Engine facts** — best: `dxe4` · eval: `-0.87 pawns` · PV: `dxe4, Nxe5, Qd5, Bxc6+, bxc6, d4`
**Checker** — clean (grounded: dxe4, Nxe5)

**Coach said:**
> You should play dxe4 because it immediately captures the center pawn and forces White to react to the pressure on their knight. This move gives you a slight advantage because it clears the path for your queen and disrupts White's setup in the middle of the board. If White plays the main response of Nxe5, how would you develop your pieces to keep the initiative?

- **A. Faithful?** Mostly yes.
- **B. Invented?** Mild — only the eval-causal sentence. The "pressure on their knight" claim is actually correct (the pawn on e4 hits Nf3).
- **C. What I'd change:** Cut/rephrase the eval justification.
- **D. Type:** causal invention (isolated)

---

### 11. King + pawn vs king  (position, beginner)

**Board (FEN)** — `8/8/4k3/8/4K3/8/4P3/8 w - - 0 1`
**Engine facts** — best: `e3` · eval: `+5.11 pawns` · PV: `e3, Kf6, Kd5, Kf7, e4, Ke7`
**Checker** — clean (grounded: e3)

**Coach said:**
> You are currently in a winning king and pawn endgame, and playing e3 is the perfect way to support your king and prepare to push your pawn all the way to promotion. By moving the pawn forward, you create a solid base that protects your king while giving you a clear path to make a queen. If you follow this plan, you will likely be able to force your opponent's king away and win the game. How do you think your opponent might try to stop your pawn from reaching the other side?

- **A. Faithful?** No.
- **B. Invented?** Yes — this one's logically backwards. "e3 supports your king" and "the pawn protects your king" get the relationship inverted; in king-and-pawn endgames the king escorts the pawn, not the other way round.
- **C. What I'd change:** Rewrite to say the king should shepherd the pawn forward, not that the pawn protects the king.
- **D. Type:** factual/logical error (causal direction reversed)

---

### 12. Rook + pawn endgame  (position, intermediate)

**Board (FEN)** — `8/8/8/4k3/8/8/4P3/4K2R w K - 0 1`
**Engine facts** — best: `Kd2` · eval: `+6.30 pawns` · PV: `Kd2, Ke4, Rg1, Kd4, e3+, Ke4`
**Checker** — clean (grounded: Kd2, Rg1, e3)

**Coach said:**
> You have a significant advantage here because your rook and king can easily coordinate to force the enemy king away from the center. Playing Kd2 is the best way to activate your king and support your pawn, as it prepares to restrict the opponent's movement while securing your position. By following up with Rg1 and e3, you’re creating a wall that will eventually force the black king to give up ground. How would you plan to safely push that e-pawn forward once your king reaches a more active square?

- **A. Faithful?** Mostly yes.
- **B. Invented?** Mild — a generic eval justification, but the Rg1/e3 follow-through is accurately grounded.
- **C. What I'd change:** Minor — tighten the opening eval sentence.
- **D. Type:** causal invention (low severity)

---

### 13. Queen vs lone king (mating)  (position, beginner)

**Board (FEN)** — `8/5k2/8/8/8/8/5K2/5Q2 w - - 0 1`
**Engine facts** — best: `Kg3+` · eval: `+5.09 pawns` · PV: `Kg3+, Kg6, Kh4, Kh6, Qf5, Kg7`
**Checker** — clean (grounded: —)

**Coach said:**
> It looks like you have a great chance to corner your opponent's king here. By moving your king to g3 with check, you force their king to move and begin cutting off their escape squares. This helps you trap them against the edge of the board so your queen can deliver a final blow. How do you think you can keep their king trapped after they move away?

- **A. Faithful?** Partially — misses the actual mechanism.
- **B. Invented?** Mild — Kg3+ is a *discovered check* via the queen on the f-file (the king was blocking it). The coach never explains this — it's the whole point of the move — and substitutes a vague "cutting off escape squares" narrative instead.
- **C. What I'd change:** Explicitly name the discovered check. A missed teaching opportunity, not a wrong claim.
- **D. Type:** missed teaching point (nothing false, just thin)

---

### 14. Central king & pawn  (position, advanced)

**Board (FEN)** — `8/8/8/3k4/8/3K4/3P4/8 w - - 0 1`
**Engine facts** — best: `Kc3` · eval: `+0.44 pawns` · PV: `Kc3, Kc5, d4+, Kb6, Kc4`
**Checker** — clean (grounded: Kc3, Kc5, d4+)

**Coach said:**
> You are facing a classic endgame scenario where the distance of your king from the opponent's critical squares determines the outcome. By playing Kc3, you adopt a waiting profile that forces your opponent to commit their king first, which is essential given that your +0.44 edge hinges on maintaining the tension while preparing to push your d-pawn. If they respond with Kc5, the critical follow-up d4+ allows you to seize the initiative and control the center, putting the burden of defense entirely on them. How do you think the dynamic shifts if your opponent tries to avoid the pawn break instead of challenging your king directly?

- **A. Faithful?** Mostly yes.
- **B. Invented?** Yes — the eval-causal claim ("+0.44 edge hinges on maintaining tension"). The Kc5/d4+ follow-up is well grounded.
- **C. What I'd change:** Cut the eval justification.
- **D. Type:** causal invention (isolated)

---

### 15. Italian: 3.Bb5 (good)  (move, beginner)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3` (the position *before* the played move)
**Engine facts** — played: `Bb5` · best: `Bb5` · grade: `Best` · evals: played `+0.44` / best `+0.35` · refutation: `a6, Ba4, Nf6, O-O, Be7, Re1`
**Checker** — clean (grounded: a6)

**Coach said:**
> That is a fantastic move! By putting your bishop on b5, you are putting direct pressure on the knight that is protecting your opponent's center pawn. If your opponent plays a6 to challenge you, you can simply retreat to a4, keeping your bishop active and ready to help you castle your king to safety soon. How do you think your opponent will try to defend their center pawn now?

- **A. Faithful?** Yes.
- **B. Invented?** No.
- **C. What I'd change:** Nothing major. Side note: the played eval (+0.44) is higher than the "best" eval (+0.35) in the data — *investigated and resolved: the inherent before/after search-root asymmetry (same depth, roots one ply apart); the grader clamps it, so grading is unaffected.*
- **D. Type:** clean

---

### 16. Opening move 1.e4 (good)  (move, beginner)

**Board (FEN)** — `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` (the position *before* the played move)
**Engine facts** — played: `e4` · best: `e4` · grade: `Best` · evals: played `+0.35` / best `+0.49` · refutation: `e5, Nf3, Nc6, Bb5, a6, Bxc6`
**Checker** — clean (grounded: e4, e5)

**Coach said:**
> Great start, playing e4 is a classic way to take control of the center and open lines for your queen and bishop. By putting a pawn in the middle, you make it much easier to develop your pieces quickly and keep your king safe. If your opponent responds with e5, how do you think you can best put pressure on that pawn next?

- **A. Faithful?** Yes.
- **B. Invented?** No.
- **C. What I'd change:** Nothing. One of the cleanest responses.
- **D. Type:** clean

---

### 17. Ruy Lopez: 4.Ba4 (good)  (move, intermediate)

**Board (FEN)** — `r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4` (the position *before* the played move)
**Engine facts** — played: `Ba4` · best: `Ba4` · grade: `Best` · evals: played `+0.48` / best `+0.42` · refutation: `Nf6, O-O, b5, Bb3, Nxe4, d4`
**Checker** — clean (grounded: Ba4, Nf6, d4, b5, Nxe4)

**Coach said:**
> Great choice playing Ba4; by keeping your bishop on the board, you maintain your pressure on the e5-pawn and keep the tension in the center. The engine shows a slight advantage here, and as your opponent likely responds with Nf6 and castles, you are well-positioned to support your center with d4 after pulling your bishop back to b3. Since your opponent will probably try to challenge your control with b5 and eventually Nxe4, how do you think you can use your lead in development to punish them if they grab that pawn too greedily?

- **A. Faithful?** Mostly yes.
- **B. Invented?** Mild — "pressure on the e5-pawn" oversimplifies (it's really pressure on the knight defending e5). "Lead in development" is unverified flavour text.
- **C. What I'd change:** Say "pressure on the knight defending e5" instead.
- **D. Type:** minor causal drift

---

### 18. Develop with ...Be7 (good)  (move, intermediate)

**Board (FEN)** — `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5` (the position *before* the played move)
**Engine facts** — played: `Be7` · best: `dxe4` · grade: `Mistake` · evals: played `-2.42` / best `-0.87` · refutation: `Nxe5, O-O, Bxc6, bxc6, Nxc6, Qd6`
**Checker** — clean (grounded: Be7, dxe4, Nxe5)

**Coach said:**
> Your move Be7 lets your opponent take control of the center because you missed the chance to simplify the position. By playing Be7 instead of dxe4, you allow White to play Nxe5, which immediately puts pressure on your knight and forces you into a defensive posture. In the expected line, White proceeds to swap off pieces, leaving you with a compromised pawn structure while they gain more space and initiative. Next time, how might you look for ways to challenge White's central pawns before they have a chance to settle in?

- **A. Faithful?** Yes — the text correctly treats it as an error, matching the real grade.
- **B. Invented?** No.
- **C. What I'd change:** Nothing in the coach text. The case *title* said "(good)" but the engine grade is Mistake (−2.42 vs −0.87 best) — dataset labeling bug #1, title corrected in `evaluate_faithfulness.py` 2026-07-03.
- **D. Type:** clean / dataset label mismatch

---

### 19. Scotch: ...exd4 (good)  (move, intermediate)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 3` (the position *before* the played move)
**Engine facts** — played: `exd4` · best: `exd4` · grade: `Best` · evals: played `-0.42` / best `-0.18` · refutation: `Nxd4, Nf6, Nxc6, dxc6, Qxd8+, Kxd8`
**Checker** — clean (grounded: Nf6)

**Coach said:**
> You played a very solid move here, as capturing the pawn challenges White's control over the center and clears the way for your pieces. By trading this pawn, you are likely heading toward an endgame where your king becomes quite active after the queens are traded off. White will likely respond by recapturing with their knight to centralize it, but this gives you the opportunity to develop your pieces toward the center with Nf6. Since the position is now very balanced, what do you think is the best square for your bishop to influence the game once your knight reaches the center?

- **A. Faithful?** Yes.
- **B. Invented?** No significant fabrication — the queen-trade/king-activity claim isn't in the "grounded" list but does match the refutation line (Qxd8+, Kxd8). A checker gap, not a coach error.
- **C. What I'd change:** Nothing major.
- **D. Type:** clean (checker under-coverage noted)

---

### 20. Scholar's mate trap: ...Nf6?? (blunder)  (move, beginner)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3` (the position *before* the played move)
**Engine facts** — played: `Nf6` · best: `g6` · grade: `Blunder` · evals: played `-100.00` / best `+0.40` · refutation: `Qxf7#`
**Checker** — clean (grounded: Qxf7#, g6)

**Coach said:**
> Oh no, by moving your knight, you left your pawn on f7 undefended, and your opponent can now play Qxf7# to end the game immediately. Your king is in big trouble because that f7 square is the weakest point in your position. Would you like to look at how playing g6 earlier would have blocked that white queen from targeting your king?

- **A. Faithful?** Yes.
- **B. Invented?** No.
- **C. What I'd change:** Nothing. Strongest case in the set — urgent tone matches severity, fully grounded.
- **D. Type:** clean

---

### 21. ...Nxe4?? drops a piece (blunder)  (move, intermediate)

**Board (FEN)** — `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5` (the position *before* the played move)
**Engine facts** — played: `Nxe4` · best: `dxe4` · grade: `Mistake` · evals: played `-2.47` / best `-0.87` · refutation: `d3, Nxf2, Bxc6+, bxc6, Rxe5+, Be6`
**Checker** — clean (grounded: d3, Nxf2, Bxc6+, dxe4)

**Coach said:**
> It looks like taking that pawn with your knight allowed White to grab the initiative. By playing d3, your opponent forces your knight to commit, and after you look for compensation with Nxf2, they can trade off your active bishop with Bxc6+ to shatter your queenside structure. This exchange leaves you with doubled pawns and gives White a comfortable lead in space, making it tough to coordinate your pieces. If you had played dxe4 instead, you would have maintained a much tighter game by keeping your pieces flexible. What do you think you could have done differently to keep your pawn structure intact?

- **A. Faithful?** Yes — very well grounded, ties d3/Nxf2/Bxc6+/dxe4 into a coherent line.
- **B. Invented?** No.
- **C. What I'd change:** Nothing in the text. The case *title* said "blunder" but the engine grade is Mistake — dataset labeling bug #2, title corrected 2026-07-03.
- **D. Type:** clean / dataset label mismatch

---

### 22. Wing push 1.a4 (passive)  (move, beginner)

**Board (FEN)** — `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` (the position *before* the played move)
**Engine facts** — played: `a4` · best: `e4` · grade: `Inaccuracy` · evals: played `-0.32` / best `+0.49` · refutation: `e5, e4, Nf6, Nf3, d5, exd5`
**Checker** — clean (grounded: a4, e5, e4)

**Coach said:**
> Starting with a4 is a bit unusual because it doesn't help you take control of the center or get your pieces ready to join the game. When you play on the edge like that, your opponent can easily claim the middle squares for themselves, like they would likely do by playing e5 to block your path. It is usually better to start by opening up space for your queen and bishop to move out, which is why playing e4 is a much stronger way to begin. If you could restart the game, how do you think moving your king's pawn forward would change your control of the board?

- **A. Faithful?** Yes.
- **B. Invented?** No major issue — "block your path" is odd phrasing (a4 wasn't going anywhere) but not factually wrong.
- **C. What I'd change:** Reword "block your path".
- **D. Type:** wording

---

### 23. Edge push 1.h4 (passive)  (move, beginner)

**Board (FEN)** — `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` (the position *before* the played move)
**Engine facts** — played: `h4` · best: `e4` · grade: `Mistake` · evals: played `-0.43` / best `+0.49` · refutation: `d5, d4, Nf6, e3, c5, c4`
**Checker** — clean (grounded: d5, e4)

**Coach said:**
> That move is a bit tricky because it doesn't help you fight for the center of the board where most of the action happens. By playing on the side, you give your opponent a chance to immediately grab the middle with a move like d5, making it easier for them to control the game. It is usually much more effective to start by moving your center pawns, like e4, to open paths for your bishop and queen. If you were starting the game again, how do you think moving your king's pawn forward would change your options?

- **A. Faithful?** Yes.
- **B. Invented?** No.
- **C. What I'd change:** Nothing factual. Note: nearly template-identical to case 22 — worth checking whether the coach is low-diversity on "passive move" responses.
- **D. Type:** clean / style repetition flag

---

### 24. Premature 3.Ng5?! (inaccuracy)  (move, advanced)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3` (the position *before* the played move)
**Engine facts** — played: `Ng5` · best: `Bb5` · grade: `Blunder` · evals: played `-4.00` / best `+0.35` · refutation: `Qxg5, d4, Qg6, dxe5, d6, exd6`
**Checker** — clean (grounded: Qxg5)

**Coach said:**
> By moving your knight to g5, you’ve committed a serious blunder that abandons your development in favor of a premature attack. Your opponent can now simply respond with Qxg5, capturing your knight for free and leaving you down a full piece for absolutely no compensation, which is exactly why the evaluation swings to -4.00. While you were likely hoping to create pressure on f7, your light-squared bishop remains trapped at home, leaving you unable to support your aggressive intentions. Does this look like the kind of position where you can afford to sacrifice a piece without a concrete forced mate?

- **A. Faithful?** Yes — correctly treats it with blunder-level urgency despite the title downgrading it.
- **B. Invented?** No. Notably, the eval-causal claim here ("−4.00 because you're down a full piece") is actually justified — a rare good example of a *grounded* causal explanation. The bishop-colour claim ("light-squared") is also correct this time.
- **C. What I'd change:** Nothing in the text. The case *title* said "inaccuracy" but the engine grade is Blunder — dataset labeling bug #3, title corrected 2026-07-03. Worth noting: the bishop colour was right here but wrong in case 4 — the model isn't reliably tracking square colour, just getting lucky/unlucky.
- **D. Type:** clean / dataset label mismatch

---

### 25. Passive 2.Na3 (inaccuracy)  (move, intermediate)

**Board (FEN)** — `rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2` (the position *before* the played move)
**Engine facts** — played: `Na3` · best: `Nf3` · grade: `Good` · evals: played `+0.06` / best `+0.36` · refutation: `e6, Nf3, a6, Be2, d5, exd5`
**Checker** — clean (grounded: Na3, Nf3, e6, d5)

**Coach said:**
> By playing Na3, you have developed a piece, but you have slightly shifted your focus away from the center compared to the standard Nf3. Your opponent will likely respond with e6, challenging your central control and preparing to push d5, which forces you to decide how to handle the pressure in the middle of the board. While your move is playable, it gives Black a bit more freedom to set up their own structure, whereas a central knight jump would have made it harder for them to equalize so easily. How do you think you will support your e4 pawn once they start pushing their d-pawn?

- **A. Faithful?** Yes — the tone correctly reflects a mild, non-serious issue (matches "Good", not "inaccuracy").
- **B. Invented?** No.
- **C. What I'd change:** Nothing in the text. The case *title* said "inaccuracy" but the engine grade is literally Good — dataset labeling bug #4, the most severe mismatch (not adjacent severities, contradictory ones); title corrected 2026-07-03.
- **D. Type:** clean / dataset label mismatch (severe)

---
