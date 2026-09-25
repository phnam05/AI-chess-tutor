# Related work and baselines: working notes

Started 2026-09-23. Each entry was checked against its abstract or web page on
that date. None has been read in full yet. Anything marked **to verify** is
still unconfirmed and must be checked before citing.

A **baseline** is a simpler method you compare your own method against. It is
what shows that your method actually helps. Reviewers of João's AIIDE paper (in
Dr. Marcolino's lab) called "too few baselines" its one weakness that couldn't
be fixed, so the baselines here are planned from the start.

---

## 1. The closest work: the paper has to say how we differ

**Hebbar, Sheng, Oh, Viswanath (2026). "Hallucinations on the Board:
Tool-Augmented Evaluation of LLM Chess Commentary." arXiv:2608.04240 (Aug 2026).**
- Their method, ACT-Eval, splits a chess commentary into single claims and
  checks each claim with 15+ chess tools, including Stockfish at depth 18.
- They compare 6 language AIs with and without tools. The share of wrong
  claims drops with tools, e.g. Gemini 3.1 Pro **10.8% → 7.5%**, GPT-5.4
  **22.0% → 9.2%**, DeepSeek V4 Pro **36.7% → 14.4%**.
- Data: 325 positions, 125 of them with expert-written "gold" claims.
- Human check: 4 chess players (Lichess 1800–2200) judged 50 claims. The
  automatic judge agreed with each of them 69–83% of the time; the humans
  agreed with each other 73–91%.
- A plain "LLM as judge" (GCC-Eval) missed errors: it gave high relevance
  scores to 39.8% of commentaries that ACT-Eval found were mostly wrong.
- **How we relate:** it's the same core finding (engine facts cut down
  made-up claims) and the same with/without-engine comparison. So a no-engine
  comparison is now *expected* of us, and this is the paper to cite for it.
- **How we differ:** they evaluate *commentary*; we build a *tutor*. Ours has
  explanations at 3 levels, a learner model, and a result they don't study:
  asking the coach for simpler words made it *less* faithful (16/25 vs 22/25).
  Their checker is heavy (a language AI using tools); ours is a light
  rule-based check. A possible experiment: run both checkers on our cases and
  compare them with human judges.
- Their human study (several raters, agreement numbers) is the standard a Q1
  reviewer will hold us to.

**Kim, Goh, Hwang, Cho, Ok (2025). "Bridging the Gap between Expert and
Language Models: Concept-guided Chess Commentary Generation and Evaluation."
NAACL 2025. arXiv:2410.20811.**
- CCC feeds engine results plus chess concepts to a language AI, which writes
  the commentary. GCC-Eval is an LLM-based judge of commentary.
- Reported: GPT-4o solves 57% of mate-in-one puzzles alone, and **95%** when
  the engine's result is in the prompt.
- **Relation:** the same "engine decides, AI phrases" design. So the design
  alone is **not new**. Our novelty has to be *measuring* faithfulness at
  each level, plus adapting to the learner. Their baselines: **to verify**
  (full paper).

**Tang, Wen, Grief-Albert, Elgabra, Yang, Dong, Anderson (2026). "Grounded
Chess Reasoning in Language Models via Master Distillation." arXiv:2603.20510.**
- Trains a small language model (C1-4B) on Stockfish-made reasoning. It's
  the other route: *train* the model to know chess, where we *give* a general
  model the engine's facts at run time. Same group as Maia (Anderson,
  Toronto). Details: **to verify**.

**Sadikov, Možina, Guid, Krivec, Bratko (2007). "Automated Chess Tutor."**
Computers and Games 2006, LNCS 4630, pp. 13–25. Turns a chess engine into a
tutor that comments on moves in terms of goals to reach or keep. It's the
pre-LLM ancestor of our "engine decides, tutor explains" split, so we must
cite it and say what's new. Found by the lab (see section 5). **To read.**

---

## 2. Guessing a player's level from their moves

- **Regan & Haworth (2011). "Intrinsic Chess Ratings." AAAI-11.** A rating
  worked out from the *quality* of the moves (deep engine evals), not from
  game results. Skill parameters are fitted to Elo on large sets of games.
  This is the classic "level from moves" method.
- **Average centipawn loss (ACPL):** the average eval a player loses per
  move. It's the simplest baseline. One study of ten grandmasters' careers
  reports a correlation above 0.98 between ACPL (with its spread) and Elo
  ("Expected Human Performance Behavior in Chess Using Centipawn Loss
  Analysis", HCI in Games 2023, Springer). That's over whole careers; it will
  be much noisier over one game.
- **McIlroy-Young et al. (2020). Maia (KDD)** and **Tang et al. (2024).
  "Maia-2: A Unified Model for Human-AI Alignment in Chess." NeurIPS 2024.**
  Maia-2 is one model covering all skill levels, with a "skill-aware"
  attention part; it predicts human moves about 2 points better than Maia. It
  says how likely a human at a given level is to play each move, which is
  exactly the *P(move | level)* in Dr. Marcolino's Bayesian idea. Its GitHub
  page says new projects should use **Maia-3**. Whether it takes the rating as
  an input, and in which ranges: **to verify** (GitHub is blocked on the
  office network).
- **Chen, Shih, Wu (2025). "Strength Estimation and Human-Like Strength
  Adjustment in Games." ICLR 2025. arXiv:2502.17109.** A "strength estimator"
  that guesses a player's level from their games, plus a way to make an engine
  play at a chosen level like a human. Main tests are in Go, **repeated on
  chess** with the same results. It's the baseline João's AIIDE paper was
  compared against, so it's the natural baseline for us too.
- **Tijhuis, Mavromoustakos Blom, Spronck (2023). "Predicting Chess Player
  Rating Based on a Single Game." IEEE CoG 2023.** Features from one game →
  the player's rating. Chess, and one game: the same setting as our after-game
  review. Also the older **Kaggle "Finding Elo"** contest (2014–15): predict
  both players' Elo from one game; top entries used Stockfish-loss features.
  No formal paper.
- **Kuboki, Ogawa, Hsueh, Yen, Ikeda (2025). "Policies of Multiple Skill
  Levels for Better Strength Estimation in Games." AIIDE 2025.
  arXiv:2505.00279.** Covers
  Go and chess. In Go: **80%** accuracy from 10 games and **92%** from 20
  (the previous best was 71% / 84%). This shows how level estimation is
  usually scored (accuracy given N games), and it's a direct baseline
  candidate.
- **Zhou, Fu, Yang (2026). "Accelerating Skill Assessment in Chess: A
  Drift-Diffusion-Enhanced Elo Rating System." IEEE CoG 2026.
  arXiv:2606.26267.** Uses move-level data so Elo adjusts faster.
- **Carlson (2026). arXiv:2606.25176.** A move model that takes the rating
  into account, plus player-style embeddings, compared against Maia-3. It's
  about *style*, not level: background only.
- **João Marcos et al. (AIIDE 2026)**, from Dr. Marcolino's lab: guessing a
  Go player's rank from their moves. Not findable online yet. **Ask Dr.
  Marcolino for it.** It's our closest level-estimation work, and it shows
  which baselines his group uses.

---

## 3. Proposed baselines for our paper (my proposal, to agree with Dr. Marcolino)

**Part A, faithfulness.** Every condition goes through the same checker and
the same positions.
1. **No engine:** the same Gemini and prompt, given only the board (FEN).
   Expected to invent far more. This is now the standard comparison (Hebbar
   et al. 2026).
2. **Best move only:** no engine line, no eval. Shows *how much* of the
   engine's facts the coach needs. Optional.
3. **Template, no language AI:** fixed sentences filled in with engine facts.
   Faithful by construction but stiff. It's the other end of the
   faithful ↔ readable trade-off.
4. **Checkers compared:** our rule-based checker vs an ACT-Eval-style
   LLM-with-tools checker, both measured against human judges.

**Part B, level guessing.** Each method is scored on real Lichess games
(where every player's real rating is known) by how close its guess is and
how many moves it needs to get there.
1. **Always guess the average rating:** the "knows nothing" floor.
2. **ACPL → rating:** a simple line fitted on the data.
3. **Regan-style intrinsic rating** (if time allows).
4. **The Chen et al. (2025) strength estimator** (ICLR 2025, works on
   chess): the published baseline João's lab already uses.
5. **Maia / Maia-2 + Bayes, updated after every move:** Dr. Marcolino's idea
   and our method.
6. Stretch goal: the Kuboki et al. (2025) method.

**End to end, adaptation:** the explanation level picked from the guessed
level, vs "intermediate" for everyone, vs the level the player says they
are. Judged by readability measures, and in the user study by the players
themselves.

---

## 4. Where to publish (goal: a Q1 journal within about a year)

- **User Modeling and User-Adapted Interaction (UMUAI):** Q1 (Education) on
  SCImago. The best fit for a learner model plus adaptation.
- **International Journal of Artificial Intelligence in Education (IJAIED):**
  Q1. Fits a tutor, and will expect evidence from real learners (a user
  study).
- **IEEE Transactions on Games:** one listing shows SJR 0.285, quartile
  unclear. **Check before targeting.**
- Also check: IEEE Transactions on Learning Technologies, ACM TiiS, Computers
  & Education (very selective, with a high bar for user studies).

Journal reviews take months. For a paper within a year, submission is needed
by about mid-2027, so the user study, and its ethics approval, is on the
critical path.

---

## 5. Found by the lab (João, Fabrício, Dr. Marcolino), not yet read

These were shared in the lab's channel between Oct 2025 and Aug 2026. Titles
were checked on 2026-09-24. This is only what was *posted*; João's own
reference list is bigger, so ask him for it.

**Tutors, and explaining game AI (closest to us)**
- **Lima (2024). "Tutor de Xadrez Adaptativo Guiado por Dados"** ("Data-Driven
  Adaptive Chess Tutor Bot"), University of Aveiro dissertation. An adaptive
  chess tutor, so it could be very close. What it actually does is **not
  confirmed** (no abstract found; the university site didn't load here).
  **Read first.**
- **Zhang, Wang, MacLellan (2025). "(A)I Can Play Gomoku: An Intelligent
  Tutoring System for Strategic Games."** CHI PLAY Companion 2025 (a demo). A
  tutor with hints and after-game review, for Gomoku.
- **Sætra (2022). "Scaffolding Human Champions: AI as a More Competent
  Other."** Human Arenas. Argues from learning theory that game AI can
  support learners, best alongside human coaches.
- **Hammersborg & Strümke (2024).** Explanation methods for chess neural
  networks. Scientific Reports. It explains the network's *insides*; we
  explain its *output* in words.
- **Pálsson (2024). "Explaining intelligent game-playing agents."** PhD
  thesis, Reykjavik University (includes chess).
- **Tomlin, He, Klein (2022).** Go games with human commentary, used to test
  whether Go networks "know" named Go ideas. ACL 2022.
- **Garrett (2023). "Explaining Go: Challenges in Achieving Explainability in
  AI Go Programs."** Journal of Go Studies. A philosophy paper; concludes
  fully explainable Go AI is unlikely.
- Also named: Jhamtani et al. (2018) and Zang et al. (2019) on chess
  commentary; Shin et al. (2021), watching AI moves alone didn't make Go
  players better (the exact paper **to verify**).

**Language AIs that *play* games (a contrast: ours only explains)**
- MasterMind (Wang et al., ICLR 2025 workshop, arXiv:2503.13980): its
  explanations are scored by similarity to human text, not by whether they're
  true. LoGos (Ma et al., NeurIPS 2025, arXiv:2601.16447). Guo et al. (2024,
  arXiv:2403.05632).

**Level**: Chen et al. (2025) and Tijhuis et al. (2023) are in section 2.
Also Coulom (2007), "Elo ratings" of Go move patterns (an old baseline).

Sources: [arXiv 2608.04240](https://arxiv.org/html/2608.04240) ·
[arXiv 2410.20811](https://arxiv.org/abs/2410.20811) ·
[arXiv 2603.20510](https://arxiv.org/pdf/2603.20510) ·
[Regan & Haworth, AAAI 2011](https://ojs.aaai.org/index.php/AAAI/article/view/7951) ·
[ACPL study, HCI in Games 2023](https://link.springer.com/chapter/10.1007/978-3-031-35979-8_19) ·
[Maia-2, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/250190819ff1dda47cd23cecc0c5a69b-Abstract-Conference.html) ·
[arXiv 2505.00279](https://arxiv.org/abs/2505.00279) ·
[arXiv 2606.26267](https://arxiv.org/abs/2606.26267) ·
[arXiv 2606.25176](https://arxiv.org/abs/2606.25176) ·
[UMUAI on SCImago](https://www.scimagojr.com/journalsearch.php?q=18947&tip=sid) ·
[IJAIED on SCImago](https://www.scimagojr.com/journalsearch.php?q=19600156811&tip=sid) ·
[IEEE ToG on SCImago](https://www.scimagojr.com/journalsearch.php?q=21101013582&tip=sid&clean=0)
