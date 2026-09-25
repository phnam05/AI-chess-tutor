# To-do list

*Last updated: 26 September 2026.* Tick a box (`[x]`) when a task is done.
Each task says **who** does it: **You**, **Claude** (you just say "go"), or
**Waiting** (someone else has to act first).

---

## The big picture (read this when you feel lost)

**Your thesis asks one question:** can an AI tutor explain chess to a player
(1) *truthfully*, saying only what the engine found, and (2) *at that
player's level*? And can we *measure* both?

**Already done:**
- A working tutor app. Stockfish (the chess engine) decides; Gemini (the
  language AI) only explains.
- A checker that catches the AI saying things the engine didn't say.
- A first test: 25 positions, about 88% of explanations fully truthful.
- A "Your patterns" panel that spots a player's repeated mistakes.
- Notes on other people's papers (`related_work.md`).

**Still missing:** proof that the 3 levels really differ; comparisons
against simpler methods; a bigger test; guessing a player's level
automatically; a study with real players; the writing.

**Rough timeline** (my guess, not yet agreed with Dr. Marcolino):
Oct–Nov 2026 the measurements · Dec–Feb level guessing · Mar–May study with
real players · Jun–Jul 2027 write and submit the journal paper.

---

## 1. Now (this week)

- [ ] **You, 5 min: look at the "Your patterns" panel.** Run
  `streamlit run app.py`, paste a game, check the panel, and tell Claude
  "it's fine" or what's wrong. No time to play? 10 simulated games are ready
  in `sim_games/`: paste `game_01.pgn`, `game_02.pgn`… one after another
  (pick Player A's colour, listed in `sim_games/README.md`) and watch the
  panel fill up.
  *Why:* it's finished work that isn't saved yet. Also, you should know what
  your own app shows before others see it.
- [x] Claude: save it (commit) and push. *(Done 26 Sep at your request,
  before your check: anything you want changed becomes a new commit.)*
- [ ] **Claude: commit the walk-through** (`board_facts.py`, `explainer.py`,
  `move_review.py`, `engine_analysis.py`, `faithfulness.py`,
  `walkthrough_eval/`, `walkthrough_audit.md`) once the board-fact fixes from
  your hand check are finished, then push (phone hotspot if the office
  network blocks GitHub).
  *Why:* held back on 26 Sep because another session was editing
  `board_facts.py` right then; committing it would have saved half-finished
  work.
- [x] You: say yes or no to the plan for clearer line walk-throughs.
  *(Approved 24 Sep; built the same day.)*
- [x] You: check the 13 fresh coach answers on the board page.
  https://claude.ai/artifact/RXVx2NjAcuirnqbXqKoqL4
  *(Done 25 Sep: 10 of 13 answers have a problem; table in
  `walkthrough_audit.md`.)*

## 2. Waiting for João

- [x] Send João a message. *(Done 24 Sep.)*
- [ ] **When he replies: paste his reference list into a Claude session.**
  *Why:* Dr. Marcolino asked whether you have all the related work João
  found. This is how you get it. Claude compares it with `related_work.md`
  and tells you what's missing.
- [ ] **Have a call with João (next week).**
  *Why:* to learn what he's working on so you don't do the same thing twice,
  and to see if you can help each other. The questions (and why) are in
  `lab_notes.md`, which stays on your laptop: they come from the private lab
  chat, and this repo is public.

## 3. Next (Claude does it, you just say "go")

- [x] Build the clearer walk-throughs and re-run the 25 test cases.
  *(Done 24 Sep: checker 44/50 → 50/50. Your hand check is in section 1.)*
- [x] Board facts: count escaping an equal or bigger attacker when nothing
  defended the piece. *(Done 26 Sep, not committed. Before, only escaping a
  cheaper attacker counted, so e.g. an undefended knight fleeing a bishop got
  no reason. Changes 1 of the 25 test prompts: Caro-Kann 3.e5 now says it
  moves the e4 pawn away from the attack by ...d5.)*
- [ ] **Fix "an attack is only an attack"** (after your hand check).
  *Why:* Gemini turns "attacks the bishop" into "forces the bishop away",
  which the board facts don't say.
- [ ] **Bring the README up to date** (after the panel and the walk-through
  are committed).
  *Why:* it's the project's front page on GitHub, the first thing Dr.
  Marcolino or a reviewer sees. It still describes the July app: no checker,
  no game review from a PGN, no learner model. Its description of the 3
  levels will be wrong once the new walk-through is kept.
- [x] Give the app's Gemini request a time limit.
  *(Done 24 Sep: 20 s per try, 3 tries; tested. Not committed yet.)*
- [ ] **Measure whether the 3 levels really differ** (beginner /
  intermediate / advanced). Do this *after* the walk-through change, so we
  measure the coach you'll actually keep.
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

- [ ] **Jacovi & Goldberg (2020), "faithfulness vs. plausibility".**
  *Why:* it names your thesis's core idea. An explanation can *look* right
  (plausible) without *being* right (faithful).
- [ ] **Hebbar et al. (2026), "Hallucinations on the Board".**
  *Why:* the paper closest to yours. Everyone will ask how you differ.
- [ ] **Sadikov et al. (2007), "Automated Chess Tutor".**
  *Why:* the old, pre-AI version of your idea. You must cite it.
- [ ] **Lima (2024), Aveiro chess tutor thesis: just the summary.**
  *Why:* it might overlap with your project. Check early.
- [ ] **Kim et al. (2025), NAACL chess commentary.**
  *Why:* it uses the same "engine decides, AI explains" design, so that
  design alone isn't your new contribution.

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
- [ ] **Tell him your decisions** (both parts, a Q1 journal paper in about
  a year, after-game review) and ask which journal he'd aim for.
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

- [ ] **Comparison: the coach *without* the engine's facts.**
  *Why:* proves that giving the AI engine facts is what makes it truthful.
  Reviewers expect this.
- [ ] **Bigger test: 100+ positions from real games** (not 25 hand-picked),
  reported with a confidence range, as Dr. Marcolino's ReCePS paper does.
  *Why:* with 25 cases, "88%" could really be anywhere from 70% to 96%.
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
- [ ] **You decide, Claude builds: stop the panel counting one problem
  several times.** Right now, if a piece stays hanging for 3 moves, that's 3
  slips. Options: count a run of back-to-back slips once, or judge
  per game instead of per move.
  *Why:* in the simulated games (`sim_games/`), two copies of the *same* bot
  got opposite verdicts after 10 games ("fine" vs "pattern" for leaving
  material), mostly because one bot's slips came in runs. Do this before
  setting the bars, since it changes the counts they're set on.
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
- [ ] **Write the paper** (goal: a Q1 journal, submitted around mid-2027).
