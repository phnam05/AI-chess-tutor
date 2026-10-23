# Does each input help? A quick look (23 Oct 2026, 17:48)

Your question: there was no comparison of the coach with and without the
board facts. The same move explained three ways, on 2 simple positions you
can check by eye. A preview of step 5's rows 1, 2 and 4 (`TODO.md`), **not**
the experiment: 2 hand-picked cases, one answer each.

- **A. Gemini alone:** the position (FEN) and the move played.
- **B. Gemini + Stockfish:** also the engine's review (label, evals, the
  line, the better move), no board facts. Version 1's prompt with the
  board-fact rules taken out.
- **C. Gemini + Stockfish + board facts:** the coach exactly as the app
  runs it (version 1).

Same model (`gemini-3.1-flash-lite`), level (intermediate), position text
and engine moves in all three. Script: `run.py`; full prompts and answers:
`results.json`.
Since 23 Oct, 18:28 the app has these as tabs 2–4 of every explanation
(`explainer.MODES`, prompts word for word the same as A, B, C here), plus a
tab 1 with no system prompt at all.
Page for the lab (`build_page.py` → `page.html`): https://claude.ai/artifact/NNS9V7SzmUPsK8p3Szkizy

## Case 1, opening — Black to move

1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.d3 Nf6 5.O-O, Black plays **5...Nxe4?**
**Truth:** the pawn on e4 was defended by the pawn on d3; 6.dxe4 and Black
has given a knight for a pawn (engine −0.21 → −4.46, Blunder). Better: 5...d6.

**A.** Taking the center pawn with ...Nxe4 certainly creates some tactical
complexity, but it actually allows White to gain a significant initiative
after d4. By attacking your knight and bishop simultaneously, White forces you
to give up your strong piece activity or lose material. You would have been in
much better shape had you simply played d6 to bolster your center and develop
your pieces naturally. Since we are in this position now, how do you plan to
respond to d4 to keep your knight from being trapped?

**B.** By taking the pawn on e4 with your knight, you open up the center in a
way that allows White to respond aggressively. The evaluation is -4.46, which
means White is ahead. White will likely capture your knight by pushing the pawn
on d3 to e4. You should respond by challenging the center, so your best reply
is ...d6. It is worth considering how you might have kept the balance with the
pawn move to d6 instead.

**C.** By capturing the pawn on e4, you have opened a path for your queen, but
you have also left your knight undefended. The evaluation is -4.46, meaning
White is ahead. Your opponent will likely respond by playing dxe4, which
recaptures your knight and opens lines for their own queen and bishop. To limit
the damage, your best reply is ...d6, as it develops your bishop. It would have
been better to play ...d6 immediately to open lines for your bishop and queen.
What do you think you missed about the safety of your knight before making that
capture?

## Case 2, middlegame — Black to move

1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7 5.e3 O-O 6.Nf3 Nbd7 7.cxd5 exd5 8.Bd3 c6
9.Qc2 Re8 10.O-O Nf8 11.Rab1, Black plays **11...Bf5?**
**Truth:** nothing of Black's defends f5, and the bishop on d3 (queen on c2
behind it) attacks it: 12.Bxf5 wins a bishop for nothing (engine −0.44 →
−5.36, Blunder). Better: 11...Ne4.

**A.** You played ...Bf5 to challenge my light-squared bishop, which is a very
active piece in this position. This is a solid move because it invites a
trade, helping you simplify the game and reduce the pressure on your king.
While I might choose to capture or retreat to keep the tension, forcing me to
make a decision about my bishop is a smart way to seize a bit of initiative. Do
you think it is better for me to trade bishops now, or should I try to keep my
pieces on the board to maintain attacking pressure?

**B.** Your move placing the bishop on f5 allows your opponent to simplify the
position by capturing your piece. The evaluation is -5.36, which means the
position now heavily favors White. White will likely respond with Bxf5 to
remove your bishop from the board. To maintain better pressure, you could have
occupied the center with a knight, so a natural idea is ...Ne4. What do you
think you could have done differently to protect your bishop before moving it?

**C.** Moving your bishop to f5 brings it into play, but the piece is left
undefended and can be captured immediately. The evaluation is -5.36, which
means White is ahead. Your opponent will likely capture your piece by playing
Bxf5. You could have challenged the bishop on g5 while opening a line for your
other bishop by playing ...Ne4. What do you think you might try differently
next time?

## Claude's reading (yours is the one that counts)

| | Case 1 (5...Nxe4?) | Case 2 (11...Bf5?) |
|---|---|---|
| A | Wrong: an invented d4 threat; never sees dxe4 | Wrong: calls a hanging bishop "solid", a trade offer |
| B | Capture right (it's in the line); reason vague ("opens the center") | Capture right; reason wrong ("simplify") |
| C | Right ("left your knight undefended"); one irrelevant fact, ...d6 "develops" the bishop (it opens its diagonal) | Right ("left undefended"); ...Ne4's idea true |

So, on these 2 cases: Stockfish fixed **what** happens, the board facts
fixed **why**. Our checker passed all 6 answers, A's invented threat
included, so only a person (or step 4's judge) can see this difference.

**Limits:** 2 cases, 1 run each (Gemini's wording varies between runs);
both cases are a hanging piece, the kind a board fact can see, picked by
Claude; a positional mistake (no board fact) may look quite different.
Step 5 tests this properly on fresh positions.
