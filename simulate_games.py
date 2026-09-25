"""Simulated games between two weak players, to fill the "Your patterns" panel.

The panel needs many of a player's moves before it can say anything (one slip
never labels anyone), and the author has time for a game or two, not ten. So
here Stockfish plays BOTH sides at its weakest setting, and every move is graded
exactly as the app grades a pasted PGN: the same full-strength engine
(engine_pool, depth 15), the same review (_review_from_infos, as review_game
uses) and the same learner model.

How weak? The weakest setting is Skill Level 0, the bottom of Stockfish's own
Elo scale, where it's labelled 1320. There is no lower setting, so a true "1000"
isn't available, and that scale comes from engine-vs-engine games, so it isn't a
human rating anyway. At Skill Level 0 Stockfish looks about one move deep and
picks at random among its top few moves: it hangs pieces to simple tactics, but
its mistakes come from noise, not from how people think.

So this data is for SEEING the panel work, and for asking how many games it
needs before its verdicts settle. It is NOT evidence about real players: don't
set the learner model's bars from it (that needs real games, see TODO.md).

Two identical players, A and B, play each other, A taking White in odd games.
The panel is worked out for each, as if each had pasted their games and picked
their own side under "You played". A and B are the same bot, so any difference
between their panels is luck: a check on how much a few games can tell.

A player resigns when the engine says they're 5+ pawns down or getting mated
(the same "decided" line as simulate_learners.py): people resign lost games,
and after that point the win-chance curve is flat, so grading says little.

Stockfish seeds its Skill Level randomness from the clock, so each run plays
different games. Everything is saved (one PGN per game + every graded move), and
--rescore re-scores the saved games after a learner-model change, no engine.

Usage:
    python simulate_games.py            # play GAMES games, write sim_games/
    python simulate_games.py --games 4  # fewer games
    python simulate_games.py --rescore  # re-score the saved games (no engine)
"""
import datetime
import json
import sys
from pathlib import Path

import chess
import chess.engine
import chess.pgn

from engine_pool import ENGINE_PATH, analyse
from move_review import _review_from_infos
from learner_model import KINDS, new_model, summary, update

GAMES = 10
SKILL = 0            # Stockfish's weakest setting
MAX_MOVES = 100      # stop a game that's still going after this many moves
RESIGN_CP = 500      # resign when 5+ pawns down
OUT = Path("sim_games")
LABELS = ("Blunder", "Mistake", "Inaccuracy")


def _lost(info, color):
    """The engine says `color` is 5+ pawns down or getting mated. The mate's
    sign is taken by comparing with Cp(0), never mate() > 0 (see CLAUDE.md)."""
    score = info["score"].pov(color)
    if score.is_mate():
        return score < chess.engine.Cp(0)
    return score.score() <= -RESIGN_CP


def play_game(player, n):
    """Game `n` (from 1): player A is White in odd games. Returns the PGN game
    and every move, graded."""
    board = chess.Board()
    a_color = chess.WHITE if n % 2 else chess.BLACK
    info = analyse(board)
    moves = []
    while True:
        side = "White" if board.turn == chess.WHITE else "Black"
        if board.is_game_over(claim_draw=True):
            outcome = board.outcome(claim_draw=True)
            result, ending = outcome.result(), outcome.termination.name.lower().replace("_", " ")
            break
        if _lost(info, board.turn):
            result = "0-1" if board.turn == chess.WHITE else "1-0"
            ending = f"{side} resigned (5+ pawns down or mate coming)"
            break
        if board.fullmove_number > MAX_MOVES:
            result, ending = "*", f"stopped after {MAX_MOVES} moves"
            break
        move = player.play(board, chess.engine.Limit(depth=5), game=n).move
        after = board.copy()
        after.push(move)
        info_after = analyse(after)
        review = _review_from_infos(board, move, info, info_after)
        moves.append({
            "game": n, "player": "A" if board.turn == a_color else "B",
            "move_no": board.fullmove_number, "color": side,
            "san": review["played_move"], "label": review["label"],
            "mistake_type": review["mistake_type"], "chances": review["chances"],
        })
        board, info = after, info_after

    game = chess.pgn.Game.from_board(board)
    game.headers.update({
        "Event": f"Simulated game: Stockfish Skill Level {SKILL} vs itself",
        "Site": "simulate_games.py", "Date": datetime.date.today().strftime("%Y.%m.%d"),
        "Round": str(n), "White": "Player A" if a_color == chess.WHITE else "Player B",
        "Black": "Player B" if a_color == chess.WHITE else "Player A",
        "Result": result, "Termination": ending,
    })
    return game, moves


def panels(moves, player):
    """What the panel says about `player` after each game, over all their moves
    so far: what the app shows if they paste the games one after another."""
    model, out = new_model(), []
    for n in sorted({m["game"] for m in moves}):
        for m in moves:
            if m["game"] == n and m["player"] == player:
                dots = "." if m["color"] == "White" else "..."
                update(model, {"played_move": m["san"], "mistake_type": m["mistake_type"],
                               "chances": m["chances"]},
                       where=f'{m["move_no"]}{dots} {m["san"]} (game {n})')
        out.append(summary(model))
    return out


def _labels(moves, n, player):
    return " / ".join(str(sum(m["label"] == lab for m in moves
                              if m["game"] == n and m["player"] == player)) for lab in LABELS)


def write_report(saved, path):
    games, moves = saved["games"], saved["moves"]
    lines = [
        '# Simulated games for the "Your patterns" panel',
        "",
        f'Generated by `simulate_games.py` on {saved["date"]}: {len(games)} games, Stockfish at '
        f"its weakest setting (Skill Level {SKILL}) playing both sides. Every move is graded by "
        "the full-strength engine with the same code the app uses for a pasted PGN.",
        "",
        "**Not real players.** Skill Level 0 is the bottom of Stockfish's own Elo scale "
        "(labelled 1320; there is no \"1000\" setting, and that scale isn't a human rating). "
        "Its mistakes come from a shallow search plus random noise, not from how people think. "
        "Use these games to see the panel work, not as evidence about real players.",
        "",
        "Players A and B are the same bot, so any difference between their panels is luck.",
        "To see a game in the app: open `game_NN.pgn`, copy all of it, paste it under "
        "\"Review a full game (PGN)\", and pick Player A's colour under \"You played\".",
        "",
        "## The games",
        "",
        "| Game | Player A played | Result | How it ended | Moves "
        "| A: blunders / mistakes / inaccuracies | B: blunders / mistakes / inaccuracies |",
        "|---|---|---|---|---|---|---|",
    ]
    for g in games:
        a_side = "White" if g["White"] == "Player A" else "Black"
        lines.append(f'| {g["game"]} | {a_side} | {g["Result"]} | {g["Termination"]} | {g["moves"]} '
                     f'| {_labels(moves, g["game"], "A")} | {_labels(moves, g["game"], "B")} |')
    for player in ("A", "B"):
        lines += ["", f"## Player {player}: what the panel says after each game", "",
                  "| After game | " + " | ".join(KINDS) + " |",
                  "|---|" + "---|" * len(KINDS)]
        for n, rows in enumerate(panels(moves, player), 1):
            cells = [f'{r["misses"]}/{r["chances"]} {r["status"]}' for r in rows]
            lines.append(f"| {n} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Cells read `slips/chances verdict`, over all the player's moves so far. A chance is "
        "every move for the first three kinds, and only the moves where the engine saw a win "
        "of material / a forced mate for the two \"missed\" kinds. *pattern* = at least 3 slips "
        "and 80% sure the rate is above the kind's bar; *fine* = 80% sure it's below; "
        "*unsure* = not enough evidence yet.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    records = OUT / "records.json"
    if "--rescore" in sys.argv:             # re-score saved games; no engine needed
        saved = json.loads(records.read_text(encoding="utf-8"))
    else:
        n_games = int(sys.argv[sys.argv.index("--games") + 1]) if "--games" in sys.argv else GAMES
        for old in OUT.glob("game_*.pgn"):  # a shorter run mustn't leave old games behind
            old.unlink()
        saved = {"date": datetime.date.today().isoformat(), "games": [], "moves": []}
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as player:
            player.configure({"Skill Level": SKILL, "Threads": 1, "Hash": 16})
            for n in range(1, n_games + 1):
                game, moves = play_game(player, n)
                (OUT / f"game_{n:02d}.pgn").write_text(str(game) + "\n", encoding="utf-8")
                saved["games"].append({"game": n, "moves": (len(moves) + 1) // 2}
                                      | {k: game.headers[k] for k in
                                         ("White", "Black", "Result", "Termination")})
                saved["moves"] += moves
                print(f'game {n}: {game.headers["Result"]}, {(len(moves) + 1) // 2} moves, '
                      f'{game.headers["Termination"]}', flush=True)
        records.write_text(json.dumps(saved, indent=1), encoding="utf-8")
    write_report(saved, OUT / "README.md")
    print(f"wrote {OUT / 'README.md'}")


if __name__ == "__main__":
    main()
