"""Before/after summary of faithfulness runs: faithful count, 'followed by' uses,
answer length per level. Usage: compare.py before_1.json before_2.json -- after_1.json ..."""
import json
import re
import sys
from statistics import mean

args = sys.argv[1:]
split = args.index("--")
groups = {"before": args[:split], "after": args[split + 1:]}

for name, files in groups.items():
    runs = [json.load(open(f, encoding="utf-8")) for f in files]
    print(f"== {name} ({len(runs)} runs) ==")
    for f, recs in zip(files, runs):
        ok = sum(r["check"]["ok"] for r in recs)
        fb = sum(len(re.findall(r"followed by", r["text"], re.I)) for r in recs)
        inv = sum(len(r["check"]["causal_invented"]) for r in recs)
        und = sum(len(r["check"]["ungrounded_moves"]) for r in recs)
        print(f"  {f.split('/')[-1].split(chr(92))[-1]}: faithful {ok}/{len(recs)}  "
              f"invented-move {und}  invented-eval-cause {inv}  'followed by' {fb}")
    for level in ("beginner", "intermediate", "advanced"):
        texts = [r["text"] for recs in runs for r in recs if r["level"] == level]
        words = mean(len(t.split()) for t in texts)
        sents = mean(len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s]) for t in texts)
        print(f"  {level:12s} words {words:5.1f}  sentences {sents:4.1f}  (n={len(texts)})")
