"""What a human would *notice* about each move — computed from the board, not guessed.

The engine gives moves and a number, never reasons. But a player finds a move by
first noticing something on the board ("that bishop is in reach of my pawn"), and
a coach that only reads out the engine's line skips that step. The language model
must not fill the gap from its own chess knowledge: invented reasons were the most
common failure in the 2026-07-03 audit. So the reasons come from here instead —
plain board geometry that python-chess can check exactly: what a move captures or
attacks, whether a pawn can chase the piece, castling, bringing a piece out,
opening a line for another piece.

One rule keeps a true fact from becoming a wrong reason: nothing here says a piece
*can be lost* unless the engine's own line goes on to capture it. (After ...Nb4 in
the Ruy Lopez the knight no longer defends e5, but 4.Nxe5? Qg5 leaves White worse;
"you left e5 undefended" would be true and misleading.)

Facts are written with colours ("White's bishop on b5"), not "you", so the same
fact reads right whichever side the student plays; explainer.py adds who is who.
"""

import chess

# The standard teaching count. The king is off the scale: it's never captured.
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
          chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100}

# Where each minor piece starts: leaving one of these squares is "bringing it out".
_MINOR_HOMES = {chess.B1, chess.G1, chess.C1, chess.F1,
                chess.B8, chess.G8, chess.C8, chess.F8}
_KNIGHT_HOMES = {chess.WHITE: (chess.B1, chess.G1), chess.BLACK: (chess.B8, chess.G8)}
_BISHOP_HOMES = {chess.WHITE: (chess.C1, chess.F1), chess.BLACK: (chess.C8, chess.F8)}

_CENTRE = {chess.D4, chess.E4, chess.D5, chess.E5}

# How far to go down each level's line, in half-moves (one side's move each).
# Beginner: their reply and yours. Deeper lines only for stronger players.
LINE_PLIES = {"beginner": 2, "intermediate": 3, "advanced": 4}


def _color(color):
    return "White" if color == chess.WHITE else "Black"


def _name(piece):
    return chess.piece_name(piece.piece_type)


def _in_opening(board, color):
    """Still developing: a knight or bishop of `color` stands on its starting
    square (the author's rule, 2026-09-26). That's when opening a line is worth
    saying for its own sake: nobody can say yet when the line will be used."""
    return (any(board.piece_at(sq) == chess.Piece(chess.KNIGHT, color) for sq in _KNIGHT_HOMES[color])
            or any(board.piece_at(sq) == chess.Piece(chess.BISHOP, color) for sq in _BISHOP_HOMES[color]))


def _later_use(after, following, square, opened):
    """SAN of the line's first move of the piece on `square`, if that move goes
    to one of the `opened` squares (the line uses the new line). None otherwise,
    or if the piece is captured before it moves."""
    board = after.copy()
    for move in following:
        if move.from_square == square:
            return board.san(move) if move.to_square in opened else None
        if move.to_square == square:
            return None
        board.push(move)
    return None


def _pieces_text(board, squares):
    """"White's queen on h5 and bishop on c4" for the pieces on `squares`."""
    parts = [f"{_name(board.piece_at(sq))} on {chess.square_name(sq)}" for sq in squares]
    owner = _color(board.color_at(squares[0]))
    return f"{owner}'s " + (parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1])


def _first_touch_is_capture(board, following, square):
    """Does the line after `board` capture what stands on `square`, before that
    piece moves away? Only then is "it can be lost" an engine fact."""
    board = board.copy()
    owner = board.color_at(square)
    for move in following:
        if move.from_square == square:
            return False                      # it moved away first
        if move.to_square == square:
            return board.is_capture(move) and board.turn != owner
        board.push(move)
    return False


def move_facts(board, move, following=(), prev_capture_square=None):
    """The noticeable facts about `move` played from `board`.

    `following` is the engine's line after the move (Move objects), used only to
    confirm that a piece left undefended really is captured. `prev_capture_square`
    is where the previous move in the line captured, so a capture there reads as
    taking back. Returns a step dict: what moved (san, piece, from, to) and
    `facts`, the list of reasons — empty when nothing noticeable can be proved.
    """
    mover = board.turn
    me, them = _color(mover), _color(not mover)
    piece = board.piece_at(move.from_square)
    after = board.copy()
    after.push(move)
    to = chess.square_name(move.to_square)
    facts = []

    if board.is_check():
        facts.append(f"gets {me}'s king out of check")

    if board.is_castling(move):
        side = "kingside" if chess.square_file(move.to_square) == 6 else "queenside"
        facts.append(f"castles {side}: {me}'s king moves away from the centre "
                     f"and a rook comes toward the middle")
    else:
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            name = _name(victim) if victim else "pawn"       # None = en passant
            if move.to_square == prev_capture_square:
                facts.append(f"takes back on {to}, capturing {them}'s {name}")
            else:
                facts.append(f"captures {them}'s {name} on {to}")
        if move.promotion:
            facts.append(f"promotes the pawn to a {chess.piece_name(move.promotion)}")
        if piece.piece_type == chess.PAWN and not board.is_capture(move) and move.to_square in _CENTRE:
            facts.append(f"puts a pawn in the centre on {to}")
        if piece.piece_type in (chess.KNIGHT, chess.BISHOP) and move.from_square in _MINOR_HOMES:
            facts.append(f"brings {me}'s {_name(piece)} into play from its starting square")

        # Stepping out of a chase: it stood attacked by something worth less, or
        # by anything at all when nothing defended it (a bishop on an undefended
        # knight is a real threat too; on a defended one it's only an even trade).
        undefended = not board.attackers(mover, move.from_square)
        for sq in board.attackers(not mover, move.from_square):
            chaser = board.piece_at(sq)
            if ((VALUES[chaser.piece_type] < VALUES[piece.piece_type] or undefended)
                    and sq != move.to_square
                    and sq not in after.attackers(not mover, move.to_square)):
                facts.append(f"moves the {_name(piece)} away from the attack by "
                             f"{them}'s {_name(chaser)} on {chess.square_name(sq)}")
                break

        # New attacks on something worth more, or on something nothing defends
        # (a pinned piece attacks nothing real). Only an attack; whether it WINS
        # anything is the engine's call, and the line shows it if so. An attack
        # on anything else (an equal piece that's defended) counts only when the
        # line's next move takes that piece away, i.e. the engine treats it as a
        # threat: 7...Ng4 hits the bishop on e3, and the line answers 8.Bd2.
        # (No "which is worth less" in the text: the coach copied it word for
        # word; "attacks the bishop with a pawn" already says it.)
        if not after.is_pinned(mover, move.to_square):
            already = board.attacks(move.from_square)
            for sq in after.attacks(move.to_square):
                target = after.piece_at(sq)
                if not target or target.color == mover or target.piece_type == chess.KING or sq in already:
                    continue
                where = f"{them}'s {_name(target)} on {chess.square_name(sq)}"
                if VALUES[target.piece_type] > VALUES[piece.piece_type]:
                    facts.append(f"attacks {where} with a {_name(piece)}")
                elif not after.attackers(not mover, sq):
                    facts.append(f"attacks {where}, which nothing defends")
                elif (VALUES[target.piece_type] == VALUES[piece.piece_type]
                      and following and following[0].from_square == sq
                      and not after.is_capture(following[0])):   # stepping away, not taking back
                    # Equal pieces only: a knight "attacking" a defended pawn
                    # on d2 that then moves to d3 wasn't a threat it escaped.
                    facts.append(f"attacks {where}, and the next move in the line moves it away")

        # Could a pawn chase it next move? Only for pieces, and only if no pawn
        # already hits it (that would be a capture, which the line would show).
        pawn_hits = [sq for sq in after.attackers(not mover, move.to_square)
                     if after.piece_type_at(sq) == chess.PAWN]
        if piece.piece_type not in (chess.PAWN, chess.KING) and not pawn_hits:
            chasers = []
            for reply in after.legal_moves:
                if after.piece_type_at(reply.from_square) == chess.PAWN and not after.is_capture(reply):
                    pushed = after.copy()
                    pushed.push(reply)
                    if move.to_square in pushed.attacks(reply.to_square):
                        chasers.append(f"the pawn on {chess.square_name(reply.from_square)} "
                                       f"to {chess.square_name(reply.to_square)}")
            # Name both squares of each push: given just "pushing a pawn: c3 or
            # a3", the coach twice wrote "the c3 pawn" for a pawn still on c2.
            if chasers:
                facts.append(f"{them} can attack it next move by pushing "
                             + ", or ".join(chasers))

        # Opening a line for another long-range piece of the same side — only
        # when the new squares are worth something at that moment (the author's
        # rule, 2026-09-26: 6.Be3 frees c1 and b1 for the queen, true and useless):
        #   now:     through the opened line the piece attacks something worth
        #            more, or undefended;
        #   opening: while still developing, the piece gains a way into the game
        #            (a new square off its home rank) — nobody can say yet when
        #            that line will be used, and that's fine in the opening;
        #   later:   the engine's line moves the piece along the opened line.
        opening = _in_opening(board, mover)
        home_rank = 0 if mover == chess.WHITE else 7
        for sq in board.pieces(chess.BISHOP, mover) | board.pieces(chess.ROOK, mover) | board.pieces(chess.QUEEN, mover):
            if sq == move.from_square:
                continue
            opened = after.attacks(sq) & ~board.attacks(sq)
            if not opened:
                continue
            line_piece = board.piece_at(sq)
            base = f"opens a line for {me}'s {_name(line_piece)} on {chess.square_name(sq)}"
            hit = next((t for t in opened
                        if after.color_at(t) == (not mover) and after.piece_type_at(t) != chess.KING
                        and (VALUES[after.piece_type_at(t)] > VALUES[line_piece.piece_type]
                             or not after.attackers(not mover, t))), None)
            if hit is not None:
                facts.append(f"{base}, which now attacks {them}'s "
                             f"{_name(after.piece_at(hit))} on {chess.square_name(hit)}")
            elif opening and any(chess.square_rank(t) != home_rank for t in opened):
                facts.append(base)
            else:
                used = _later_use(after, following, sq, opened)
                if used:
                    facts.append(f"{base}, which the line goes on to use ({used})")

        # Preparing the side's next move in the line: a pawn move that now covers
        # the square that move goes to (4.c3 ... 5.d4: the pawn on c3 defends d4;
        # ...c6 ... ...d5). Pawns only, and not before a capture: "...Nb4 prepares
        # c6" or "Bc4 prepares exd5" were true geometry and nonsense as reasons.
        # Checked after the opponent's reply, in case that reply changes it.
        if piece.piece_type == chess.PAWN and len(following) >= 2:
            mid = after.copy()
            mid.push(following[0])
            nxt = following[1]
            if (mid.piece_at(move.to_square) == after.piece_at(move.to_square)
                    and nxt.from_square != move.to_square
                    and nxt.to_square in mid.attacks(move.to_square)
                    and nxt.to_square not in board.attacks(move.from_square)
                    and mid.is_legal(nxt) and not mid.is_capture(nxt)):
                nsan = mid.san(nxt)
                facts.append(f"prepares {nsan}: the {_name(piece)} now defends "
                             f"{chess.square_name(nxt.to_square)}, where the line plays {nsan} next")

        # A defender walking away — stated only if the line then captures it.
        for sq in board.attacks(move.from_square):
            friend = board.piece_at(sq)
            if (friend and friend.color == mover and friend.piece_type != chess.KING
                    and sq not in after.attacks(move.to_square)
                    and _first_touch_is_capture(after, following, sq)):
                facts.append(f"no longer defends {me}'s {_name(friend)} on "
                             f"{chess.square_name(sq)}, which the line goes on to capture")

        # The plainest fact of all: the line's very next move takes this piece.
        # (3.Ng5?? Qxg5 — "a pawn can chase it" would bury the real point.) When
        # nothing defends it there, say so: the piece was simply left to be taken
        # for free — what a player calls hanging it.
        if following and following[0].to_square == move.to_square and after.is_capture(following[0]):
            taken = board.piece_at(move.to_square) if board.is_capture(move) else None
            gained = VALUES[taken.piece_type] if taken else (1 if board.is_capture(move) else 0)
            # "Hanging" = lost for less than it's worth; Bxc6 dxc6 is a trade.
            if not after.attackers(mover, move.to_square) and gained < VALUES[piece.piece_type]:
                facts.insert(0, f"nothing defends it on {to}, and the very next move in the line captures it")
            else:
                facts.insert(0, f"the very next move in the line captures it on {to}")

    # Allowing mate: the line's next move is checkmate. Name the pieces that
    # hit the mating square — that's what the student had to see (3...Nf6??
    # Qxf7#: the queen on h5 and the bishop on c4 both attack f7).
    if following and not after.is_checkmate():
        mate_board = after.copy()
        mate_board.push(following[0])
        if mate_board.is_checkmate():
            target = following[0].to_square
            hitters = sorted(after.attackers(not mover, target))
            mate = f"allows checkmate next move ({after.san(following[0])})"
            if hitters:                            # a pawn push or castling mate has none
                verb = "attacks" if len(hitters) == 1 else "both attack" if len(hitters) == 2 else "all attack"
                mate += f": {_pieces_text(after, hitters)} {verb} {chess.square_name(target)}"
            facts.insert(0, mate)

    if after.is_checkmate():
        facts.append("gives checkmate")
    elif after.is_check():
        facts.append(f"gives check to {them}'s king")

    return {
        "san": board.san(move),
        "color": me,
        "piece": _name(piece),
        "from": chess.square_name(move.from_square),
        "to": to,
        "capture": board.is_capture(move),
        "facts": facts,
    }


def _parse_line(board, sans):
    """SAN strings -> Move objects, played from `board`. A move that doesn't
    parse ends the line: a stale or corrupt tail shouldn't break the coaching."""
    moves, b = [], board.copy()
    for san in sans:
        try:
            move = b.parse_san(san)
        except ValueError:
            break
        moves.append(move)
        b.push(move)
    return moves


def line_steps(board, sans, prev_capture_square=None):
    """Facts for every move of an engine line given as SAN from `board`.
    `prev_capture_square`: where the move just before the line captured (the
    student's own move, in a review), so a first move there reads as taking back."""
    moves = _parse_line(board, sans)
    steps, b, prev_capture = [], board.copy(), prev_capture_square
    for i, move in enumerate(moves):
        steps.append(move_facts(b, move, moves[i + 1:], prev_capture))
        prev_capture = move.to_square if b.is_capture(move) else None
        b.push(move)
    return steps


def played_facts(board, san, following_sans):
    """Facts for the single move `san` from `board`, confirmed against the line
    that follows it. None if the move doesn't parse."""
    moves = _parse_line(board, [san] + list(following_sans))
    if not moves:
        return None
    return move_facts(board, moves[0], moves[1:])


def cut_line(steps, max_plies, student_color, damage=False):
    """The part of the line the coach should walk through.

    Cut at `max_plies` half-moves — but never between a capture and the
    capture that answers it (a line stopped at "...Qxf4" reads as a hung queen
    when the next move is Bxf4). Unlike render_line, it doesn't reach past the
    cut to *start* an exchange: ending on "your opponent takes the pawn on e4"
    with no answer shown would teach a loss the engine doesn't expect.
    Then stop before the first of the *student's* moves (after the opening one)
    that has no fact to explain it: the coach gives the idea before every move
    it recommends, and with no fact there is no honest idea to give. Better a
    short line than a move out of nowhere.

    `damage`: the student's move lost material or allowed mate. Then the line
    after the punishment is only damage control, so keep just the opponent's
    reply and the student's one answer to it (the author, 2026-09-26: "could
    just be shorter on how to minimize the damage"; after 3.Ng5?? Qxg5 there
    is "not much to discuss further").
    """
    if damage:
        first_own = next((i for i, s in enumerate(steps) if s["color"] == student_color), None)
        if first_own is not None:
            max_plies = min(max_plies, first_own + 1)
    kept = list(steps[:max_plies])
    while (kept and kept[-1]["capture"] and len(kept) < len(steps)
           and steps[len(kept)]["capture"] and steps[len(kept)]["to"] == kept[-1]["to"]):
        kept.append(steps[len(kept)])            # a take-back on the same square
    for i, step in enumerate(kept):
        if i > 0 and step["color"] == student_color and not step["facts"]:
            return kept[:i]
    return kept


if __name__ == "__main__":
    # The case that started this file: ...Nb4 in the Ruy Lopez, a Mistake. The
    # engine's line after it is O-O c6 Bc4 d5 exd5 Bd6 (hard-coded so this runs
    # without the engine). Expect: the knight can be chased by a3/c3, and NO
    # "no longer defends e5" (the line never takes e5: 4.Nxe5? Qg5).
    fen = "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"
    board = chess.Board(fen)
    line = ["O-O", "c6", "Bc4", "d5", "exd5", "Bd6"]
    played = played_facts(board, "Nb4", line)
    print(f"...{played['san']}: {played['facts']}")
    after = board.copy()
    after.push_san("Nb4")
    steps = line_steps(after, line)
    for s in steps:
        print(f"  {s['color']:5s} {s['san']:5s} {s['facts']}")
    for level, plies in LINE_PLIES.items():
        print(f"{level:12s} ->", [s["san"] for s in cut_line(steps, plies, "Black")])

    # The defender rule, the other way round: here the line DOES take the pawn
    # the knight stopped defending, so the fact must appear.
    b = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 3 3")
    print("\n...Nb4 then Nxe5:", played_facts(b, "Nb4", ["Nxe5"])["facts"])

    # A recapture reads as taking back; a check is named.
    b = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
    steps = line_steps(b, ["Bxc6", "dxc6", "Nxe5", "Qd4"])
    for s in steps:
        print(f"  {s['color']:5s} {s['san']:5s} {s['facts']}")
    # Cut after one move: the take-back dxc6 is kept, the new capture Nxe5 isn't.
    print("cut at 1 ->", [s["san"] for s in cut_line(steps, 1, "White")], "(expect Bxc6, dxc6)")

    # Escaping an equal-value attacker counts only when nothing defended the
    # piece: the bishop on e2 threatens the lone knight on g4, but with the h5
    # pawn guarding g4, Bxg4 would just be an even trade.
    b = chess.Board("4k3/8/8/8/6n1/8/4B3/4K3 b - - 0 1")
    print("\nundefended ...Nf6:", played_facts(b, "Nf6", [])["facts"], "(expect: moves away from the bishop)")
    b = chess.Board("4k3/8/8/7p/6n1/8/4B3/4K3 b - - 0 1")
    print("defended ...Nf6:  ", played_facts(b, "Nf6", [])["facts"], "(expect: [])")

    # The author's hand check, 2026-09-25/26 (engine lines copied from that run).
    print("\n--- author's cases ---")
    def show(label, fen, san, line, expect):
        print(f"{label}: {played_facts(chess.Board(fen), san, line)['facts']}\n   expect: {expect}")

    najdorf = "rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6"
    show("6.Be3", najdorf, "Be3", ["e5", "Nb3", "Ng4", "Bd2", "Nf6"],
         "no line for the queen (it only gains c1 and b1)")
    b = chess.Board(najdorf)
    for san in ["Be3", "e5", "Nb3"]:
        b.push_san(san)
    show("7...Ng4", b.fen(), "Ng4", ["Bd2", "Nf6"], "attacks the bishop on e3, and the line moves it away")
    italian = "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    show("4.c3", italian, "c3", ["Nf6", "d4", "exd4", "e5", "d5"],
         "opens a line for the queen (opening, she gets out) + prepares d4")
    qgd = "rnbqk2r/ppp1bppp/4pn2/3p2B1/2PP4/2N5/PP2PPPP/R2QKBNR w KQkq - 4 5"
    show("5.e3", qgd, "e3", ["h6", "Bh4", "O-O", "Nf3"], "opens lines for the queen and the bishop on f1")
    start = chess.STARTING_FEN
    show("1.a4", start, "a4", ["e5", "e4"], "opens a line for the rook on a1 (opening)")
    show("1.e4", start, "e4", ["e5", "Nf3"], "puts a pawn in the centre; lines for queen and bishop")
    ng5 = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    show("3.Ng5", ng5, "Ng5", ["Qxg5", "d4", "Qg6"], "nothing defends it on g5, and the next move captures it")
    b = chess.Board(ng5)
    for san in ["Ng5", "Qxg5"]:
        b.push_san(san)
    show("4.d4", b.fen(), "d4", ["Qg6", "dxe5"], "opens a line for the bishop on c1, which now attacks the queen on g5")
    scholar = "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3"
    show("3...Nf6", scholar, "Nf6", ["Qxf7#"], "allows checkmate next move (Qxf7#): bishop c4 and queen h5 both attack f7")

    # Damage control: after a lost piece keep only the reply and one answer.
    b = chess.Board(ng5)
    b.push_san("Ng5")
    steps = line_steps(b, ["Qxg5", "d4", "Qg6", "dxe5", "d6"])
    print("3.Ng5 damage cut (advanced) ->", [s["san"] for s in cut_line(steps, 4, "White", damage=True)],
          "(expect Qxg5, d4)")
