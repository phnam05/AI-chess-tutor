# Faithfulness evaluation

**24 of 25 explanations (96%) passed both checks: every move they named was one the engine produced, and no sentence asserted a cause for the evaluation the engine didn't back.**

Each explanation was produced by the real coach (Stockfish facts → Gemini prose) and checked by `faithfulness.check_faithfulness`.

## What this measures — and what it does not

This is an automatic, string-based check with two parts. The *move* check reads the moves the coach named in notation (e.g. `Nf3`, `Bxc3+`, `O-O`) and confirms each was a move the engine actually gave — its best move, its principal variation, or (for a graded move) its refutation line. The *eval-causality* check — added after the 2026-07-03 human audit found invented reasons were the dominant failure — reads sentences that both name the evaluation and assert a cause for it. Its scope is deliberate:

- **Catches** invented piece moves, captures, checks and mates — the attention-grabbing hallucination ("you can play Nxe5, forking the king").
- **Catches** invented *reasons* for the evaluation ("the edge comes from your active pieces") when the sentence cites no engine move at all; a causal sentence that does cite a grounded move is reported as *unverified* rather than failed, because the audit saw that kind be right.
- **Does not hard-flag** a bare pawn push written as a square (e.g. `c3`, `h4`): the coach may simply be pointing at a square, so these are reported as *unverified* rather than failed, to avoid false alarms.
- **Does not check** other verbal claims ("this pins the knight") or whether a move's stated *purpose* matches the engine's line.

These limits are validated two ways: a *positive control* (planting fake piece-moves in real explanations confirms the check flags them) and a *human audit* (how often this automatic verdict agrees with a person's judgement — see `validate_checker.py`, which scores the eval-causality check against the audited 25 cases).

| # | Position | Phase | Type | Level | Faithful | Grounded moves | Invented | Eval-causal claim |
|--:|----------|-------|------|-------|:--------:|----------------|----------|-------------------|
| 1 | Ruy Lopez (after 3...a6) | opening | position | beginner | yes | — | — | — |
| 2 | Italian Game (Giuoco Piano) | opening | position | intermediate | yes | c3, d4, Nf6, e5 | — | — |
| 3 | Sicilian Najdorf | opening | position | advanced | yes | Be3, e5 | — | — |
| 4 | Queen's Gambit Declined | opening | position | intermediate | yes | e3, h6? | — | — |
| 5 | French Defence (Winawer) | opening | position | advanced | yes | e5 | — | unverified |
| 6 | King's Indian Defence | opening | position | intermediate | yes | Nf3, Be2, Be3, e5 | — | — |
| 7 | Caro-Kann Defence | opening | position | beginner | yes | e5 | — | — |
| 8 | Closed centre, Black to plan | middlegame | position | intermediate | yes | Qc7 | — | — |
| 9 | Queen on f4, White attacking | middlegame | position | advanced | yes | Be3, Qd5 | — | — |
| 10 | Open game, Black to move | middlegame | position | beginner | yes | dxe4 | — | — |
| 11 | King + pawn vs king | endgame | position | beginner | yes | e3 | — | — |
| 12 | Rook + pawn endgame | endgame | position | intermediate | yes | Kd2, Rg1 | — | — |
| 13 | Queen vs lone king (mating) | endgame | position | beginner | yes | Kg3+ | — | — |
| 14 | Central king & pawn | endgame | position | advanced | yes | Kc3, Kc5, d4+ | — | — |
| 15 | Italian: 3.Bb5 (good) | opening | move | beginner | yes | a6 | — | unverified |
| 16 | Opening move 1.e4 (good) | opening | move | beginner | yes | e4, e5 | — | — |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | intermediate | yes | Ba4, Nf6, b5, d4 | — | — |
| 18 | Develop with ...Be7 (mistake) | middlegame | move | intermediate | yes | Be7, dxe4, Nxe5 | — | — |
| 19 | Scotch: ...exd4 (good) | opening | move | intermediate | yes | exd4, Nxd4, Nf6, dxc6, Qxd8+ | — | — |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | beginner | yes | Qxf7, Nf6, g6 | — | — |
| 21 | ...Nxe4? loses material (mistake) | middlegame | move | intermediate | yes | d3 | — | — |
| 22 | Wing push 1.a4 (passive) | opening | move | beginner | yes | a4, e5, e4 | — | — |
| 23 | Edge push 1.h4 (passive) | opening | move | beginner | **NO** | h4, d5, e4 | — | **invented** |
| 24 | Premature 3.Ng5?? (blunder) | opening | move | advanced | yes | Qxg5, d4, dxe5, Bb5 | — | unverified |
| 25 | Passive 2.Na3 (good) | opening | move | intermediate | yes | Na3, e6, d5, Nf3 | — | — |

## Explanations

**1. Ruy Lopez (after 3...a6)** (position, beginner) — engine: Ba4

> It is a good idea to pull your bishop back to a4 so you keep your pressure on the e5-pawn while staying safe from the black pawn that wants to kick you away. The engine evaluates the position at +0.42, which means you have a very slight advantage as White. If Black continues with the main plan of attacking your center, how do you think you should defend your e4-pawn after they jump their knight in?

**2. Italian Game (Giuoco Piano)** (position, intermediate) — engine: c3

> The engine evaluates this position at +0.20, which gives you a very slight edge as White in this early opening phase. By playing c3, you are preparing to secure the center by supporting a future d4 push, which is a common way to challenge Black's control. The predicted line suggests that if Black responds with Nf6, you can follow up with d4 to force an exchange and eventually strike with e5 to gain space and initiate active play in the center. How do you think your position might change if Black chooses to ignore your central pressure instead of trading pawns?

**3. Sicilian Najdorf** (position, advanced) — engine: Be3

> The engine evaluates this position at +0.51, giving you a slight but stable advantage as you solidify your control over the center. By playing Be3, you prepare to anchor your development and create a flexible setup that restricts Black’s ability to comfortably expand. The predicted line suggests that Black will likely challenge your knight on d4 with e5, which clarifies the tension and allows you to reposition your forces while maintaining space. How do you think your choice of square for the knight on b3 will influence your long-term plan for attacking their kingside?

**4. Queen's Gambit Declined** (position, intermediate) — engine: e3

> Playing e3 is a solid choice here because it shores up your center and opens a path for your dark-squared bishop to develop. The evaluation is +0.31, which shows a very slight edge for you, suggesting that you have a tiny head start in this balanced opening. Following the predicted line, your plan is to maintain your central tension while carefully handling the bishop pair as your opponent develops their kingside. How would you choose to respond if your opponent tries to challenge your center early instead of playing h6?

**5. French Defence (Winawer)** (position, advanced) — engine: e5

> Playing e5 is the best way to leverage your space advantage by locking the center and fixing the pawn structure. This move forces Black to define their setup quickly, and the engine’s line suggests they will likely challenge your c3-knight to compromise your queenside structure. With an evaluation of +0.64, you hold a slight but persistent edge that stems from this structural tension. How would you plan to handle the isolated c3-pawn and the potential pressure on your d4-square once the queenside trades conclude?

**6. King's Indian Defence** (position, intermediate) — engine: Nf3

> You have a solid setup here, and playing Nf3 is the best way to continue developing your pieces toward the center. With an evaluation of +0.65, the engine shows you have a slight but steady edge as you finish your development. By heading toward a setup with Be2 and Be3, you are preparing to control the e5 square and manage the center as Black eventually attempts to break through with their own e5 push. If you continue with this development plan, how do you think you should coordinate your pieces once the center opens up?

**7. Caro-Kann Defence** (position, beginner) — engine: e5

> You should play e5 to gain more space in the center and restrict your opponent's pieces. The engine gives this position a +0.30 evaluation, which means you have a very slight advantage as White. If your opponent follows the most likely path by moving their bishop to f5, how do you think you can continue to challenge their control of the center?

**8. Closed centre, Black to plan** (position, intermediate) — engine: Qc7

> You are doing well here, and the engine evaluation of -4.79 shows a very comfortable advantage for you. By playing Qc7, you prepare to connect your rooks and put pressure on the center while keeping your queen safely active behind your pawns. Following the engine's suggested line, your next step is likely to bring the rook to the d-file to challenge the center after White develops their bishop. How do you think you can best use that extra space in the center to create attacking opportunities later?

**9. Queen on f4, White attacking** (position, advanced) — engine: Be3

> Your position is very strong here with an evaluation of +2.68, reflecting a significant advantage in development and control of the center. Playing Be3 is the most precise way to consolidate, as it prepares to support your queenside structure while clearing the back rank for your rooks. The engine’s line suggests that after Qd5, you can retreat your bishop to c4, aiming to maintain your central dominance even if the queens are traded off. Since you are ahead in activity, how do you think your long-term prospects compare once the queens leave the board?

**10. Open game, Black to move** (position, beginner) — engine: dxe4

> You should play dxe4 because it captures a pawn and opens up the center for your pieces. The evaluation of -0.87 means you have a small but clear advantage here. If White plays the expected line, you will trade off pieces to reach a position where your development looks quite solid. How do you feel about the activity your pieces will have after these trades?

**11. King + pawn vs king** (position, beginner) — engine: e3

> It looks like we are in an endgame, and playing e3 is a great way to start securing your king's position while preparing to support your pawn. The engine gives this an evaluation of +5.11, which shows you have a very strong advantage here. If play continues as expected, you will be able to move your king toward the center and push your pawn forward safely. How do you think your opponent will try to stop your pawn from reaching the other side?

**12. Rook + pawn endgame** (position, intermediate) — engine: Kd2

> You have a winning advantage here with an evaluation of +6.30, which means your position is significantly better for White. Playing Kd2 is a strong choice because it brings your king toward the center to support your rook and prepare for the coming endgame push. In the main line, you will likely continue with Rg1 to control the board while creating space to advance your e-pawn forward. How do you think moving your king helps you restrain their king from attacking your pieces?

**13. Queen vs lone king (mating)** (position, beginner) — engine: Kg3+

> You are currently up quite a bit of material, and the engine gives you a strong advantage of +5.09, which means your position is winning. By playing Kg3+, you move your king closer to your opponent's king while putting it in check, which forces their king to move away and helps you shepherd them toward the edge of the board. How do you think moving your king forward like this helps you get closer to setting up a checkmate?

**14. Central king & pawn** (position, advanced) — engine: Kc3

> Your position is evaluated at +0.44, which gives you a slight but meaningful edge in this endgame. By playing Kc3, you actively restrict the enemy king and prepare to support your d-pawn as it advances to challenge the center. The engine's line suggests that if Black responds with Kc5, you can immediately push with d4+ to seize space and force the black king into a more passive defensive role. How would you plan to coordinate your king and pawn if Black tries to avoid that central breakthrough?

**15. Italian: 3.Bb5 (good)** (move, beginner) — engine: played Bb5 / best Bb5 (Best)

> That is a very solid choice, as you are putting immediate pressure on the knight defending the center pawn. The engine evaluation of +0.44 shows you have a slight edge, and your bishop is well-placed to influence the game as your opponent likely responds by challenging you with a6. How do you plan to handle it if they try to push your bishop away right now?

**16. Opening move 1.e4 (good)** (move, beginner) — engine: played e4 / best e4 (Best)

> Great choice starting with e4, as it instantly grabs the center and opens paths for your queen and bishop to join the game. The engine gives this an evaluation of +0.35, which means you have a tiny, pleasant advantage as you begin the match. If your opponent responds with e5, how do you think you want to develop your knight on the next turn?

**17. Ruy Lopez: 4.Ba4 (good)** (move, intermediate) — engine: played Ba4 / best Ba4 (Best)

> Excellent choice playing Ba4, as it keeps the pressure on the black pawn at e5 and maintains your presence in the center. The engine evaluates this as a solid +0.48 advantage for you, indicating a slightly more comfortable position as you prepare to castle. If your opponent chooses the main path of Nf6 and b5, your bishop will retreat to b3 to keep its scope, eventually leading to a tactical skirmish where you fight for control after d4. Since your bishop is now safely placed to retreat, how do you think you should handle the tension if they aggressively challenge your knight on f3?

**18. Develop with ...Be7 (mistake)** (move, intermediate) — engine: played Be7 / best dxe4 (Mistake)

> You missed an opportunity to simplify the center, and now your position is a bit tougher to manage with an evaluation of -2.42, which favors your opponent. By playing Be7 instead of dxe4, you allowed your opponent to play Nxe5, which immediately puts pressure on your knight and forces you to defend your structure while they gain central space. In the line the engine suggests, your opponent can follow up by trading pieces on c6 and jumping their knight into the center, putting you on the defensive. Since we are now facing this challenge, how would you respond if they play that knight move to e5?

**19. Scotch: ...exd4 (good)** (move, intermediate) — engine: played exd4 / best exd4 (Best)

> Great choice playing exd4, as you've successfully opened the center and challenged White's control. The engine evaluation of -0.42 shows a slight edge for your opponent, as White will likely look to recapture with Nxd4 to centralize their knight and gain some initiative. By following up with Nf6 and eventually trading queens with dxc6 and Qxd8+, you are simplifying the position toward an endgame where your king becomes quite active. How do you feel about heading into an endgame this early in the game?

**20. Scholar's mate trap: ...Nf6?? (blunder)** (move, beginner) — engine: played Nf6 / best g6 (Blunder)

> It looks like your move unfortunately leaves your king in immediate danger. Because you moved your knight, your opponent can now play Qxf7, which delivers a direct checkmate because your f7-pawn is pinned and cannot capture back. Instead of Nf6, playing g6 would have blocked the attack on that pawn and kept your king safe. Can you see why that pawn on f7 was so important to protect before moving your knight?

**21. ...Nxe4? loses material (mistake)** (move, intermediate) — engine: played Nxe4 / best dxe4 (Mistake)

> That move unfortunately allows your opponent to gain a significant advantage, as the engine currently evaluates the position at -2.47 in your favor, which is a drop from where you could have been. By taking with the knight, you let your opponent play d3 to attack your knight and disrupt your coordination, leading to a sequence where they can trade bishops and eventually check you with the rook after you lose the f2-pawn. It is better to capture with the d-pawn instead, which would have kept the evaluation much closer to even. What do you think changes about the center if you capture with the pawn instead of the knight?

**22. Wing push 1.a4 (passive)** (move, beginner) — engine: played a4 / best e4 (Inaccuracy)

> By playing a4, you are moving a side pawn instead of controlling the center, which gives your opponent a chance to claim that space with e5. The engine evaluation is -0.32, which slightly favors your opponent, as they can now easily develop their pieces toward the middle of the board. Next time, how might playing a move like e4 help you control more of the board right from the start?

**23. Edge push 1.h4 (passive)** (move, beginner) — engine: played h4 / best e4 (Mistake)

> Starting the game with h4 doesn't help you take control of the center, which lets your opponent play d5 to claim that space for themselves instead. The engine evaluates your position at -0.43, meaning your opponent now has a slight advantage because you didn't fight for the middle squares right away. If you played e4 instead, you would have established a strong presence in the center immediately. How do you think controlling the center squares helps you develop your pieces more easily later on?

**24. Premature 3.Ng5?? (blunder)** (move, advanced) — engine: played Ng5 / best Bb5 (Blunder)

> By moving your knight to g5, you have overlooked that your opponent can simply capture it with Qxg5, leaving you down a full piece for no compensation. The current evaluation of -4.00 shows a significant disadvantage for you, as the engine expects your opponent to follow up by controlling the center with d4 and eventually trading down after dxe5. Instead of this premature attack, playing Bb5 would have maintained a slight +0.35 advantage by developing your pieces and putting pressure on the c6 knight. How would you adjust your opening setup if you knew you had to prioritize piece coordination over early aggression?

**25. Passive 2.Na3 (good)** (move, intermediate) — engine: played Na3 / best Nf3 (Good)

> You chose to develop your knight to the edge of the board with Na3, which keeps the position very balanced at +0.06. This move is solid, but the engine notes that it allows your opponent to easily control the center with e6 and d5, which is why Nf3 is generally preferred to challenge the center more directly. By following the engine’s predicted line, you can see how your opponent might try to equalize the space by pushing their pawns forward. How would you plan to challenge their central pawns once they establish that d5 square?
