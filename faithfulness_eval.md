# Faithfulness evaluation

**25 of 25 explanations (100%) named only moves the engine actually produced.**

Each explanation was produced by the real coach (Stockfish facts → Gemini prose) and checked by `faithfulness.check_faithfulness`. A case is *faithful* when the prose invents no move the engine never gave.

## What this measures — and what it does not

This is an automatic, string-based check: it reads the moves the coach named *in notation* (e.g. `Nf3`, `Bxc3+`, `O-O`) and confirms each was a move the engine actually gave — its best move, its principal variation, or (for a graded move) its refutation line. Its scope is deliberate:

- **Catches** invented piece moves, captures, checks and mates — the attention-grabbing hallucination ("you can play Nxe5, forking the king").
- **Does not hard-flag** a bare pawn push written as a square (e.g. `c3`, `h4`): the coach may simply be pointing at a square, so these are reported as *unverified* rather than failed, to avoid false alarms.
- **Does not check** eval numbers or verbal claims ("this pins the knight") — only moves written in notation.

These limits are validated two ways: a *positive control* (planting fake piece-moves in real explanations confirms the check flags them) and a *human audit* (how often this automatic verdict agrees with a person's judgement).

| # | Position | Phase | Type | Level | Faithful | Grounded moves | Invented |
|--:|----------|-------|------|-------|:--------:|----------------|----------|
| 1 | Ruy Lopez (after 3...a6) | opening | position | beginner | yes | — | — |
| 2 | Italian Game (Giuoco Piano) | opening | position | intermediate | yes | c3, d4, Nf6 | — |
| 3 | Sicilian Najdorf | opening | position | advanced | yes | Be3, e5 | — |
| 4 | Queen's Gambit Declined | opening | position | intermediate | yes | e3, h6 | — |
| 5 | French Defence (Winawer) | opening | position | advanced | yes | e5, c5 | — |
| 6 | King's Indian Defence | opening | position | intermediate | yes | e5 | — |
| 7 | Caro-Kann Defence | opening | position | beginner | yes | e5 | — |
| 8 | Closed centre, Black to plan | middlegame | position | intermediate | yes | Qc7 | — |
| 9 | Queen on f4, White attacking | middlegame | position | advanced | yes | Be3 | — |
| 10 | Open game, Black to move | middlegame | position | beginner | yes | dxe4, Nxe5 | — |
| 11 | King + pawn vs king | endgame | position | beginner | yes | e3 | — |
| 12 | Rook + pawn endgame | endgame | position | intermediate | yes | Kd2, Rg1, e3 | — |
| 13 | Queen vs lone king (mating) | endgame | position | beginner | yes | — | — |
| 14 | Central king & pawn | endgame | position | advanced | yes | Kc3, Kc5, d4+ | — |
| 15 | Italian: 3.Bb5 (good) | opening | move | beginner | yes | a6 | — |
| 16 | Opening move 1.e4 (good) | opening | move | beginner | yes | e4, e5 | — |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | intermediate | yes | Ba4, Nf6, d4, b5, Nxe4 | — |
| 18 | Develop with ...Be7 (good) | middlegame | move | intermediate | yes | Be7, dxe4, Nxe5 | — |
| 19 | Scotch: ...exd4 (good) | opening | move | intermediate | yes | Nf6 | — |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | beginner | yes | Qxf7#, g6 | — |
| 21 | ...Nxe4?? drops a piece (blunder) | middlegame | move | intermediate | yes | d3, Nxf2, Bxc6+, dxe4 | — |
| 22 | Wing push 1.a4 (passive) | opening | move | beginner | yes | a4, e5, e4 | — |
| 23 | Edge push 1.h4 (passive) | opening | move | beginner | yes | d5, e4 | — |
| 24 | Premature 3.Ng5?! (inaccuracy) | opening | move | advanced | yes | Qxg5 | — |
| 25 | Passive 2.Na3 (inaccuracy) | opening | move | intermediate | yes | Na3, Nf3, e6, d5 | — |

## Explanations

**1. Ruy Lopez (after 3...a6)** (position, beginner) — engine: Ba4

> Pulling your bishop back to a4 keeps it safe while maintaining pressure on the knight that is protecting the center pawn. The slight edge for you comes from keeping your pieces active and ready to castle your king to safety soon. If your opponent tries to chase the bishop away, how do you think your center pawns might help you control more of the board?

**2. Italian Game (Giuoco Piano)** (position, intermediate) — engine: c3

> It is great to see you developing your pieces so well, and playing c3 here is a smart way to prepare for a central push. By supporting a future d4 move, you are aiming to claim more space in the center and challenge their control of the board. If black responds with Nf6, you can follow through with d4 to open lines for your pieces and fight for the initiative. If you were sitting at the board, where do you think your pieces would be most active once that central pawn tension is resolved?

**3. Sicilian Najdorf** (position, advanced) — engine: Be3

> By playing Be3, you are cementing your control over the d4-square and preparing for a solid Sicilian setup that balances space with flexibility. This move secures a slight edge of +0.51 because it anticipates the common e5 push, allowing you to reposition your knight to b3 to maintain central tension while preparing to challenge the kingside knight. Think about how this development choice dictates the flow of the game compared to a more aggressive or immediate pawn expansion; how would you plan to maneuver your pieces if your opponent chooses a more restrained development instead?

**4. Queen's Gambit Declined** (position, intermediate) — engine: e3

> Playing e3 is a solid choice here because it secures your central pawn structure and opens the path for your light-squared bishop to retreat safely if challenged. By tucking the bishop away to h4 after black plays h6, you maintain long-term pressure on the board and keep your pieces flexible for the upcoming middlegame. This move keeps the evaluation slightly in your favor by ensuring your development remains harmonious while you wait to see how black chooses to challenge your center. Given how you want to deploy your knights and complete your kingside development, where do you think your pieces will have the most influence once you castle?

**5. French Defence (Winawer)** (position, advanced) — engine: e5

> By playing e5, you immediately claim central space and force the black knight to relocate to a less ideal square, which justifies your +0.64 advantage. This push creates a clear strategic imbalance where you accept a slightly compromised pawn structure in exchange for superior control of the center and long-term attacking potential. If black continues with the critical line of c5 and an exchange on c3, you are left with the bishop pair and a solid space advantage to work with in the resulting middlegame. How would you plan to utilize your extra space to restrict black's pieces once the minor pieces start coming off the board?

**6. King's Indian Defence** (position, intermediate) — engine: Nf3

> It is time to develop your knight to f3 to support your center and prepare for kingside castling. By doing this, you are solidifying your control over the d4 and e5 squares, which gives you a slight edge in space and long-term stability. Your opponent will likely look to challenge your control of the center with e5, but by following up with your bishop, you maintain a strong setup that keeps your pieces coordinated. How would you plan to react if black continues to pressure your center after you castle?

**7. Caro-Kann Defence** (position, beginner) — engine: e5

> Pushing your pawn to e5 is a great way to grab extra space in the center and cramp your opponent's pieces. This move forces their bishop to move again and sets you up to control more of the board. Since the game is still very even, how would you decide where to develop your knights next to support this space advantage?

**8. Closed centre, Black to plan** (position, intermediate) — engine: Qc7

> You are in a very solid position here, and playing Qc7 is a great way to centralize your queen while keeping your options flexible. By stepping off the d-file, you clear the way for your rook to join the fight, setting you up to control the center and put pressure on their d4 pawn. The evaluation is heavily in your favor because your pieces are poised to dominate the open files, making it hard for White to find any counterplay. How do you think your rook on d8 will change the way White has to defend their central pawns?

**9. Queen on f4, White attacking** (position, advanced) — engine: Be3

> With an evaluation of +2.68, you have a commanding advantage here because your space advantage and central control severely cramp Black’s development. Playing Be3 is the strongest continuation because it brings your final minor piece into the game while reinforcing the critical d4 square and preparing to link your rooks. By solidifying the center, you effectively neutralize Black's attempts to challenge your advanced e5 pawn, allowing you to transition into a long-term squeeze. How would you plan to coordinate your rooks once you complete your development?

**10. Open game, Black to move** (position, beginner) — engine: dxe4

> You should play dxe4 because it immediately captures the center pawn and forces White to react to the pressure on their knight. This move gives you a slight advantage because it clears the path for your queen and disrupts White's setup in the middle of the board. If White plays the main response of Nxe5, how would you develop your pieces to keep the initiative?

**11. King + pawn vs king** (position, beginner) — engine: e3

> You are currently in a winning king and pawn endgame, and playing e3 is the perfect way to support your king and prepare to push your pawn all the way to promotion. By moving the pawn forward, you create a solid base that protects your king while giving you a clear path to make a queen. If you follow this plan, you will likely be able to force your opponent's king away and win the game. How do you think your opponent might try to stop your pawn from reaching the other side?

**12. Rook + pawn endgame** (position, intermediate) — engine: Kd2

> You have a significant advantage here because your rook and king can easily coordinate to force the enemy king away from the center. Playing Kd2 is the best way to activate your king and support your pawn, as it prepares to restrict the opponent's movement while securing your position. By following up with Rg1 and e3, you’re creating a wall that will eventually force the black king to give up ground. How would you plan to safely push that e-pawn forward once your king reaches a more active square?

**13. Queen vs lone king (mating)** (position, beginner) — engine: Kg3+

> It looks like you have a great chance to corner your opponent's king here. By moving your king to g3 with check, you force their king to move and begin cutting off their escape squares. This helps you trap them against the edge of the board so your queen can deliver a final blow. How do you think you can keep their king trapped after they move away?

**14. Central king & pawn** (position, advanced) — engine: Kc3

> You are facing a classic endgame scenario where the distance of your king from the opponent's critical squares determines the outcome. By playing Kc3, you adopt a waiting profile that forces your opponent to commit their king first, which is essential given that your +0.44 edge hinges on maintaining the tension while preparing to push your d-pawn. If they respond with Kc5, the critical follow-up d4+ allows you to seize the initiative and control the center, putting the burden of defense entirely on them. How do you think the dynamic shifts if your opponent tries to avoid the pawn break instead of challenging your king directly?

**15. Italian: 3.Bb5 (good)** (move, beginner) — engine: played Bb5 / best Bb5 (Best)

> That is a fantastic move! By putting your bishop on b5, you are putting direct pressure on the knight that is protecting your opponent's center pawn. If your opponent plays a6 to challenge you, you can simply retreat to a4, keeping your bishop active and ready to help you castle your king to safety soon. How do you think your opponent will try to defend their center pawn now?

**16. Opening move 1.e4 (good)** (move, beginner) — engine: played e4 / best e4 (Best)

> Great start, playing e4 is a classic way to take control of the center and open lines for your queen and bishop. By putting a pawn in the middle, you make it much easier to develop your pieces quickly and keep your king safe. If your opponent responds with e5, how do you think you can best put pressure on that pawn next?

**17. Ruy Lopez: 4.Ba4 (good)** (move, intermediate) — engine: played Ba4 / best Ba4 (Best)

> Great choice playing Ba4; by keeping your bishop on the board, you maintain your pressure on the e5-pawn and keep the tension in the center. The engine shows a slight advantage here, and as your opponent likely responds with Nf6 and castles, you are well-positioned to support your center with d4 after pulling your bishop back to b3. Since your opponent will probably try to challenge your control with b5 and eventually Nxe4, how do you think you can use your lead in development to punish them if they grab that pawn too greedily?

**18. Develop with ...Be7 (good)** (move, intermediate) — engine: played Be7 / best dxe4 (Mistake)

> Your move Be7 lets your opponent take control of the center because you missed the chance to simplify the position. By playing Be7 instead of dxe4, you allow White to play Nxe5, which immediately puts pressure on your knight and forces you into a defensive posture. In the expected line, White proceeds to swap off pieces, leaving you with a compromised pawn structure while they gain more space and initiative. Next time, how might you look for ways to challenge White's central pawns before they have a chance to settle in?

**19. Scotch: ...exd4 (good)** (move, intermediate) — engine: played exd4 / best exd4 (Best)

> You played a very solid move here, as capturing the pawn challenges White's control over the center and clears the way for your pieces. By trading this pawn, you are likely heading toward an endgame where your king becomes quite active after the queens are traded off. White will likely respond by recapturing with their knight to centralize it, but this gives you the opportunity to develop your pieces toward the center with Nf6. Since the position is now very balanced, what do you think is the best square for your bishop to influence the game once your knight reaches the center?

**20. Scholar's mate trap: ...Nf6?? (blunder)** (move, beginner) — engine: played Nf6 / best g6 (Blunder)

> Oh no, by moving your knight, you left your pawn on f7 undefended, and your opponent can now play Qxf7# to end the game immediately. Your king is in big trouble because that f7 square is the weakest point in your position. Would you like to look at how playing g6 earlier would have blocked that white queen from targeting your king?

**21. ...Nxe4?? drops a piece (blunder)** (move, intermediate) — engine: played Nxe4 / best dxe4 (Mistake)

> It looks like taking that pawn with your knight allowed White to grab the initiative. By playing d3, your opponent forces your knight to commit, and after you look for compensation with Nxf2, they can trade off your active bishop with Bxc6+ to shatter your queenside structure. This exchange leaves you with doubled pawns and gives White a comfortable lead in space, making it tough to coordinate your pieces. If you had played dxe4 instead, you would have maintained a much tighter game by keeping your pieces flexible. What do you think you could have done differently to keep your pawn structure intact?

**22. Wing push 1.a4 (passive)** (move, beginner) — engine: played a4 / best e4 (Inaccuracy)

> Starting with a4 is a bit unusual because it doesn't help you take control of the center or get your pieces ready to join the game. When you play on the edge like that, your opponent can easily claim the middle squares for themselves, like they would likely do by playing e5 to block your path. It is usually better to start by opening up space for your queen and bishop to move out, which is why playing e4 is a much stronger way to begin. If you could restart the game, how do you think moving your king's pawn forward would change your control of the board?

**23. Edge push 1.h4 (passive)** (move, beginner) — engine: played h4 / best e4 (Mistake)

> That move is a bit tricky because it doesn't help you fight for the center of the board where most of the action happens. By playing on the side, you give your opponent a chance to immediately grab the middle with a move like d5, making it easier for them to control the game. It is usually much more effective to start by moving your center pawns, like e4, to open paths for your bishop and queen. If you were starting the game again, how do you think moving your king's pawn forward would change your options?

**24. Premature 3.Ng5?! (inaccuracy)** (move, advanced) — engine: played Ng5 / best Bb5 (Blunder)

> By moving your knight to g5, you’ve committed a serious blunder that abandons your development in favor of a premature attack. Your opponent can now simply respond with Qxg5, capturing your knight for free and leaving you down a full piece for absolutely no compensation, which is exactly why the evaluation swings to -4.00. While you were likely hoping to create pressure on f7, your light-squared bishop remains trapped at home, leaving you unable to support your aggressive intentions. Does this look like the kind of position where you can afford to sacrifice a piece without a concrete forced mate?

**25. Passive 2.Na3 (inaccuracy)** (move, intermediate) — engine: played Na3 / best Nf3 (Good)

> By playing Na3, you have developed a piece, but you have slightly shifted your focus away from the center compared to the standard Nf3. Your opponent will likely respond with e6, challenging your central control and preparing to push d5, which forces you to decide how to handle the pressure in the middle of the board. While your move is playable, it gives Black a bit more freedom to set up their own structure, whereas a central knight jump would have made it harder for them to equalize so easily. How do you think you will support your e4 pawn once they start pushing their d-pawn?
