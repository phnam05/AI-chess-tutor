# Faithfulness evaluation

**22 of 25 explanations (88%) passed both checks: every move they named was one the engine produced, and no sentence asserted a cause for the evaluation the engine didn't back.**

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
| 1 | Ruy Lopez (after 3...a6) | opening | position | beginner | yes | Ba4, Nf6 | — | — |
| 2 | Italian Game (Giuoco Piano) | opening | position | intermediate | yes | c3, d4, Nf6, exd4, e5 | — | — |
| 3 | Sicilian Najdorf | opening | position | advanced | yes | Be3, e5 | — | — |
| 4 | Queen's Gambit Declined | opening | position | intermediate | yes | e3, h6, Bh4, Ne4 | — | — |
| 5 | French Defence (Winawer) | opening | position | advanced | yes | e5, c5, a3, Bxc3+, bxc3, Qc7 | — | unverified |
| 6 | King's Indian Defence | opening | position | intermediate | yes | Nf3, Be2, Be3, dxe5 | — | — |
| 7 | Caro-Kann Defence | opening | position | beginner | yes | e5, Bf5, c4, e6, Nc3, Ne7 | — | — |
| 8 | Closed centre, Black to plan | middlegame | position | intermediate | yes | Qc7, Rad8, Bc2, a4 | — | — |
| 9 | Queen on f4, White attacking | middlegame | position | advanced | yes | Be3, Qd5, Bc4, Qxe5, O-O-O, Qxf4, Bxf4 | — | — |
| 10 | Open game, Black to move | middlegame | position | beginner | yes | Nxe5, d4 | — | — |
| 11 | King + pawn vs king | endgame | position | beginner | yes | e3, e4 | — | — |
| 12 | Rook + pawn endgame | endgame | position | intermediate | **NO** | Kd2, Rg1, e3+ | — | **invented** |
| 13 | Queen vs lone king (mating) | endgame | position | beginner | yes | Kg3+, Kh4, Kh6 | — | — |
| 14 | Central king & pawn | endgame | position | advanced | **NO** | Kc3, Kc5, d4+ | — | **invented** |
| 15 | Italian: 3.Bb5 (good) | opening | move | beginner | yes | a6 | — | — |
| 16 | Opening move 1.e4 (good) | opening | move | beginner | yes | e4, e5 | — | — |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | intermediate | yes | Ba4, Nf6, O-O, b5, Nxe4, d4 | — | — |
| 18 | Develop with ...Be7 (mistake) | middlegame | move | intermediate | yes | Nxe5, Bxc6, dxe4 | — | — |
| 19 | Scotch: ...exd4 (good) | opening | move | intermediate | yes | Nxd4, Nf6, Nxc6, dxc6, Qxd8+ | — | — |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | beginner | yes | Nf6, Qxf7#, g6 | — | — |
| 21 | ...Nxe4? loses material (mistake) | middlegame | move | intermediate | **NO** | d3, Bxc6+, Rxe5+, dxe4 | — | **invented** |
| 22 | Wing push 1.a4 (passive) | opening | move | beginner | yes | a4, e5, e4, Nf6, Nf3 | — | — |
| 23 | Edge push 1.h4 (passive) | opening | move | beginner | yes | h4, d5, e4 | — | unverified |
| 24 | Premature 3.Ng5?? (blunder) | opening | move | advanced | yes | Ng5, Qxg5, d4, Qg6, Bb5 | — | unverified |
| 25 | Passive 2.Na3 (good) | opening | move | intermediate | yes | Na3, e6, Nf3, a6, Be2, d5 | — | — |

## Explanations

**1. Ruy Lopez (after 3...a6)** (position, beginner) — engine: Ba4

> Moving your bishop back to a4 keeps your eye on the center while keeping your piece safe from being challenged by the pawn. The engine evaluation of +0.42 shows a slight edge for you, as your pieces are developing nicely. After you play Ba4, your opponent might reply with Nf6, and then you would castle to bring your king to safety before continuing the battle in the center. If you were playing this game right now, where would you want to place your knight next?

**2. Italian Game (Giuoco Piano)** (position, intermediate) — engine: c3

> The engine evaluates this position at +0.20, which gives you a very slight edge as you continue developing your pieces. By playing c3, you are preparing to control the center with d4, which will challenge the opponent's grip on the middle of the board. If your opponent responds with Nf6, you would follow up with d4, and after they take your pawn with exd4, your next move e5 would gain space and force their knight to move again. How would you plan to keep the pressure on their center once their knight retreats?

**3. Sicilian Najdorf** (position, advanced) — engine: Be3

> The engine gives you a +0.51 advantage, reflecting a slight but persistent edge for White in this Sicilian structure. Playing Be3 is a flexible way to develop your bishop while reinforcing the d4-square, and if your opponent responds with e5, your knight will likely retreat to b3 to maintain central control. This sequence keeps the tension in the center while preparing to meet the pressure from their knights. How would you plan to challenge their kingside development if they commit to this early push?

**4. Queen's Gambit Declined** (position, intermediate) — engine: e3

> You are currently sitting with a solid position where the evaluation of +0.31 suggests a very slight edge for you. By playing e3, you solidify your central control and open a diagonal for your light-squared bishop. The engine expects a quiet development phase where you respond to black's h6 with Bh4, followed by your knight jumping to f3, which prepares you to challenge black's setup after they play Ne4. How do you think your pieces will coordinate once your king is safely tucked away after you develop your knight?

**5. French Defence (Winawer)** (position, advanced) — engine: e5

> By playing e5, you immediately challenge Black's center and lock the pawn structure, which secures you a slight edge of +0.64. Your move forces Black to clarify their intentions with c5, and after the exchange sequence of a3, Bxc3+, and bxc3, you are left with a solid pawn structure and a space advantage that compensates for your doubled c-pawns. Looking at how this structure settles into the main line with Qc7, how do you think your long-term prospects in this French-style setup compare to the pressure Black gains from their activity?

**6. King's Indian Defence** (position, intermediate) — engine: Nf3

> The engine evaluates this position at +0.65, which means you have a small but pleasant advantage as White. Playing Nf3 is the most natural move here because it completes your minor piece development and prepares you to castle your king to safety. By following up with Be2 and Be3, you are building a solid central structure that allows you to eventually challenge their setup with dxe5. How do you think your development compares to theirs as you prepare to open the center?

**7. Caro-Kann Defence** (position, beginner) — engine: e5

> Playing e5 is your best choice here because it gains space in the center and forces your opponent's bishop to move. With an evaluation of +0.30, the computer thinks you have a very slight advantage as you move toward the lines like Bf5, then your c4, then e6, and finally Nc3 and Ne7. If you push that pawn forward, how do you think your pieces will find good squares to develop behind it?

**8. Closed centre, Black to plan** (position, intermediate) — engine: Qc7

> It looks like the engine evaluates this position at -4.79, which strongly favors you as Black. Playing Qc7 is an excellent way to consolidate your control over the center and prepare to contest the d4-square. By following up with Rad8, you are likely planning to build pressure against White's center, as the engine suggests your opponent will respond with Bc2 and a4 to try and stabilize their position. Since you have such a significant advantage here, how would you start coordinating your pieces to turn this pressure into a lasting initiative?

**9. Queen on f4, White attacking** (position, advanced) — engine: Be3

> The evaluation of +2.68 confirms a significant advantage for you, primarily driven by your space advantage and the pressure you exert on the queenside. Playing Be3 is a strong developing move that prepares for long castling, which likely leads to the sequence Qd5, your Bc4, and then Qxe5, followed by your O-O-O, Qxf4, and finally Bxf4. This line effectively transitions the game into a favorable endgame where your central control and piece activity remain dominant. How do you plan to leverage that endgame advantage once your bishop lands on f4?

**10. Open game, Black to move** (position, beginner) — engine: dxe4

> Taking the pawn on e4 with your d-pawn is the strongest move here, and the engine gives you a small edge of -0.87. After you take, White will likely strike back with Nxe5, but you can respond by bringing your queen to d5 to pressure their knight. If they trade bishops and then play d4, how do you think your pieces will hold up in the center?

**11. King + pawn vs king** (position, beginner) — engine: e3

> You are in a winning position with an evaluation of +5.11 for you, which means you have a very strong advantage. By playing e3, you prepare to advance your pawn safely while keeping your king active. If the game follows the predicted line, you will move your king to d5 and then advance your pawn to e4 to help control the center. How do you think your opponent will try to stop your pawn from reaching the other side?

**12. Rook + pawn endgame** (position, intermediate) — engine: Kd2

> The engine evaluates this position at +6.30, giving you a very strong advantage because you are winning the endgame with your extra rook. By playing Kd2, you move your king toward the center to support your rook and limit the mobility of your opponent's king. In the predicted line, you would follow up by playing Rg1 to prepare your e-pawn, which then pushes with e3+ to force the opponent's king to relocate. How do you think you can best use that pawn push to secure your winning position?

**13. Queen vs lone king (mating)** (position, beginner) — engine: Kg3+

> You have a winning position here with an evaluation of +5.09, which means you have a very strong advantage. By playing Kg3+, you immediately put the enemy king in check, forcing it to move to g6. After that, if you play Kh4, Kh6, and then move your queen to f5, you are actively moving your pieces toward the center to restrict the king's movement. How do you think you can use your queen and king together to trap the black king?

**14. Central king & pawn** (position, advanced) — engine: Kc3

> The position sits at an evaluation of +0.44, giving you a slight but stable edge as you look to activate your king toward the center. By playing Kc3, you immediately seize the opposition and prepare to challenge the black king's reach. The engine expects a sequence where Black likely responds with Kc5, followed by your d4+ push to gain space, leading to a position where your king advances further toward c4 to maintain pressure on the d-file. How do you think controlling this central corridor will dictate the endgame tempo as both sides maneuver for the pawn breakthrough?

**15. Italian: 3.Bb5 (good)** (move, beginner) — engine: played Bb5 / best Bb5 (Best)

> You played an excellent move by bringing your bishop out to put pressure on your opponent's knight, which is currently guarding the center. The engine gives this a +0.44 evaluation, which shows you have a slight edge. Your opponent will likely respond by challenging your bishop with a6, but if you retreat to a4, you keep a solid hold on the position. How do you think you should defend that bishop if they continue to chase it with b5 later?

**16. Opening move 1.e4 (good)** (move, beginner) — engine: played e4 / best e4 (Best)

> Great choice starting with e4, as it instantly grabs the center and opens paths for your queen and bishop to join the game. The engine gives this an evaluation of +0.35, which means you have a tiny, pleasant edge. If your opponent plays e5, we might see both sides develop their knights and bishops toward the middle to fight for control of the board. How do you think you want to handle the center if they decide to mirror your opening moves?

**17. Ruy Lopez: 4.Ba4 (good)** (move, intermediate) — engine: played Ba4 / best Ba4 (Best)

> You played a great move by choosing Ba4, keeping your bishop active while maintaining pressure on Black's center. The engine evaluates this as a +0.48 advantage for you, which suggests you have a slight, comfortable edge out of the opening. Looking ahead, if your opponent plays Nf6 and you follow with O-O, they might push their b-pawn to b5 to challenge your bishop, which forces you to retreat to b3 and prepares for a central battle after Nxe4 and d4. How do you think you should handle the tension in the center once that pawn swap happens?

**18. Develop with ...Be7 (mistake)** (move, intermediate) — engine: played Be7 / best dxe4 (Mistake)

> It looks like your choice to develop your bishop to e7 lets White take control of the center with Nxe5. In this line, after you castle, White will trade bishops with Bxc6 and eventually pick up your c6 pawn, leaving you under pressure with a -2.42 evaluation that heavily favors your opponent. Instead of passively developing, taking the center immediately with dxe4 would have kept the position much more balanced. Given the tension in the center, how do you think you could have prepared to challenge those central pawns more effectively?

**19. Scotch: ...exd4 (good)** (move, intermediate) — engine: played exd4 / best exd4 (Best)

> You played a solid move by taking the pawn, which helps you contest the center immediately. The evaluation of -0.42 shows that while the position is very balanced, white now has a slight edge in development after the expected sequence of Nxd4, Nf6, Nxc6, dxc6, and the trade of queens with Qxd8+. By inviting these early exchanges, you are simplifying the position toward an endgame where your king safely moves to d8. How do you feel about playing a slightly more open game from this position?

**20. Scholar's mate trap: ...Nf6?? (blunder)** (move, beginner) — engine: played Nf6 / best g6 (Blunder)

> Oh no, by playing Nf6, you left your f7-pawn undefended, which allows your opponent to play Qxf7# and checkmate your king immediately. Since the evaluation has dropped to -100.00, it shows that your king is now in big trouble. Next time, it is much safer to play g6 to block the threat against that pawn. Can you see how that simple move would have kept your king safe?

**21. ...Nxe4? loses material (mistake)** (move, intermediate) — engine: played Nxe4 / best dxe4 (Mistake)

> Your move loses a significant amount of ground, with the evaluation shifting to -2.47 in favor of your opponent because it leaves you vulnerable to a sharp counterattack. After your opponent plays d3, they prepare to trap your knight by forcing a trade with Bxc6+, which leaves you with doubled pawns and allows them to follow up with Rxe5+ to reclaim material. By capturing the other way with dxe4 instead, you would have maintained a much more stable position with an evaluation of -0.87. Take a look at that line again—how could you have kept your king safer while still putting pressure on their center?

**22. Wing push 1.a4 (passive)** (move, beginner) — engine: played a4 / best e4 (Inaccuracy)

> Starting with a4 doesn't help you control the important center squares, leaving your opponent room to play e5 and claim that space for themselves. After e5, the game might continue with e4, Nf6, and Nf3, allowing black to develop their pieces toward the middle of the board while yours stay tucked away. It is usually much better to lead with a move like e4 to open lines for your queen and bishop right away. What do you think is the biggest advantage of having your pieces out in the center early?

**23. Edge push 1.h4 (passive)** (move, beginner) — engine: played h4 / best e4 (Mistake)

> Your move h4 doesn't help you control the center, which is why the evaluation has dipped to -0.43, favoring your opponent slightly. By playing d5, your opponent can immediately claim space in the middle of the board while you are still working on your first move. Taking control of the center with e4 right away is usually much stronger because it opens paths for your pieces to enter the game. How do you think you can develop your knights and bishops most effectively from here?

**24. Premature 3.Ng5?? (blunder)** (move, advanced) — engine: played Ng5 / best Bb5 (Blunder)

> Your move Ng5 turns out to be a significant error because it allows Black to simply capture your knight with Qxg5. The engine expects that after you respond by playing d4, Black will continue with Qg6, leading to a position where you are down a piece for very little compensation, reflected in the -4.00 evaluation. Instead of committing the knight early, playing Bb5 would have maintained a balanced position of +0.35 by putting pressure on Black's control of the center. When you look at the board again, can you see why overextending that knight creates such a permanent disadvantage in your material balance?

**25. Passive 2.Na3 (good)** (move, intermediate) — engine: played Na3 / best Nf3 (Good)

> Your move of Na3 is a flexible choice that keeps the game balanced, though it slightly reduces your opening advantage to +0.06. By playing this, you allow your opponent to challenge the center more comfortably with e6, followed by your Nf3, their a6, your Be2, and finally their d5, which opens the game up for them. While Nf3 would have been a slightly more direct way to fight for the center, your move still develops a piece toward the rim where it aims to support future control of the c4 square. How do you think you might reposition that knight later to make it more influential in the game?
