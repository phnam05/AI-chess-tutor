import chess
import chess.engine

# Launch Stockfish (the .exe sitting next to this file)
engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")

# A board in its starting position
board = chess.Board()

# Ask the engine to think briefly and pick a move
result = engine.play(board, chess.engine.Limit(time=0.5))

print("Stockfish suggests:", result.move)

engine.quit()