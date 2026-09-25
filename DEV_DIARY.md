# Development Diary — AI Chess Tutor

MSc project, **VinUniversity** · supervisor **Dr. Leandro Marcolino** · author: phnam05

The project's story, a few lines per working day. **What to do next is in
`TODO.md`**, not here. Every detail up to 24 Sep 2026 is in the frozen long
version, `DEV_DIARY_full.md` (on your laptop only, not on GitHub): open it
only when you need one day in full.
Words in *italics* are in the Glossary at the bottom.

---

## Where the project stands (26 Sep 2026)

**The idea:** the *engine* (Stockfish) decides the chess; a language AI
(Gemini), called **the coach** here, only puts the engine's facts into words,
at the player's level.

**Research question:** can an AI tutor explain a strong engine's decisions
(1) *faithfully*, saying nothing the engine didn't support, and (2) adapted to
the learner? And can both be measured?

**Your decisions (23 Sep):** the thesis covers both parts · aim for a paper in
a *Q1 journal* within about a year · the study uses after-game review (pasting
a finished game), not help during live play.

| Step | What | Status |
|---|---|---|
| 1 | Checker: compares the coach's text with the engine's facts | ✅ Done |
| 2 | Test: 25 cases, your hand audit, a measured faithful rate | ✅ Done |
| 3a | Name the *kind* of each bad move | ✅ Done |
| 3b | Learner model: how often *this* player makes each kind | ✅ Built |
| 3c | Show it in the app · give it to the coach | ✅ In the app (on GitHub, 26 Sep) · coach later |
| 3d | Test it on *bots* with a planted weakness | ✅ First run |
| — | Walk through engine lines your way (your rules, 24 Sep) | Built, not committed · your hand check (25 Sep): 10 of 13 answers have a problem · board-fact fixes in progress (26 Sep) |

**Numbers you can quote**
- Your hand audit of 25 coach answers (3 Jul, before the coach fix), asking "did the coach stick to the engine's facts?": 11 Yes · 5 Mostly yes · 7 Partially · 2 No.
- Checker vs. your audit: of the 10 answers you marked as inventing a reason for the eval, it found **all 10**, and it wrongly failed **0** good answers.
- *Planted-lie test*: **25/25** fake moves and **25/25** fake reasons caught.
- *Faithful rate*: 19/25 (76%) → **22/25 (≈88%)** after the fixes to the coach's instructions on 3 and 17 Jul (22/25 in every July re-run; 21 and 23 when re-run on 24 Sep). Invented moves: **0**.
- Asking for plainer words made it worse (16/25 vs. 22/25), so it was removed.

**What the thesis still needs** (the 23 Sep verdict plus the plan; most important first)
1. **More test cases.** With 25, "88%" really means somewhere in 70–96% (the *confidence range*), so the fix isn't proven yet. ~100 positions from real games narrows it to ~80–93%. Report it with a confidence range, as Dr. Marcolino's ReCePS paper does.
2. **A check on the grading.** You are the only judge and also the author. Plan: grade *blind* (not knowing which version wrote each answer), re-grade some weeks later, and ask Dr. Marcolino for a second person.
3. **Proof that the 3 levels really differ.** Nothing yet shows "beginner" text is simpler, and advanced-level text still uses heavy vocabulary.
4. **Guessing the player's level automatically** from their moves, so the tutor picks the level itself (Dr. Marcolino's *Bayes' rule* idea, using *Maia*). This is the core of the "adapt to the learner" half.
5. **Proof that it helps people learn:** a study with real players. It needs ethics approval, which takes months, so start early.
6. **Comparisons (*baselines*)**, e.g. the coach without the engine's facts. Reviewers expect them.
7. **The learner model on real human games** (*Lichess* is blocked by the office *firewall*). Its bars are still hand-set guesses, and it isn't given to the coach yet.
8. **A related-work chapter** (started in `related_work.md`).

**Git:** everything is on GitHub except the walk-through code (board facts,
the coach's new instructions, their test files), which is still being fixed.
The office firewall usually blocks GitHub (and Lichess, Maia); pushing over
your phone hotspot works. The repo is public, so private lab notes live in
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

### 23 Sep — Accepted into the MSc; Step 3 begins
- **News:** accepted at VinUniversity with Dr. Marcolino; he agreed to chess instead of Go.
- **Did:** re-checked the checker from scratch (planted lies caught 25/25 and 25/25; the same text always gets the same verdict). Fixed a checkmate graded "Blunder". Built the mistake detector (Step 3a): each bad move gets one of 5 *kinds*, read from the engine's lines and a *material* count, no AI guessing. Limit: it sees only about 6 moves ahead.
- **The coach failed during your demo to Dr. Marcolino.** The cause was temporary (the free plan's limit of 15 requests a minute, or Gemini briefly busy), but the app made it permanent. Now it tries up to 3 times, names the real cause instead of always "check GOOGLE_API_KEY", and shows a "Try again" button. A missing key stops only the coach, not the whole app. The add-on libraries are locked to tested versions (the cloud used to install the newest, untested ones).
- **Problems → fixes:** the checker errs both ways. It misses "…, as your pieces are developing" (no trigger word) and wrongly flags a true "your extra rook" (it can't see the board) → by hand the rate is still ≈88%, ± a case or two. Lesson: the coach may have learned to avoid "because" and use softer words the checker doesn't catch, so a human spot-check is needed now and then. What to do about these two blind spots is **still your decision**. `git push` failed: the office firewall intercepts GitHub's secure connection → push from another network. Don't switch off git's security check to get around it: anyone on the network could then pretend to be GitHub.

### 23 Sep (later) — Honest verdict; the learner model
- **Did:** wrote the verdict above. Built the learner model (Step 3b). For each mistake kind it counts *chances* and *misses*. Every player starts from a guess that sits exactly on the bar and weighs as much as 10 moves of evidence, so one slip can't label anyone. A kind becomes a **pattern** only when we're 80% sure the player's rate is above a bar (e.g. "hangs material on more than 1 move in 10") and it has happened at least 3 times. The maths was checked against 200,000 random samples.
- **Limit:** the bars are my guesses, set by hand, and one is already known to be too lenient ("misses more than half its chances", when the engine misses none).
- **Test (Step 3d):** 4 kinds of bots that play like Stockfish except for one planted weakness: **hangs** (leaves pieces to be taken), **misses** (skips free material), **drifts** (makes random quiet moves), **solid** (no weakness: the control, i.e. the comparison group). 5 bots of each kind, 40 moves each against Stockfish.
- **Result:** "hangs" found **5/5** (after about 9 moves); the solid bots were never flagged; "misses" and "drifts" **not found**. Why: a bot's planned mistake often wasn't what the engine judged its move to be; one habit got split across two kinds; and chances to win material are rare (~7 in 40 moves). The one extra flag was a drifter that really lost material on 8 of 40 moves: a real weakness, not a false alarm. Re-runs give identical games, so the test is repeatable.
- **Decision:** don't tune the rules until my own bots pass (that would be marking my own exam). Set the bars from real Lichess games instead, and check there that weaker players hang more pieces.

### 23 Sep (evening) — Reading the lab's chat
- **Did:** read the lab's Discord chat (Aug 2025 – Aug 2026) as background only. What we learned about the lab's people and plans is in `lab_notes.md` (kept off GitHub: the repo is public). Turned it into questions for Dr. Marcolino (in `TODO.md`); the papers named in the chat are in `related_work.md` and `TODO.md`.
- **Problem → fix:** the chat file holds personal data → told git never to save it (`.gitignore`).

### 23 Sep (night) — "Your patterns" in the app
- **Did:** the app shows the learner model ("Your patterns"): each mistake kind as Pattern / Not sure yet / Fine, with the moves as evidence. Only your moves count: pasted games get a "You played: White / Black / Both" choice. The notes build up across games until the page is reloaded. You decided the direction (above). Started `related_work.md`.
- **Found:** a very close new paper, "Hallucinations on the Board" (Aug 2026; a "hallucination" is an AI making things up), and a paper at NAACL 2025 (a big AI conference) already using the "engine decides, AI phrases" design → that design alone isn't our contribution; the *tutor* is (levels, learner model, level guessing, all measured). A comparison against the coach without engine facts is now expected of us.
- **End state:** panel built and tested (9/9 checks passed: grading as Black, re-grading as White, a second game, New game, Undo…), not committed; you'll check it first.

### 24 Sep — Getting ready to talk to João
- **Did:** Dr. Marcolino suggested you talk to João. Re-read the chat for João's work, named the ~20 untitled paper links (now in `related_work.md`), and prepared questions for him (in `lab_notes.md`). Message sent; he's busy until his 25 Sep deadline.
- **Learned:** two chess papers on guessing a player's level (one from ICLR 2025, a big AI conference; "Predicting Chess Player Rating Based on a Single Game", 2023), now proposed comparisons. The rest (who works on what, Dr. Marcolino's remarks, ethics) is in `lab_notes.md`, kept off GitHub.

### 24 Sep (midday) — Pushed; the online coach lost its key
- **Did:** pushed the 7 waiting commits over your phone hotspot (it works; the office network still doesn't). That also updated the online app with the coach's retries and plain error messages.
- **Problem → fix:** the online coach then said "no API key". I changed the code twice and pushed both, before you tried the simple fix: re-paste the secret and reboot the app. That fixed it. Kept: the key is now looked up on first use, not at start-up (so a newly added key works without a reboot), and a log line names the secrets it found (never their values). Undone: looking under other key names (4b46dbb). Lesson: let you try the simple fix first.
- **End state:** 1 commit (4b46dbb) waits to be pushed.

### 24 Sep (later) — Your rules for walking through a line
- **Your complaint:** after your ...Nb4 (a Mistake), the coach said "O-O… followed by a6". It's unclear who plays a6, and there's no reason anyone would find it.
- **Checked:** our engine agrees ...Nb4 is a Mistake (from Black's side the eval went −0.44 → −1.46: from slightly worse to clearly worse), but its line is O-O then **...c6**, not ...a6 (the online app probably runs a different Stockfish version). Both attack White's bishop on b5, so your point holds.
- **Your rules** (also in `CLAUDE.md`): say who plays every move; say what the bad move changed; give the idea before each recommended move; only 1–2 moves deep; adapt to the level.
- **Claude's pushback:** the engine gives no reasons, so reasons must be computed by code, not invented by Gemini. Example: after ...Nb4 the knight no longer defends e5, but taking it is bad for White (4.Nxe5? Qg5), so "you lose e5" would be a wrong reason. Also: the move you *should have played instead* (...a6) is kept apart from your *best reply now* (...c6).

### 24 Sep (evening) — The new walk-through, built and measured
- **Did:** the new `board_facts.py` works out what a player would notice about each move (captures, checks, attacks, "a pawn can chase it"…). Every move is labelled in code with who plays it. How deep to go is set by level (2 / 3 / 4 *half-moves*), and the line stops before any of your moves that has no fact to explain it. New coach instructions around your rules. The checker changed too: it now also accepts squares and moves named in the board facts, but judges reasons for the eval exactly as strictly as before (still 10/10 against your audit).
- **Result:** the 25 cases, run twice (50 answers): the checker passed 44/50 before → **50/50** after; "followed by" 11 → 0. But the same 25 cases were used to build it, the checker itself changed (so this isn't directly comparable with July's numbers), and it can't see an invented *idea*. Reading by hand still finds: "attacks" stretched into "forces"; "the c3 or a3 pawn" once; a board fact linked to the verdict ("…can be chased, so your move was a mistake"); notation in square brackets.
- **Problems → fixes:** Gemini got the eval backwards (told Black "−1.46 favors you") → the code now spells out who is ahead. A test run froze for minutes on one Gemini request → measurements use a 60-second limit; the app got its own limit later that day (below).
- **End state:** not committed. Next: your hand check in `walkthrough_audit.md`, then the rule "an attack is only an attack".

### 24 Sep (night) — A shorter diary
- **Did:** the diary had grown to 1,050 lines and was a hassle to read. Rewrote it as this short version; the full text is frozen in `DEV_DIARY_full.md`. To-dos now live only in `TODO.md`. Two checks (mine, then a fresh reviewer's) put back what the first cut lost: the level-guessing step, key findings and limits, open decisions, and explanations for ~25 words.

### 24 Sep (late) — A time limit for the coach
- **Did:** the app's Gemini request now gives up after 20 seconds per try (3 tries, so about a minute at worst; a normal answer takes ~3 s). Before, one stuck connection could leave the coach waiting forever. When time runs out, the app says so in plain words ("Gemini didn't answer in time…") and keeps its "Try again" button.
- **Tested:** a forced time-out gave up after 3 tries with that message; a normal call still answered in 3.2 s.
- **End state:** not committed (with the rest of today's work).

### 24 Sep (late night) — Are the notes up to date?
- **Did:** checked every `.md` file against the code. Fixed: `CLAUDE.md` and `README.md` still said the engine stops after 1 second (removed on 1 Jul, because a time limit made it unrepeatable); the README said Python 3.9+ (the locked libraries need 3.10+) and had a placeholder GitHub address; this diary had no entry for the push and the key problem (added above, "midday").
- **Left for later:** the README (the project's GitHub front page) still describes the July app: no checker, no game review from a PGN, no learner model. Its 3-level description will be wrong once the new walk-through is kept → update it after the panel and walk-through are committed (in `TODO.md`).

### 25 Sep — A hand check you can actually do
- **Did:** turned your hand check into a web page (link in `walkthrough_audit.md` and `TODO.md`). It shows 13 coach answers, freshly generated with the same code, each in full. Every case has a board you can step through move by move, whose caption always says who just moved and who is to move; the engine's facts, with move numbers; and one question per answer: "Any problem?". Your answers save on the page and Claude reads them from there.
- **Problems → fixes:** the 265-line sheet was too long → 9 yes/no questions. Text alone wasn't enough → boards. My first boards showed positions several moves deep, with arrows for both sides mixed together, which made it hard to tell who played what → redone in the format of your "Chess Coach Correctness" page (board before the move, red = played, green = engine's best). Only excerpts of the answers → full answers.
- **Result:** the checker passes the fresh run 25/25 again. Reading it by hand found one new problem: in the ...Nxe4 case the coach stops at 7...bxc6, just before 9.Kxf2 wins the knight, so ...Nxf2 sounds like a good move. That comes from our code's level cut, not from Gemini. Still there: "the c3 or a3 pawn", the missing reason for ...Ng4 (it attacks the bishop on e3; our board facts don't see that), and "−100.00" shown to a beginner instead of "checkmate".
- **Your verdict:** 10 of 13 answers have a problem (fine: 1.h4, Ruy Lopez, QGD). In short: our code's facts are too thin or misleading (Be3 "opens a line for the queen" only frees back-rank squares; no fact for a piece left to be taken for free, for the attack on f7, or for claiming the centre); after a lost piece the coach should stop instead of walking on; it never says *why* the better move is better; wording (guessing what you "want", "the c3 pawn", copying "worth less"). Full table in `walkthrough_audit.md`.
- **End state:** nothing committed. Next: agree which fixes to do first.

### 26 Sep — Why board facts exist; one gap closed
- **Your question:** where do the board facts come from, and why have them? → They're plain code (`board_facts.py`), not AI: a fixed list of yes/no checks on the board, each "yes" filling in a ready-made sentence, handed to Gemini as English. They exist because your rules ask for the *idea* behind each move ("on b4 it can be chased by c3 or a3"), and Stockfish gives no ideas. So the engine says what's good, the code says what's visible on the board, and Gemini only words it.
- **Found while explaining:** "moves away from the attack" only counted attackers worth *less*. An undefended knight fleeing a bishop got no reason → now any attacker counts when nothing defended the piece (a defended piece attacked by an equal one is just an even trade, so still nothing).
- **Result:** self-test passes (undefended knight → fact; defended → none; the ...Nb4 example unchanged). Of the 25 test cases, 1 prompt changes: Caro-Kann 3.e5 now "moves the pawn away from the attack by Black's pawn on d5" (true, and the real reason for e5). Side effect: pawns can now get this fact too. Not re-run through Gemini.
- **End state:** not committed.

### 26 Sep (later) — Simulated games for the patterns panel
- **Your ask:** no time to play 10 games, so simulate games between 1000-rated players. → New `simulate_games.py`: Stockfish plays both sides at its weakest setting, and every move is graded exactly as the app grades a pasted game. 10 games in under a minute, saved in `sim_games/` (one PGN per game, ready to paste, plus a report).
- **Limit:** Stockfish can't go below "1320", and that's an engine rating, not a human one. Its mistakes are random, not human (it once took a rook and promoted to a knight instead of a queen). Good for seeing the panel work; not evidence about real players, so not for setting the bars.
- **Found:** players A and B are the *same* bot, yet after 10 games the panel calls "leaving material to be taken" *fine* for A (15 in 286 moves) and a *pattern* for B (40 in 287). B's slips come in runs: in game 10 one attacked knight on f3 was counted on 3 moves (20, 21, 23), because each move that didn't save it counts again. So the panel treats one problem as several pieces of evidence and gets sure too fast. This matters for real 1000-rated games too, where hung pieces often stay on the board for a few moves.
- **End state:** not committed. The fix is your call (in `TODO.md`).

### 26 Sep (night) — Saved to GitHub; private notes kept local
- **Did:** committed and pushed the finished work: the "Your patterns" panel, the simulated games, and the notes (this diary, the to-do list, related work, README fixes).
- **Found → fix:** the GitHub repo is public, and the diary and to-do list quoted the private lab chat (remarks about people in the lab and their unpublished work). → Moved those lines into `lab_notes.md`, which git ignores, as it now does `DEV_DIARY_full.md`; the diary and to-do list point there. None of it reached GitHub.
- **Held back:** the walk-through code (`board_facts.py`, the coach's instructions, their test files). Another Claude session was changing `board_facts.py` at that very moment (the fixes from your hand check), so committing it would have saved half-finished work.
- **End state:** pushed; the walk-through is committed once those fixes are done.

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
| `simulate_games.py` · `sim_games/` | Weakest-Stockfish games against itself, graded like a pasted PGN · the saved games (paste any `game_NN.pgn` into the app) and what the panel says after each |
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
- **This diary:** one short entry per session (a few bullets: did → problems and fixes → end state), and refresh "Where the project stands". To-dos go in `TODO.md`, not here.

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
