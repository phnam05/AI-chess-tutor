"""Full-answer board check: every coach answer in full, one card per position,
board before the move (red = played, green = engine's best), a stepper through
the engine's line with "X to move" captions, the facts the coach was given,
and a Yes/No "any problem?" per answer.
Usage (from the repo root, with the venv python):
  build_full_check.py <records.json> <nb4.json> <notes.json> <out.html>
                      [<previous_answers.json> <db collection> <round label> <changes.html>]
With previous answers, each answer shows what the author said last round."""
import html
import json
import re
import sys

import chess
import chess.svg

import board_facts

records_path, nb4_path, notes_path, OUT = sys.argv[1:5]
PREV = json.load(open(sys.argv[5], encoding="utf-8")) if len(sys.argv) > 5 else {}
COLL = sys.argv[6] if len(sys.argv) > 6 else "full"
ROUND = sys.argv[7] if len(sys.argv) > 7 else "fresh run"
CHANGES = open(sys.argv[8], encoding="utf-8").read() if len(sys.argv) > 8 else ""

COLORS = {
    "square light": "#ECE7D6", "square dark": "#8FA67F",
    "square light lastmove": "#E6DF9E", "square dark lastmove": "#B9B568",
    "margin": "#26302B", "coord": "#E4E8E2",
    "arrow red": "#B5462F", "arrow green": "#1F6B45",
}


def esc(s):
    return html.escape(s, quote=False)


def mv(text):
    return f'<span class="mv">{esc(text)}</span>'


def numbered_list(fen, sans):
    """[(label, board_after, move)] with move numbers: '5...Be7', '6.Nxe5', 'O-O'."""
    b = chess.Board(fen)
    out = []
    for i, san in enumerate(sans):
        n = b.fullmove_number
        if b.turn == chess.WHITE:
            label = f"{n}.{san}"
        elif i == 0:
            label = f"{n}...{san}"
        else:
            label = san
        mover = "White" if b.turn == chess.WHITE else "Black"
        move = b.push_san(san)
        out.append((label, b.copy(), move, mover, n))
    return out


def full_label(fen, sans, i):
    """The move number spelled out even mid-line: '7...bxc6'."""
    b = chess.Board(fen)
    for san in sans[:i]:
        b.push_san(san)
    n = b.fullmove_number
    return f"{n}.{sans[i]}" if b.turn == chess.WHITE else f"{n}...{sans[i]}"


def numbered(fen, sans):
    return " ".join(label for label, *_ in numbered_list(fen, sans))


def strip_svg(s):
    s = re.sub(r"<desc>.*?</desc>", "", s, flags=re.S)
    return re.sub(r"<defs>.*?</defs>", "", s, flags=re.S)


DEFS = re.search(r"<defs>.*?</defs>", chess.svg.board(chess.Board()), flags=re.S).group(0)


def board(b, orientation, arrows=(), last=None):
    """One step for the page's own board drawer: placement, last move, arrows."""
    lm = [chess.square_name(last.from_square), chess.square_name(last.to_square)] if last else None
    return {"b": b.board_fen(), "last": lm, "arrows": [list(a) for a in arrows]}


def eval_words(v, side):
    x = float(v.split()[0]) if not v.startswith("Mate") else None
    if v.startswith("Mate"):
        n = int(v.split()[-1])
        return f"{mv(v)} ({side}'s side: {'mate for ' + side if n > 0 else 'mate against ' + side})"
    if abs(x) >= 100:
        return f"{mv(v)} ({side}'s side: a forced mate {'for' if x > 0 else 'against'} {side})"
    return f"{mv(v.replace('-', '−'))} ({side}'s side)"


def facts_rows(fen, steps, n_show):
    """Board facts per move of the line, as the coach was given them."""
    sans = [s["san"] for s in steps]
    rows = []
    for i, s in enumerate(steps[:n_show]):
        f = "; ".join(s["facts"]) if s["facts"] else "<span class='muted'>(no facts)</span>"
        rows.append(f"<tr><td class='num'>{esc(full_label(fen, sans, i))}</td><td>{s['color']}</td><td>{f}</td></tr>")
    return rows


# ---- load the cases -------------------------------------------------------

recs = json.load(open(records_path, encoding="utf-8"))
nb4 = json.load(open(nb4_path, encoding="utf-8"))
notes = json.load(open(notes_path, encoding="utf-8"))

weak = [r for r in recs if r["kind"] == "move" and r["facts"]["label"] in ("Inaccuracy", "Mistake", "Blunder")]
positions = [r for r in recs if r["kind"] == "position"]
picked = weak[:6]
for level in ("beginner", "intermediate", "advanced"):
    picked += [r for r in positions if r["level"] == level and r not in picked][:1]
picked += [r for r in positions if r not in picked][:10 - len(picked)]

cases = [dict(name="Your example: 3...Nb4", kind="move", facts=nb4[0]["facts"],
              answers=[dict(key=f"nb4-{a['level']}", level=a["level"], text=a["text"], check=a["check"]) for a in nb4])]
for r in picked:
    cases.append(dict(name=r["name"], kind=r["kind"], facts=r["facts"],
                      answers=[dict(key=r["name"], level=r["level"], text=r["text"], check=r["check"])]))


# ---- render ----------------------------------------------------------------

def card(ci, c, qstart):
    f = c["facts"]
    fen = f["fen"]
    start = chess.Board(fen)
    student = "White" if start.turn == chess.WHITE else "Black"
    orient = start.turn
    to_move = f"{student} to move"

    if c["kind"] == "move":
        played, best = f["played_move"], f["best_move"]
        p_move = start.parse_san(played)
        b_move = start.parse_san(best)
        p_lab = numbered(fen, [played])
        b_lab = numbered(fen, [best])
        arrows = [(chess.square_name(p_move.from_square), chess.square_name(p_move.to_square), "red")]
        cap0 = f"{to_move}. Red: played {mv(p_lab)}."
        if best != played:
            arrows.append((chess.square_name(b_move.from_square), chess.square_name(b_move.to_square), "green"))
            cap0 += f" Green: engine's best {mv(b_lab)}."
        line = [played] + list(f["refutation"])
        steps = f["line_steps"]              # the line after the played move
        steps_fen = start.copy(); steps_fen.push(p_move); steps_fen = steps_fen.fen()
    else:
        best = f["best_move"]
        b_move = start.parse_san(best)
        arrows = [(chess.square_name(b_move.from_square), chess.square_name(b_move.to_square), "green")]
        cap0 = f"{to_move}. Green: engine's best {mv(numbered(fen, [best]))}."
        line = list(f["principal_variation"])
        steps = f["line_steps"]
        steps_fen = fen

    # Stepper boards: start, then after each move of the line.
    plies = [(board(start, orient, arrows), cap0, "Start")]
    for i, (label, b, move, mover, n) in enumerate(numbered_list(fen, line)):
        nxt = "White" if b.turn == chess.WHITE else "Black"
        state = "Checkmate." if b.is_checkmate() else f"{nxt} to move."
        plies.append((board(b, orient, last=move),
                      f"After {mv(full_label(fen, line, i))} ({mover}). {state}", label))

    # How much of the line each answer's coach was shown (cut by level).
    shown = {}
    for a in c["answers"]:
        cut = board_facts.cut_line(steps, board_facts.LINE_PLIES[a["level"]], student)
        shown[a["key"]] = len(cut)
    n_show = max(shown.values()) if shown else 0
    offset = 1 if c["kind"] == "move" else 0   # the played move is ply 1 of `line`

    moves_html = ['<button type="button" class="step-mv" data-i="0">Start</button>']
    for i, (_, _, lab) in enumerate(plies[1:], 1):
        cls = "step-mv shown" if offset <= i - 1 < offset + n_show or (offset and i == 1) else "step-mv"
        moves_html.append(f'<button type="button" class="{cls}" data-i="{i}">{esc(lab)}</button>')
    data = [dict(d, cap=cap) for d, cap, _ in plies]
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    stepper = f"""
    <div class="board stepper" id="st{ci}" data-orient="{'w' if orient == chess.WHITE else 'b'}">
      <script type="application/json" class="plies">{blob}</script>
      <div class="svgbox" role="img" aria-label="Chess board"></div>
      <div class="cap" aria-live="polite">{cap0}</div>
      <div class="step-ctrl">
        <button type="button" class="nav prev" aria-label="Previous move">&#9664;</button>
        <button type="button" class="nav next" aria-label="Next move">&#9654;</button>
        <span class="step-hint">Step through the engine's line</span>
      </div>
      <div class="step-moves">{''.join(moves_html)}</div>
    </div>"""

    # Facts panel.
    rows = []
    if c["kind"] == "move":
        rows.append(("Played", f"{mv(numbered(fen, [f['played_move']]))}, graded <strong>{f['label']}</strong>"))
        rows.append(("Evaluation", f"{eval_words(f['best_eval'], student)} with the best move; "
                                   f"{eval_words(f['played_eval'], student)} after {mv(f['played_move'])}"))
        if f["best_move"] != f["played_move"]:
            bf = "; ".join(f["best_facts"]["facts"]) if f.get("best_facts") else ""
            rows.append(("Best instead", f"{mv(numbered(fen, [f['best_move']]))}" + (f" — {esc(bf)}" if bf else "")))
        pf = "; ".join(f["played_facts"]["facts"]) if f.get("played_facts") else ""
        rows.append((f"Facts for {esc(f['played_move'])}", esc(pf) or "<span class='muted'>(none)</span>"))
        rows.append(("Engine line after it", mv(numbered(steps_fen, list(f["refutation"])))))
    else:
        rows.append(("Best move", mv(numbered(fen, [f["best_move"]]))))
        rows.append(("Evaluation", eval_words(f["eval_text"], student)))
        rows.append(("Engine line", mv(numbered(fen, list(f["principal_variation"])))))
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    ft = facts_rows(steps_fen, steps, n_show)
    table = ""
    if ft:
        table = f"""
    <details class="bf" open><summary>Board facts the coach was given, move by move</summary>
      <div class="table-box"><table><thead><tr><th>Move</th><th>Side</th><th>Facts</th></tr></thead>
      <tbody>{''.join(ft)}</tbody></table></div>
    </details>"""

    # Answers.
    ans_html = []
    for j, a in enumerate(c["answers"]):
        n = qstart + j
        qid = f"a{n}"
        text = esc(a["text"])
        note_items = notes.get(a["key"], [])
        for item in note_items:
            ph = esc(item["phrase"])
            if not ph:                     # a note about the answer as a whole
                continue
            if ph in text:
                text = text.replace(ph, f'<mark class="bad">{ph}</mark>', 1)
            else:
                print("WARNING: phrase not found:", a["key"], item["phrase"])
        paras = "".join(f"<p>{p.strip()}</p>" for p in text.split("\n") if p.strip())
        k = shown[a["key"]]
        shown_moves = [s["san"] for s in steps[:k]]
        shown_txt = mv(numbered(steps_fen, shown_moves)) if shown_moves else "none"
        pill = ('<span class="pill ok">CHECKER: PASS</span>' if a["check"]["ok"]
                else '<span class="pill no">CHECKER: FLAG</span>')
        noticed = ""
        if note_items:
            lis = "".join(f"<li>{it['note']}</li>" for it in note_items)
            noticed = f'<div class="noticed"><div class="who">What Claude noticed (red underlines)</div><ul>{lis}</ul></div>'
        else:
            noticed = '<div class="noticed"><div class="who">What Claude noticed</div><p class="muted">Nothing. Check it yourself.</p></div>'
        prev_html = ""
        prev = PREV.get(a["key"])
        if prev:
            said = "a problem" if prev["answer"] == "Y" else "no problem"
            note = esc(prev["note"].strip()) if prev["note"].strip() else "<span class='muted'>(no note)</span>"
            prev_html = (f'<div class="prev"><div class="who">Last round you said: {said}</div>'
                         f'<p>{note}</p></div>')
        ans_html.append(f"""
    <div class="qa" id="{qid}">
      {prev_html}
      <div class="quote">
        <div class="who"><span class="num">{n}</span>Coach, {a['level']} level</div>
        {paras}
      </div>
      <div class="verdict">{pill}<span>Line the coach was shown: {shown_txt}</span></div>
      {noticed}
      <div class="askrow">
        <p class="ask">Any problem in this answer?</p>
        <div class="yn" role="group" aria-label="Answer {n}">
          <button type="button" class="yes" data-q="{qid}" data-v="Y" aria-pressed="false">Yes</button>
          <button type="button" class="no" data-q="{qid}" data-v="N" aria-pressed="false">No</button>
        </div>
      </div>
      <label class="note-label" for="note-{qid}">What's wrong? (optional)</label>
      <textarea id="note-{qid}" data-q="{qid}" rows="2" placeholder="Quote the sentence and say what's wrong"></textarea>
    </div>""")

    level_txt = ", ".join(a["level"] for a in c["answers"])
    return f"""
<section id="case{ci}">
  <h2>{esc(c['name'])} <span class="lvl">{level_txt}</span></h2>
  <div class="case">
    <div class="case-top">{stepper}
      <div class="facts"><h3>What the engine said</h3><dl>{dl}</dl></div>
    </div>
    {table}
    {''.join(ans_html)}
  </div>
</section>"""


parts, n = [], 1
for ci, c in enumerate(cases, 1):
    parts.append(card(ci, c, n))
    n += len(c["answers"])
total = n - 1

TEMPLATE = open(__file__.replace("build_full_check.py", "full_check_template.html"), encoding="utf-8").read()
page = (TEMPLATE.replace("%%DEFS%%", DEFS).replace("%%COLORS%%", json.dumps(COLORS)).replace("%%SECTIONS%%", "\n".join(parts))
        .replace("%%COUNT%%", str(total)).replace("%%CASES%%", str(len(cases)))
        .replace("%%COLL%%", COLL).replace("%%ROUND%%", esc(ROUND)).replace("%%CHANGES%%", CHANGES))
open(OUT, "w", encoding="utf-8").write(page)
print(OUT, len(page) // 1024, "KB,", total, "answers,", len(cases), "cases")
