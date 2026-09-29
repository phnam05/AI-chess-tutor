# To-do list

*Last updated: 30 September 2026, 02:30 (Vietnam time).* Tick a box (`[x]`) when a task is done.
Each task says **who** does it: **You**, **Claude** (you just say "go"), or
**Waiting** (someone else has to act first).

---

## The big picture (read this when you feel lost)

**The goal: 2 Q1 journal papers over the 2 years of the MSc.**
- **Paper 1 (now):** are the coach's explanations **correct** (every claim
  true) and **relevant** (they name the reason that matters, not just any true
  fact)? How do we measure that?
- **Paper 2 (later):** do they fit **this player**, their level? That's the 3
  levels, guessing the level, the "Your patterns" panel, and a study with real
  players.

Why this order: background in `lab_notes.md` (25 Sep). It stays on your
laptop, because it comes from the private lab chat and this repo is public.

**Already done:**
- A working tutor app. Stockfish (the chess engine) decides; Gemini (the
  language AI) only explains.
- A checker that catches the AI saying things the engine didn't say.
- A first test: 25 positions, about 88% of explanations fully truthful.
- A "Your patterns" panel that spots a player's repeated mistakes.
- Notes on other people's papers (`related_work.md`).

**Still missing for paper 1:** a test on new positions, with comparisons
against simpler methods, graded by you and a second person; a way to judge
"relevant".

---

## 1. Now: the 4 steps, in this order

- [x] **Step 1. You: check round 2 on the board page.**
  *(Done 29 Sep, 14:05: 9 of 13 answers still have a problem (round 1: 10).
  The biggest group: it doesn't say why the better move is better. Table in
  `walkthrough_audit.md`.)*
- [x] **Step 1b. You decide: freeze the tutor as version 1 now?** Then Claude
  saves it (commits the walk-through) and we stop changing it while it's
  tested.
  *Why:* the test has to measure one fixed tutor.
  *(Done 29 Sep, 16:43: you said freeze now. Saved as commit `37aef2a`, on
  GitHub since 30 Sep, 01:41. The 9 problems left from round 2 are version
  1's known limits.)*
- [ ] **Step 2. You: talk to João.** Ask how his approach works and whether
  the two could be combined, and about Go. The questions (and why) are in
  `lab_notes.md`.
  *Why:* working together, and possibly combining the two approaches, is what
  Dr. Marcolino asked for (background in `lab_notes.md`).
- [ ] **Step 3. Claude builds, you grade: the first real experiment.** On new
  positions the coach has never seen, is each explanation correct and
  relevant? It's compared with Gemini without the engine's facts.
  *Why:* the 25 old cases were used to build the coach, so they can't prove
  it works. This is the first result for paper 1.
  *Plan (28 Sep, 16:40):* use the free test set from Hebbar et al. (2026):
  125 positions where experts wrote down the key points. Correct = the share
  of the coach's claims that are true. Relevant = the share of the expert's
  key points it covers. Their numbers for other AIs sit right next to ours.
  Details in `related_work.md`, section 1.
  *Network:* the office network blocks GitHub (tested 28 Sep, 16:40); your
  home wifi doesn't (tested 30 Sep, 01:10). So the set
  (https://github.com/hebbarashwin/act_eval) is downloaded at home or over
  the phone hotspot, when step 3 starts (after step 2).
- [ ] **Step 4. You: read two papers,** Hebbar et al. (2026) "Hallucinations
  on the Board" and Kim et al. (2025), the NAACL chess commentary paper
  (details in `related_work.md`, section 1).
  *Why:* they're the closest to paper 1; everyone will ask how yours differs.

## 2. Done recently, and waiting

- [x] Claude: save the panel (commit) and push. *(Done 26 Sep, 03:54.)*
- [x] You: say yes or no to the plan for clearer line walk-throughs.
  *(Approved 24 Sep, 14:27; built the same day, by 15:17.)*
- [x] You: check the 13 fresh coach answers on the board page.
  *(Done 25 Sep, 15:48: 10 of 13 answers have a problem; table in
  `walkthrough_audit.md`. Fixed 26 Sep, 11:47; see section 3.)*
- [x] Send João a message. *(Done 24 Sep, 14:29.)*
- [x] Claude: commit the walk-through. *(Done 29 Sep, 16:43: commit
  `37aef2a`, "Tutor version 1".)*
- [x] Claude: push version 1 and the notes to GitHub. *(Done 30 Sep, 01:41,
  from your home wifi. The live app now runs the version 1 coach. Held back:
  `CLAUDE.md`, which also describes the counting fix, so it goes up with
  that fix.)*
- [ ] **When João sends his reference list: paste it into a Claude session.**
  *Why:* Dr. Marcolino asked whether you have all the related work João
  found. Claude compares it with `related_work.md` and tells you what's
  missing.
- [ ] **You, optional, 5 min: look at the "Your patterns" panel** (paper 2).
  Run `streamlit run app.py` and paste `sim_games/game_01.pgn`,
  `game_02.pgn`… one after another (pick Player A's colour, listed in
  `sim_games/README.md`).
  *Why:* the counting fix (section 6) waits for this before it's committed.

## 3. Next (Claude does it, you just say "go")

- [x] Build the clearer walk-throughs and re-run the 25 test cases.
  *(Done 24 Sep, 15:17: checker 44/50 → 50/50. Your hand check is in section 1.)*
- [x] Board facts: count escaping an equal or bigger attacker when nothing
  defended the piece. *(Done 26 Sep, 00:43; in version 1. Before, only escaping a
  cheaper attacker counted, so e.g. an undefended knight fleeing a bishop got
  no reason. Changes 1 of the 25 test prompts: Caro-Kann 3.e5 now says it
  moves the e4 pawn away from the attack by ...d5.)*
- [x] Fix what your hand check found. *(Done 26 Sep, 11:47; in version 1: "opens a
  line" only when useful (your rule, opening vs later); new facts for a hanging
  piece, allowing mate, the centre, "prepares d4"; short damage control; wording
  rules incl. "an attack is only an attack"; checker reports misnamed pawns.)*
- [ ] **Talk through: how to say why the better move is better** (your point
  in answers 1 and 2 of the hand check). Part of step 3: it's what
  "relevant" means.
  *Why:* players need to know why ...a6 beats ...Nb4, not just that it does.
  It needs a new engine fact (comparing the two lines), and sometimes the only
  honest answer is "the engine rates it higher", so agree the approach first.
- [ ] **Bring the README up to date** (ready now: the panel and version 1
  are both on GitHub).
  *Why:* it's the project's front page on GitHub, the first thing Dr.
  Marcolino or a reviewer sees. It still describes the July app: no checker,
  no game review from a PGN, no learner model. Its description of the 3
  levels will be wrong once the new walk-through is kept.
- [x] Give the app's Gemini request a time limit.
  *(Done 24 Sep, 16:11: 20 s per try, 3 tries; tested. In version 1.)*
- [ ] **Paper 2, later: measure whether the 3 levels really differ** (beginner /
  intermediate / advanced), on version 1 of the coach.
  *Why:* the app *claims* it explains at 3 levels, but nobody has checked
  that "beginner" text is actually simpler. The thesis promises "at the
  player's level", so it must be measured. (You already noticed in July that
  advanced-level text uses heavy vocabulary; that's still open.)
- [ ] **Draft a one-page research plan** (after the call with João; Claude
  drafts, you rewrite it in your words).
  *Why:* Dr. Marcolino hasn't agreed to a written plan yet. It also gives
  you a 2-minute answer to "what's your project?"

## 4. Reading (when you have time, in this order)

After each one, write 3–5 lines in `related_work.md`: what they did, what
they found, how you differ. Ask Claude to explain anything unclear.

Hebbar et al. (2026) and Kim et al. (2025) moved up to step 4.

- [ ] **Jacovi & Goldberg (2020), "faithfulness vs. plausibility".**
  *Why:* it names your thesis's core idea. An explanation can *look* right
  (plausible) without *being* right (faithful).
- [ ] **Sadikov et al. (2007), "Automated Chess Tutor".**
  *Why:* the old, pre-AI version of your idea. You must cite it.
- [ ] **Lima (2024), Aveiro chess tutor thesis: just the summary.**
  *Why:* it might overlap with your project. Check early.

Later, for the related-work chapter (check each before citing):
- McGrath et al. (2022), *Acquisition of chess knowledge in AlphaZero*
  (PNAS): what a chess AI "knows" inside.
- Bull & Kay: *open learner models* (a learner model the student can see,
  like "Your patterns"; the project brief asks for them).
- Dr. Marcolino's own papers: on-line estimators of teammates' types
  (JAAMAS 2022), *It Is Among Us* (AAMAS 2024), *Every Team Deserves a
  Second Chance*. *Why:* working out a hidden "type" from actions is his
  field, and our learner model is the chess version.
- KaTrain: a Go trainer much like ours (named in the lab chat).

## 5. Ask Dr. Marcolino (next time you talk)

- [ ] **A second person to grade some coach answers** (someone in the lab,
  the VinUni chess club, or paid graders). They don't need to be strong
  players: they check the text against the engine's facts, not the chess.
  *Why:* journal reviewers don't fully trust results graded only by the
  author.
- [ ] **Can the chess study go under his ethics application?** (Background
  in `lab_notes.md`.)
  *Why:* a study with real people needs ethics approval, which takes months.
- [ ] **Are our planned comparisons enough?** (The list is in
  `related_work.md`, section 3.)
  *Why:* reviewers look hard at comparisons (background in `lab_notes.md`).
- [ ] **Guessing the player's level:** does he want his "update after every
  move" idea done in chess? Does it overlap with João?
  *Why:* it's the "adapt to the learner" half of the thesis.
- [ ] **Tell him your plan** (2 Q1 papers over 2 years: paper 1 = correct and
  relevant, paper 2 = fits the player; after-game review) and ask which
  journals he'd aim for.
- [ ] **Ask for João's AIIDE 2026 paper** (guessing Go ranks).
  *Why:* the closest work on level guessing; shows which comparisons his
  group uses.
- [ ] **How would he position us against "Hallucinations on the Board"?**
  (Our answer: a tutor, with levels and a learner model, not commentary.)
- [ ] **Explain an easier near-best move?** An idea from his Go group: explain
  the 2nd- or 3rd-best move when it's easier to understand. Worth a small
  experiment?
- [ ] **Can Haoran share his explanation work?**

## 6. Later: the big pieces of the thesis

- [ ] **Comparison: the coach *without* the engine's facts.** Starts in step 3.
  *Why:* proves that giving the AI engine facts is what makes it truthful.
  Reviewers expect this.
- [ ] **Bigger test: 100+ positions from real games** (not 25 hand-picked),
  reported with a confidence range, as Dr. Marcolino's ReCePS paper does.
  Starts in step 3.
  *Why:* with 25 cases, "88%" could really be anywhere from 70% to 96%.
- [x] **You: decide about test case 8** ("Closed centre, Black to plan").
  *(Found 30 Sep, 01:18. You said fix it; fixed 30 Sep, 02:06.)* Its
  position had no Black bishop on c8, so Black was a bishop down (−4.79,
  and the coach told Black "heavily in your favor"). Now the bishop is back:
  about equal (+0.26), and the engine's plan is ...b6 and ...Bb7. The same
  mistyped position in the two self-tests is fixed too. The frozen July
  audit and all old runs stay as they were; they measured the old position.
- [ ] **You: decide what to do about the checker's two blind spots.** It
  misses reasons without a trigger word ("…, as your pieces are
  developing") and wrongly fails a true "your extra rook" (it can't see the
  board). Fix them, or keep them as stated limits plus a human spot-check.
  *Why:* the coach may have learned softer words the checker can't catch.
- [ ] **Your grading, done more carefully** (worth doing even if a second
  person is found): grade without knowing which version wrote each answer,
  re-grade some weeks later, and add a second AI as a machine judge next to
  the checker.
  *Why:* makes the grading trustworthy while you're the only human judge.
- [x] You decide, Claude builds: stop the panel counting one problem
  several times. *(Done 26 Sep, 04:01: you chose "a run of back-to-back slips
  counts once". Slips now vary like coin flips (spread 1.5 → 1.0 over 40
  simulated games), so the panel's "80% sure" holds again. Not committed yet.
  Details: diary, 26 Sep, 04:01.)*
- [ ] **Claude: save the counting fix (commit), with `CLAUDE.md`**, once
  you've seen the panel's new small print in the app.
  *Why:* it's finished and tested, but only on this laptop until committed.
  `CLAUDE.md` waits with it because it describes the fix.
- [ ] **Claude: set the learner model's bars from real Lichess games**, and
  check that weaker players hang more pieces. Needs the Lichess download, so
  off the office network.
  *Why:* the bars are hand-set guesses now, and one is already known to be
  too lenient.
- [ ] **Guess the player's level from their moves** (with the Maia engine).
  Needs Lichess games and Maia downloads, so it has to be done off the office
  network.
  *Why:* then the tutor can pick the right explanation level by itself.
- [ ] **You (optional): ask IT to let github.com and lichess.org through the
  firewall.**
  *Why:* the two items above need Lichess and Maia, and pushing wouldn't
  need the hotspot any more.
- [ ] **A small study with real players** (after ethics approval).
  *Why:* the project's goal is helping people learn. Only real people can
  show that.
- [ ] **Write the papers** (goal: 2 Q1 journal papers over the 2 years of the
  MSc; paper 1 first).
