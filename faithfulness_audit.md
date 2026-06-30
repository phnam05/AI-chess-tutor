# Faithfulness — human audit

**You are the ground truth.** For each explanation judge ONLY whether the coach stuck to the engine's facts or invented something — *fidelity to the engine*, not whether it is the best chess. Then, separately, note anything you would reword even when it is faithful.

Per case, fill:

- **A. Faithful to the engine?** — `Yes` / `No`
- **B. If No, what did it invent?** — the move or claim, else `—`
- **C. What I'd change (even if faithful)** — free text, else `nothing`
- **D. (optional) Change type** — `wording` / `too long` / `too short` / `too vague` / `missed teaching point` / `level off` / `other`

## Summary

| # | Case | Phase | Type | Checker | A. Faithful? | Agree w/ checker? | D. Change type |
|--:|------|-------|------|:-------:|:------------:|:-----------------:|----------------|
| 1 | Ruy Lopez (after 3...a6) | opening | position | clean | ____ | ____ | ____ |
| 2 | Italian Game (Giuoco Piano) | opening | position | clean | ____ | ____ | ____ |
| 3 | Sicilian Najdorf | opening | position | clean | ____ | ____ | ____ |
| 4 | Queen's Gambit Declined | opening | position | clean | ____ | ____ | ____ |
| 5 | French Defence (Winawer) | opening | position | clean | ____ | ____ | ____ |
| 6 | King's Indian Defence | opening | position | clean | ____ | ____ | ____ |
| 7 | Caro-Kann Defence | opening | position | clean | ____ | ____ | ____ |
| 8 | Closed centre, Black to plan | middlegame | position | clean | ____ | ____ | ____ |
| 9 | Queen on f4, White attacking | middlegame | position | clean | ____ | ____ | ____ |
| 10 | Open game, Black to move | middlegame | position | clean | ____ | ____ | ____ |
| 11 | King + pawn vs king | endgame | position | clean | ____ | ____ | ____ |
| 12 | Rook + pawn endgame | endgame | position | clean | ____ | ____ | ____ |
| 13 | Queen vs lone king (mating) | endgame | position | clean | ____ | ____ | ____ |
| 14 | Central king & pawn | endgame | position | clean | ____ | ____ | ____ |
| 15 | Italian: 3.Bb5 (good) | opening | move | clean | ____ | ____ | ____ |
| 16 | Opening move 1.e4 (good) | opening | move | clean | ____ | ____ | ____ |
| 17 | Ruy Lopez: 4.Ba4 (good) | opening | move | clean | ____ | ____ | ____ |
| 18 | Develop with ...Be7 (good) | middlegame | move | clean | ____ | ____ | ____ |
| 19 | Scotch: ...exd4 (good) | opening | move | clean | ____ | ____ | ____ |
| 20 | Scholar's mate trap: ...Nf6?? (blunder) | opening | move | clean | ____ | ____ | ____ |
| 21 | ...Nxe4?? drops a piece (blunder) | middlegame | move | clean | ____ | ____ | ____ |
| 22 | Wing push 1.a4 (passive) | opening | move | clean | ____ | ____ | ____ |
| 23 | Edge push 1.h4 (passive) | opening | move | clean | ____ | ____ | ____ |
| 24 | Premature 3.Ng5?! (inaccuracy) | opening | move | clean | ____ | ____ | ____ |
| 25 | Passive 2.Na3 (inaccuracy) | opening | move | clean | ____ | ____ | ____ |

## Cases

### 1. Ruy Lopez (after 3...a6)  (position, beginner)

**Board (FEN)** — `r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4`
**Engine facts** — best: `Ba4` · eval: `+0.42 pawns` · PV: `Ba4, Nf6, O-O, Nxe4, d4, b5`
**Checker** — clean (grounded: —)

**Coach said:**
> Pulling your bishop back to a4 keeps it safe while maintaining pressure on the knight that is protecting the center pawn. The slight edge for you comes from keeping your pieces active and ready to castle your king to safety soon. If your opponent tries to chase the bishop away, how do you think your center pawns might help you control more of the board?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 2. Italian Game (Giuoco Piano)  (position, intermediate)

**Board (FEN)** — `r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4`
**Engine facts** — best: `c3` · eval: `+0.20 pawns` · PV: `c3, Nf6, d4, exd4, e5, d5`
**Checker** — clean (grounded: c3, d4, Nf6)

**Coach said:**
> It is great to see you developing your pieces so well, and playing c3 here is a smart way to prepare for a central push. By supporting a future d4 move, you are aiming to claim more space in the center and challenge their control of the board. If black responds with Nf6, you can follow through with d4 to open lines for your pieces and fight for the initiative. If you were sitting at the board, where do you think your pieces would be most active once that central pawn tension is resolved?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 3. Sicilian Najdorf  (position, advanced)

**Board (FEN)** — `rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6`
**Engine facts** — best: `Be3` · eval: `+0.51 pawns` · PV: `Be3, e5, Nb3, Ng4, Bd2, Nf6`
**Checker** — clean (grounded: Be3, e5)

**Coach said:**
> By playing Be3, you are cementing your control over the d4-square and preparing for a solid Sicilian setup that balances space with flexibility. This move secures a slight edge of +0.51 because it anticipates the common e5 push, allowing you to reposition your knight to b3 to maintain central tension while preparing to challenge the kingside knight. Think about how this development choice dictates the flow of the game compared to a more aggressive or immediate pawn expansion; how would you plan to maneuver your pieces if your opponent chooses a more restrained development instead?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 4. Queen's Gambit Declined  (position, intermediate)

**Board (FEN)** — `rnbqk2r/ppp1bppp/4pn2/3p2B1/2PP4/2N5/PP2PPPP/R2QKBNR w KQkq - 4 5`
**Engine facts** — best: `e3` · eval: `+0.31 pawns` · PV: `e3, h6, Bh4, O-O, Nf3, Ne4`
**Checker** — clean (grounded: e3, h6)

**Coach said:**
> Playing e3 is a solid choice here because it secures your central pawn structure and opens the path for your light-squared bishop to retreat safely if challenged. By tucking the bishop away to h4 after black plays h6, you maintain long-term pressure on the board and keep your pieces flexible for the upcoming middlegame. This move keeps the evaluation slightly in your favor by ensuring your development remains harmonious while you wait to see how black chooses to challenge your center. Given how you want to deploy your knights and complete your kingside development, where do you think your pieces will have the most influence once you castle?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 5. French Defence (Winawer)  (position, advanced)

**Board (FEN)** — `rnbqk1nr/ppp2ppp/4p3/3p4/1b1PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 2 4`
**Engine facts** — best: `e5` · eval: `+0.64 pawns` · PV: `e5, c5, a3, Bxc3+, bxc3, Qc7`
**Checker** — clean (grounded: e5, c5)

**Coach said:**
> By playing e5, you immediately claim central space and force the black knight to relocate to a less ideal square, which justifies your +0.64 advantage. This push creates a clear strategic imbalance where you accept a slightly compromised pawn structure in exchange for superior control of the center and long-term attacking potential. If black continues with the critical line of c5 and an exchange on c3, you are left with the bishop pair and a solid space advantage to work with in the resulting middlegame. How would you plan to utilize your extra space to restrict black's pieces once the minor pieces start coming off the board?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 6. King's Indian Defence  (position, intermediate)

**Board (FEN)** — `rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N5/PP3PPP/R1BQKBNR w KQkq - 0 5`
**Engine facts** — best: `Nf3` · eval: `+0.65 pawns` · PV: `Nf3, O-O, Be2, e5, Be3, Qe8`
**Checker** — clean (grounded: e5)

**Coach said:**
> It is time to develop your knight to f3 to support your center and prepare for kingside castling. By doing this, you are solidifying your control over the d4 and e5 squares, which gives you a slight edge in space and long-term stability. Your opponent will likely look to challenge your control of the center with e5, but by following up with your bishop, you maintain a strong setup that keeps your pieces coordinated. How would you plan to react if black continues to pressure your center after you castle?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 7. Caro-Kann Defence  (position, beginner)

**Board (FEN)** — `rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3`
**Engine facts** — best: `e5` · eval: `+0.30 pawns` · PV: `e5, Bf5, c4, e6, Nc3, Ne7`
**Checker** — clean (grounded: e5)

**Coach said:**
> Pushing your pawn to e5 is a great way to grab extra space in the center and cramp your opponent's pieces. This move forces their bishop to move again and sets you up to control more of the board. Since the game is still very even, how would you decide where to develop your knights next to support this space advantage?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 8. Closed centre, Black to plan  (position, intermediate)

**Board (FEN)** — `r2q1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 b - - 0 9`
**Engine facts** — best: `Qc7` · eval: `-4.79 pawns` · PV: `Qc7, Bc2, Rad8, a4, Rfe8, Qe2`
**Checker** — clean (grounded: Qc7)

**Coach said:**
> You are in a very solid position here, and playing Qc7 is a great way to centralize your queen while keeping your options flexible. By stepping off the d-file, you clear the way for your rook to join the fight, setting you up to control the center and put pressure on their d4 pawn. The evaluation is heavily in your favor because your pieces are poised to dominate the open files, making it hard for White to find any counterplay. How do you think your rook on d8 will change the way White has to defend their central pawns?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 9. Queen on f4, White attacking  (position, advanced)

**Board (FEN)** — `r1bq1rk1/pp3pp1/2n1p3/2P1P2p/5Q2/8/PPP2PPP/R1B1KB1R w KQ - 1 13`
**Engine facts** — best: `Be3` · eval: `+2.68 pawns` · PV: `Be3, Qd5, Bc4, Qxe5, O-O-O, Qxf4`
**Checker** — clean (grounded: Be3)

**Coach said:**
> With an evaluation of +2.68, you have a commanding advantage here because your space advantage and central control severely cramp Black’s development. Playing Be3 is the strongest continuation because it brings your final minor piece into the game while reinforcing the critical d4 square and preparing to link your rooks. By solidifying the center, you effectively neutralize Black's attempts to challenge your advanced e5 pawn, allowing you to transition into a long-term squeeze. How would you plan to coordinate your rooks once you complete your development?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 10. Open game, Black to move  (position, beginner)

**Board (FEN)** — `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5`
**Engine facts** — best: `dxe4` · eval: `-0.87 pawns` · PV: `dxe4, Nxe5, Qd5, Bxc6+, bxc6, d4`
**Checker** — clean (grounded: dxe4, Nxe5)

**Coach said:**
> You should play dxe4 because it immediately captures the center pawn and forces White to react to the pressure on their knight. This move gives you a slight advantage because it clears the path for your queen and disrupts White's setup in the middle of the board. If White plays the main response of Nxe5, how would you develop your pieces to keep the initiative?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 11. King + pawn vs king  (position, beginner)

**Board (FEN)** — `8/8/4k3/8/4K3/8/4P3/8 w - - 0 1`
**Engine facts** — best: `e3` · eval: `+5.11 pawns` · PV: `e3, Kf6, Kd5, Kf7, e4, Ke7`
**Checker** — clean (grounded: e3)

**Coach said:**
> You are currently in a winning king and pawn endgame, and playing e3 is the perfect way to support your king and prepare to push your pawn all the way to promotion. By moving the pawn forward, you create a solid base that protects your king while giving you a clear path to make a queen. If you follow this plan, you will likely be able to force your opponent's king away and win the game. How do you think your opponent might try to stop your pawn from reaching the other side?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 12. Rook + pawn endgame  (position, intermediate)

**Board (FEN)** — `8/8/8/4k3/8/8/4P3/4K2R w K - 0 1`
**Engine facts** — best: `Kd2` · eval: `+6.30 pawns` · PV: `Kd2, Ke4, Rg1, Kd4, e3+, Ke4`
**Checker** — clean (grounded: Kd2, Rg1, e3)

**Coach said:**
> You have a significant advantage here because your rook and king can easily coordinate to force the enemy king away from the center. Playing Kd2 is the best way to activate your king and support your pawn, as it prepares to restrict the opponent's movement while securing your position. By following up with Rg1 and e3, you’re creating a wall that will eventually force the black king to give up ground. How would you plan to safely push that e-pawn forward once your king reaches a more active square?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 13. Queen vs lone king (mating)  (position, beginner)

**Board (FEN)** — `8/5k2/8/8/8/8/5K2/5Q2 w - - 0 1`
**Engine facts** — best: `Kg3+` · eval: `+5.09 pawns` · PV: `Kg3+, Kg6, Kh4, Kh6, Qf5, Kg7`
**Checker** — clean (grounded: —)

**Coach said:**
> It looks like you have a great chance to corner your opponent's king here. By moving your king to g3 with check, you force their king to move and begin cutting off their escape squares. This helps you trap them against the edge of the board so your queen can deliver a final blow. How do you think you can keep their king trapped after they move away?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 14. Central king & pawn  (position, advanced)

**Board (FEN)** — `8/8/8/3k4/8/3K4/3P4/8 w - - 0 1`
**Engine facts** — best: `Kc3` · eval: `+0.44 pawns` · PV: `Kc3, Kc5, d4+, Kb6, Kc4`
**Checker** — clean (grounded: Kc3, Kc5, d4+)

**Coach said:**
> You are facing a classic endgame scenario where the distance of your king from the opponent's critical squares determines the outcome. By playing Kc3, you adopt a waiting profile that forces your opponent to commit their king first, which is essential given that your +0.44 edge hinges on maintaining the tension while preparing to push your d-pawn. If they respond with Kc5, the critical follow-up d4+ allows you to seize the initiative and control the center, putting the burden of defense entirely on them. How do you think the dynamic shifts if your opponent tries to avoid the pawn break instead of challenging your king directly?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 15. Italian: 3.Bb5 (good)  (move, beginner)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3` (the position *before* the played move)
**Engine facts** — played: `Bb5` · best: `Bb5` · grade: `Best` · evals: played `+0.44` / best `+0.35` · refutation: `a6, Ba4, Nf6, O-O, Be7, Re1`
**Checker** — clean (grounded: a6)

**Coach said:**
> That is a fantastic move! By putting your bishop on b5, you are putting direct pressure on the knight that is protecting your opponent's center pawn. If your opponent plays a6 to challenge you, you can simply retreat to a4, keeping your bishop active and ready to help you castle your king to safety soon. How do you think your opponent will try to defend their center pawn now?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 16. Opening move 1.e4 (good)  (move, beginner)

**Board (FEN)** — `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` (the position *before* the played move)
**Engine facts** — played: `e4` · best: `e4` · grade: `Best` · evals: played `+0.35` / best `+0.49` · refutation: `e5, Nf3, Nc6, Bb5, a6, Bxc6`
**Checker** — clean (grounded: e4, e5)

**Coach said:**
> Great start, playing e4 is a classic way to take control of the center and open lines for your queen and bishop. By putting a pawn in the middle, you make it much easier to develop your pieces quickly and keep your king safe. If your opponent responds with e5, how do you think you can best put pressure on that pawn next?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 17. Ruy Lopez: 4.Ba4 (good)  (move, intermediate)

**Board (FEN)** — `r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4` (the position *before* the played move)
**Engine facts** — played: `Ba4` · best: `Ba4` · grade: `Best` · evals: played `+0.48` / best `+0.42` · refutation: `Nf6, O-O, b5, Bb3, Nxe4, d4`
**Checker** — clean (grounded: Ba4, Nf6, d4, b5, Nxe4)

**Coach said:**
> Great choice playing Ba4; by keeping your bishop on the board, you maintain your pressure on the e5-pawn and keep the tension in the center. The engine shows a slight advantage here, and as your opponent likely responds with Nf6 and castles, you are well-positioned to support your center with d4 after pulling your bishop back to b3. Since your opponent will probably try to challenge your control with b5 and eventually Nxe4, how do you think you can use your lead in development to punish them if they grab that pawn too greedily?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 18. Develop with ...Be7 (good)  (move, intermediate)

**Board (FEN)** — `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5` (the position *before* the played move)
**Engine facts** — played: `Be7` · best: `dxe4` · grade: `Mistake` · evals: played `-2.42` / best `-0.87` · refutation: `Nxe5, O-O, Bxc6, bxc6, Nxc6, Qd6`
**Checker** — clean (grounded: Be7, dxe4, Nxe5)

**Coach said:**
> Your move Be7 lets your opponent take control of the center because you missed the chance to simplify the position. By playing Be7 instead of dxe4, you allow White to play Nxe5, which immediately puts pressure on your knight and forces you into a defensive posture. In the expected line, White proceeds to swap off pieces, leaving you with a compromised pawn structure while they gain more space and initiative. Next time, how might you look for ways to challenge White's central pawns before they have a chance to settle in?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 19. Scotch: ...exd4 (good)  (move, intermediate)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 3` (the position *before* the played move)
**Engine facts** — played: `exd4` · best: `exd4` · grade: `Best` · evals: played `-0.42` / best `-0.18` · refutation: `Nxd4, Nf6, Nxc6, dxc6, Qxd8+, Kxd8`
**Checker** — clean (grounded: Nf6)

**Coach said:**
> You played a very solid move here, as capturing the pawn challenges White's control over the center and clears the way for your pieces. By trading this pawn, you are likely heading toward an endgame where your king becomes quite active after the queens are traded off. White will likely respond by recapturing with their knight to centralize it, but this gives you the opportunity to develop your pieces toward the center with Nf6. Since the position is now very balanced, what do you think is the best square for your bishop to influence the game once your knight reaches the center?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 20. Scholar's mate trap: ...Nf6?? (blunder)  (move, beginner)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3` (the position *before* the played move)
**Engine facts** — played: `Nf6` · best: `g6` · grade: `Blunder` · evals: played `-100.00` / best `+0.40` · refutation: `Qxf7#`
**Checker** — clean (grounded: Qxf7#, g6)

**Coach said:**
> Oh no, by moving your knight, you left your pawn on f7 undefended, and your opponent can now play Qxf7# to end the game immediately. Your king is in big trouble because that f7 square is the weakest point in your position. Would you like to look at how playing g6 earlier would have blocked that white queen from targeting your king?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 21. ...Nxe4?? drops a piece (blunder)  (move, intermediate)

**Board (FEN)** — `r1bqkb1r/ppp2ppp/2n2n2/1B1pp3/4P3/5N2/PPPP1PPP/RNBQR1K1 b kq - 1 5` (the position *before* the played move)
**Engine facts** — played: `Nxe4` · best: `dxe4` · grade: `Mistake` · evals: played `-2.47` / best `-0.87` · refutation: `d3, Nxf2, Bxc6+, bxc6, Rxe5+, Be6`
**Checker** — clean (grounded: d3, Nxf2, Bxc6+, dxe4)

**Coach said:**
> It looks like taking that pawn with your knight allowed White to grab the initiative. By playing d3, your opponent forces your knight to commit, and after you look for compensation with Nxf2, they can trade off your active bishop with Bxc6+ to shatter your queenside structure. This exchange leaves you with doubled pawns and gives White a comfortable lead in space, making it tough to coordinate your pieces. If you had played dxe4 instead, you would have maintained a much tighter game by keeping your pieces flexible. What do you think you could have done differently to keep your pawn structure intact?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 22. Wing push 1.a4 (passive)  (move, beginner)

**Board (FEN)** — `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` (the position *before* the played move)
**Engine facts** — played: `a4` · best: `e4` · grade: `Inaccuracy` · evals: played `-0.32` / best `+0.49` · refutation: `e5, e4, Nf6, Nf3, d5, exd5`
**Checker** — clean (grounded: a4, e5, e4)

**Coach said:**
> Starting with a4 is a bit unusual because it doesn't help you take control of the center or get your pieces ready to join the game. When you play on the edge like that, your opponent can easily claim the middle squares for themselves, like they would likely do by playing e5 to block your path. It is usually better to start by opening up space for your queen and bishop to move out, which is why playing e4 is a much stronger way to begin. If you could restart the game, how do you think moving your king's pawn forward would change your control of the board?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 23. Edge push 1.h4 (passive)  (move, beginner)

**Board (FEN)** — `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` (the position *before* the played move)
**Engine facts** — played: `h4` · best: `e4` · grade: `Mistake` · evals: played `-0.43` / best `+0.49` · refutation: `d5, d4, Nf6, e3, c5, c4`
**Checker** — clean (grounded: d5, e4)

**Coach said:**
> That move is a bit tricky because it doesn't help you fight for the center of the board where most of the action happens. By playing on the side, you give your opponent a chance to immediately grab the middle with a move like d5, making it easier for them to control the game. It is usually much more effective to start by moving your center pawns, like e4, to open paths for your bishop and queen. If you were starting the game again, how do you think moving your king's pawn forward would change your options?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 24. Premature 3.Ng5?! (inaccuracy)  (move, advanced)

**Board (FEN)** — `r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3` (the position *before* the played move)
**Engine facts** — played: `Ng5` · best: `Bb5` · grade: `Blunder` · evals: played `-4.00` / best `+0.35` · refutation: `Qxg5, d4, Qg6, dxe5, d6, exd6`
**Checker** — clean (grounded: Qxg5)

**Coach said:**
> By moving your knight to g5, you’ve committed a serious blunder that abandons your development in favor of a premature attack. Your opponent can now simply respond with Qxg5, capturing your knight for free and leaving you down a full piece for absolutely no compensation, which is exactly why the evaluation swings to -4.00. While you were likely hoping to create pressure on f7, your light-squared bishop remains trapped at home, leaving you unable to support your aggressive intentions. Does this look like the kind of position where you can afford to sacrifice a piece without a concrete forced mate?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---

### 25. Passive 2.Na3 (inaccuracy)  (move, intermediate)

**Board (FEN)** — `rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2` (the position *before* the played move)
**Engine facts** — played: `Na3` · best: `Nf3` · grade: `Good` · evals: played `+0.06` / best `+0.36` · refutation: `e6, Nf3, a6, Be2, d5, exd5`
**Checker** — clean (grounded: Na3, Nf3, e6, d5)

**Coach said:**
> By playing Na3, you have developed a piece, but you have slightly shifted your focus away from the center compared to the standard Nf3. Your opponent will likely respond with e6, challenging your central control and preparing to push d5, which forces you to decide how to handle the pressure in the middle of the board. While your move is playable, it gives Black a bit more freedom to set up their own structure, whereas a central knight jump would have made it harder for them to equalize so easily. How do you think you will support your e4 pawn once they start pushing their d-pawn?

- **A. Faithful?** 
- **B. Invented?** 
- **C. What I'd change:** 
- **D. Type:** 

---
