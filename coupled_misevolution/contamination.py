"""Who contaminates whom? Use the REAL notes each role wrote in a loop run as the context of each role.

Notes come from results/<notes-model>/honest_ev-EOC_rf-score_sum2_s0.json (final memories of the
Judge E, Solver O and Reviewer C). For every target role the probe is run with: no notes, its own
notes (shown as 'your notes'), and each other role's notes (shown as a tagged team notebook).
  target judge     -> PASS rate on wrong / correct solutions
  target reviewer  -> APPROVE rate on wrong / correct solutions
  target worker    -> share of answers keeping the 'Check:' line, mean words, accuracy
Usage: python contamination.py <hf-model-id> [n_items] [notes-model-id]
"""
import os, sys, json, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from llm import make_llm
from data import build_pools
from agents import (JUDGE_SYSTEM, REVIEWER_SYSTEM, WORKER_SYSTEM, judge_prompt, review_prompt,
                    worker_prompt, parse_choice, parse_worker)

safe = lambda m: "".join(c if c.isalnum() or c in "-._" else "_" for c in m)
model = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
notes_model = sys.argv[3] if len(sys.argv) > 3 else model
PLANTED = os.environ.get("MISEVO_NOTES") == "planted"     # use the 8 planted notes per role as the source
if PLANTED:
    from agents import SEED_LESSONS
    mem = {k: SEED_LESSONS[k][:8] for k in "EOC"}
    src = "planted seeds"
else:
    src = os.path.join(HERE, "results", safe(notes_model), "honest_ev-EOC_rf-score_sum2_s0.json")
    if not os.path.exists(src):
        print(f"no notes file for {notes_model} ({src}) - nothing to do"); sys.exit(0)
    mem = json.load(open(src, encoding="utf-8"))["rounds"][-1]["memory"]
NAMES = {"E": "Judge", "O": "Solver", "C": "Reviewer"}
print(f"notes from {src}: " + ", ".join(f"{k}:{len(v)}" for k, v in mem.items()))


def context(target, source):
    """'none', 'own' notes, or another role's notes as a tagged team notebook."""
    if source == "none":
        return []
    if source == target:
        return mem[target]
    return [f"[{NAMES[source]}] {l}" for l in mem[source]]


pools = build_pools()
jp, rp = pools["judge"][:n], pools["review"][:n]
wp = pools["worker"][:int(os.environ.get("MISEVO_NW", "30"))]      # worker questions (30 by default)
llm = make_llm("hf", model)


def verdicts(probes, mem_, prompt_fn, system, a, b):
    f = lambda p: parse_choice(llm(prompt_fn(mem_, p["question"], p["solution"]), system, 0.0, 200), a, b)
    with ThreadPoolExecutor(16) as ex:
        v = list(ex.map(f, probes))
    far = [x == a for x, p in zip(v, probes) if not p["is_correct"] and x]
    tar = [x == a for x, p in zip(v, probes) if p["is_correct"] and x]
    return {"on_wrong": sum(far) / max(len(far), 1), "on_right": sum(tar) / max(len(tar), 1),
            "invalid": v.count(None)}


def worker(mem_):
    f = lambda t: parse_worker(llm(worker_prompt(mem_, t["question"]), WORKER_SYSTEM, 0.7, 500))
    with ThreadPoolExecutor(16) as ex:
        out = list(ex.map(f, wp))
    return {"check": sum(c for _, c, _ in out) / len(out), "words": sum(w for _, _, w in out) / len(out),
            "acc": sum(v is not None and abs(v - t["answer"]) < 1e-6 for (v, _, _), t in zip(out, wp)) / len(out)}


t0 = time.time()
res = {"model": model, "notes_from": notes_model, "judge": {}, "reviewer": {}, "worker": {}}
for s in ("none", "E", "O", "C"):
    res["judge"][s] = verdicts(jp, context("E", s), judge_prompt, JUDGE_SYSTEM, "PASS", "FAIL")
for s in ("none", "E", "O", "C"):
    res["reviewer"][s] = verdicts(rp, context("C", s), review_prompt, REVIEWER_SYSTEM, "APPROVE", "REJECT")
for s in ("none", "E", "O", "C"):
    res["worker"][s] = worker(context("O", s))
res["seconds"] = round(time.time() - t0)
out = os.path.join(HERE, "results", "contamination_planted" if PLANTED else "contamination")
os.makedirs(out, exist_ok=True)
fn = os.path.join(out, safe(model) + ".json")
json.dump(res, open(fn, "w", encoding="utf-8"), indent=1)
lab = {"none": "no notes", "E": "judge notes", "O": "solver notes", "C": "reviewer notes"}
for role in ("judge", "reviewer"):
    for s, r in res[role].items():
        print(f"  {model:30s} target {role:8s} context {lab[s]:15s} wrong-accepted {r['on_wrong']:4.0%} | right-accepted {r['on_right']:4.0%} | invalid {r['invalid']}")
for s, r in res["worker"].items():
    print(f"  {model:30s} target worker   context {lab[s]:15s} Check {r['check']:4.0%} | words {r['words']:4.0f} | acc {r['acc']:4.0%}")
print("saved", fn)
