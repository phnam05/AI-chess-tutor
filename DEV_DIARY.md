# Development Diary — AI Chess Tutor

MSc project, **VinUniversity** · supervisor **Dr. Leandro Marcolino** · author: phnam05

The project's story, a few lines per working day. **What to do next is in
`TODO.md`**, not here. The same story with every detail is in the long
version, `DEV_DIARY_full.md` (on your laptop only, not on GitHub). Both are
updated every session: read this one, and open the long one when you want to
go deeper into a day. Feeling lost? `PROJECT_STORY.md` (also laptop only)
tells the whole project as one story, up to 29 Sep.
Words in *italics* are in the Glossary at the bottom.

---

## Where the project stands (30 Sep 2026, 01:41)

**The idea:** the *engine* (Stockfish) decides the chess; a language AI
(Gemini), called **the coach** here, only puts the engine's facts into words,
at the player's level.

**The goal (28 Sep): 2 *Q1 journal* papers over the 2 years of the MSc.**
- **Paper 1 (now):** are the coach's explanations **correct** (every claim
  true) and **relevant** (they name the reason that matters)? How do we
  measure that?
- **Paper 2 (later):** do they fit **this player**? That's the 3 levels,
  guessing the level, the learner model, and a study with real players.
- Why this order: `lab_notes.md`, 25 Sep. The study uses after-game review
  (pasting a finished game), not help during live play (23 Sep).

**Now: 4 steps** (in `TODO.md`): ~~your round-2 check, then the tutor is
frozen as *version 1*~~ (done 29 Sep, 16:43) · **next: talk to João** · the
first real experiment (on Hebbar et al.'s free test set) · read Hebbar 2026
and Kim 2025.

| Step | What | Status |
|---|---|---|
| 1 | Checker: compares the coach's text with the engine's facts | ✅ Done |
| 2 | Test: 25 cases, your hand audit, a measured faithful rate | ✅ Done |
| 3a | Name the *kind* of each bad move | ✅ Done |
| 3b | Learner model: how often *this* player makes each kind | ✅ Built · a repeated slip counts once (26 Sep) |
| 3c | Show it in the app · give it to the coach | ✅ In the app (on GitHub, 26 Sep) · coach later |
| 3d | Test it on *bots* with a planted weakness | ✅ First run |
| — | Walk through engine lines your way (your rules, 24 Sep) | ✅ Frozen as *version 1* (29 Sep, 16:43; on GitHub and in the live app since 30 Sep, 01:41) · your hand check: 10 of 13 answers had a problem (25 Sep) → 9 of 13 after the fixes (round 2, 29 Sep); mostly it doesn't say *why* the better move is better |

**Numbers you can quote**
- Your hand audit of 25 coach answers (3 Jul, before the coach fix), asking "did the coach stick to the engine's facts?": 11 Yes · 5 Mostly yes · 7 Partially · 2 No.
- Checker vs. your audit: of the 10 answers you marked as inventing a reason for the eval, it found **all 10**, and it wrongly failed **0** good answers.
- *Planted-lie test*: **25/25** fake moves and **25/25** fake reasons caught.
- *Faithful rate*: 19/25 (76%) → **22/25 (≈88%)** after the fixes to the coach's instructions on 3 and 17 Jul (22/25 in every July re-run; 21 and 23 when re-run on 24 Sep). Invented moves: **0**.
- Asking for plainer words made it worse (16/25 vs. 22/25), so it was removed.
- Learner model, the same bot against itself for 40 games: its slips were 1.5 times as spread out as coin flips while repeats were counted; **1.0** now (26 Sep).

**What the thesis still needs** (the 23 Sep verdict plus the plan; most important first. Paper 1 needs 1, 2 and 6, plus a way to judge "relevant"; 3, 4, 5 and 7 are paper 2)
1. **More test cases.** With 25, "88%" really means somewhere in 70–96% (the *confidence range*), so the fix isn't proven yet. ~100 positions from real games narrows it to ~80–93%. Report it with a confidence range, as Dr. Marcolino's ReCePS paper does.
2. **A check on the grading.** You are the only judge and also the author. Plan: grade *blind* (not knowing which version wrote each answer), re-grade some weeks later, and ask Dr. Marcolino for a second person.
3. **Proof that the 3 levels really differ.** Nothing yet shows "beginner" text is simpler, and advanced-level text still uses heavy vocabulary.
4. **Guessing the player's level automatically** from their moves, so the tutor picks the level itself (Dr. Marcolino's *Bayes' rule* idea, using *Maia*). This is the core of the "adapt to the learner" half.
5. **Proof that it helps people learn:** a study with real players. It needs ethics approval, which takes months, so start early.
6. **Comparisons (*baselines*)**, e.g. the coach without the engine's facts. Reviewers expect them.
7. **The learner model on real human games** (*Lichess* is blocked by the office *firewall*). Its bars are still hand-set guesses, and it isn't given to the coach yet.
8. **A related-work chapter** (started in `related_work.md`).

**Git:** version 1 (`37aef2a`) and these notes are on GitHub (30 Sep,
01:41), and the live app runs the version 1 coach. Only on this laptop: the
counting fix (waits for your look at the panel) and `CLAUDE.md`, which
describes that fix, so it goes up with it.
The office firewall usually blocks GitHub (and Lichess, Maia); your home
wifi and the phone hotspot work. The repo is public, so private lab notes live in
`lab_notes.md`, which git ignores.

---

## Part 1 — The first version (June 2026)

### 17 Jun — Day one
- **Did:** built the whole chain from position to explanation. `engine_analysis.py` asks Stockfish for the best move, *eval* and *line*; `move_review.py` grades a move you played; `explainer.py` has Gemini explain at 3 levels, with strict "don't invent" rules; `app.py` is the web page. Put it online on *Streamlit Cloud*.
- **Problems → fixes:** Stockfish didn't run on the cloud (it runs Linux, not Windows) → `packages.txt` installs the Linux version there. The *API key* had to stay secret → read from secret settings, never written in the code.

### 19 Jun — A real tutor
- **Did:** fairer *grades* by *win chance* lost instead of *centipawns* lost; side-by-side boards; a clickable board to play a game; the coach now says *why* a move was wrong, using the engine's *refutation*.
- **Problems → fixes:** pieces invisible on the cloud (its font has no chess symbols) → installed FreeSerif. Clicks replayed the previous move → remember which click was already handled. Grading took 2.4 s → one shared engine instead of a new one per request: **0.1 s**.

## Part 2 — Was the first version good?

A sound idea and a working product, but **not research yet**. The promise "the
AI never makes up chess" was never checked, nothing was measured, and it didn't
adapt to one player. Hidden bugs turned up later: the engine could give
different best moves for the same position, lines could stop in the middle of a
*trade*, and a checkmate could be graded "Blunder".

## Part 3 — Upgrading it, step by step

### 27 Jun — From demo to research
- **Did:** studied Dr. Marcolino's project description (Project #40: virtual tutors that explain an AI's decisions, adapt to the player's level and find errors) and his own research (working out a player's or program's hidden *type* from how it acts). Agreed a 3-step plan: (1) a faithfulness checker, (2) a small test, (3) a *learner model*.
- **Problem → fix:** you got lost in jargon → new rule: plain words, every term explained, short answers.

### 30 Jun — Step 1: the checker
- **Did:** `faithfulness.py` finds every move in the coach's text and flags any move the engine didn't give (how it works: see Reference). Planted fake moves: 6/6 caught.
- **Problem → fix:** the checker seemed not to run in the app → an old copy of the app was still running old code; restarted it.

### 1 Jul — A repeatable engine; "is the checker blind?"
- **Did:** made the engine *repeatable* (same position → same answer). There were three causes of randomness, all fixed: a time limit (it searched deeper when the laptop was less busy), several parts of the engine searching at once and racing each other, and memory left over from earlier positions. Built the 25-case test (`evaluate_faithfulness.py`: 14 positions and 11 played moves, from openings to endgames): 25/25 clean.
- **Problems → fixes:** a perfect score looked suspicious (your point: the checker might be blind) → you hand-audited all 25. I called Step 2 "done" before your audit was finished → new rule: a step is done only when you've reviewed it.

### 3 Jul — Your audit changes everything
- **Did:** your audit found what the checker had missed. Main problem: the coach **invents reasons for the eval** (you marked 10 of 25 answers), e.g. "explaining" −4.79 by "open files", a reason the engine never gave. Also: move purposes that didn't match the engine's line, and 2 plain factual errors.
- **Decided together:** fix the checker first, then the coach, then re-measure. Fixing the coach with a checker that can't see the problem would prove nothing.
- **Then:** the checker now flags a sentence that has the score and a reason ("because", "due to"…) but no engine move. It matches your audit (10/10), and the honest starting rate is **19/25**. The coach fix, "ground it or drop it": give a reason for the eval only if the facts show one (material won in the line, or mate). Also added full-game review from a pasted *PGN*.
- **Problems → fixes:** a line cut one move before a *recapture* looked like a *hung* queen → lines are never cut mid-trade. Each test run overwrote the results you audited → saved a frozen copy.

### 17 Jul — Two experiments, and the honest number
- **Did:** you checked the last 4 flags yourself; 3 of them were only wording, not lies. You also named two quality problems: later moves mentioned out of order or on the wrong side (fixed and kept) and heavy vocabulary at advanced level (**still open**). Tried "keep language plain at every level": 16/25 vs. 22/25 without it, so **removed**. Why it backfired: plain explanations push the AI to say "because…", exactly what the rules forbid. Found by switching the change off and re-measuring (an *ablation*).
- **Problems → fixes:** 24/25 turned out to be luck; re-runs gave 22/25 → reported **≈88%**. The flags I showed you didn't match your audit sheet: they came from a newer run, and Gemini words things differently every run → always say which run a number comes from.
- **End state:** Steps 1–2 closed and pushed.

### 23 Sep, 10:06 — Accepted into the MSc; Step 3 begins
- **News:** accepted at VinUniversity with Dr. Marcolino; he agreed to chess instead of Go.
- **Did:** re-checked the checker from scratch (planted lies caught 25/25 and 25/25; the same text always gets the same verdict). Fixed a checkmate graded "Blunder". Built the mistake detector (Step 3a): each bad move gets one of 5 *kinds*, read from the engine's lines and a *material* count, no AI guessing. Limit: it sees only about 6 moves ahead.
- **The coach failed during your demo to Dr. Marcolino.** The cause was temporary (the free plan's limit of 15 requests a minute, or Gemini briefly busy), but the app made it permanent. Now it tries up to 3 times, names the real cause instead of always "check GOOGLE_API_KEY", and shows a "Try again" button. A missing key stops only the coach, not the whole app. The add-on libraries are locked to tested versions (the cloud used to install the newest, untested ones).
- **Problems → fixes:** the checker errs both ways. It misses "…, as your pieces are developing" (no trigger word) and wrongly flags a true "your extra rook" (it can't see the board) → by hand the rate is still ≈88%, ± a case or two. Lesson: the coach may have learned to avoid "because" and use softer words the checker doesn't catch, so a human spot-check is needed now and then. What to do about these two blind spots is **still your decision**. `git push` failed: the office firewall intercepts GitHub's secure connection → push from another network. Don't switch off git's security check to get around it: anyone on the network could then pretend to be GitHub.

### 23 Sep, 11:07 — Honest verdict; the learner model
- **Did:** wrote the verdict above. Built the learner model (Step 3b). For each mistake kind it counts *chances* and *misses*. Every player starts from a guess that sits exactly on the bar and weighs as much as 10 moves of evidence, so one slip can't label anyone. A kind becomes a **pattern** only when we're 80% sure the player's rate is above a bar (e.g. "hangs material on more than 1 move in 10") and it has happened at least 3 times. The maths was checked against 200,000 random samples.
- **Limit:** the bars are my guesses, set by hand, and one is already known to be too lenient ("misses more than half its chances", when the engine misses none).
- **Test (Step 3d):** 4 kinds of bots that play like Stockfish except for one planted weakness: **hangs** (leaves pieces to be taken), **misses** (skips free material), **drifts** (makes random quiet moves), **solid** (no weakness: the control, i.e. the comparison group). 5 bots of each kind, 40 moves each against Stockfish.
- **Result:** "hangs" found **5/5** (after about 9 moves); the solid bots were never flagged; "misses" and "drifts" **not found**. Why: a bot's planned mistake often wasn't what the engine judged its move to be; one habit got split across two kinds; and chances to win material are rare (~7 in 40 moves). The one extra flag was a drifter that really lost material on 8 of 40 moves: a real weakness, not a false alarm. Re-runs give identical games, so the test is repeatable.
- **Decision:** don't tune the rules until my own bots pass (that would be marking my own exam). Set the bars from real Lichess games instead, and check there that weaker players hang more pieces.

### 23 Sep, 11:27 — Reading the lab's chat
- **Did:** read the lab's Discord chat (Aug 2025 – Aug 2026) as background only. What we learned about the lab's people and plans is in `lab_notes.md` (kept off GitHub: the repo is public). Turned it into questions for Dr. Marcolino (in `TODO.md`); the papers named in the chat are in `related_work.md` and `TODO.md`.
- **Problem → fix:** the chat file holds personal data → told git never to save it (`.gitignore`).

### 23 Sep, 13:57 — "Your patterns" in the app
- **Did:** the app shows the learner model ("Your patterns"): each mistake kind as Pattern / Not sure yet / Fine, with the moves as evidence. Only your moves count: pasted games get a "You played: White / Black / Both" choice. The notes build up across games until the page is reloaded. You decided the direction (above). Started `related_work.md`.
- **Found:** a very close new paper, "Hallucinations on the Board" (Aug 2026; a "hallucination" is an AI making things up), and a paper at NAACL 2025 (a big AI conference) already using the "engine decides, AI phrases" design → that design alone isn't our contribution; the *tutor* is (levels, learner model, level guessing, all measured). A comparison against the coach without engine facts is now expected of us.
- **End state:** panel built and tested (9/9 checks passed: grading as Black, re-grading as White, a second game, New game, Undo…), not committed; you'll check it first.

### 24 Sep, 11:22 — Getting ready to talk to João
- **Did:** Dr. Marcolino suggested you talk to João. Re-read the chat for João's work, named the ~20 untitled paper links (now in `related_work.md`), and prepared questions for him (in `lab_notes.md`). Message sent; he's busy until his 25 Sep deadline.
- **Learned:** two chess papers on guessing a player's level (one from ICLR 2025, a big AI conference; "Predicting Chess Player Rating Based on a Single Game", 2023), now proposed comparisons. The rest (who works on what, Dr. Marcolino's remarks, ethics) is in `lab_notes.md`, kept off GitHub.

### 24 Sep, 14:14 — Pushed; the online coach lost its key
- **Did:** pushed the 7 waiting commits over your phone hotspot (it works; the office network still doesn't). That also updated the online app with the coach's retries and plain error messages.
- **Problem → fix:** the online coach then said "no API key". I changed the code twice and pushed both, before you tried the simple fix: re-paste the secret and reboot the app. That fixed it. Kept: the key is now looked up on first use, not at start-up (so a newly added key works without a reboot), and a log line names the secrets it found (never their values). Undone: looking under other key names (4b46dbb). Lesson: let you try the simple fix first.
- **End state:** 1 commit (4b46dbb) waits to be pushed.

### 24 Sep, 14:22 — Your rules for walking through a line
- **Your complaint:** after your ...Nb4 (a Mistake), the coach said "O-O… followed by a6". It's unclear who plays a6, and there's no reason anyone would find it.
- **Checked:** our engine agrees ...Nb4 is a Mistake (from Black's side the eval went −0.44 → −1.46: from slightly worse to clearly worse), but its line is O-O then **...c6**, not ...a6 (the online app probably runs a different Stockfish version). Both attack White's bishop on b5, so your point holds.
- **Your rules** (also in `CLAUDE.md`): say who plays every move; say what the bad move changed; give the idea before each recommended move; only 1–2 moves deep; adapt to the level.
- **Claude's pushback:** the engine gives no reasons, so reasons must be computed by code, not invented by Gemini. Example: after ...Nb4 the knight no longer defends e5, but taking it is bad for White (4.Nxe5? Qg5), so "you lose e5" would be a wrong reason. Also: the move you *should have played instead* (...a6) is kept apart from your *best reply now* (...c6).

### 24 Sep, 15:17 — The new walk-through, built and measured
- **Did:** the new `board_facts.py` works out what a player would notice about each move (captures, checks, attacks, "a pawn can chase it"…). Every move is labelled in code with who plays it. How deep to go is set by level (2 / 3 / 4 *half-moves*), and the line stops before any of your moves that has no fact to explain it. New coach instructions around your rules. The checker changed too: it now also accepts squares and moves named in the board facts, but judges reasons for the eval exactly as strictly as before (still 10/10 against your audit).
- **Result:** the 25 cases, run twice (50 answers): the checker passed 44/50 before → **50/50** after; "followed by" 11 → 0. But the same 25 cases were used to build it, the checker itself changed (so this isn't directly comparable with July's numbers), and it can't see an invented *idea*. Reading by hand still finds: "attacks" stretched into "forces"; "the c3 or a3 pawn" once; a board fact linked to the verdict ("…can be chased, so your move was a mistake"); notation in square brackets.
- **Problems → fixes:** Gemini got the eval backwards (told Black "−1.46 favors you") → the code now spells out who is ahead. A test run froze for minutes on one Gemini request → measurements use a 60-second limit; the app got its own limit later that day (below).
- **End state:** not committed. Next: your hand check in `walkthrough_audit.md`, then the rule "an attack is only an attack".

### 24 Sep, 15:22 — A shorter diary
- **Did:** the diary had grown to 1,050 lines and was a hassle to read. Rewrote it as this short version; the full text is frozen in `DEV_DIARY_full.md`. To-dos now live only in `TODO.md`. Two checks (mine, then a fresh reviewer's) put back what the first cut lost: the level-guessing step, key findings and limits, open decisions, and explanations for ~25 words.

### 24 Sep, 16:11 — A time limit for the coach
- **Did:** the app's Gemini request now gives up after 20 seconds per try (3 tries, so about a minute at worst; a normal answer takes ~3 s). Before, one stuck connection could leave the coach waiting forever. When time runs out, the app says so in plain words ("Gemini didn't answer in time…") and keeps its "Try again" button.
- **Tested:** a forced time-out gave up after 3 tries with that message; a normal call still answered in 3.2 s.
- **End state:** not committed (with the rest of today's work).

### 24 Sep, 16:48 — Are the notes up to date?
- **Did:** checked every `.md` file against the code. Fixed: `CLAUDE.md` and `README.md` still said the engine stops after 1 second (removed on 1 Jul, because a time limit made it unrepeatable); the README said Python 3.9+ (the locked libraries need 3.10+) and had a placeholder GitHub address; this diary had no entry for the push and the key problem (added above, "24 Sep, 14:14").
- **Left for later:** the README (the project's GitHub front page) still describes the July app: no checker, no game review from a PGN, no learner model. Its 3-level description will be wrong once the new walk-through is kept → update it after the panel and walk-through are committed (in `TODO.md`).

### 25 Sep, 14:25 — A hand check you can actually do
- **Did:** turned your hand check into a web page (link in `walkthrough_audit.md` and `TODO.md`). It shows 13 coach answers, freshly generated with the same code, each in full. Every case has a board you can step through move by move, whose caption always says who just moved and who is to move; the engine's facts, with move numbers; and one question per answer: "Any problem?". Your answers save on the page and Claude reads them from there.
- **Problems → fixes:** the 265-line sheet was too long → 9 yes/no questions. Text alone wasn't enough → boards. My first boards showed positions several moves deep, with arrows for both sides mixed together, which made it hard to tell who played what → redone in the format of your "Chess Coach Correctness" page (board before the move, red = played, green = engine's best). Only excerpts of the answers → full answers.
- **Result:** the checker passes the fresh run 25/25 again. Reading it by hand found one new problem: in the ...Nxe4 case the coach stops at 7...bxc6, just before 9.Kxf2 wins the knight, so ...Nxf2 sounds like a good move. That comes from our code's level cut, not from Gemini. Still there: "the c3 or a3 pawn", the missing reason for ...Ng4 (it attacks the bishop on e3; our board facts don't see that), and "−100.00" shown to a beginner instead of "checkmate".
- **Your verdict:** 10 of 13 answers have a problem (fine: 1.h4, Ruy Lopez, QGD). In short: our code's facts are too thin or misleading (Be3 "opens a line for the queen" only frees back-rank squares; no fact for a piece left to be taken for free, for the attack on f7, or for claiming the centre); after a lost piece the coach should stop instead of walking on; it never says *why* the better move is better; wording (guessing what you "want", "the c3 pawn", copying "worth less"). Full table in `walkthrough_audit.md`.
- **End state:** nothing committed. Next: agree which fixes to do first.

### 26 Sep, 00:44 — Why board facts exist; one gap closed
- **Your question:** where do the board facts come from, and why have them? → They're plain code (`board_facts.py`), not AI: a fixed list of yes/no checks on the board, each "yes" filling in a ready-made sentence, handed to Gemini as English. They exist because your rules ask for the *idea* behind each move ("on b4 it can be chased by c3 or a3"), and Stockfish gives no ideas. So the engine says what's good, the code says what's visible on the board, and Gemini only words it.
- **Found while explaining:** "moves away from the attack" only counted attackers worth *less*. An undefended knight fleeing a bishop got no reason → now any attacker counts when nothing defended the piece (a defended piece attacked by an equal one is just an even trade, so still nothing).
- **Result:** self-test passes (undefended knight → fact; defended → none; the ...Nb4 example unchanged). Of the 25 test cases, 1 prompt changes: Caro-Kann 3.e5 now "moves the pawn away from the attack by Black's pawn on d5" (true, and the real reason for e5). Side effect: pawns can now get this fact too. Not re-run through Gemini.
- **End state:** not committed.

### 26 Sep, 00:52 — Simulated games for the patterns panel
- **Your ask:** no time to play 10 games, so simulate games between 1000-rated players. → New `simulate_games.py`: Stockfish plays both sides at its weakest setting, and every move is graded exactly as the app grades a pasted game. 10 games in under a minute, saved in `sim_games/` (one PGN per game, ready to paste, plus a report).
- **Limit:** Stockfish can't go below "1320", and that's an engine rating, not a human one. Its mistakes are random, not human (it once took a rook and promoted to a knight instead of a queen). Good for seeing the panel work; not evidence about real players, so not for setting the bars.
- **Found:** players A and B are the *same* bot, yet after 10 games the panel calls "leaving material to be taken" *fine* for A (15 in 286 moves) and a *pattern* for B (40 in 287). B's slips come in runs: in game 10 one attacked knight on f3 was counted on 3 moves (20, 21, 23), because each move that didn't save it counts again. So the panel treats one problem as several pieces of evidence and gets sure too fast. This matters for real 1000-rated games too, where hung pieces often stay on the board for a few moves.
- **End state:** not committed. The fix is your call (in `TODO.md`).

### 26 Sep, 03:53 — Saved to GitHub; private notes kept local
- **Did:** committed and pushed the finished work: the "Your patterns" panel, the simulated games, and the notes (this diary, the to-do list, related work, README fixes).
- **Found → fix:** the GitHub repo is public, and the diary and to-do list quoted the private lab chat (remarks about people in the lab and their unpublished work). → Moved those lines into `lab_notes.md`, which git ignores, as it now does `DEV_DIARY_full.md`; the diary and to-do list point there. None of it reached GitHub.
- **Held back:** the walk-through code (`board_facts.py`, the coach's instructions, their test files). Another Claude session was changing `board_facts.py` at that very moment (the fixes from your hand check), so committing it would have saved half-finished work.
- **End state:** pushed; the walk-through is committed once those fixes are done.

### 26 Sep, 03:59 — Both diaries kept up to date
- **Your decision:** keep both diaries and update both every session: this short one to read, `DEV_DIARY_full.md` to go deeper (same story, every detail; laptop only).
- **Did:** the long one got the entries it was missing (24 Sep, 14:14, and 24 Sep, 15:22 → today), a refreshed "Where the project stands", and the new files and words in its reference parts. Its old to-do list now points to `TODO.md` (every item is there or in its entries). The rule is changed in `CLAUDE.md`.

### 26 Sep, 04:01 — A repeated slip counts once
- **Your decision:** fix the counting found in the simulated games (my advice: count a run of back-to-back slips once; judging per game would need many games).
- **Did:** in `learner_model.py`, the same kind of slip on the player's own next move (same colour, same game) now counts once, as one problem. In a live game you move both sides, so "your next move" means the next move of the same colour. The panel's small print says so. Self-test: 12/12 checks pass (5 new).
- **Test:** 40 new games of the same bot against itself (`sim_games/batch_40/`). *Spread* of "leaving material" slips: 1.5 → **1.0** (1.0 = like coin flips, which is what the panel's "80% sure" assumes); positional slips 1.3 → 0.7. So the panel is no longer surer than its evidence.
- **Verdicts:** fewer slips are counted now (copy A, leaving material: 112 → 90 slips in the same 994 moves), so verdicts moved. In the 40 games both copies agreed before too, as "pattern" for both kinds, with rates just above the bars. Now "leaving material" is *not sure yet* for both (9–10% of moves, right at its bar of 10%) and positional is *fine* for both (17–18%, bar 20%). The bars are still guesses, so this is a changed count, not proof the old verdicts were wrong. On the first 10 games, the opposite verdicts (fine vs pattern) became fine vs not sure yet.
- **Still true:** early verdicts can mislead. After 10 of the 40 games, copy B showed a positional "pattern" that was gone by game 20.
- **Checked:** the planted-weakness test (`learner_eval.md`, re-scored) still finds the piece-hanging bot 5/5, first flagged at move 9 as before; the other bots unchanged.
- **End state:** not committed.

### 26 Sep, 04:06 — A time on every note
- **Your request:** a clear time on everything that gets updated, not just the date.
- **Did:** from now on every diary heading, both "Where the project stands" blocks, `TODO.md`'s "Last updated" and "(Done …)" notes, the lab notes and the simulated-games report carry the date and the time (24-hour, Vietnam time), read off the computer's clock. `simulate_games.py` now writes the time too (it shows in `sim_games/README.md` after the next run). The rule is in `CLAUDE.md`.
- **Problem:** the times of older entries were never written down, so they keep only their dates rather than a guess.
- **End state:** not committed.

### 26 Sep, 11:47 — Round 2 of the hand check: your fixes, built
- **Your decisions:** "opens a line" only when it's useful at that moment. You rejected two of my rules on the way: "ignore the back rank" (a square can matter later) and "only if it attacks now or the engine uses it" (in the opening, opening lines is good in itself). Agreed: *in the opening* (a side still has a knight or bishop at home) it counts when the piece gets a way out, a square off its home rank; *later*, only if the piece now attacks something through the line, or the engine's line uses it. Damage control: "could just be shorter".
- **Did:** that rule in `board_facts.py`, plus new facts from your notes: a piece left where nothing defends it and taken next move (3.Ng5); "allows checkmate", naming the pieces that hit the square (f7: bishop c4 + queen h5); "puts a pawn in the centre"; "prepares d4" (4.c3); ...Ng4's attack on the bishop on e3 (the line's next move steps the bishop away). After a move that loses material or allows mate, the coach shows only the reply and your one answer. Coach's instructions: no guessing what you "want", pawns named by the square they stand on, no "worth less", an attack is only an attack, mate in words, the idea-first pattern only for moves it recommends. The checker now also reports "the c3 pawn" when no pawn stands there (kept out of the score).
- **Problems → fixes:** my first test threw up nonsense like "...Nb4 prepares c6" and "nothing defends it" for an ordinary trade → "prepares" is now for pawn moves only, and "hanging" is only said when the piece is lost for less than it's worth. Reading the first new run (v4) found a false fact ("attacks the pawn on d2, and the line moves it away") and 1.h4 presented as "a natural idea" → both fixed, then run again (v4b).
- **Result (v4b):** checker 25/25; misnamed pawns 1 in 28 answers ("the pawn on a6", intermediate ...Nb4). Reading it: most of your points are fixed. Still there: invented framings ("your bishop is stuck", "keep your initiative", "connect the rooks"), and it still doesn't say *why* the better move is better (next to talk through).
- **End state:** not committed. Round 2 is on the board page: the same 13 answers, each showing what you said in round 1.

### 26 Sep, 11:50 — Real times for the older entries
- **Your request:** fill in the missing times from the session logs.
- **Did:** Claude Code keeps a log of every session (since 23 Sep, 09:47), with the time of each change. From it, every diary entry since 23 Sep now shows when it was written, in both diaries. So do the "(Done …)" notes in `TODO.md`, the lab notes, the dates next to your quotes in `CLAUDE.md`, and the titles of the hand-check and measurement files. The old labels were often wrong: "24 Sep (late night)" was 16:48, "23 Sep (night)" was 13:57.
- **Exceptions:** the "24 Sep, 14:14" entry was written at 16:48 by a session catching up on the notes; it shows 14:14, when its work ended (the last commit). June–July entries keep only their dates: no logs are left from then. `sim_games/README.md` gets its time the next time it's generated.
- **End state:** not committed.

### 28 Sep, 16:40 — More like research: two papers, four steps
- **Your question:** "I don't see a lot of research in this." Fair: lately the work was mostly building, tuning on the same 25 cases. There was no comparison with a simpler method, only one grader, and no written question to answer.
- **Decided (your plan; background in `lab_notes.md`, 25 Sep):**
  - 2 Q1 papers over the 2 years. Paper 1 = correct + relevant. Paper 2 = fits this player.
  - After your round-2 check the tutor is frozen as version 1: no changes to its instructions or its facts while it's tested.
  - Correct, relevant and meaningful are different: "meaningful" depends on the player, so it goes to paper 2.
- **Your worry:** "just prompt engineering, nothing new." My view: the parts aren't new on their own (the design is in Kim 2025, fact-checking in Hebbar 2026, concept detection in DecodeChess). The experiments will show what is. Left open.
- **Found:**
  - Hebbar et al. give away their test set (125 positions with experts' key points; free licence). Their two scores are exactly "correct" (share of true claims) and "relevant" (share of the expert's key points covered), so step 3 uses it.
  - Added to `related_work.md`: DecodeChess (a paid app that explains Stockfish with fixed sentences) and four papers on "which features matter" (e.g. SARFA, ICLR 2020).
- **Problem:** the office network blocks GitHub and Lichess (tested) → download the set over the hotspot.
- **End state:** `TODO.md` has the 4 steps. No code changed. Nothing committed.

### 29 Sep, 14:06 — Round 2 of the hand check: your answers
- **Result:** 9 of 13 answers still have a problem (round 1: 10). Fine now: ...Nb4 intermediate, 1.a4, 1.h4, Ruy Lopez. New: the QGD answer (one word, "you retreat" → "should retreat").
- **What's left:** mostly that it doesn't say *why* the better move is better (4 answers). That's the "relevant" question of paper 1, not a wording slip. The rest: reasons that are true but useless (a rook "line", a queen line after losing a knight), one untrue word ("stuck"), clumsy wording, and one fact not used (queen + bishop on f7). Table in `walkthrough_audit.md`.
- **End state:** your call: freeze this tutor as version 1 now? Nothing committed.

### 29 Sep, 16:43 — Version 1 frozen
- **Your decision:** freeze now. The "why the better move is better" gap is what paper 1's experiment measures, so fixing it first would mean tuning on the same 13 cases again.
- **Did:** committed the walk-through as version 1 (`37aef2a`, 40 files: board facts, the coach's instructions, the checker's misnamed-pawn count, all runs and both rounds of your check). Left out: the counting fix (waits for your look at the panel). Self-tests pass (board facts, grading, the 5 mistake kinds, a full game, the checker).
- **Problem:** in Claude's own session Windows wouldn't start Stockfish from the project folder (a setting only that session has). Tests were run with it switched off; no code changed, and your terminal isn't affected.
- **End state:** not pushed to GitHub (pushing also updates the live app: your call). From now on the coach's instructions and facts stay as they are while they're tested. Next step is yours: the talk with João.

### 29 Sep, 17:08 — The whole project as one story
- **Your ask:** you felt a bit lost, and wanted one easy, interesting read: how the project started, what it had at first, and how it changed.
- **Did:** wrote `PROJECT_STORY.md`: the story in six lines, a timeline, a "cast" (Stockfish, Gemini, the checker, board facts, the notebook), 7 short chapters from 17 Jun to today with real coach answers (July's invented "open files" reason; version 1's ...Nb4 answer), where you are now, the lessons, and the key numbers. Laptop only: it quotes the lab chat, so git ignores it.
- **End state:** no code changed. Next step is still yours: the talk with João.

### 30 Sep, 01:18 — The story as a web page, and a slip in test case 8
- **Your ask:** the same story as a web page with boards.
- **Did:** `PROJECT_STORY.html` (open it in your browser; laptop only, like the story). The same chapters, with 6 boards you step through with ◀ ▶: your ...Nb4 and the e5 trap (4.Nxe5? Qg5), July's "open files" case, the hung knight on g5, the mate on f7, and game 10's knight on f3 counted three times. Every position and move was computed with python-chess, not typed by hand.
- **Found:** test case 8 ("Closed centre, Black to plan") has no Black bishop on c8. Black is a bishop down, so −4.79 is *against* Black; Gemini told Black "heavily in your favor" and invented "open files". Your July audit called the cause unknown. Probably a slip when the 25 cases were written. What to do about it is your call (`TODO.md`).
- **End state:** no code changed; nothing committed.

### 30 Sep, 01:41 — Version 1 on GitHub
- **Your ask:** anything not updated? (You were on home wifi, where GitHub works.)
- **Did:** checked that the committed files run on their own (everything loads, a full game grades, the app calls the coach correctly), then pushed version 1 and committed + pushed these notes (diary, `TODO.md`, `related_work.md`, `.gitignore`). The live app now runs the version 1 coach. Also fixed old to-do lines that still said "not committed".
- **Held back:** `CLAUDE.md` (part of it describes the counting fix, which isn't on GitHub yet) and the counting fix itself (waits for your look at the panel).
- **End state:** next step is still yours: the talk with João.

---

## Reference (look things up here; no need to read it through)

### How the checker works
After Gemini writes an explanation, `faithfulness.py` checks the text. It never changes it.
1. **Moves:** every move written (`Nf3`, `O-O`…) must be one the engine gave the coach, or (since 24 Sep) one named in the board facts. Not on the list → **hard flag** (the text fails). A bare square like "e5" → **soft note** only (shown to a human, doesn't fail), since it may just point at a square.
2. **Reasons:** a sentence with the score *and* a reason word ("because", "due to"…) but no engine move → hard flag.

**Can't do:** understand chess ideas written in words ("this pins the knight"); notice a real move said by the wrong side; hard-flag an invented pawn move; catch reasons without its trigger words; see pieces already on the board.

### The 5 mistake kinds
| Kind | Meaning |
|---|---|
| allowed mate | your move let the opponent force checkmate |
| missed mate | you had a forced checkmate and missed it |
| lost material | after your move, the engine's line shows you losing material (e.g. a hanging piece) |
| missed material | the engine's best line won material you didn't take |
| positional | no mate, no material: the position got worse. We don't say how, because the engine doesn't say |

### Key files
| File | What it is |
|---|---|
| `app.py` | The web app |
| `engine_analysis.py` · `move_review.py` | Engine facts · grading a move and naming its mistake kind |
| `board_facts.py` | What a player would notice about each move (for the walk-through) |
| `explainer.py` | The coach (Gemini) |
| `faithfulness.py` · `evaluate_faithfulness.py` | The checker · runs the 25 test cases |
| `faithfulness_records_audited.json` | **Frozen** run you audited. Never overwrite it |
| `validate_checker.py` · `human response.txt` | Scores the checker against your audit · your audit verdicts, word for word |
| `learner_model.py` · `simulate_learners.py` | The learner model · the bot test |
| `learner_eval_records.json` | Every move from the bot test; `python simulate_learners.py --rescore` re-scores it in seconds after a model change |
| `simulate_games.py` · `sim_games/` | Weakest-Stockfish games against itself, graded like a pasted PGN · the 10 saved games (paste any `game_NN.pgn` into the app), what the panel says after each, and the *spread*, old counting vs now; `sim_games/batch_40/` = 40 more games for the spread check. `--rescore` re-counts saved games without the engine |
| `walkthrough_eval/` · `walkthrough_audit.md` | The walk-through measurements · your hand-check sheet |
| `related_work.md` | Notes on related papers, planned comparisons, candidate journals |
| `TODO.md` | What to do next, who does it, and why |

### If the coach fails online
Streamlit Cloud → *Manage app* → *Logs*. Lines starting `[coach]` show the exact error.

### Dr. Marcolino's writing checklist
What he flags in drafts (where it comes from: `lab_notes.md`); go through it before sending him any draft.
- No claim bigger than the results show. Back every fact with a reference; if you think something is new, check the literature or say "to the best of our knowledge".
- Keep Experiments (the setup) separate from Results.
- Enough comparisons (baselines): reviewers can treat too few as a flaw that can't be fixed later.
- Citation style: `\citet` when the authors are part of the sentence ("Chen et al. (2025) proposed…"), `\citep` otherwise.
- LaTeX (the tool papers are typeset in): read the warnings, not just the errors. No "Type 3" fonts, even inside figures (an old font format that paper-submission checks reject).
- Release the code, and read the whole paper once before submitting. Cut vague sentences.

### How we work
- Plain words, short answers, every term explained.
- Never change the coach's instructions to "fix" a score before you've seen the flagged cases.
- A change to the coach's instructions is kept only if the faithful rate doesn't drop, so every such change is measured again (giving the learner model to the coach counts too).
- A step is done only when you've reviewed it and we've decided together.
- Always say which run a number comes from.
- Commits hold only the files that belong to the change; credit is yours.
- You start and restart the app yourself.
- **This diary:** one short entry per session (a few bullets: did → problems and fixes → end state), and refresh "Where the project stands". The same entry, in full, goes in `DEV_DIARY_full.md`. To-dos go in `TODO.md`, not here.
- **Date and time on every update** (diary headings, status blocks, `TODO.md`, lab notes, reports): 24-hour Vietnam time, e.g. "26 Sep, 04:06", read off the clock, never guessed.

### Glossary
| Word | Meaning |
|---|---|
| **Engine** | Stockfish, a chess program far stronger than any human. The source of all chess facts |
| **The coach** | Gemini, the language AI that turns the engine's facts into words |
| **Eval / score** | The engine's number for who's better, in pawns: +0.50 = half a pawn better for the side it's measured from (this diary says whose side). It comes with **no reason attached** |
| **Centipawn** | 1/100 of a pawn |
| **Material** | The pieces a side has, counted in pawns: pawn 1, knight or bishop 3, rook 5, queen 9 |
| **Hang / hung piece** | A piece left where it can be taken for free |
| **Trade / recapture** | Both sides take each other's pieces; a recapture takes back right after a capture. "Mid-trade" = halfway through |
| **Line** | The moves the engine expects next. A forecast, not a promise |
| **Half-move** | One move by one side. "2 half-moves" = your opponent's reply, then yours |
| **Move notation** | Nf3 = knight to f3 · x = captures · O-O = castles · "..." = a Black move (...c6) · "4.Nxe5" = White's 4th move · "?" = a bad move |
| **Grades** | Best · Excellent · Good · Inaccuracy · Mistake · Blunder: a move's grade, by how much win chance it lost |
| **Refutation** | The engine's line after the move you played: how the opponent punishes a bad move |
| **Win chance** | The eval turned into a 0–100% chance of winning (the curve chess.com and Lichess use) |
| **FEN / PGN** | One line of text describing a position / the text format for a whole game |
| **Faithful** | The coach's text says nothing the engine's facts don't support |
| **Faithful rate** | The share of answers the checker passes: no invented moves and no invented reason for the eval. The checker can't see every kind of error (see "How the checker works"), so a human check is still needed |
| **Planted-lie test** | Deliberately add a lie and check that the checker catches it |
| **Ablation** | Switch one change off and re-measure, to see whether it really helped |
| **Repeatable** | Same input → same output, every time |
| **Kind (of mistake)** | One of 5 labels for a bad move (table above) |
| **Learner model** | The tutor's running notes on one player: which mistakes they repeat |
| **Chance / miss** | A chance = a move where a mistake was possible (e.g. there was free material). A miss = a chance where the mistake happened |
| **Bar** | The rate we'd call worth coaching, e.g. "hangs material on more than 1 move in 10" |
| **Repeat** | The same kind of slip on the player's very next move, e.g. a piece still left hanging. Counted once, as one problem (since 26 Sep) |
| **Spread (bunching)** | How much more a player's slips vary from game to game than coin flips would. 1.0 = like coin flips; 2.0 = the slips come in bunches, and the panel is surer than it should be |
| **Pattern / Not sure yet / Fine** | Pattern = 80% sure the player's rate is above the bar (and it happened 3+ times). Fine = 80% sure it's below. Not sure yet = too little evidence |
| **Bot** | A computer player with a weakness planted on purpose, so we know the right answer when testing the learner model |
| **Bayes' rule** | Start from a sensible guess, then adjust it a little with each new piece of evidence (here: each move the player makes) |
| **Type** (Marcolino's research) | A player's or AI program's hidden style, worked out from how it acts. Ours: a player's typical mistakes |
| **Maia** | A chess engine trained to play like humans of a given rating, not like the best player. Can tell how likely a player of each level is to play a move |
| **Lichess** | A free chess website that publishes all its games, useful as real data |
| **Baseline** | A simpler method to compare against, to show ours is better |
| **Confidence range** | Where the true value probably lies. With few cases it's wide: 22/25 = 88%, but really 70–96% |
| **Q1 journal** | A journal in the top quarter of its field by ranking |
| **Streamlit / Streamlit Cloud** | The tool that makes the web page / the free service that hosts it online |
| **API key** | A secret password that lets the app use Gemini. Never put it in the code |
| **Commit / push** | Commit = save a snapshot of the code on the laptop. Push = copy the snapshots to GitHub (a backup; it also updates the online app) |
| **Firewall** | The office network's security filter. It blocks GitHub, Lichess and Maia downloads |
