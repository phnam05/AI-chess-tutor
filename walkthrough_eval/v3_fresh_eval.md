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
| 1 | Ruy Lopez (after 3...a6) | opening | position | beginner | yes | b5, a6, Ba4, Nf6, e4 | — | — |
| 2 | Italian Game (Giuoco Piano) | opening | position | intermediate | yes | d1, c3, Nf6, e4, c5, d4 | — | — |
| 3 | Sicilian Najdorf | opening | position | advanced | yes | Be3, e5, d4, Nb3, Ng4, g4? | — | — |
| 4 | Queen's Gambit Declined | opening | position | intermediate | yes | e3, h6, g5, Bh4, g7 | — | — |
| 5 | French Defence (Winawer) | opening | position | advanced | yes | e5, c5, d8, b4, a3, Bxc3+, bxc3 | — | — |
| 6 | King's Indian Defence | opening | position | intermediate | yes | Nf3, O-O, Be2 | — | — |
| 7 | Caro-Kann Defence | opening | position | beginner | yes | e5, Bf5, g4 | — | — |
| 8 | Closed centre, Black to plan | middlegame | position | intermediate | yes | a8, f8, Qc7, Bc2 | — | — |
| 9 | Queen on f4, White attacking | middlegame | position | advanced | yes | Be3, Qd5, c4, Bc4, Qxe5, b2 | — | — |
| 10 | Open game, Black to move | middlegame | position | beginner | yes | e4, dxe4, e5, Nxe5, c6? | — | — |
| 11 | King + pawn vs king | endgame | position | beginner | yes | e3, Kf6 | — | — |
| 12 | Rook + pawn endgame | endgame | position | intermediate | yes | h1, Kd2, Ke4 | — | — |
| 13 | Queen vs lone king (mating) | endgame | position | beginner | yes | Kg3+, Kg6 | — | — |
| 14 | Central king & pawn | endgame | position | advanced | yes | Kc3, Kc5, d4+, Kb6 | — | — |
| 15 | Italian: 3.Bb5 (good) | opening | move | beginner | yes | a6, a4, Ba4 | — | — |
| 16 | Opening move 1.e4 (good) | opening | move | beginner | yes | e4, e5, Nf3 | — | — |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | intermediate | yes | a6, b5, Nf6, e4, O-O | — | — |
| 18 | Develop with ...Be7 (mistake) | middlegame | move | intermediate | yes | Be7, e5, Nxe5, O-O, c6, Bxc6, bxc6, Nxc6, e4, dxe4 | — | — |
| 19 | Scotch: ...exd4 (good) | opening | move | intermediate | yes | d4, Nxd4, Nf6, Nxc6, dxc6 | — | — |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | beginner | yes | Nf6, f7, Qxf7#, g6 | — | — |
| 21 | ...Nxe4? loses material (mistake) | middlegame | move | intermediate | yes | e4, d3, f2, Nxf2, Bxc6+, bxc6, dxe4 | — | — |
| 22 | Wing push 1.a4 (passive) | opening | move | beginner | yes | a1, a4, e5, e4 | — | — |
| 23 | Edge push 1.h4 (passive) | opening | move | beginner | yes | h1, h4, d5, c8, d8, d4, d1, c1, e4, f1 | — | — |
| 24 | Premature 3.Ng5?? (blunder) | opening | move | advanced | yes | Ng5, Qxg5, d4, c1, Qg6, e4, dxe5, Bb5, a6 | — | — |
| 25 | Passive 2.Na3 (good) | opening | move | intermediate | yes | Na3, e6, f3, a6 | — | — |

## Explanations

**1. Ruy Lopez (after 3...a6)** (position, beginner) — engine: Ba4

> Your bishop on b5 is currently under attack by the pawn on a6, so a natural idea is to keep it safe by moving it. That is why your best reply is Ba4. Your opponent's strongest answer is probably ...Nf6, which brings their knight into play and attacks your pawn on e4. The current evaluation is +0.42, which favors you. How would you choose to protect your pawn on e4 after that move?

**2. Italian Game (Giuoco Piano)** (position, intermediate) — engine: c3

> You have a slight edge here with an evaluation of +0.20 for White. Since you want to open a line for your queen on d1, a natural idea is to push the c-pawn, so your best reply is c3. Your opponent's strongest answer is probably ...Nf6, which brings their knight into play from its starting square while attacking your pawn on e4. To challenge their position by attacking their bishop on c5 with a pawn that is worth less, your best move is d4. How do you think the center will shape up after these pieces are exchanged?

**3. Sicilian Najdorf** (position, advanced) — engine: Be3

> Bringing your bishop into play from its starting square also opens a line for your queen, so a natural idea is Be3. Your opponent's strongest answer is probably ...e5, which attacks your knight on d4 with a pawn. Moving your knight away from the attack by the pawn on e5 opens lines for your queen and your bishop, so your best reply is Nb3. Your opponent will likely play ...Ng4, which opens a line for their queen. The evaluation is +0.51, favoring White. How would you choose to challenge that knight on g4?

**4. Queen's Gambit Declined** (position, intermediate) — engine: e3

> You have the opportunity to open lines for your queen and your light-squared bishop, so a natural idea is e3. The evaluation is +0.31, which means you are slightly ahead. Your opponent's strongest answer is probably ...h6, which attacks your bishop on g5 with a pawn of lesser value. To move your bishop away from that attack, your best reply is Bh4, although note that Black could then choose to attack it again by pushing the pawn on g7 to g5. How do you think you should handle that potential pressure on your bishop?

**5. French Defence (Winawer)** (position, advanced) — engine: e5

> The evaluation is +0.64, favoring you. Since there is no specific board fact for your next step, a natural idea is simply e5. Your opponent's strongest answer is probably ...c5, which opens a line for their queen on d8. To challenge the bishop on b4 with a pawn of lower value, your best reply is a3. Your opponent will likely respond with ...Bxc3+, which gives check while moving the bishop away from your pawn. Finally, to get your king out of check and capture the bishop, your best move is bxc3. How would you like to build your development from this structure?

**6. King's Indian Defence** (position, intermediate) — engine: Nf3

> You want to bring your knight into play from its starting square, so a natural idea is Nf3. The current evaluation is +0.65, which favors you. Your opponent will likely castle kingside, moving their king away from the center while bringing a rook toward the middle with ...O-O. To continue developing your bishop from its starting square, you should play Be2. How do you feel about the position of your pieces now?

**7. Caro-Kann Defence** (position, beginner) — engine: e5

> The evaluation is +0.30, which means White is ahead. A natural idea for your turn is to advance your pawn, so your best reply is e5. Your opponent's strongest answer is probably to bring their bishop into play [ ...Bf5 ], which gives you a chance to chase it away by moving your pawn to g4. What do you think about challenging their position this way?

**8. Closed centre, Black to plan** (position, intermediate) — engine: Qc7

> The evaluation is -4.79, so White is currently ahead. Since moving the queen opens lines for your rooks on a8 and f8, a natural idea is to reposition the queen, so your best reply is ...Qc7. Your opponent's strongest answer is probably Bc2. How do you think these new lines will affect your strategy moving forward?

**9. Queen on f4, White attacking** (position, advanced) — engine: Be3

> Bringing your bishop into play and opening a line for your rook is a priority, so a natural idea is Be3. The evaluation is +2.68, which favors you. Your opponent's strongest answer is probably ...Qd5, which gives you an opportunity to attack the queen by pushing your pawn to c4. To continue, developing your bishop to target their queen is effective, so your best reply is Bc4. Your opponent will likely respond with ...Qxe5 to capture your pawn and pressure your b2 square. How do you plan to handle this developing pressure on your queenside?

**10. Open game, Black to move** (position, beginner) — engine: dxe4

> You can capture White's pawn on e4 and attack their knight at the same time, so a natural idea is to trade pawns. That's why your best reply is ...dxe4. Your opponent will likely move their knight to e5 to capture your pawn and open a line for their queen (Nxe5). The evaluation is -0.87, which means White is ahead. How do you think you should handle the pressure on your knight at c6?

**11. King + pawn vs king** (position, beginner) — engine: e3

> The evaluation is +5.11, which shows you are ahead. Since there is no specific purpose to point out for this move, your best reply is e3. Your opponent's strongest answer is probably ...Kf6. How would you plan to move your pieces forward from here?

**12. Rook + pawn endgame** (position, intermediate) — engine: Kd2

> The current evaluation is +6.30, which favors you. Since you can open a line for your rook on h1, a natural idea is to move your king. That is why your best reply is Kd2. Your opponent's strongest answer is probably ...Ke4. How do you plan to coordinate your pieces once your rook is free to move?

**13. Queen vs lone king (mating)** (position, beginner) — engine: Kg3+

> You want to open a line for your queen and put the black king in check, so your best move is [Kg3+]. The evaluation is +5.09, which means you are ahead. Your opponent will likely try to get their king out of check and away from your queen by playing [...Kg6]. How do you think you can continue to pressure their king after that?

**14. Central king & pawn** (position, advanced) — engine: Kc3

> The evaluation is +0.44, which favors you. Since there are no specific tactical requirements for your king, a natural idea is simply repositioning, so your best reply is Kc3. Your opponent's strongest answer is probably ...Kc5. You can then advance your pawn to force a response, so your best follow-up is d4+. Your opponent will likely move ...Kb6 to get their king out of check and away from the attack. How do you plan to restrict their king's mobility after this?

**15. Italian: 3.Bb5 (good)** (move, beginner) — engine: played Bb5 / best Bb5 (Best)

> That was a great choice because it brings your bishop into play from its starting square. The evaluation is +0.44, which means you are ahead. 

Your opponent will likely push their pawn to a6 (...a6), which attacks your bishop with a pawn of lower value. To get your bishop out of the way of that attack, your best reply is to move it to a4 (Ba4). 

What do you think will happen if your opponent continues to chase your bishop after that?

**16. Opening move 1.e4 (good)** (move, beginner) — engine: played e4 / best e4 (Best)

> You chose a great opening move by opening lines for your queen and bishop (e4). The current evaluation is +0.35, which favors you. Your opponent will likely challenge your control of the center by opening lines for their queen and bishop (...e5). Since your knight can attack their pawn on e5, a natural idea is to develop your knight into play, so your best reply is Nf3. How would you plan to defend your center if they decide to chase your knight away?

**17. Ruy Lopez: 4.Ba4 (good)** (move, intermediate) — engine: played Ba4 / best Ba4 (Best)

> You moved your bishop to avoid the attack from the pawn on a6, though keep in mind that Black can challenge that bishop again by pushing the pawn to b5. The evaluation is +0.48, which means White is ahead. Your opponent will likely play ...Nf6 to bring their knight into play and attack your undefended pawn on e4. To secure your king and bring a rook into the game, your best reply is O-O. Your opponent's strongest answer is probably ...b5, which attacks your bishop with a pawn. How do you plan to handle the pressure on your bishop once Black pushes that pawn?

**18. Develop with ...Be7 (mistake)** (move, intermediate) — engine: played Be7 / best dxe4 (Mistake)

> You brought your bishop into play with ...Be7, but this move was a mistake. The evaluation is -2.42, which means White is ahead. Your opponent will likely capture your pawn on e5 with Nxe5, opening a line for their queen. You should then secure your king by castling with ...O-O. Your opponent will likely challenge your knight on c6 with Bxc6, and you will respond by recapturing with ...bxc6. Finally, White will likely strike back with Nxc6, attacking your queen with their knight. It would have been stronger to capture the pawn on e4 to challenge the knight and open the queen's line with ...dxe4. What do you think about the pressure building on the c6 square?

**19. Scotch: ...exd4 (good)** (move, intermediate) — engine: played exd4 / best exd4 (Best)

> You made a great choice by capturing White's pawn on d4. The evaluation is -0.42, which means White is ahead. Your opponent will likely recapture by playing Nxd4 to open a line for their queen. To develop your forces and challenge White's central pawn, your best reply is ...Nf6. Your opponent might then choose to play Nxc6, which attacks your queen and captures your knight. You should respond by playing ...dxc6, which captures their knight while opening lines for your bishop and queen. How do you feel about the way these exchanges are reshaping the center?

**20. Scholar's mate trap: ...Nf6?? (blunder)** (move, beginner) — engine: played Nf6 / best g6 (Blunder)

> You brought your knight [Nf6] into play, but it also placed your king in a difficult position. The evaluation is -100.00, which heavily favors White. White will likely play queen to f7 [Qxf7#], which delivers checkmate. You could have challenged their queen by moving your pawn [g6] instead; how do you think we can better protect the f7 square next time?

**21. ...Nxe4? loses material (mistake)** (move, intermediate) — engine: played Nxe4 / best dxe4 (Mistake)

> By capturing the pawn on e4, you have opened a line for your queen, but you have also invited your opponent to challenge your knight. The current evaluation is -2.47, meaning White is ahead. Your opponent will likely play d3 to attack your knight with their pawn. To respond, you should aim to capture the pawn on f2 and attack their queen, so your best reply is ...Nxf2. Your opponent's strongest answer is probably Bxc6+, putting your king in check. You must get your king out of check by playing ...bxc6. How do you think this sequence changes the activity of your pieces compared to playing ...dxe4 to attack their knight?

**22. Wing push 1.a4 (passive)** (move, beginner) — engine: played a4 / best e4 (Inaccuracy)

> You opened a line for your rook on a1 with your move [a4]. The current evaluation is -0.32, which means Black is now ahead.

Your opponent's strongest answer is probably to move their pawn to [e5], which opens lines for their queen and bishop. You should then move your pawn to [e4] to open lines for your queen and bishop. Since the best move was to open lines for your queen and bishop by playing [e4], how do you think your choice compares to that?

**23. Edge push 1.h4 (passive)** (move, beginner) — engine: played h4 / best e4 (Mistake)

> You opened a line for your rook on h1 by moving your pawn [h4]. The evaluation is -0.43, which means Black is currently ahead. Your opponent will likely play the pawn to d5 [...d5] to open lines for their bishop on c8 and their queen on d8. You should then move your pawn to d4 [d4] to open lines for your queen on d1 and your bishop on c1. You might have preferred playing the pawn to e4 [e4] to open lines for your queen on d1 and your bishop on f1, but how do you think your current position might change after the next few moves?

**24. Premature 3.Ng5?? (blunder)** (move, advanced) — engine: played Ng5 / best Bb5 (Blunder)

> Your move Ng5 allows Black to capture your knight, although it does open a line for your queen. The evaluation is -4.00, meaning Black is now ahead. Your opponent's strongest answer is probably ...Qxg5, which captures your knight. You should then play d4, which opens a line for your bishop on c1. Your opponent will likely respond with ...Qg6, which moves the queen away from your bishop's attack while targeting your e4 pawn. You should follow with dxe5, which captures their pawn. You might consider how this position differs from the one created by Bb5, which would have developed your bishop while inviting a pawn attack on a6.

**25. Passive 2.Na3 (good)** (move, intermediate) — engine: played Na3 / best Nf3 (Good)

> You did a nice job bringing your knight into play from its starting square with Na3. The evaluation is +0.06, which means you are currently ahead. Your opponent will likely play ...e6 to open lines for their queen and bishop. To continue your development, you should move your other knight to f3, which brings your knight into play from its starting square. Your opponent might then follow up with ...a6. Since you wanted to develop your kingside, would you consider how your next few moves could control the center?
