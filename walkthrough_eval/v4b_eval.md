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
| 2 | Italian Game (Giuoco Piano) | opening | position | intermediate | yes | d4, c3, Nf6, e4 | — | — |
| 3 | Sicilian Najdorf | opening | position | advanced | yes | Be3, e5, Nb3, Ng4 | — | — |
| 4 | Queen's Gambit Declined | opening | position | intermediate | yes | e3, h6, h4, g5? | — | — |
| 5 | French Defence (Winawer) | opening | position | advanced | yes | e5, c5, b4, a3, Bxc3+, bxc3 | — | — |
| 6 | King's Indian Defence | opening | position | intermediate | yes | Nf3, O-O, Be2 | — | — |
| 7 | Caro-Kann Defence | opening | position | beginner | yes | e4, d5, e5, Bf5 | — | — |
| 8 | Closed centre, Black to plan | middlegame | position | intermediate | yes | Qc7, Bc2 | — | — |
| 9 | Queen on f4, White attacking | middlegame | position | advanced | yes | Be3, Qd5, c2, d5, Bc4, Qxe5, b2 | — | — |
| 10 | Open game, Black to move | middlegame | position | beginner | yes | e4, f3, dxe4, e5, Nxe5 | — | — |
| 11 | King + pawn vs king | endgame | position | beginner | yes | e3, f6, Kf6 | — | — |
| 12 | Rook + pawn endgame | endgame | position | intermediate | yes | Kd2, Ke4 | — | — |
| 13 | Queen vs lone king (mating) | endgame | position | beginner | yes | g3, Kg3+, g6, Kg6 | — | — |
| 14 | Central king & pawn | endgame | position | advanced | yes | c3, Kc5, d4+, b6 | — | — |
| 15 | Italian: 3.Bb5 (good) | opening | move | beginner | yes | Bb5, a6, Ba4 | — | — |
| 16 | Opening move 1.e4 (good) | opening | move | beginner | yes | e4, e5, Nf3 | — | — |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | intermediate | yes | a6, Nf6, e4, O-O, a4, b5 | — | — |
| 18 | Develop with ...Be7 (mistake) | middlegame | move | intermediate | yes | Nxe5, O-O, e4 | — | — |
| 19 | Scotch: ...exd4 (good) | opening | move | intermediate | yes | d4, Nxd4, e4, Nf6, Nxc6, dxc6, c6? | — | — |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | beginner | yes | f6, Nf6, e4, f7, Qxf7#, g6 | — | — |
| 21 | ...Nxe4? loses material (mistake) | middlegame | move | intermediate | yes | e4, d2, d3, f2, dxe4, f3 | — | — |
| 22 | Wing push 1.a4 (passive) | opening | move | beginner | yes | a4, a1, e5, e4 | — | — |
| 23 | Edge push 1.h4 (passive) | opening | move | beginner | yes | h1, h4, d5, d4, e4 | — | — |
| 24 | Premature 3.Ng5?? (blunder) | opening | move | advanced | yes | g5, Qxg5, d4, c1, Bb5 | — | — |
| 25 | Passive 2.Na3 (good) | opening | move | intermediate | yes | e6, Nf3, a6, f3 | — | — |

## Explanations

**1. Ruy Lopez (after 3...a6)** (position, beginner) — engine: Ba4

> Your bishop is being challenged by the pawn on a6, so a natural idea is to move it to safety. That is why your best reply is Ba4. The evaluation is +0.42, which favors you. Your opponent's strongest answer is probably ...Nf6, which brings the knight into play and puts your pawn on e4 under pressure. How would you like to protect that pawn?

**2. Italian Game (Giuoco Piano)** (position, intermediate) — engine: c3

> You are currently ahead with an evaluation of +0.20 for White. By opening a path for your queen and setting up your pawn to control the d4 square, your best reply is c3. Your opponent will likely play ...Nf6 to develop their knight while targeting your pawn on e4. You should then occupy the center and strike at their bishop by playing d4. How do you think their next response might shift the tension in the center?

**3. Sicilian Najdorf** (position, advanced) — engine: Be3

> Your bishop is currently stuck, so a natural idea is to bring it into play to develop your position. That's why your best reply is Be3. The evaluation is +0.51, favoring White. Your opponent's strongest answer is probably ...e5, which controls the center and threatens your knight. To avoid the threat, a natural idea is to reposition your knight to a safer square. That's why your best reply is Nb3. Your opponent will likely respond with ...Ng4, which puts pressure on your bishop. How would you choose to react to that knight move?

**4. Queen's Gambit Declined** (position, intermediate) — engine: e3

> You open paths for your queen and bishop by moving your pawn to e3. The evaluation is +0.31, which favors you. Your opponent will likely challenge your bishop by playing ...h6. To keep your piece safe from that pawn, you retreat your bishop to h4. How do you think the board will change if your opponent decides to push their pawn to g5?

**5. French Defence (Winawer)** (position, advanced) — engine: e5

> By placing a pawn in the center, you strengthen your position, so your best move is e5. The current evaluation is +0.64 in favor of White. Your opponent's strongest answer is probably ...c5, which opens a line for their queen. To attack the bishop on b4 with your pawn, your best reply is a3. Your opponent will likely play ...Bxc3+ to capture your knight while delivering a check. To remove your king from check and take the bishop, your best move is bxc3. Does this sequence change how you view the tension in the center?

**6. King's Indian Defence** (position, intermediate) — engine: Nf3

> Developing your knight from its starting square helps you control the center, so your best move is Nf3. Your opponent will likely castle kingside by playing ...O-O, which moves their king to safety and brings a rook toward the center. Finally, you can continue to develop your bishop from its starting square with Be2. The current evaluation is +0.65, which means you have a slight advantage. How do you think these pieces will work together once they are fully developed?

**7. Caro-Kann Defence** (position, beginner) — engine: e5

> You can push the pawn on e4 forward to escape the threat from the black pawn on d5 and take control of the center, so your best move is e5. The current evaluation is +0.30, which favors you. Your opponent's strongest answer is probably ...Bf5, which brings their bishop into play. Does seeing that pawn move forward change how you view the center?

**8. Closed centre, Black to plan** (position, intermediate) — engine: Qc7

> The engine evaluation is -4.79, which favors White. You should bring your queen to a more active diagonal by playing ...Qc7. Your opponent will likely reposition their bishop by playing Bc2. How do you think this change in placement affects the activity of your pieces?

**9. Queen on f4, White attacking** (position, advanced) — engine: Be3

> Bringing your bishop into play from its starting square is a natural idea, so your best reply is Be3. The evaluation is +2.68, favoring White. Your opponent's strongest answer is probably ...Qd5, where White can attack the queen next with the pawn on c2. To bring your bishop into the game and attack the queen on d5, your best response is Bc4. Your opponent will likely play ...Qxe5 to capture the pawn and remove the queen from the attack. How do you plan to handle the tension once your pawn on b2 is left undefended?

**10. Open game, Black to move** (position, beginner) — engine: dxe4

> You capture White's pawn on e4 and attack their knight on f3, so a natural idea is taking the pawn (dxe4). The evaluation is -0.87, which favors Black. Your opponent's strongest answer is probably capturing your pawn on e5 with their knight (Nxe5). How do you think that changes the balance of the board?

**11. King + pawn vs king** (position, beginner) — engine: e3

> The evaluation is +5.11, which favors you. To proceed, your best move is e3 (e3). Your opponent will likely move their king to f6 (...Kf6). How do you think this change will affect the board?

**12. Rook + pawn endgame** (position, intermediate) — engine: Kd2

> The evaluation is +6.30, which means the position is significantly in your favor. You should move your king to support your position, so your best reply is Kd2. Your opponent will likely respond with ...Ke4. What do you think your next plan should be now that our kings have moved?

**13. Queen vs lone king (mating)** (position, beginner) — engine: Kg3+

> You can open a line for your queen and put the black king in check by moving your king to g3 (Kg3+). The evaluation is +5.09, which favors you. Your opponent will likely move their king to g6 (...Kg6) to escape your attack. How do you think you should coordinate your pieces to keep the pressure on?

**14. Central king & pawn** (position, advanced) — engine: Kc3

> The current evaluation is +0.44, favoring White. To continue, you move your king to c3. Your opponent will likely respond with ...Kc5. To place a pawn in the center and deliver a check, you should play d4+. Your opponent will then probably move their king to b6 to escape the check and move away from your pawn. What do you think is the best way to maintain your advantage after this sequence?

**15. Italian: 3.Bb5 (good)** (move, beginner) — engine: played Bb5 / best Bb5 (Best)

> Your bishop moves out to take an active role on the board [Bb5]. The evaluation is +0.44, favoring White. Your opponent will likely challenge your piece by moving their pawn [a6]. To stay safe, you should move your bishop to safety [Ba4]. What do you think your opponent will try to do to your bishop next?

**16. Opening move 1.e4 (good)** (move, beginner) — engine: played e4 / best e4 (Best)

> You placed your pawn in the center to open paths for your queen and your bishop [e4]. The evaluation is +0.35, which means you are slightly ahead. Your opponent will likely move their pawn to the center [e5]. To attack that pawn with your knight, your best reply is Nf3 [Nf3]. What do you think your opponent will do next to defend that pawn?

**17. Ruy Lopez: 4.Ba4 (good)** (move, intermediate) — engine: played Ba4 / best Ba4 (Best)

> You saved your bishop from the pawn on a6 by moving it to safety. The current evaluation is +0.48, which shows you are ahead. Your opponent will likely develop their knight by playing ...Nf6 to threaten your pawn on e4. To bring your king to safety and activate your rook, your best reply is O-O. Your opponent will probably then attack your bishop on a4 by playing ...b5. How do you plan to handle the pressure on your bishop once that pawn moves?

**18. Develop with ...Be7 (mistake)** (move, intermediate) — engine: played Be7 / best dxe4 (Mistake)

> Your move brings your bishop into play, but it misses an opportunity to challenge White. The evaluation is -2.42, which means White is ahead. Your opponent will likely play Nxe5 to capture your pawn and open a line for their queen. You can then look to move to O-O to get your king to safety. You might instead consider grabbing the pawn on e4 to attack the knight and open lines for your queen. How do you think you can better prepare for your opponent's pressure in the center?

**19. Scotch: ...exd4 (good)** (move, intermediate) — engine: played exd4 / best exd4 (Best)

> You made a great choice by capturing the pawn on d4. The evaluation is -0.42, which shows White is currently ahead. Your opponent will likely play Nxd4 to regain the material. To build your development and target the pawn on e4, a natural idea is Nf6, so your best reply is ...Nf6. Your opponent might then choose Nxc6 to challenge your queen, and you should respond by taking back with ...dxc6 to open lines for your pieces. What do you think your next plan should be after you recapture on c6?

**20. Scholar's mate trap: ...Nf6?? (blunder)** (move, beginner) — engine: played Nf6 / best g6 (Blunder)

> By bringing your knight out to f6 (...Nf6), you attack the White queen and the pawn on e4, but you also allow White's pieces to focus their power on your f7 pawn. The evaluation is now a forced win for White. Your opponent's strongest answer is probably the queen move (Qxf7#), which delivers checkmate. You could have challenged the queen and opened a path for your bishop by playing the pawn move (...g6).

**21. ...Nxe4? loses material (mistake)** (move, intermediate) — engine: played Nxe4 / best dxe4 (Mistake)

> By taking the pawn on e4, you opened a path for your queen, but now the pawn on d2 can challenge your knight. The current evaluation is -2.47, which means White is ahead. Your opponent will likely play d3 to attack your knight with a pawn and open lines for their bishop and queen. You should respond by moving the knight to f2 to get it out of that attack while striking at their queen. You could have instead played ...dxe4 to pressure their knight on f3 with your pawn. What do you think is the best way to keep your initiative after these exchanges?

**22. Wing push 1.a4 (passive)** (move, beginner) — engine: played a4 / best e4 (Inaccuracy)

> By pushing the pawn to a4 (a4), you open a path for your rook on a1. The evaluation is -0.32, which means Black is currently ahead.

Your opponent's strongest answer is probably to move the pawn to the center with ...e5. To respond to that, you should put your own pawn in the center to open lines for your queen and bishop by moving e4 (e4). You might wonder why putting a pawn in the center with e4 (e4) is considered stronger instead?

**23. Edge push 1.h4 (passive)** (move, beginner) — engine: played h4 / best e4 (Mistake)

> By moving your pawn to the side, you open a path for your rook on h1 [h4]. The evaluation is -0.43, which means Black is ahead.

Your opponent will likely place a pawn in the center on d5 [...d5]. To challenge the center yourself, you should move your pawn to d4 [d4]. It might have been better to put a pawn in the center to open paths for your queen and bishop by playing [e4]. What do you think about controlling the middle of the board?

**24. Premature 3.Ng5?? (blunder)** (move, advanced) — engine: played Ng5 / best Bb5 (Blunder)

> By placing your knight on g5, you left it undefended, and the move opens a line for your queen. The evaluation is -4.00, favoring Black. Your opponent will likely play ...Qxg5 to capture your knight. You should play d4 to put a pawn in the center and attack the queen with your bishop on c1. This follows your blunder instead of the suggested Bb5, which would have developed your bishop from its starting square; how would you have handled the incoming pawn attack on your bishop?

**25. Passive 2.Na3 (good)** (move, intermediate) — engine: played Na3 / best Nf3 (Good)

> You brought your knight into play from its starting square, which is a solid way to continue your development. The evaluation is +0.06, which favors you. Your opponent will likely play ...e6 to open lines for their queen and bishop. You should then bring your knight into play from its starting square with Nf3. Your opponent might then play ...a6 to open a line for their rook. Since your knight development was slightly less optimal than the engine's preference, next time consider that bringing your knight to f3 also develops from its starting square.
