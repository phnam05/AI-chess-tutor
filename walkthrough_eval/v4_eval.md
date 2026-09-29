# Faithfulness evaluation

**25 of 25 explanations (100%) passed both checks: every move they named was one the engine produced, and no sentence asserted a cause for the evaluation the engine didn't back.**

Each explanation was produced by the real coach (Stockfish facts → Gemini prose) and checked by `faithfulness.check_faithfulness`.

This is a single run. The engine facts are deterministic, but the coach (Gemini) is not — so the rate moves run to run and a different handful of cases flags each time. Across repeated runs it sits near 88% (e.g. 22/25); read the number as a sample of that rate, not a fixed score. The residual flags are invented *causes* for the evaluation, the known limit a string checker and a prompt guardrail can reduce but not eliminate.

## What this measures — and what it does not

This is an automatic, string-based check with two parts. The *move* check reads the moves the coach named in notation (e.g. `Nf3`, `Bxc3+`, `O-O`) and confirms each was a move the engine actually gave — its best move, its principal variation, or (for a graded move) its refutation line. The *eval-causality* check — added after the 2026-07-03 human audit found invented reasons were the dominant failure — reads sentences that both name the evaluation and assert a cause for it. Its scope is deliberate:

- **Catches** invented piece moves, captures, checks and mates — the attention-grabbing hallucination ("you can play Nxe5, forking the king").
- **Catches** invented *reasons* for the evaluation ("the edge comes from your active pieces") when the sentence cites no engine move at all; a causal sentence that does cite a grounded move is reported as *unverified* rather than failed, because the audit saw that kind be right.
- **Does not hard-flag** a bare pawn push written as a square (e.g. `c3`, `h4`): the coach may simply be pointing at a square, so these are reported as *unverified* rather than failed, to avoid false alarms.
- **Does not check** other verbal claims ("this pins the knight") or whether a move's stated *purpose* matches the engine's line.

These limits are validated two ways: a *positive control* (planting fake piece-moves in real explanations confirms the check flags them) and a *human audit* (how often this automatic verdict agrees with a person's judgement — see `validate_checker.py`, which scores the eval-causality check against the audited 25 cases).

| # | Position | Phase | Type | Level | Faithful | Grounded moves | Invented | Eval-causal claim |
|--:|----------|-------|------|-------|:--------:|----------------|----------|-------------------|
| 1 | Ruy Lopez (after 3...a6) | opening | position | beginner | yes | a6, Ba4, Nf6, e4 | — | — |
| 2 | Italian Game (Giuoco Piano) | opening | position | intermediate | yes | c3, Nf6, e4, d4 | — | — |
| 3 | Sicilian Najdorf | opening | position | advanced | yes | Be3, e5, b3, Ng4, g4? | — | — |
| 4 | Queen's Gambit Declined | opening | position | intermediate | yes | e3, h6, Bh4, g7, g5? | — | — |
| 5 | French Defence (Winawer) | opening | position | advanced | yes | e5, c5, d8, b4, a3, Bxc3+, bxc3, c1? | — | — |
| 6 | King's Indian Defence | opening | position | intermediate | yes | Nf3, O-O, Be2 | — | — |
| 7 | Caro-Kann Defence | opening | position | beginner | yes | e5, Bf5 | — | — |
| 8 | Closed centre, Black to plan | middlegame | position | intermediate | yes | Qc7, Bc2 | — | — |
| 9 | Queen on f4, White attacking | middlegame | position | advanced | yes | Be3, Qd5, Bc4, Qxe5, b2 | — | — |
| 10 | Open game, Black to move | middlegame | position | beginner | yes | e4, d5, dxe4, e5, Nxe5 | — | — |
| 11 | King + pawn vs king | endgame | position | beginner | yes | e2, e3, f6, Kf6 | — | — |
| 12 | Rook + pawn endgame | endgame | position | intermediate | yes | Kd2, Ke4 | — | — |
| 13 | Queen vs lone king (mating) | endgame | position | beginner | yes | Kg3+, Kg6 | — | — |
| 14 | Central king & pawn | endgame | position | advanced | yes | Kc3, Kc5, d4+, d4, Kb6 | — | — |
| 15 | Italian: 3.Bb5 (good) | opening | move | beginner | yes | Bb5, a6, Ba4 | — | — |
| 16 | Opening move 1.e4 (good) | opening | move | beginner | yes | e4, e5, Nf3 | — | — |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | intermediate | yes | a6, f6, e4, O-O, b5 | — | — |
| 18 | Develop with ...Be7 (mistake) | middlegame | move | intermediate | yes | e7, e5, Nxe5, O-O, e4, f3, dxe4 | — | — |
| 19 | Scotch: ...exd4 (good) | opening | move | intermediate | yes | d4, Nxd4, e4, Nf6, Nxc6, dxc6 | — | — |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | beginner | yes | f6, Nf6, f7, Qxf7#, g6 | — | — |
| 21 | ...Nxe4? loses material (mistake) | middlegame | move | intermediate | yes | e4, d3, Nxf2, dxe4 | — | — |
| 22 | Wing push 1.a4 (passive) | opening | move | beginner | yes | a4, a1, e5, e4 | — | — |
| 23 | Edge push 1.h4 (passive) | opening | move | beginner | yes | h4, d5, d4, e4 | — | — |
| 24 | Premature 3.Ng5?? (blunder) | opening | move | advanced | yes | g5, Qxg5, d2, d4, b5 | — | — |
| 25 | Passive 2.Na3 (good) | opening | move | intermediate | yes | e6, Nf3, a6, g1, f3 | — | — |

## Explanations

**1. Ruy Lopez (after 3...a6)** (position, beginner) — engine: Ba4

> The bishop is currently under attack by the pawn on a6, so a natural idea is to move your bishop to safety. That is why your best reply is Ba4. Your opponent's strongest answer is probably ...Nf6, which brings their knight into play and attacks your pawn on e4. The evaluation is +0.42, which favors you. How would you plan to defend your pawn on e4 after that knight move?

**2. Italian Game (Giuoco Piano)** (position, intermediate) — engine: c3

> You are currently ahead with an evaluation of +0.20 for White. Opening a path for your queen and preparing to support a push to the center are your priorities, so your best reply is c3. Your opponent will likely respond with ...Nf6 to develop their knight while attacking your pawn on e4. By pushing your pawn to the center to attack their bishop and open lines for your queen and bishop, your best move is d4. How do you think the board will look after those pieces start trading in the center?

**3. Sicilian Najdorf** (position, advanced) — engine: Be3

> Your bishop is currently restricted at home, so a natural idea is to develop it to an active square. That is why your best reply is Be3. Your opponent's strongest answer is probably ...e5, putting a pawn in the center while putting your knight under fire. To address the threat to your knight, you should retreat to b3. Your opponent will likely respond with ...Ng4, which directs pressure toward your bishop. The evaluation is +0.51 in White's favor; how do you think you should handle that knight on g4?

**4. Queen's Gambit Declined** (position, intermediate) — engine: e3

> You have an opening that grants your queen and bishop more room to move, so your best reply is e3. The evaluation is +0.31, which means you are slightly ahead. Your opponent’s strongest answer is probably ...h6 to challenge your piece. Since your bishop is currently under fire, moving it to safety is a good idea, so your best response is Bh4. What do you think your next move should be if they push their pawn on g7 to g5?

**5. French Defence (Winawer)** (position, advanced) — engine: e5

> To build a central outpost for your pawn, your best move is e5. The evaluation is +0.64, favoring you. Your opponent will likely play ...c5 to open a path for their queen on d8. To challenge the bishop on b4 while clearing a file for your rook, you should play a3. Your opponent’s strongest answer is probably ...Bxc3+, which checks your king and moves their bishop. To escape the check and capture that bishop, your best reply is bxc3. How do you feel about the resulting structure for your bishop on c1?

**6. King's Indian Defence** (position, intermediate) — engine: Nf3

> The evaluation is +0.65, which means the position currently favors you. Since you want to bring your knight into play from its starting square, your best move is Nf3. Your opponent will likely castle kingside by playing ...O-O, which moves their king away from the center and brings a rook toward the middle. To continue your development by bringing your bishop into play from its starting square, you should play Be2. How do you feel about the balance of pieces on the board right now?

**7. Caro-Kann Defence** (position, beginner) — engine: e5

> You can move your pawn to the center to escape the attack from Black's pawn, so your best move is e5. The current evaluation is +0.30, which favors you. Black will likely bring their bishop into play by moving ...Bf5. How do you think you can respond to that bishop?

**8. Closed centre, Black to plan** (position, intermediate) — engine: Qc7

> The evaluation is -4.79, which favors White. You should place your queen on a new square, so a natural idea is ...Qc7. Your opponent will likely reposition their bishop by playing Bc2. What do you think about how these pieces will influence the center as the game continues?

**9. Queen on f4, White attacking** (position, advanced) — engine: Be3

> You can improve the activity of your bishop by moving it to its most influential diagonal, so your best reply is Be3. The evaluation is +2.68, favoring you. Your opponent's strongest answer is probably ...Qd5, where they challenge your central control. To capitalize on the fact that you can attack this queen, a natural idea is to re-deploy your bishop to a more aggressive post, so your best move is Bc4. Your opponent will likely respond with ...Qxe5 to capture your pawn and pressure your queenside. How do you plan to handle the tension developing on your b2-pawn?

**10. Open game, Black to move** (position, beginner) — engine: dxe4

> You capture the pawn on e4 and attack the white knight with your pawn on d5, so a natural idea is taking (dxe4). The evaluation is -0.87, which favors you as Black. Your opponent's strongest answer is probably moving the knight to capture your pawn on e5 (Nxe5). How do you feel about the position now that the center has opened up?

**11. King + pawn vs king** (position, beginner) — engine: e3

> The evaluation is +5.11, so it favors you. You should start by pushing the pawn on e2 to e3 (e3). Your opponent's strongest answer is probably moving their king to f6 (...Kf6). How do you think you will proceed from here?

**12. Rook + pawn endgame** (position, intermediate) — engine: Kd2

> The evaluation is +6.30, which favors you. You should focus on bringing your king closer to the center, so your best reply is Kd2. Your opponent will likely respond with ...Ke4. How do you plan to use your active king to make progress from here?

**13. Queen vs lone king (mating)** (position, beginner) — engine: Kg3+

> Your king is currently in front of your queen, so you can move your king to the side to open a line for your queen to attack. That is why your best move is Kg3+ (Kg3+). Your opponent's strongest answer is probably ...Kg6 (...Kg6), which moves their king to safety. The evaluation is +5.09, which favors you. Can you see how moving your king creates a new path for your pieces to work together?

**14. Central king & pawn** (position, advanced) — engine: Kc3

> The evaluation is +0.44, which favors White. You should start by moving your king, so your best reply is Kc3. Your opponent's strongest answer is probably ...Kc5. Pushing your pawn to the center creates a check, so a natural idea is d4+. Your opponent will likely move the king away from the attack by your pawn on d4 with ...Kb6. How do you see the game unfolding from this position?

**15. Italian: 3.Bb5 (good)** (move, beginner) — engine: played Bb5 / best Bb5 (Best)

> Your bishop now comes into play from its starting square, so a great way to develop is Bb5. The evaluation is +0.44, which means you are slightly ahead. Your opponent’s strongest answer is probably ...a6, which attacks your bishop with a pawn and opens a line for their rook. To keep your piece safe from that pawn, your best reply is Ba4. How do you think your bishop will be placed after you move it to that new square?

**16. Opening move 1.e4 (good)** (move, beginner) — engine: played e4 / best e4 (Best)

> By pushing your pawn to e4, you control the center and open paths for your queen and bishop. The evaluation is +0.35, which favors you. Your opponent will likely play ...e5 to match your control of the center. Because your knight attacks the pawn on e5, a natural idea is to develop that piece, so your best reply is Nf3. What do you think your opponent might do next if you follow through with that plan?

**17. Ruy Lopez: 4.Ba4 (good)** (move, intermediate) — engine: played Ba4 / best Ba4 (Best)

> You moved your bishop to safety because the pawn on a6 was threatening it, so this was a solid choice. The current evaluation is +0.48, which means you are ahead. Your opponent will likely respond by bringing their knight to f6 to challenge your pawn on e4. You should then secure your king and develop your rook by castling, so your best reply is O-O. Your opponent will likely push their pawn to b5 to attack your bishop and clear a path for their own bishop. How would you plan to deal with that pawn push?

**18. Develop with ...Be7 (mistake)** (move, intermediate) — engine: played Be7 / best dxe4 (Mistake)

> By developing your bishop to e7, you bring that piece into play from its starting square. The evaluation is -2.42, which means White is ahead. Your opponent will likely capture the pawn on e5 to open a line for their queen with Nxe5. You can then castle kingside to move your king to safety with ...O-O. Instead, capturing the pawn on e4 to attack the knight on f3 would have been ...dxe4. How do you think you can improve your piece coordination after the king moves to safety?

**19. Scotch: ...exd4 (good)** (move, intermediate) — engine: played exd4 / best exd4 (Best)

> By capturing the pawn on d4, you have opened the center, and it is a strong move. The evaluation is -0.42, which means White is ahead. Your opponent will likely play Nxd4 to take back your pawn and open a line for their queen. To develop your piece and apply pressure to the pawn on e4, your best reply is ...Nf6. Your opponent might then play Nxc6 to capture your knight and attack your queen, so you should respond by playing ...dxc6 to capture their knight and open lines for your bishop and queen. How do you feel about the trade of knights that might occur here?

**20. Scholar's mate trap: ...Nf6?? (blunder)** (move, beginner) — engine: played Nf6 / best g6 (Blunder)

> By moving your knight from its starting square to f6 [...Nf6], you have left the f7 pawn vulnerable to White's pieces. The current evaluation is a forced checkmate for White. White will likely use their queen to capture the pawn on f7 [Qxf7#], which ends the game immediately. You might have considered playing ...g6 instead to push the pawn and attack White's queen.

**21. ...Nxe4? loses material (mistake)** (move, intermediate) — engine: played Nxe4 / best dxe4 (Mistake)

> By taking the pawn on e4, you open a line for your queen. The evaluation is -2.47, favoring White. Your opponent's strongest answer is probably d3, which attacks your knight and opens lines for their pieces. To move your knight out of that attack, your best reply is ...Nxf2. You could have instead captured the knight by playing ...dxe4. What do you think you missed before capturing that pawn?

**22. Wing push 1.a4 (passive)** (move, beginner) — engine: played a4 / best e4 (Inaccuracy)

> Pushing the pawn on a4 opens a line for your rook on a1. The evaluation is -0.32, which means Black is ahead. 

Your opponent's strongest answer is probably ...e5, as this puts a pawn in the centre on e5. To challenge that, a natural idea is to take control of the center by moving your pawn to e4. That is why your best reply is e4. 

Instead of pushing the pawn on a4, putting a pawn in the centre on e4 would have been your best move. What do you think about fighting for the center immediately?

**23. Edge push 1.h4 (passive)** (move, beginner) — engine: played h4 / best e4 (Mistake)

> By pushing the pawn on h4, you open a path for your rook to move out, so a natural idea is h4. The evaluation is -0.43, meaning Black is ahead. Your opponent's strongest answer is probably to put a pawn in the center on d5 (...d5). Then, you should put a pawn in the center on d4 to open paths for your bishop and queen, so your best reply is d4. You could have instead put a pawn in the center on e4 to open lines for your queen and bishop by playing e4. What do you think about the space you created for your rook?

**24. Premature 3.Ng5?? (blunder)** (move, advanced) — engine: played Ng5 / best Bb5 (Blunder)

> By moving your knight to g5, you opened a path for your queen, but you left the piece undefended. The evaluation is -4.00, favoring Black. Your opponent will likely respond by capturing your knight with ...Qxg5. You should then push the pawn on d2 to d4 to bring your bishop into the fight, which is the best way to handle the situation after your mistake. You might consider how the game would look if you had developed your bishop to b5 instead.

**25. Passive 2.Na3 (good)** (move, intermediate) — engine: played Na3 / best Nf3 (Good)

> You brought your knight into play, which is a solid way to start developing your pieces. The evaluation is +0.06, which means you are slightly ahead. Your opponent will likely open lines for their queen and bishop by moving ...e6. You should then continue your development by bringing your knight to the center, so your best reply is Nf3. Finally, your opponent will likely open a path for their rook by playing ...a6. Since you wanted to get pieces out, consider why you chose to lead with the knight on the a-file instead of moving the knight on g1 to f3 first.
