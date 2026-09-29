# Walkthrough audit: old vs new coach (24 Sep 2026, 15:15)

For each case: what the new coach was given (who plays each move, and the
board facts it may use as reasons), then the old answer and the new one.
Tick the boxes for the **new** answer. A reason that isn't in the board
facts or the line is an invented reason, even if it sounds right.

## 0. Your example: ...Nb4 (all three levels)

```
Your move: ...Nb4 (Mistake, -0.44 → -1.46). Board facts: White can attack it next move by pushing the pawn on c2 to c3, or the pawn on a2 to a3.
1. Opponent (White), likely reply: O-O (the king, e1 to g1). Board facts: castles kingside: White's king moves away from the centre and a rook comes toward the middle.
2. Student (Black), best move: ...c6 (the pawn, c7 to c6). Board facts: attacks White's bishop on b5 with a pawn, which is worth less; opens a line for Black's queen on d8.
3. Opponent (White), likely reply: Bc4 (the bishop, b5 to c4). Board facts: moves the bishop away from the attack by Black's pawn on c6; Black can attack it next move by pushing the pawn on d7 to d5, or the pawn on b7 to b5.
4. Student (Black), best move: ...d5 (the pawn, d7 to d5). Board facts: the very next move in the line captures it on d5; attacks White's bishop on c4 with a pawn, which is worth less; attacks White's pawn on e4, which nothing defends; opens a line for Black's bishop on c8; opens a line for Black's queen on d8.
Instead: ...a6. Board facts: attacks White's bishop on b5 with a pawn, which is worth less.
```

**New, beginner:** Your move allows White to attack your knight with the c-pawn or the a-pawn, so moving your knight to b4 [Nb4] was a mistake. The evaluation is -1.46, meaning White is ahead.

White will likely move their king to safety and bring a rook to the center with castle (O-O). You should then challenge White's bishop, so a natural idea is to move your pawn to c6 [c6].

What do you think might happen if you had instead challenged the bishop by moving your pawn to a6 [a6]?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

**New, intermediate:** By moving your knight to b4, you have placed it where White can target it by pushing their c2 or a2 pawns. The evaluation is -1.46, which means White is ahead. Your opponent will likely castle kingside by playing O-O. To challenge the bishop on b5, your best reply is ...c6. Your opponent's strongest answer is probably Bc4, moving the bishop to safety. Since this move was a mistake, do you see why attacking the bishop with the pawn on a6 might have been more effective?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

**New, advanced:** Your move allows White to attack your knight with either the c3 or a3 pawn. The evaluation is -1.46, which favors White. White will likely O-O. To challenge the bishop on b5, your best reply is ...c6. White will likely play Bc4. To open lines for your pieces and attack the e4 pawn, your best move is ...d5. It is a pity you didn't play ...a6, which would have forced the bishop to retreat. How do you plan to handle the pressure on your knight after your next move?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 1. Develop with ...Be7 (mistake) (move, intermediate)

FEN: `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5`

```
Your move: ...Be7 (Mistake, -0.87 → -2.42). Board facts: brings Black's bishop into play from its starting square.
1. Opponent (White), likely reply: Nxe5 (the knight, f3 to e5). Board facts: captures Black's pawn on e5; opens a line for White's queen on d1.
2. Student (Black), best move: ...O-O (the king, e8 to g8). Board facts: castles kingside: Black's king moves away from the centre and a rook comes toward the middle.
3. Opponent (White), likely reply: Bxc6 (the bishop, b5 to c6). Board facts: the very next move in the line captures it on c6; captures Black's knight on c6.
4. Student (Black), best move: ...bxc6 (the pawn, b7 to c6). Board facts: the very next move in the line captures it on c6; takes back on c6, capturing White's bishop.
5. Opponent (White), likely reply: Nxc6 (the knight, e5 to c6). Board facts: takes back on c6, capturing Black's pawn; attacks Black's queen on d8 with a knight, which is worth less.
Instead: ...dxe4. Board facts: captures White's pawn on e4; attacks White's knight on f3 with a pawn, which is worth less; opens a line for Black's queen on d8.
```

**Old:** It looks like your move Be7 allows your opponent to gain a significant advantage, shifting the evaluation to -2.42 in their favor. By playing this way, you allow them to follow up with Nxe5, putting immediate pressure on your center, and after you castle, they can play Bxc6 to break up your queenside structure before winning the pawn on c6 with Nxc6. They end up with a much stronger position because you missed the chance to simplify the center yourself with dxe4. Given how the game is unfolding, why do you think taking that central pawn might have been safer for your position?

**New:** Your move brings your bishop into play from its starting square. The evaluation is -2.42, which favors White. 

White will likely capture your pawn on e5 with Nxe5, opening a line for their queen. You should then get your king to safety by playing ...O-O. White's bishop will likely capture your knight with Bxc6. You will then recapture the bishop with your pawn, playing ...bxc6. White will likely reply with Nxc6, attacking your queen with a knight. How might you prepare for that knight jump, considering you could have instead played ...dxe4 to capture White's pawn and attack their knight?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 2. Scholar's mate trap: ...Nf6?? (blunder) (move, beginner)

FEN: `r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3`

```
Your move: ...Nf6 (Blunder, +0.40 → -100.00). Board facts: brings Black's knight into play from its starting square; attacks White's pawn on e4, which nothing defends; attacks White's queen on h5 with a knight, which is worth less.
1. Opponent (White), likely reply: Qxf7# (the queen, h5 to f7). Board facts: captures Black's pawn on f7; moves the queen away from the attack by Black's knight on f6; gives checkmate.
Instead: ...g6. Board facts: attacks White's queen on h5 with a pawn, which is worth less.
```

**Old:** That move is a mistake because it leaves your king vulnerable to an immediate checkmate. Your opponent can now play Qxf7, which uses the bishop you already have staring at that pawn to trap your king with no way out. Before you bring your knight out, it is much safer to play g6 to block that direct line to your weak f7 square. Can you see why that pawn push would have kept your king safe?

**New:** By moving your knight [Nf6], you bring it into play and attack the pawn on e4, but you also put your knight in a position where it ignores the threat to your f7 pawn. The evaluation is -100.00, which favors White. Your opponent's strongest answer is probably queen takes f7 [Qxf7#], which delivers checkmate. You could have attacked the queen with your pawn [g6] instead. What do you think you might have missed about your king's safety?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 3. ...Nxe4? loses material (mistake) (move, intermediate)

FEN: `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5`

```
Your move: ...Nxe4 (Mistake, -0.87 → -2.47). Board facts: captures White's pawn on e4; White can attack it next move by pushing the pawn on d2 to d3; opens a line for Black's queen on d8.
1. Opponent (White), likely reply: d3 (the pawn, d2 to d3). Board facts: attacks Black's knight on e4 with a pawn, which is worth less; opens a line for White's bishop on c1.
2. Student (Black), best move: ...Nxf2 (the knight, e4 to f2). Board facts: captures White's pawn on f2; moves the knight away from the attack by White's pawn on d3; attacks White's queen on d1 with a knight, which is worth less.
3. Opponent (White), likely reply: Bxc6+ (the bishop, b5 to c6). Board facts: the very next move in the line captures it on c6; captures Black's knight on c6; gives check to Black's king.
4. Student (Black), best move: ...bxc6 (the pawn, b7 to c6). Board facts: gets Black's king out of check; takes back on c6, capturing White's bishop.
Instead: ...dxe4. Board facts: captures White's pawn on e4; attacks White's knight on f3 with a pawn, which is worth less; opens a line for Black's queen on d8.
```

**Old:** Taking the pawn with your knight was a tough mistake here, as it allows your opponent to disrupt your position with d3. If they play that, your knight on e4 is immediately hit, and after you likely respond with Nxf2, they can respond with Bxc6+ followed by bxc6 to dismantle your queenside structure. Because you lose that pressure and allow them to stabilize with a lead of -2.47, you are now facing a significantly harder defense than you would have had with dxe4. How would you have handled the center if you had captured with the pawn instead?

**New:** By capturing the pawn on e4, you have opened a line for your queen, but you have also invited White to attack your knight with a d3 pawn push. The evaluation is -2.47, favoring White. Your opponent will likely play d3 to attack your knight and develop their bishop. You should then capture the pawn on f2 with your knight to force White's queen away, so your best reply is ...Nxf2. White will likely play Bxc6+ to put your king in check. You then use your pawn to capture the bishop, so your best reply is ...bxc6. It is interesting to compare this to how the position might have looked if you had played ...dxe4 to attack the knight on f3 instead.

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 4. Wing push 1.a4 (passive) (move, beginner)

FEN: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`

```
Your move: a4 (Inaccuracy, +0.49 → -0.32). Board facts: opens a line for White's rook on a1.
1. Opponent (Black), likely reply: ...e5 (the pawn, e7 to e5). Board facts: opens a line for Black's queen on d8; opens a line for Black's bishop on f8.
2. Student (White), best move: e4 (the pawn, e2 to e4). Board facts: opens a line for White's queen on d1; opens a line for White's bishop on f1.
Instead: e4. Board facts: opens a line for White's queen on d1; opens a line for White's bishop on f1.
```

**Old:** Starting with a4 doesn't help you control the center, and the engine shows an evaluation of -0.32, which means your opponent now has a slight edge. After your move, they are likely to respond with e5 to grab that central space, followed by your e4, their Nf6, your Nf3, their d5, and finally an exchange where you lose your pawn on d5. Playing e4 instead would have helped you claim the middle of the board right from the start. Since you want to fight for the center early, what piece do you think would be most helpful to bring out first?

**New:** You opened a line for your rook on a1 with your move [a4]. The current evaluation is -0.32, which means Black is ahead. 

Your opponent will likely respond by pushing their pawn [e5] to open lines for their queen and bishop. You should then bring your own pawn into play [e4] to open lines for your queen and bishop. Since your first move was an inaccuracy, perhaps you can see why playing [e4] to open lines for your queen and bishop is more effective?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 5. Edge push 1.h4 (passive) (move, beginner)

FEN: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`

```
Your move: h4 (Mistake, +0.49 → -0.43). Board facts: opens a line for White's rook on h1.
1. Opponent (Black), likely reply: ...d5 (the pawn, d7 to d5). Board facts: opens a line for Black's bishop on c8; opens a line for Black's queen on d8.
2. Student (White), best move: d4 (the pawn, d2 to d4). Board facts: opens a line for White's bishop on c1; opens a line for White's queen on d1.
Instead: e4. Board facts: opens a line for White's queen on d1; opens a line for White's bishop on f1.
```

**Old:** You played h4, but that move doesn't help you take control of the center, and the computer now gives you a slightly negative score of -0.43. Your opponent might respond with d5 to claim space in the middle, followed by moves like d4 and Nf6 that let them develop their pieces faster than yours. Playing e4 instead would have put a pawn in the center to help open paths for your bishop and queen. What do you think is the best way to get your center pawns into the game?

**New:** By playing h4, you open a line for your rook on h1. The evaluation is -0.43, which means Black is currently ahead. Your opponent will likely play ...d5 to open lines for their bishop and queen. You should then play d4 to open lines for your own queen and bishop. You could have instead opened lines for your queen and bishop by playing e4. What do you think about the placement of your pieces now?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 6. Premature 3.Ng5?? (blunder) (move, advanced)

FEN: `r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3`

```
Your move: Ng5 (Blunder, +0.35 → -4.00). Board facts: the very next move in the line captures it on g5; Black can attack it next move by pushing the pawn on h7 to h6, or the pawn on f7 to f6; opens a line for White's queen on d1.
1. Opponent (Black), likely reply: ...Qxg5 (the queen, d8 to g5). Board facts: captures White's knight on g5; White can attack it next move by pushing the pawn on h2 to h4, or the pawn on f2 to f4.
2. Student (White), best move: d4 (the pawn, d2 to d4). Board facts: opens a line for White's bishop on c1; opens a line for White's queen on d1.
3. Opponent (Black), likely reply: ...Qg6 (the queen, g5 to g6). Board facts: moves the queen away from the attack by White's bishop on c1; attacks White's pawn on e4, which nothing defends; no longer defends Black's pawn on e5, which the line goes on to capture.
4. Student (White), best move: dxe5 (the pawn, d4 to e5). Board facts: captures Black's pawn on e5; opens a line for White's queen on d1.
Instead: Bb5. Board facts: brings White's bishop into play from its starting square; Black can attack it next move by pushing the pawn on a7 to a6.
```

**Old:** Moving your knight to g5 was a tough misstep because it invites your opponent to simply play Qxg5, winning a piece for nothing and leaving you with a -4.00 evaluation that heavily favors black. Even if you follow the engine’s predicted path of d4, Qg6, dxe5, d6, and exd6, the exchange of your pawn allows them to centralize their bishop with Bxd6, leaving you significantly behind in material. While your intention was likely to eye the f7 square, it neglected the fundamental need for sound development that a move like Bb5 would have provided to keep the position at +0.35. Looking at the board now, how would you approach your development differently if you could reset this position?

**New:** Your move opens a line for your queen, but it leaves your knight on g5 where it can be captured or attacked by h6 or f6. The evaluation is -4.00, meaning Black is ahead. Your opponent will likely play ...Qxg5, capturing your knight. You should then play d4 to open lines for your bishop and queen. Your opponent will likely respond with ...Qg6 to escape your bishop and attack your e4 pawn. You then play dxe5 to capture their pawn and open a line for your queen. You could have instead developed your bishop with Bb5 to bring it into play. What do you think about how the position shifts after these exchanges?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 7. Ruy Lopez (after 3...a6) (position, beginner)

FEN: `r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4`

```
Eval: +0.42 pawns.
1. Student (White), best move: Ba4 (the bishop, b5 to a4). Board facts: moves the bishop away from the attack by Black's pawn on a6; Black can attack it next move by pushing the pawn on b7 to b5.
2. Opponent (Black), likely reply: ...Nf6 (the knight, g8 to f6). Board facts: brings Black's knight into play from its starting square; attacks White's pawn on e4, which nothing defends.
```

**Old:** Your bishop is under attack by the pawn, so moving it to a4 keeps it active while staying safe from that pawn's reach. The evaluation is +0.42, which means the position is currently slightly better for you. After you play Ba4, your opponent will likely continue with Nf6, then you can castle to get your king to safety before preparing to challenge their center. If you were playing this game, what do you think your main plan should be after you finish developing your pieces?

**New:** Your bishop is currently under attack by Black's pawn on a6, so a natural idea is to move the bishop to safety. That's why your best reply is Ba4 [Ba4]. Your opponent's strongest answer is probably to bring their knight into play from g8 to f6 [...Nf6]. This evaluation is +0.42, which favors you. How would you plan to protect your pawn on e4 after their knight moves?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 8. Italian Game (Giuoco Piano) (position, intermediate)

FEN: `r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4`

```
Eval: +0.20 pawns.
1. Student (White), best move: c3 (the pawn, c2 to c3). Board facts: opens a line for White's queen on d1.
2. Opponent (Black), likely reply: ...Nf6 (the knight, g8 to f6). Board facts: brings Black's knight into play from its starting square; attacks White's pawn on e4, which nothing defends; opens a line for Black's rook on h8.
3. Student (White), best move: d4 (the pawn, d2 to d4). Board facts: the very next move in the line captures it on d4; attacks Black's bishop on c5 with a pawn, which is worth less; opens a line for White's bishop on c1; opens a line for White's queen on d1.
```

**Old:** It’s a balanced position with an evaluation of +0.20 for you, meaning you have a tiny edge just from being White. By playing c3, you are preparing to secure the center by supporting a d4 pawn push. Following this, you likely will play d4 to challenge their bishop, and if they exchange, you can drive their knight away with e5, ultimately gaining more space and central control. How do you think you can maintain that pressure if your opponent decides to ignore your pawn expansion?

**New:** To prepare for your queen to move, a natural idea is to open a path for her, so your best reply is c3. The evaluation is +0.20, which favors you. Your opponent’s strongest answer is probably ...Nf6, as this brings their knight into play and attacks your unprotected pawn on e4. To challenge the bishop on c5 while opening lines for your queen and bishop, a natural idea is to strike in the center, so your best response is d4. How do you feel about the position of your pieces now?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 9. Sicilian Najdorf (position, advanced)

FEN: `rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6`

```
Eval: +0.51 pawns.
1. Student (White), best move: Be3 (the bishop, c1 to e3). Board facts: brings White's bishop into play from its starting square; opens a line for White's queen on d1.
2. Opponent (Black), likely reply: ...e5 (the pawn, e7 to e5). Board facts: attacks White's knight on d4 with a pawn, which is worth less.
3. Student (White), best move: Nb3 (the knight, d4 to b3). Board facts: moves the knight away from the attack by Black's pawn on e5; opens a line for White's queen on d1; opens a line for White's bishop on e3.
4. Opponent (Black), likely reply: ...Ng4 (the knight, f6 to g4). Board facts: White can attack it next move by pushing the pawn on h2 to h3, or the pawn on f2 to f3; opens a line for Black's queen on d8.
```

**Old:** The engine evaluates this position at +0.51, giving you a slight but stable opening edge. Playing Be3 is a strong developing move that reinforces your control over the center and prepares to meet your opponent's expansion. In the main line, Black likely continues with e5 to challenge your knight, which prompts you to retreat to b3 before rerouting the bishop to d2 to address the pressure from Ng4. Does this structure feel solid to you, or would you have preferred to challenge the d6 pawn immediately?

**New:** You want to bring your bishop into play and open a line for your queen, so a natural idea is Be3. The evaluation is +0.51, favoring White. Your opponent's strongest answer is probably ...e5, which attacks your knight with a pawn of lower value. To move your knight away from that attack and open lines for your queen and bishop, your best reply is Nb3. Finally, your opponent will likely play ...Ng4, which allows you to attack their knight later by pushing a pawn to h3 or f3. How do you think these pawn structures will affect your control of the center?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:

## 10. Queen's Gambit Declined (position, intermediate)

FEN: `rnbqk2r/ppp1bppp/4pn2/3p2B1/2PP4/2N5/PP2PPPP/R2QKBNR w KQkq - 4 5`

```
Eval: +0.31 pawns.
1. Student (White), best move: e3 (the pawn, e2 to e3). Board facts: opens a line for White's queen on d1; opens a line for White's bishop on f1.
2. Opponent (Black), likely reply: ...h6 (the pawn, h7 to h6). Board facts: attacks White's bishop on g5 with a pawn, which is worth less.
3. Student (White), best move: Bh4 (the bishop, g5 to h4). Board facts: moves the bishop away from the attack by Black's pawn on h6; Black can attack it next move by pushing the pawn on g7 to g5.
```

**Old:** Playing e3 is a solid choice here because it shores up your center and prepares to develop your kingside pieces, giving you a slight edge with an evaluation of +0.31. The main plan is to tuck your bishop back to h4 if your opponent challenges it with h6, which keeps the pressure on their pinned knight while you finish your development with Nf3. Once you trade your bishop for their knight after they jump into the center with Ne4, you will have a stable position to build your middle-game attack. Since your opponent might try to mirror your development by castling, how would you like to coordinate your rooks to support your center once the queenside is clear?

**New:** You need to open lines for your queen on d1 and bishop on f1, so a natural idea is e3. The evaluation is +0.31, which means you are currently ahead. Your opponent's strongest answer is probably ...h6, which attacks your bishop on g5 with a pawn. Since you need to move your bishop away from that attack, your best reply is Bh4. What do you think your next plan should be if they push their pawn to g5?

- [ ] Every move says who plays it (no "followed by" across sides)
- [ ] The idea comes before each move recommended to you
- [ ] Every reason matches a board fact above, or what the line shows
- [ ] No wrong chess claim
- Notes:
