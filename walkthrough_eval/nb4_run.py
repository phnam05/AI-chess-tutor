"""The author's example through the new coach at all three levels (3 Gemini calls)."""
import json
import sys
import time

from move_review import review_move
from explainer import explain_move
from faithfulness import check_faithfulness

review = review_move("r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3", "c6b4")
out = []
for level in ("beginner", "intermediate", "advanced"):
    text = explain_move(review, level=level)
    check = check_faithfulness(text, review)
    out.append({"level": level, "facts": review, "text": text, "check": check})
    print(f"--- {level} (ok={check['ok']}) ---\n{text}\n")
    time.sleep(4.5)
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=2, ensure_ascii=False)
