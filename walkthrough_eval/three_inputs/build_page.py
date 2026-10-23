"""Build page.html from results.json: each position's board, the 3 answers side
by side with right/wrong parts marked, and the exact prompt each version got.

    python walkthrough_eval/three_inputs/build_page.py
"""
import html
import json
import re
from pathlib import Path

import chess
import chess.svg

HERE = Path(__file__).parent
DATA = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
OUT = HERE / "page.html"

A, B, C = "A. Gemini alone", "B. Gemini + Stockfish", "C. Gemini + Stockfish + board facts"
LABELS = {A: ("A", "Gemini alone", "the position and the move"),
          B: ("B", "+ Stockfish", "+ the engine's review: label, scores, line, better move"),
          C: ("C", "+ Stockfish + board facts", "+ what each move does on the board, from code")}

# Per case: the PGN, the move that punishes it (for the arrow), the truth, and
# for each answer a verdict plus the phrases to mark (good / bad / vague).
NOTES = [
    {"pgn": "1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.d3 Nf6 5.O-O",
     "move": "5...Nxe4?", "reply": "d3e4", "best": "5...d6",
     "truth": "The pawn on e4 is defended by the pawn on d3. After 6.dxe4 Black has "
              "given a knight for a pawn.",
     A: ("bad", "Wrong: invents a d4 threat, never sees dxe4",
         [("it actually allows White to gain a significant initiative after d4", "bad"),
          ("By attacking your knight and bishop simultaneously, White forces you to give up "
           "your strong piece activity or lose material", "bad"),
          ("respond to d4 to keep your knight from being trapped", "bad")]),
     B: ("vague", "Right capture, vague reason",
         [("you open up the center in a way that allows White to respond aggressively", "vague"),
          ("White will likely capture your knight by pushing the pawn on d3 to e4", "good"),
          ("You should respond by challenging the center", "vague")]),
     C: ("good", "Right reason: the knight was undefended",
         [("you have opened a path for your queen", "vague"),
          ("you have also left your knight undefended", "good"),
          ("dxe4, which recaptures your knight", "good"),
          ("as it develops your bishop", "vague")])},
    {"pgn": ("1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7 5.e3 O-O 6.Nf3 Nbd7 7.cxd5 exd5 "
             "8.Bd3 c6 9.Qc2 Re8 10.O-O Nf8 11.Rab1"),
     "move": "11...Bf5?", "reply": "d3f5", "best": "11...Ne4",
     "truth": "Nothing of Black's defends f5, and White's bishop on d3 (with the queen "
              "behind it) attacks it. 12.Bxf5 wins a bishop for nothing.",
     A: ("bad", "Wrong: calls a hanging bishop “a solid move”",
         [("to challenge my light-squared bishop", "bad"),
          ("This is a solid move because it invites a trade", "bad"),
          ("forcing me to make a decision about my bishop is a smart way to seize a bit of "
           "initiative", "bad")]),
     B: ("vague", "Right capture, wrong reason",
         [("allows your opponent to simplify the position by capturing your piece", "bad"),
          ("White will likely respond with Bxf5 to remove your bishop from the board", "good"),
          ("you could have occupied the center with a knight", "vague")]),
     C: ("good", "Right reason: the bishop was undefended",
         [("the piece is left undefended and can be captured immediately", "good"),
          ("capture your piece by playing Bxf5", "good"),
          ("challenged the bishop on g5 while opening a line for your other bishop", "good")])},
]

PHASE = ["Opening", "Middlegame"]


def esc(s):
    return html.escape(s, quote=False)


def marked(text, marks):
    out = esc(text)
    for phrase, kind in marks:
        p = esc(phrase)
        assert p in out, phrase
        out = out.replace(p, f'<mark class="{kind}">{p}</mark>', 1)
    return out


def prompt_html(text):
    """The message, with the board facts (all C gets that B doesn't) marked."""
    out = esc(text)
    return re.sub(r"(Board facts: |What their move did, from the board: )([^\n]*?)(\.)(?=\n|$)",
                  r'\1<span class="bf">\2</span>\3', out)


def board_svg(fen, played_uci, reply_uci):
    board = chess.Board(fen)
    played = chess.Move.from_uci(played_uci)
    reply = chess.Move.from_uci(reply_uci)
    return chess.svg.board(
        board, size=360, coordinates=True,
        arrows=[chess.svg.Arrow(played.from_square, played.to_square, color="#c8372dcc"),
                chess.svg.Arrow(reply.from_square, reply.to_square, color="#2a62b8cc")],
        colors={"square light": "#ebe6d6", "square dark": "#93a487",
                "margin": "#26302b", "coord": "#ebe6d6"})


def case_html(i, case, note):
    phase = PHASE[i]
    eng = case["engine"]
    played_uci = case["played"]
    cols = []
    for key in (A, B, C):
        arm = case["arms"][key]
        letter, name, _ = LABELS[key]
        kind, verdict, marks = note[key]
        cols.append(f"""
      <article class="ver ver-{letter.lower()}">
        <header><span class="tag">{letter}</span><h4>{name}</h4></header>
        <p class="verdict {kind}">{verdict}</p>
        <p class="answer">{marked(arm['text'].strip(), marks)}</p>
        <div class="prompt">
          <div class="plabel">Message sent to Gemini</div>
          <pre>{prompt_html(arm['contents'])}</pre>
          <details><summary>System instruction (same for both positions)</summary>
            <pre>{esc(arm['system'])}</pre></details>
        </div>
      </article>""")
    return f"""
  <section class="case" id="case{i + 1}">
    <div class="eyebrow">Position {i + 1} · {phase} · Black to move</div>
    <h2>Black plays <span class="mv">{note['move']}</span></h2>
    <div class="setup">
      <figure class="board">{board_svg(case['fen'], played_uci, note['reply'])}
        <figcaption><span class="key red"></span>Black's move
          <span class="key blue"></span>White's answer</figcaption></figure>
      <div class="facts">
        <p class="pgn">{note['pgn']} <strong>{note['move'][len(note['move'].split('.')[0]) + 3:]}</strong></p>
        <div class="truth"><div class="plabel">What is really going on</div>
          <p>{note['truth']}</p>
          <p class="better">Better was <span class="mv">{note['best']}</span>.</p></div>
        <dl class="eng">
          <div><dt>Engine score before</dt><dd>{eng['best_eval']}</dd></div>
          <div><dt>after the move</dt><dd>{eng['played_eval']}</dd></div>
          <div><dt>Label</dt><dd>{eng['label']}</dd></div>
        </dl>
        <p class="small">Scores in pawns, from Black's side (Stockfish, depth 15).</p>
      </div>
    </div>
    <div class="vers">{''.join(cols)}
    </div>
  </section>"""


def grid_html():
    rows = []
    for i, note in enumerate(NOTES):
        cells = "".join(f'<td><span class="chip {note[k][0]}">{note[k][1]}</span></td>'
                        for k in (A, B, C))
        rows.append(f'<tr><th scope="row"><a href="#case{i + 1}">{PHASE[i]}</a>'
                    f'<span class="mv">{note["move"]}</span></th>{cells}</tr>')
    heads = "".join(f'<th scope="col"><span class="tag">{LABELS[k][0]}</span> {LABELS[k][1]}'
                    f'<span class="gets">{LABELS[k][2]}</span></th>' for k in (A, B, C))
    return f"""<div class="gridwrap"><table class="grid">
      <thead><tr><th></th>{heads}</tr></thead>
      <tbody>{''.join(rows)}</tbody></table></div>"""


CSS = """
/* Layout: one column of cases; inside each, board + truth, then 3 answers side by side. */
:root {
  --bg: #f4f6f3; --card: #ffffff; --fg: #1c231f; --muted: #5b6760; --line: #d9dfd9;
  --accent: #2c6a4e;
  --good-bg: #d6efdf; --good-fg: #1d5b3a; --bad-bg: #f7d6d1; --bad-fg: #8e2a20;
  --vague-bg: #f5e6bf; --vague-fg: #6e5413; --bf-bg: #dde7f6; --bf-fg: #23467e;
  --pre-bg: #eef1ed;
  --display: "Newsreader", Georgia, "Times New Roman", serif;
  --body: "Public Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #111613; --card: #181f1b; --fg: #e3e9e5; --muted: #9ba7a0; --line: #2b3530;
  --accent: #74c59e;
  --good-bg: #1d4430; --good-fg: #b9ebcd; --bad-bg: #552521; --bad-fg: #f6c4bc;
  --vague-bg: #4a3c1a; --vague-fg: #f0dca3; --bf-bg: #20314c; --bf-fg: #c4d6f5;
  --pre-bg: #141a17; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #111613; --card: #181f1b; --fg: #e3e9e5; --muted: #9ba7a0; --line: #2b3530;
  --accent: #74c59e;
  --good-bg: #1d4430; --good-fg: #b9ebcd; --bad-bg: #552521; --bad-fg: #f6c4bc;
  --vague-bg: #4a3c1a; --vague-fg: #f0dca3; --bf-bg: #20314c; --bf-fg: #c4d6f5;
  --pre-bg: #141a17; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font: 15px/1.55 var(--body); }
.wrap { max-width: 1280px; margin: 0 auto; padding-block: 40px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 48px; }
h1, h2 { font-family: var(--display); font-weight: 600; text-wrap: balance; margin: 0; }
h1 { font-size: clamp(30px, 4.4vw, 46px); line-height: 1.1; letter-spacing: -0.01em; }
h2 { font-size: clamp(24px, 3vw, 32px); line-height: 1.15; }
h4 { margin: 0; font-size: 15px; }
.lede { max-width: 68ch; color: var(--muted); font-size: 17px; margin: 12px 0 0; }
.eyebrow, .plabel { font-size: 11.5px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; }
.mv { font-family: var(--mono); font-size: 0.92em; white-space: nowrap; }
.tag { display: inline-grid; place-items: center; width: 22px; height: 22px; border-radius: 4px;
  background: var(--fg); color: var(--bg); font: 600 12px var(--mono); flex: none; }
/* summary grid */
.gridwrap { overflow-x: auto; }
.grid { border-collapse: collapse; width: 100%; min-width: 640px; }
.grid th, .grid td { text-align: left; padding: 12px 14px; border-bottom: 1px solid var(--line);
  vertical-align: top; }
.grid thead th { font-weight: 600; font-size: 14px; }
.grid .gets { display: block; font-weight: 400; color: var(--muted); font-size: 12.5px; margin-top: 4px; }
.grid tbody th { font-weight: 600; white-space: nowrap; }
.grid tbody th a { color: var(--fg); }
.grid tbody th .mv { display: block; font-weight: 400; color: var(--muted); margin-top: 2px; }
.chip, .verdict { display: inline-block; padding: 3px 9px; border-radius: 4px; font-weight: 600;
  font-size: 13.5px; }
.good { background: var(--good-bg); color: var(--good-fg); }
.bad { background: var(--bad-bg); color: var(--bad-fg); }
.vague { background: var(--vague-bg); color: var(--vague-fg); }
.takeaway { max-width: 72ch; font-size: 16.5px; margin: 0; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 18px; font-size: 13.5px; color: var(--muted); }
.legend mark { padding: 1px 6px; border-radius: 3px; }
/* a case */
.case { display: grid; gap: 20px; border-top: 2px solid var(--fg); padding-top: 20px; }
.setup { display: grid; grid-template-columns: minmax(0, 360px) minmax(0, 1fr); gap: 28px; align-items: start; }
.board { margin: 0; max-width: 360px; }
.board svg { width: 100%; height: auto; display: block; border-radius: 3px; }
figcaption { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--muted);
  margin-top: 8px; flex-wrap: wrap; }
.key { width: 18px; height: 4px; border-radius: 2px; display: inline-block; }
.key.red { background: #c8372d; } .key.blue { background: #2a62b8; margin-left: 10px; }
.facts { display: grid; gap: 14px; min-width: 0; max-width: 62ch; }
.pgn { font-family: var(--mono); font-size: 13.5px; margin: 0; color: var(--muted); }
.pgn strong { color: var(--fg); }
.truth { background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; }
.truth p { margin: 6px 0 0; font-size: 16px; }
.truth .better { color: var(--muted); font-size: 14.5px; }
.eng { display: flex; flex-wrap: wrap; gap: 8px 28px; margin: 0; }
.eng dt { font-size: 12px; color: var(--muted); }
.eng dd { margin: 0; font: 600 18px var(--mono); font-variant-numeric: tabular-nums; }
.small { font-size: 12.5px; color: var(--muted); margin: 0; }
.vers { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.ver { background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 16px;
  display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.ver-c { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
.ver header { display: flex; align-items: center; gap: 8px; }
.verdict { align-self: flex-start; margin: 0; }
.answer { margin: 0; font-size: 15.5px; line-height: 1.6; }
.answer mark { padding: 1px 2px; border-radius: 3px; }
mark.good { background: var(--good-bg); color: var(--good-fg); }
mark.bad { background: var(--bad-bg); color: var(--bad-fg); }
mark.vague { background: var(--vague-bg); color: var(--vague-fg); }
.prompt { margin-top: auto; border-top: 1px dashed var(--line); padding-top: 12px; display: grid; gap: 8px; min-width: 0; }
pre { font: 12px/1.5 var(--mono); background: var(--pre-bg); border: 1px solid var(--line);
  border-radius: 4px; padding: 10px 12px; margin: 0; white-space: pre-wrap; overflow-wrap: anywhere;
  max-height: 340px; overflow: auto; }
.bf { background: var(--bf-bg); color: var(--bf-fg); border-radius: 2px; }
details summary { cursor: pointer; font-size: 13px; color: var(--muted); }
details[open] summary { margin-bottom: 8px; }
summary:focus-visible, a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.limits { border-top: 1px solid var(--line); padding-top: 20px; max-width: 75ch; }
.limits h3 { font-family: var(--display); font-size: 21px; margin: 0 0 8px; }
.limits ul { margin: 0; padding-left: 20px; display: grid; gap: 6px; }
@media (max-width: 980px) { .vers { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 700px) { .setup { grid-template-columns: minmax(0, 1fr); } }
"""


def main():
    cases = "".join(case_html(i, c, NOTES[i]) for i, c in enumerate(DATA["cases"]))
    page = f"""<title>Three Coaches, Two Blunders</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=Public+Sans:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>{CSS}</style>
<main class="wrap">
  <header>
    <div class="eyebrow">AI chess tutor · what each input adds · 23 Oct 2026</div>
    <h1>The same blunder, explained by three coaches</h1>
    <p class="lede">One language model (Gemini, <span class="mv">{DATA['model']}</span>, level
      “{DATA['level']}”) explains a student's move three times. Each version gets one more input
      than the one before. Everything else is the same: the position, the model, the level and
      the engine's moves.</p>
  </header>
  <section>{grid_html()}</section>
  <p class="takeaway">On both positions, Gemini alone got the chess wrong. Adding Stockfish
    fixed <em>what</em> happens: it named the capture that punishes the move. Adding the board
    facts fixed <em>why</em>: only that version said the piece had been left undefended.</p>
  <div class="legend"><span>In the answers:</span>
    <span><mark class="good">right</mark> true and the point</span>
    <span><mark class="vague">off</mark> vague, or true but beside the point</span>
    <span><mark class="bad">wrong</mark> false</span>
    <span>In the prompts: <span class="bf">board facts</span>, the only thing C gets that B doesn't</span></div>
  {cases}
  <section class="limits">
    <h3>How far this goes</h3>
    <ul>
      <li>Two positions, one answer per version. Gemini's wording changes from run to run.</li>
      <li>Both positions were picked by hand, and both are a hanging piece, the kind of mistake
        the board facts are built to see. A positional mistake, where no board fact applies,
        is not tested here.</li>
      <li>Version B uses version C's instructions with the board-fact rules taken out, so the
        difference between B and C is the facts plus the rule to use only them.</li>
      <li>Our automatic checker passed all six answers, including both wrong ones from A. A
        wrong reason can only be caught by a person, or by a stronger judge.</li>
      <li>Next: the same comparison on new positions, more cases and positional mistakes.</li>
    </ul>
  </section>
</main>
"""
    OUT.write_text(page, encoding="utf-8")
    print("wrote", OUT, f"{OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
