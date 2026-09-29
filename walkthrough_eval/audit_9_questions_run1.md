# Walkthrough check: 9 yes/no questions (24 Sep 2026, 17:00)

**Answer these with boards:** https://claude.ai/artifact/RXVx2NjAcuirnqbXqKoqL4 (answers save there; Claude reads them).

I read all 13 new coach answers. Every one says who plays each move, and "followed by"
is gone. Below are the only sentences I have doubts about. Answer each **Y** or **N**
(in chat, like `1Y 2N 3Y …`, is fine). The full answers and facts are in
`walkthrough_eval/audit_full.md` if you want them. You don't need to open it.

## A. Did the coach claim more than the facts say?

**1.** (...Nb4, advanced) Coach: "...a6 would have **forced** the bishop to retreat."
Facts: a6 only **attacks** the bishop. The bishop could also take your knight on c6.
Wrong? **Y / N**

**2.** (...Nb4, advanced) Coach: "White can attack your knight with **the c3 or a3 pawn**."
Facts: the pawns are on **c2 and a2**. They would go to c3 or a3.
Wrong? **Y / N**

**3.** (...Nb4, beginner) Coach: "White can attack your knight with the c- or a-pawn,
**so** moving it to b4 was a mistake." Facts: the engine's line never plays c3 or a3,
so nothing shows that's *why* it was a mistake.
Wrong? **Y / N**

**4.** (...Nxe4, intermediate) Coach: "capture on f2 with your knight to **force White's
queen away**." Facts: Nxf2 only attacks the queen, and in the engine's line White
never moves the queen (it plays Bxc6+ instead).
Wrong? **Y / N**

**5.** (Sicilian, advanced) Coach: "your opponent will likely play ...Ng4, which
**allows you** to attack their knight later with h3 or f3." It makes Black's best move
sound like a gift for you. (Our board facts miss what Ng4 is really for.)
Misleading? **Y / N**

**6.** (Italian, intermediate) Coach: c3's idea is "to open a path for your queen."
That's true per the facts, but the main idea of c3 is to prepare d4, which the line
plays next.
Is a true but minor reason misleading? **Y / N**

## B. Is it OK for the coach to stay silent?

**7.** For ...Be7, a4 and h4, the coach never says *why* the move was bad. It only says
"brings your bishop out" / "opens a line for your rook". Our board facts found no
reason, so the coach correctly made nothing up.
Is that acceptable for now? **Y / N**

## C. Style

**8.** Small evals are worded strongly: "+0.31 means **you are ahead**", "-0.32 means
**Black is ahead**." Should anything under about 0.5 say "about equal"? **Y / N**

**9.** Beginners get notation in brackets: "move your pawn to c6 **[c6]**",
"Ba4 **[Ba4]**". Keep the brackets? **Y / N**

## Your answers

1: · 2: · 3: · 4: · 5: · 6: · 7: · 8: · 9:
