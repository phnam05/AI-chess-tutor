# Development Diary — AI Chess Tutor

MSc project, **VinUniversity** · supervisor **Dr. Leandro Marcolino** · author: phnam05

This is the story of the project, in order, from the first day. It has three parts:

1. **The first version**: how and what we built at the start.
2. **Was the first version good?** An honest verdict.
3. **Upgrading it, step by step**: one entry per working day, including the
   problems we hit and how we got past them.

A new entry is added at the end of every working session. Words in *italics*
are explained in the **Glossary** at the bottom.

---

## Where the project stands — updated 2026-09-23

**In one line:** a chess tutor where **the engine decides the chess and the AI
only explains it**. The *engine* (Stockfish) supplies every fact; the language
AI (Gemini) only puts those facts into words at the player's level.

**Research question (working version):** can an AI tutor explain a strong AI's
decisions to a human (1) *faithfully*, saying nothing the engine didn't support,
and (2) adapted to that particular learner? And can both be *measured*?
Steps 1–2 answer part (1). Step 3 is part (2).

**Where we are:** Steps 1–2 done. Step 3's mistake detector, learner model and
first simulation test are done; the learner model isn't in the app yet. Recent
commits are on the laptop only, waiting to be pushed.

| Step | What | Status |
|---|---|---|
| 1 | Faithfulness checker: a program that checks the coach's text against the engine's facts | ✅ Done (re-checked 2026-09-23) |
| 2 | Evaluation: 25 test cases, your hand audit, a measured faithful rate | ✅ Done |
| 3a | Mistake detector: name the *kind* of each bad move | ✅ Done 2026-09-23 |
| 3b | Learner model: estimate how often *this player* makes each kind | ✅ Built 2026-09-23 |
| 3d | Test it: computer players with a *planted* weakness; does the model find it? | ✅ First run 2026-09-23 |
| 3c | Use it: show it to the player (app), then give it to the coach (a prompt change, so re-measure faithfulness) | Next |
| 6 | **Bigger faithfulness test:** ~100+ positions from real games, not 25 hand-picked | Needed for the thesis |
| 7 | **Second judge:** someone else rates part of the cases; report how often you agree | Needed for the thesis |
| 8 | **Measure the levels:** is "beginner" text really simpler? | Needed for the thesis |
| 9 | **Small study with real players** (needs ethics approval: apply early) | Needed for the thesis |
| 4 | Writing: related work, README built around the research question | Planned |
| 5 | Optional: faithful rate with a confidence range (like Marcolino's ReCePS paper) | Idea |

**Headline numbers you can quote**

| Measurement | Result |
|---|---|
| Your hand audit of 25 coach answers (before the fixes) | 11 Yes · 5 Mostly · 7 Partially · 2 No |
| Checker vs. your audit, on invented reasons | found **10 of 10** you marked; **0** good answers wrongly failed |
| Planted-lie test (2026-09-23) | **25/25** fake moves caught · **25/25** fake reasons caught |
| Faithful rate: before the prompt fix → after | 19/25 (76%) → **22/25 (≈88%)**, same in repeated runs |
| "Explain plainly" experiment | 16/25 with it vs. 22/25 without, so it was removed |
| Invented moves in the latest run | **0** |

**Waiting on you:** **push the latest commits from a network outside the
company firewall** (`git push`); until then the live app runs the old code.

### Is it good enough for a master's thesis? (honest verdict, 23 Sep 2026)

**As a working system and a first study: yes, and it's more rigorous than most
student projects.** It has a clear design idea (the engine decides, the AI
explains). It measures its own honesty with a checker that was *itself* tested
(planted lies, a human judge). It reports failures openly (the "explain plainly"
backfire, the lucky 24/25). And it has real findings: the AI rarely invents
*moves* but often invents *reasons*, and asking for simpler words made it
*less* faithful.

**As a complete thesis: not yet.** What's missing, most important first:

1. **Too few test cases.** With 25 cases, "88% faithful" really means
   *somewhere between 70% and 96%*, and the before/after ranges overlap
   (76%: 57–89%; 88%: 70–96%). So we can't yet *prove* the prompt fix helped.
   About 100 positions narrows it to roughly 80–93%. Re-running the same 25
   doesn't help much; it needs *different* positions, ideally from real games
   rather than hand-picked.
2. **One judge, who is also the author.** A thesis needs a second, independent
   person to rate part of the cases, and a number for how often you agree.
3. **The levels are claimed, never measured.** Nothing yet shows the
   "beginner" text is actually easier to read.
4. **No evidence yet that it helps people learn**, which is the aim of Project
   #40 ("fostering learning"). That needs a small study with real players, and
   studies with people need ethics approval, which takes time, so plan it early.
5. **The learner model** now works on computer players (see 23 Sep), but it's
   not in the app yet, its bars are set by hand, and it hasn't seen real human
   games.
6. **No related-work chapter yet**: the thesis must show where it sits among
   existing research (reading list below).

**Reading list to start with** (check each one before citing it):
- Jacovi & Goldberg (2020): *faithfulness* vs. *plausibility* of AI explanations (ACL). This is the core idea behind Step 1.
- Jhamtani et al. (2018): generating move-by-move chess commentary (ACL).
- McGrath et al. (2022): *Acquisition of chess knowledge in AlphaZero* (PNAS).
- McIlroy-Young et al. (2020): **Maia**, human-like chess engines for each rating level (KDD).
- Bull & Kay: *open learner models* (the brief's "open learning models").
- Marcolino's group: on-line estimators of teammates' types and parameters (JAAMAS 2022); *It Is Among Us* (AAMAS 2024).

**An idea worth raising with Dr. Marcolino:** use Maia to work out a player's
*level* from their moves (the same "work out the hidden type from actions"
problem as his research), then pick the explanation level automatically. That
would tie the brief's "adapt to the player's level" directly to his methods.

---

# Part 1 — The first version (17–19 June 2026)

### 17 June 2026 — Day one: the idea and the first working app

**The idea.** Chess engines know the best move, but they only give a number, not
an explanation. Language AIs explain well, but they're bad at chess: they make
up moves and miscount pieces. So we split the work. **The engine decides, the AI
only explains.** The engine gives the facts (best move, score, expected line);
the AI is told to put those facts into words and never judge the position itself.

**What we built:**
- `engine_analysis.py`: gives a position to Stockfish and gets back the best
  move, the *eval* and the *line*.
- `move_review.py`: grades a move you played by how many *centipawns* it lost
  compared with the best move (Best / Good / Inaccurate / Mistake / Blunder).
- `explainer.py`: sends those facts to Gemini with strict rules ("don't suggest
  a different move, don't invent tactics") and three levels: beginner,
  intermediate, advanced.
- `app.py`: a Streamlit web page with two screens. **Analyze a position**: paste
  a position (*FEN*) and press "Coach me". **Review my move**: pick the move you
  played from a dropdown.
- Put online on Streamlit Cloud.

**Difficulties → how we got past them**
- *The engine wouldn't start on Streamlit Cloud.* The cloud runs Linux, not
  Windows, so `stockfish.exe` doesn't work there. → `packages.txt` installs the
  Linux Stockfish, and the code looks for whichever one exists.
- *The API key had to stay secret.* → Read from Streamlit's secret settings,
  never written into the code; `.gitignore` keeps key files out of GitHub.
- *Git got tangled.* Editing on the GitHub website and on the laptop at the
  same time caused merge commits. → From then on, changes were made on the
  laptop and pushed.

**State at end of day:** a working online prototype. You could analyse a
position or grade one move, with an explanation at your level.

### 19 June 2026 — Making it a real tutor: fair grading, a playable board, speed

**What we built:**
- **Fairer grading.** Switched from "centipawns lost" to **win-chance lost**.
  Losing half a pawn matters a lot when the game is equal and hardly at all when
  you're already winning by a queen. Win chance captures that.
- The numbers behind each grade are shown (win chance before → after, the eval).
- **Side-by-side boards:** your move vs. the engine's best, with arrows.
- **Play-a-game mode:** a clickable board. You play both sides and every move
  gets graded.
- **"Why was my move wrong?"** Before, the coach only named the better move.
  Now it gets the engine's *refutation* (the opponent's punishing reply) and
  starts with that.
- The coach says what will *likely* happen, not what *will* happen.
- Merged the screens into one; added a copyable FEN box and "re-explain at a new
  level".

**Difficulties → how we got past them**
- *A grading label never showed its colour.* The grader said "Inaccurate" but
  the page expected "Inaccuracy". → Fixed the label.
- *The app crashed locally with no secrets file.* → A guarded lookup falls back
  to an environment variable.
- *The engine wouldn't launch on Windows* (a relative file path). → Use the full
  path.
- *Pieces were invisible on Streamlit Cloud.* The Cloud's font has no chess
  symbols. → Install a font that has them (FreeSerif).
- *The board was cut off on the right.* → Changed a display setting ("auto" →
  "always") so it scales to the column.
- *Clicks replayed the previous move.* The click widget keeps reporting the last
  click on every redraw. → Remember the last click already handled and ignore it.
- *Grading one move took ~2.4 seconds.* A new Stockfish was started and shut
  down for every request. → Keep one engine running and share it: **~0.1s**.
  (During this work I ran many silent commands and killed processes, and you
  got lost. We agreed I explain each step as I go.)

**State at end of day:** a complete, playable tutor: board, grading, "why it was
wrong", three levels, online.

---

# Part 2 — Was the first version good?

**What was good**
- **The core design was right.** Keeping the chess with the engine and the words
  with the AI avoids the AI's biggest weakness (making up moves).
- **It worked as a product:** online, playable, grades every move, explains at
  three levels, and says *why* a move fails.
- Grading on win chance is the same idea chess.com and Lichess use.

**What was not good enough**
1. **The main promise was never checked.** We *said* the AI never makes up chess,
   but nothing verified it. It was a promise, not a measurement.
2. **No evaluation.** There was no answer to the first question any supervisor
   asks: *how do you know it works?*
3. **Not personal.** Three fixed levels, but no memory of *this* player's
   repeated mistakes. That's the "adapting to the learner" part of Project #40.
4. **Hidden faults we only found later:** the engine could give a *different*
   best move for the same position (found 1 July); engine lines could stop
   mid-trade and look like a blunder (3 July); a checkmating move could be
   graded "Blunder" (23 September); one Gemini hiccup killed an explanation for
   good (23 September).
5. **It read as an engineering demo, not research** (our own review on 27 June).

**Verdict:** a good prototype and a sound idea, but **not yet research**. It
claimed things it couldn't prove. Everything from Part 3 onward is about
turning claims into measured results and making the tutor adapt to one person.

---

# Part 3 — Upgrading it, step by step

### 27 June 2026 — Taking stock: from demo to research

**What we did**
- Studied Dr. Marcolino's Project #40 ("virtual tutors for complex decision
  problems": explain AI decisions, adapt to the player's level, find errors) and
  his papers. His own field is multi-agent systems: working out a teammate's
  hidden *type* from how it acts, plus robustness and guarantees for AI.
- **Honest verdict:** a strong fit with the project, but the work looked like an
  engineering demo.
- **A 3-step plan came out of this** (agreed by 30 June): (1) a *faithfulness* checker, (2) a small evaluation,
  (3) a *learner model*, which is the closest link to his "work out the type"
  research.
- Layout fixes: the coach panel is always on screen; a chess.com-style move log
  with quality badges (★ ! ✓ ?! ? ??).

**Difficulties → how we got past them**
- *You got lost in your own project.* I'd used words like "PV", "SAN",
  "refutation" without explaining them, and went too deep too fast. → New rule:
  plain words, every term explained, one stage at a time, and I pause to check
  you're following. (The next day you asked for shorter answers too; also a rule now.)

**State:** a clear research plan. Step 1 next.

### 30 June 2026 — Step 1: a checker that reads what the coach wrote

**What we did**
- Built `faithfulness.py`. After Gemini writes an explanation, it finds every
  chess move in the text and checks that each one is a move the engine actually
  gave. A made-up piece move is a **hard flag**. A bare square like "e5" is only
  a **soft note**, because "your pawn on e5" is pointing at a square, not
  claiming a move.
- Connected it to the app: every explanation is checked and saved to a log,
  without ever changing what the coach says.
- **Planted-lie test:** we added fake moves (Nxe5, Bxf7+, Qh5, Qxf7#) to real
  coach text, and all 6 were flagged. So the alarm isn't dead.
- First run of the 25-case test: 25/25 clean.

**Difficulties → how we got past them**
- *The checker seemed not to run in the app.* An old Streamlit server from the
  previous day was still running and serving the old code. → Stopped every old
  server and restarted cleanly. Then the log filled up as expected.
- *Two limits showed up:* (a) an invented **pawn** move (e.g. "c3") is only a soft
  note; (b) re-running the engine sometimes gave slightly different lines, so
  facts couldn't be reproduced later. → (a) Kept as a documented limit, to avoid
  false alarms. (b) Fixed the next day.

**State:** the checker works and is connected. Step 2 started.

### 1 July 2026 — A repeatable engine, and the key question: "is the checker blind?"

**What we did**
- **Made the engine repeatable.** Same position → same best move, eval and line,
  every time.
- **Step 2:** `evaluate_faithfulness.py` runs 25 hand-picked cases (14 positions,
  11 moves; openings, middlegames, endgames; good and bad moves) through the real
  engine → coach → checker, and writes a report. Result: **25/25** clean.
- Built the human audit sheet (`faithfulness_audit.md`) so you could grade all
  25 answers yourself.

**Difficulties → how we got past them**
- *The engine gave different best moves for the same position* (you'd noticed it
  in the app too). Three causes: a time limit (it stopped at different depths
  depending on computer load), several threads racing each other, and memory
  left over from earlier positions. → Fixed all three. Measuring showed fixing
  only one wasn't enough. Speed cost: negligible.
- *A perfect 25/25 looked suspicious.* Your question: "a checker that never flags
  anything might just be blind." → That became the reason for the human audit:
  **check the checker**, not just the coach.
- *Found a real leniency:* case 4 said "bishop back to h4" (the move Bh4, not in
  the engine's line) and wasn't flagged, because "h4" reads as a bare square.
  → Recorded as a limit.
- *I called Step 2 "done" while your audit was still unfinished*, and you were
  rightly upset. → New rule: a step is only done when your review is finished
  and we've decided together.

**State:** repeatable engine; 25-case test built; your audit pending.

### 3 July 2026 — Your audit changes everything; the checker learns to see reasons

**What we did**
- **Your audit of all 25:** 11 Yes · 5 Mostly · 7 Partially · 2 No. The checker
  had said 25/25 clean, so you and it agreed only ~64% of the time. The gap was
  the finding:
  - **Main problem: invented reasons for the score** (~13/25). The engine gives a
    number with no reason, and the coach kept making one up. Worst: case 8, where
    −4.79 was "explained" by open files.
  - Move purposes that don't match the engine's line (cases 2, 3, 9, 17).
  - Two plain factual errors: case 4 (wrong bishop colour), case 11 (king and
    pawn roles swapped).
- **Decided together: fix the checker first, then the coach, then re-measure.**
  Fixing the coach with a checker that can't see the problem would prove nothing.
- **Checker upgrade:** a second check for sentences that mention the score AND
  give a reason ("because", "due to", "comes from"…). No engine move in the
  sentence → hard flag. An engine move cited → soft note.
- **Validated against your audit:** found **10 of 10** cases you marked, **0**
  good answers wrongly failed. Honest new baseline: **19/25**.
- **Coach fix ("ground it or drop it"):** state the score and who it favours,
  but only say *why* if the facts show it (material won in the line, or mate).
  Re-measured: 24/25.
- Also: full-game review from a pasted *PGN*; clickable move log.

**Difficulties → how we got past them**
- *"Gives you an edge" can be a translation or a made-up reason.* "Evaluated at
  +0.20, which gives you a slight edge" is fine. "Your active pieces give you an
  edge" is invented. → If the sentence credits the engine ("the engine
  evaluates…"), it counts as a translation.
- *"Edge" also means the edge of the board.* → "the edge" is ignored; only "a /
  your / slight edge" counts.
- *Case 9 looked like the engine hanging its queen* ("…Qxf4"). The line had just
  been cut one move before the recapture. → Engine lines are now never cut in
  the middle of a trade.
- *After following the engine's line, a fresh search picked a different move*
  (Qd5 vs Qa5+). → Explained, not "fixed": a line is a forecast, and later moves
  in it are searched less deeply. Caching old lines would give worse answers.
- *Four test cases had titles that disagreed with the engine's grade.* Checked:
  the titles were my hand-written guesses and never reached the coach. → Titles
  corrected.
- *Every test run overwrites the results file*, which would destroy the exact
  run you audited. → Saved a **frozen** copy (`faithfulness_records_audited.json`)
  that the validator always uses.

**State:** the checker sees both failure types and agrees with your audit. The
coach is improved and measured.

### 17 July 2026 — Two experiments, and the honest number

**What we did**
- You checked the last 4 flags yourself: case 23 accepted; cases 5, 15, 24 are
  wording, not lies.
- You named two quality problems: heavy vocabulary at advanced level, and deep
  engine moves dropped in with no context and on the wrong side (case 24:
  "…after dxe5", which was actually *your* move, 4 moves deep).
- **Experiment 1, kept:** when the coach mentions a later move, it must walk
  through the moves leading to it, in order, each on the right side. Case 24 is
  now told correctly.
- **Experiment 2, reverted:** "keep language plain at every level". Result:
  **16/25** with it vs. **22/25** without, run twice.

**Difficulties → how we got past them**
- *The flags I showed you didn't match your audit sheet.* You spotted it. The
  sheet shows the frozen July-3 run; the flags came from a newer run, and Gemini
  words things differently each time. → Explained; no bug. Lesson: always say
  which run a number comes from.
- *"Explain plainly" backfired.* Plain explanations push the AI into
  "because…", the exact thing the rules forbid. → Found by an *ablation*
  (switch one change off and re-measure). Removed.
- *24/25 turned out to be luck.* Re-runs gave 22/25 each time. → Reported the
  honest, stable rate: **≈88%**. The report now warns that one run is one sample.

**State:** Steps 1 and 2 closed and pushed. Remaining failures: occasional
invented reasons, a documented limit. Next: Step 3.

### 23 September 2026 — Accepted into the MSc; Step 1 re-checked; live app fixed; Step 3 begins

**News:** accepted into the MSc at VinUniversity, with Dr. Marcolino as
supervisor. His original idea was Go, but he agreed the project can continue
with chess.

**What we did**
1. **Re-checked Step 1 from scratch** (offline, no AI calls):
   - The audit comparison still holds: 10/10 found, 0 good answers wrongly failed.
   - Planted lies in all 25 real coach texts: a *legal* move the engine never
     gave → **25/25 flagged**; a made-up reason → **25/25 flagged**.
   - Same text → same verdict: 25/25.
2. **Fixed the live app.** The coach failed while you were showing it to Dr.
   Marcolino.
3. **Fixed a grading bug:** a checkmate could be graded "Blunder".
4. **Step 3a:** built the mistake detector (below).
5. Started this diary.

**Difficulties → how we got past them** (the last one isn't solved yet)
- *The checker makes mistakes in both directions (found today in the latest
  run):*
  - **Miss:** case 1 says "+0.42 … a slight edge, **as** your pieces are
    developing nicely", an invented reason. "As" isn't one of its trigger words.
  - **False alarm:** case 12 says "+6.30 … because you're winning with your extra
    rook", which is **true** (king + rook + pawn vs. a lone king). The checker
    can't see pieces already on the board.
  - → Judged by hand, the latest run is 20–23 of 25 depending on three
    borderline sentences, so **≈88% still stands, ± a case or two**. Lesson for
    the thesis: the coach fix taught the AI to avoid "because", and it may have
    moved to softer words the checker doesn't look for. A human spot-check now
    and then guards against that. (Next step for this: your decision.)
- *The coach failed during the demo.* I tested it: the key works, the model
  still exists, and a live call answers in ~3s, so the failure was
  **temporary** (the free plan's 15-requests-a-minute limit, or Gemini briefly
  busy). But the app turned temporary failures into permanent ones:
  - The Gemini library **never retries** by default. → It now tries up to 3
    times (waits ~2s, then ~4s). Tested with a fake always-busy server: 3
    attempts, then a clear message.
  - Every failure said "check GOOGLE_API_KEY", even when the key was fine. → It
    now says the real reason: usage limit, busy, key rejected, or model retired.
  - After one failure the Explain button **disappeared** for that move. → It now
    comes back as **Try again**. Tested end to end in Streamlit's test mode.
  - Newer versions of the Gemini library **crash the whole app** if the key is
    missing. → Now only the coach stops; the board and engine keep working.
  - Streamlit Cloud installed the **newest version of every package** on each
    update, so an untested upgrade could break a demo. → Versions are now fixed
    to the ones tested on your computer.
  - Tip: if it happens again, Streamlit Cloud → *Manage app* → *Logs* shows lines
    starting `[coach]` with the exact error.
- *A checkmate graded "Blunder".* With two mating moves (Ra8# and Rb8#), the one
  the engine didn't list first was graded Blunder, and mating scores showed −100
  instead of +100. The cause: a sign test that mistook "you just gave mate" for
  "you are mated". → One-line fix, tested.
- *Pushing to GitHub failed:* "certificate … not trusted". Checked: the
  certificate that arrives for github.com is issued by **Fortinet**, a company
  firewall on this network that opens and inspects secure connections. Git
  correctly refuses it, because it can't tell the firewall from an attacker. The
  SSH route is blocked too, and this laptop has no SSH key. → **Not solved on
  this network, on purpose:** turning off git's security check would let anyone
  on the network impersonate GitHub. The commits are safe on the laptop; push them
  from another network (home Wi-Fi or a phone hotspot) with `git push`. Long term:
  ask IT to install the firewall's certificate, or to exempt github.com.

**Step 3a: the mistake detector.** Every bad move now gets one of five kinds,
decided only from the engine's lines and a piece count (pawn 1, knight/bishop 3,
rook 5, queen 9). No AI guessing:

| Kind | Meaning |
|---|---|
| allowed_mate | your move let the opponent force checkmate |
| missed_mate | you had a forced checkmate and missed it |
| lost_material | the engine's line after your move shows you losing material (e.g. a hanging piece) |
| missed_material | the engine's best line won material you didn't take |
| positional | no mate, no material: the problem is the position. We don't say which part, because the engine doesn't tell us |

Tested with one position per kind; all correct. Limit: it only sees about 6
moves ahead.

**Commits (made, not yet pushed; see the GitHub difficulty above):** `8c415ac`
mistake detector + mate fix · `27f5e1b` coach reliability + fixed versions ·
`c842515` and the next commit: this diary.

**State after this part:** Steps 1–2 done and re-verified; 3a done; the coach
fix is ready. **The live app keeps the old behaviour until the commits are
pushed** (Streamlit Cloud rebuilds from GitHub). **Next:** push from another
network; your OK on the Step 3b method; then build the learner model.

### 23 September 2026 (later the same day) — An honest verdict; the learner model built and put to the test

You couldn't reach another network yet, so pushing waits. You asked me to carry
on with what I think should come next, and to judge honestly whether the
results are good enough.

**What we did**
1. **The verdict** (full text in "Is it good enough for a master's thesis?" at
   the top). In short: a strong prototype and first study, but not yet a full
   thesis. The biggest issue is the sample: with 25 cases, "88%" really means
   *70–96%*, so the prompt fix is likely but not proven.
2. **"Chances" added to every move review:** two engine facts about the position
   *before* the move: was there a forced mate, and did the engine's best line win
   material? A "missed" mistake is only possible when a chance was there.
3. **Step 3b, the learner model** (`learner_model.py`). For each mistake kind it
   counts *chances* (moves where that mistake was possible) and *misses* (times
   it happened). Every player starts from a starting guess worth 10 moves, so
   one slip can't label anyone. A kind becomes a **pattern** only when we're 80%
   sure the player's rate is above a bar (e.g. "hangs material on more than 1
   move in 10") **and** it has happened at least 3 times. It's **fine** when
   we're 80% sure the rate is below the bar, and **unsure** in between. The math
   is exact, and was checked against 200,000 random samples.
4. **Step 3d, the test** (`simulate_learners.py`). Four computer "players" play
   like the engine except for one planted weakness (**hangs** pieces, **misses**
   free material, **drifts** with random quiet moves, and **solid**, the control
   with no weakness). Each plays real games against Stockfish, and every move
   goes through the real pipeline. There are 5 players per bot, 40 moves each.

**First results**

| Bot | Weakness found? | Other kinds flagged | Engine agreed with the planted mistake |
|---|---|---|---|
| hangs | **5 of 5**, after about 4 moves | 0 | **44 of 44** |
| misses | 0 of 5 | 0 | 12 of 24 |
| drifts | 0 of 5 | 1 | 34 of 78 |
| solid (control) | correctly nothing | **0** | — |

**Difficulties → how we got past them**
- *My first bots were too crude.* A "safe quiet" move only checked the piece
  that moved, so it often left *another* piece hanging. → The bots now check
  every piece. Even so, the engine still finds losses the simple check can't see
  (pins, forks).
- *"misses" and "drifts" weren't found.* Looking at every move showed the
  learner model was doing its job; the causes were elsewhere:
  - **The plan isn't the move.** 24 of the drifter's "safe" moves really lost
    material, and when the misser skipped a recapture, the opponent often took
    *more*. The engine judges what the move really was, so the planted label
    isn't a clean answer key.
  - **One habit, split across two kinds.** Skipping a recapture was labelled
    "missed material" half the time and "lost material" the other half, so
    neither count reached its bar.
  - **Chances are rare.** Only about 7 chances to win material per 40 moves, so
    a "misses chances" habit needs many games before anyone can be sure.
  - **The bars are guesses.** "Misses more than half its chances" is too
    lenient: the engine itself misses 0%.
  - The one "other kind flagged" was a drifter losing material on 8 of 40
    moves. That's a **real** weakness it showed, not a false alarm.
  - → **Decided not to tune the rules until my own bots pass.** That would be
    marking my own exam. The proper fix is real human games (next point).
- *Real games were blocked.* Lichess publishes all its games for free, which
  would let us set the bars from data and check that weaker players show more
  hung pieces. The company firewall blocks it, just like GitHub. → Next time
  you're on another network.
- *A pattern flickered on and off.* In the first run, "positional" was flagged
  after just 2 moves (2 slips in 2 moves) and vanished later. That breaks the
  model's own rule that a slip or two must not label a player. → New rule:
  **at least 3 mistakes of a kind before it can be called a pattern.** The
  experiment was re-run (below).
- *Re-running cost 15 minutes each time.* → The experiment now saves every
  graded move, so a future change to the model can be re-scored in seconds.

**Re-run with the new rule**

| Bot | Weakness found? | First flagged at move (median) | Other kinds flagged |
|---|---|---|---|
| hangs | **5 of 5** | 9 (was 4) | 0 |
| misses | 0 of 5 | — | 0 |
| drifts | 0 of 5 | — (the move-2 flicker is gone) | 1 (the real material losses) |
| solid (control) | correctly nothing | — | **0** |

- Every game came out **identical** to the first run (same games, same planted
  moves for all 20 players), so the experiment is repeatable.
- Trade-off, chosen on purpose: the model now needs 3 hung pieces before saying
  "habit", so it's slower (move 9 instead of 4) but never jumps to conclusions.
- **What this shows:** the model reliably finds a clear, frequent habit (hanging
  pieces, the classic beginner problem), never labels a clean player, and
  refuses to guess on thin evidence. What it can't do yet is find *rare* habits
  (missed chances) within one 40-move session, or sort overlapping kinds. Both
  need real data to fix properly.

**Commits:** made on the laptop, **not pushed yet** (firewall).

**State at end of day:** Steps 1–2 done; Step 3's detector, learner model and
first simulation test done. The model is not yet in the app. **Next:**
(1) push from another network; (2) on that network, download real Lichess games
to set the bars from data and test the model on real people; (3) show the
learner model in the app (the "open learner model"); (4) only then give it to
the coach, which is a prompt change, so faithfulness is re-measured.

---

# Appendices

## A. How the faithfulness checker works (Step 1)

After Gemini writes an explanation, `faithfulness.py` runs two checks on the text:

1. **Move check.** Every chess move written in the text (`Nf3`, `Bxc6`, `O-O`…)
   must be one the engine gave the coach: the best move, the engine's line, the
   player's move, or the line after it. The allowed list is *exactly* what the
   coach was shown, so a move is flagged even if it's legal and sensible,
   whenever the engine didn't give it.
   - A piece move, capture or castle not on the list → **hard flag** (fails).
   - A bare square ("e5") → **soft note** only (might just be pointing at a square).
2. **Reason check.** A sentence that mentions the score ("+0.42", "advantage",
   "edge") **and** gives a reason ("because", "due to", "comes from"…):
   - no engine move in it → **hard flag** (the reason came from nowhere);
   - an engine move cited → **soft note** (a human should confirm the story).

It is **passive**: it never changes the coach's words. Every check is logged in
`faithfulness_log.jsonl`.

**How we know it works:** its self-test (9 cases); planted lies caught (25/25
moves, 25/25 reasons); agreement with your audit (10/10 found, 0 wrong fails);
same verdict every time (25/25).

**What it can't do:** understand chess claims made in words ("this pins the
knight"); notice a real move said at the wrong time or by the wrong side; hard-flag
an invented pawn move; catch reasons without its trigger words ("…, as your pieces
are developing"); see pieces already on the board (so it can flag a true "your
extra rook").

## B. Key files

| File | What it is |
|---|---|
| `app.py` | The web app (the only entry point) |
| `engine_analysis.py` · `move_review.py` | Engine facts: best move, eval, line · grading a move and naming its mistake kind |
| `explainer.py` | The coach (Gemini): rules, levels, retries |
| `faithfulness.py` | The checker |
| `evaluate_faithfulness.py` | Runs the 25 test cases and writes `faithfulness_eval.md` |
| `faithfulness_records.json` | Latest run's texts + facts (**overwritten** each run) |
| `faithfulness_records_audited.json` | **Frozen** copy of the run you audited. Never overwrite it |
| `faithfulness_audit.md` · `human response.txt` | Your audit sheet · your verdicts |
| `validate_checker.py` | Scores the checker against your audit |
| `learner_model.py` | Step 3: the tutor's running notes on one player (chances, misses, pattern / fine / unsure) |
| `simulate_learners.py` | Step 3d: computer players with planted weaknesses play Stockfish; writes `learner_eval.md` |
| `learner_eval.md` · `learner_eval_records.json` | The simulation's report · every graded move (so a model change can be re-scored with `--rescore`) |

## C. How we work (agreed rules)

- Plain words and short answers; every term explained; one stage at a time.
- **No coach-prompt changes to "fix" a score before you've seen the flagged
  cases.** A low flag count might mean a blind checker, not a faithful coach.
- A step is done only when your review is finished and we've decided together.
- Commits contain only the files that belong to the change; credit is yours.
- You start and restart the app yourself.
- **This diary gets a new entry at the end of every working session**, in the
  same shape: what we did → difficulties and how we got past them → state at end
  of day. The "Where the project stands" section is updated too.

## D. Glossary

| Word | Meaning |
|---|---|
| **Engine** | Stockfish, a chess program far stronger than any human. The source of all chess facts |
| **Eval / score** | The engine's number for who's better, in pawns: +0.50 = the side to move is half a pawn better. It comes with **no reason attached** |
| **Centipawn** | 1/100 of a pawn (50 centipawns = 0.50) |
| **Line** (PV) | The moves the engine expects next with best play. A forecast, not a promise |
| **Refutation** | The engine's line *after the move you played*: how the opponent punishes a bad move |
| **Win chance** | The eval turned into a 0–100% chance of winning (the curve chess.com and Lichess use) |
| **SAN** | The usual way to write a move: `Nf3`, `Bxc6`, `O-O` |
| **FEN** | One line of text describing a whole position |
| **PGN** | The text format for a whole game |
| **LLM** | A language AI (here Gemini). Writes well, but can make up chess facts |
| **Faithful** | The coach's text says nothing the engine's facts don't support |
| **Hard flag / soft note** | Hard = the checker fails the text. Soft = shown to a human, doesn't fail |
| **Planted-lie test** | Deliberately add a lie and check that the checker catches it |
| **Ablation** | Switch one change off and re-measure, to see whether it really helped |
| **Repeatable** (deterministic) | Same input → same output, every time |
| **Learner model** | The tutor's running notes on one player: which mistakes they repeat |
| **Open learner model** | A learner model the player can see (the project brief mentions "open learning models") |
| **Type** (Marcolino's research) | An agent's hidden style or habit, worked out from how it acts. Our analogue: a player's typical mistakes |
| **Bayesian updating** | Start from a sensible starting guess, then adjust it with each piece of evidence, so one slip doesn't label a player |
| **Chance / miss** | A *chance* is a move where a mistake was possible (e.g. there was free material). A *miss* is a chance where the mistake happened |
| **Bar** | The rate we'd call worth coaching, e.g. "hangs material on more than 1 move in 10" |
| **Pattern / fine / unsure** | Pattern = 80% sure the player's rate is above the bar (and it has happened 3+ times). Fine = 80% sure it's below. Unsure = not enough evidence yet |
| **Confidence range** | The range the true value probably lies in. With few cases it's wide: 22/25 = 88%, but really 70–96% |
| **Simulated player (bot)** | A computer player with a weakness we planted on purpose, so we know the right answer when testing the learner model |
