"""One persistent Stockfish process, shared across the whole app.
(Plus a second, deliberately weak one that plays the bot opponent; see bot_move.)

The original design spawned a fresh engine for every request and quit it
afterwards (the note CLAUDE.md anticipated: "pool or reuse the engine"). That
paid a full process launch + UCI handshake on every call — ~0.3s on Windows —
and `review_move` paid it on top of *two* one-second searches, so grading a
single move cost ~2.4s. That was the lag you felt on every move.

Streamlit imports a module once per process, so a module-level engine here is
reused across every rerun and every call. Measured locally, an analysis drops
from ~1.4s (spawn + time=1.0) to ~0.02-0.23s — reuse, not a time cap, is the win
(see DEFAULT_DEPTH for why we dropped the cap). One lock serialises access: a
single SimpleEngine can't run two analyses at once, and Streamlit may call in
from session threads.

This is also the single source of truth for engine discovery — `find_engine`
used to be copy-pasted into engine_analysis.py and move_review.py, and the two
copies had drifted (one returned a bare relative "stockfish.exe" that won't
launch as a subprocess on Windows).
"""

import atexit
import os
import shutil
import threading
import chess
import chess.engine


def find_engine():
    """Locate the Stockfish binary across the environments we run in."""
    # Common command names first (Streamlit Cloud installs via apt/packages.txt).
    for name in ("stockfish", "Stockfish"):
        found = shutil.which(name)
        if found:
            return found
    # Versioned Debian install paths.
    for path in ("/usr/games/stockfish", "/usr/bin/stockfish"):
        if os.path.exists(path):
            return path
    # Local Windows fallback: the .exe next to the source. Return an ABSOLUTE
    # path — a bare "stockfish.exe" doesn't reliably launch as a subprocess.
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish.exe")
    if os.path.exists(local):
        return local
    found = shutil.which("stockfish.exe")
    if found:
        return found
    raise RuntimeError(
        "Stockfish engine not found. On Streamlit Cloud, ensure packages.txt "
        "(at repo root) contains the line 'stockfish'. Locally, place "
        "stockfish.exe next to the source."
    )


ENGINE_PATH = find_engine()

# How hard the engine thinks — and why its answer is DETERMINISTIC (same position
# -> same best move, every run). Reproducibility matters here: the coaching and the
# faithfulness evaluation must rest on facts that don't wobble between runs. Three
# settings make it so, and each was measured to matter (single-threading alone is
# NOT enough):
#   1. Limit by DEPTH only, never wall-clock time. A time cap stops the search at a
#      load-dependent depth, so the "best move" changes run to run; a fixed depth
#      always explores the same tree. (Bonus: move grading searches the before- and
#      after-move positions to the SAME depth, so their evals stay comparable.)
#   2. One thread. Parallel workers finish in a timing-dependent order and race on
#      shared memory, so >1 thread wobbles even at a fixed depth.
#   3. Wipe the transposition table before each search (see analyse). A reused engine
#      keeps its memory between calls, so the same position could resolve differently
#      depending on what ran before — this was the main cause of the app showing a
#      different "best move" on repeated clicks.
# depth-15 Stockfish is still far stronger than any student, so "the engine decides
# the chess" holds; measured cost is ~0.02-0.23s per call (the process is still
# reused — that, not a time cap, is what keeps it fast).
DEFAULT_DEPTH = 15

_engine = None
_lock = threading.Lock()


def _new_engine():
    eng = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
    # Single-threaded ON PURPOSE: multi-threaded search is non-deterministic (the
    # workers race), and a stable answer is worth more here than raw speed — depth-15
    # single-thread still returns in a fraction of a second. Hash still gives the
    # search a transposition table within one call; we wipe it between calls (see
    # analyse) so a result never depends on what was searched before.
    try:
        eng.configure({"Threads": 1, "Hash": 128})
    except chess.engine.EngineError:
        pass
    return eng


def _new_bot():
    # The bot needs no big hash table: it's meant to play weakly, not deeply.
    eng = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
    try:
        eng.configure({"Threads": 1, "Hash": 16})
    except chess.engine.EngineError:
        pass
    return eng


def _spawn(make=_new_engine):
    """Launch Stockfish from a short-lived *daemon* thread.

    python-chess runs each engine's event loop on a background thread, and that
    thread inherits its daemon flag from whoever creates it (the library never
    sets one). Create the engine from the main thread and the loop thread is
    *non-daemon*, so at interpreter exit Python blocks forever trying to join it
    — and the atexit hook where we'd quit the engine runs only *after* that join,
    so it never gets the chance (the process hangs and orphans Stockfish).
    Launching from a daemon thread makes the loop thread a daemon too: shutdown
    never blocks, and the atexit quit below still closes the engine cleanly on a
    normal exit."""
    box = {}

    def _launch():
        try:
            box["engine"] = make()
        except BaseException as exc:  # report the real error to the caller
            box["error"] = exc

    t = threading.Thread(target=_launch, name="stockfish-spawn", daemon=True)
    t.start()
    t.join()
    if "error" in box:
        raise box["error"]
    return box["engine"]


def analyse(board, *, depth=DEFAULT_DEPTH):
    """Analyse `board` on the shared, reused engine, under the lock.

    Respawns once if the engine has died, so a crashed Stockfish degrades into a
    slow call rather than taking the whole app down.
    """
    global _engine
    limit = chess.engine.Limit(depth=depth)
    with _lock:
        if _engine is None:
            _engine = _spawn()
        try:
            # A fresh `game` token each call makes python-chess send `ucinewgame`,
            # so Stockfish clears its transposition table before searching — the
            # wipe that, with single-threading + fixed depth, makes the result
            # deterministic. The process itself is still reused (the speed win).
            return _engine.analyse(board, limit, game=object())
        except chess.engine.EngineError:
            _engine = _spawn()
            return _engine.analyse(board, limit, game=object())


# The sparring partner for "Play against: Bot". It is a SECOND Stockfish process,
# never the shared engine above: Skill Level makes Stockfish play worse on
# purpose, and on the grading engine it would weaken every verdict. Unlike the
# grader it isn't meant to be repeatable: below Skill Level 20 Stockfish picks
# at random among its top few moves, so the same position can get a different
# reply. BOT_TIME_S (0.3 s a move) is hand-picked: quick enough to feel instant,
# and at Skill Level 20 still far stronger than a student.
BOT_TIME_S = 0.3
_bot = None
_bot_lock = threading.Lock()


def bot_move(board, skill):
    """The bot's move in `board` at Stockfish Skill Level `skill` (0 = weakest,
    20 = full strength). Respawns once if the process has died, like analyse."""
    global _bot
    limit = chess.engine.Limit(time=BOT_TIME_S)
    with _bot_lock:
        if _bot is None:
            _bot = _spawn(_new_bot)
        try:
            _bot.configure({"Skill Level": skill})
            return _bot.play(board, limit).move
        except chess.engine.EngineError:
            _bot = _spawn(_new_bot)
            _bot.configure({"Skill Level": skill})
            return _bot.play(board, limit).move


def warmup():
    """Pre-spawn the engine so the first real analysis isn't cold (~0.5s launch).

    Best-effort: called once at app load so the cost is paid while the page is
    rendering, not mid-click on the student's first move. Swallows failures — if
    the launch genuinely can't happen, the real analyse() call surfaces it."""
    global _engine
    try:
        with _lock:
            if _engine is None:
                _engine = _spawn()
    except Exception:
        pass


@atexit.register
def _shutdown():
    """Quit the engines on exit so we don't orphan a Stockfish subprocess."""
    global _engine, _bot
    for eng in (_engine, _bot):
        if eng is not None:
            try:
                eng.quit()
            except Exception:
                pass
    _engine = _bot = None


if __name__ == "__main__":
    # Self-test: prove the engine is found, and that the second analysis is far
    # cheaper than the first — the whole reason this module exists. The first
    # call pays the one-time launch; every call after reuses the same process.
    import time

    print("engine:", ENGINE_PATH)
    board = chess.Board()

    t0 = time.perf_counter()
    info = analyse(board)
    cold = time.perf_counter() - t0
    print(f"first  analysis: {cold:6.3f}s  (cold - includes spawn) best={board.san(info['pv'][0])}")

    t0 = time.perf_counter()
    analyse(board)
    warm = time.perf_counter() - t0
    print(f"second analysis: {warm:6.3f}s  (warm - reused engine)")

    # The bot is its own process: a weak reply here must not change the grader.
    replies = {board.san(bot_move(board, 0)) for _ in range(5)}
    print(f"bot (Skill 0), 5 tries from the start: {sorted(replies)}")
    again = analyse(board)
    print(f"grader after the bot: best={board.san(again['pv'][0])} (same as above)")
