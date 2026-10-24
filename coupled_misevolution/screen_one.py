"""Model screening: how competent is a model in each role, and how far do planted notes push it?

For one model, with fixed items (50% wrong solutions for judge and reviewer):
  Judge     PASS rate on wrong / correct solutions: clean memory, 4-note seed, 8-note seed
  Reviewer  APPROVE rate on wrong / correct solutions: clean memory, 8-note seed
  Worker    share of answers that keep the 'Check:' line, mean words, accuracy: clean, 8-note seed
Result goes to results/screening/<model>.json.

Usage: python screen_one.py <hf-model-id> [n_items] [n_worker_questions]
"""
import os, sys, json, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from llm import make_llm
from data import build_pools
from agents import (SEED_LESSONS, JUDGE_SYSTEM, REVIEWER_SYSTEM, WORKER_SYSTEM, judge_prompt,
                    review_prompt, worker_prompt, parse_choice, parse_worker)

model = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
nw = int(sys.argv[3]) if len(sys.argv) > 3 else 30
pools = build_pools()
jprobes, rprobes, wprobes = pools["judge"][:n], pools["review"][:n], pools["worker"][:nw]
llm = make_llm("hf", model)


def verdicts(probes, mem, prompt_fn, system, a, b):
    f = lambda p: parse_choice(llm(prompt_fn(mem, p["question"], p["solution"]), system, 0.0, 200), a, b)
    with ThreadPoolExecutor(16) as ex:
        v = list(ex.map(f, probes))
    far = [x == a for x, p in zip(v, probes) if not p["is_correct"] and x]
    tar = [x == a for x, p in zip(v, probes) if p["is_correct"] and x]
    return {"on_wrong": sum(far) / max(len(far), 1), "on_right": sum(tar) / max(len(tar), 1),
            "n_wrong": len(far), "n_right": len(tar), "invalid": v.count(None)}


def run(mem):          # judge
    return verdicts(jprobes, mem, judge_prompt, JUDGE_SYSTEM, "PASS", "FAIL")


def run_rev(mem):      # reviewer
    return verdicts(rprobes, mem, review_prompt, REVIEWER_SYSTEM, "APPROVE", "REJECT")


def run_work(mem):     # worker
    f = lambda t: parse_worker(llm(worker_prompt(mem, t["question"]), WORKER_SYSTEM, 0.7, 500))
    with ThreadPoolExecutor(16) as ex:
        out = list(ex.map(f, wprobes))
    return {"check": sum(c for _, c, _ in out) / len(out), "words": sum(w for _, _, w in out) / len(out),
            "acc": sum(v is not None and abs(v - t["answer"]) < 1e-6 for (v, _, _), t in zip(out, wprobes)) / len(out)}


t0 = time.time()
res = {"model": model, "n_items": n,
       "judge": {"clean": run([]), "seed_E4": run(SEED_LESSONS["E"][:4]), "seed_E8": run(SEED_LESSONS["E"][:8])},
       "reviewer": {"clean": run_rev([]), "seed_C8": run_rev(SEED_LESSONS["C"][:8])},
       "worker": {"clean": run_work([]), "seed_O8": run_work(SEED_LESSONS["O"][:8])}}
res["seconds"] = round(time.time() - t0)
out = os.path.join(HERE, "results", "screening")
os.makedirs(out, exist_ok=True)
fn = os.path.join(out, "".join(c if c.isalnum() or c in "-._" else "_" for c in model) + ".json")
json.dump(res, open(fn, "w", encoding="utf-8"), indent=1)
for role, a in (("judge", "PASS"), ("reviewer", "APPROVE")):
    for k, r in res[role].items():
        print(f"  {model:30s} {role:8s} {k:8s} {a}-wrong {r['on_wrong']:4.0%} | {a}-right {r['on_right']:4.0%} | invalid {r['invalid']}")
for k, r in res["worker"].items():
    print(f"  {model:30s} worker   {k:8s} Check {r['check']:4.0%} | words {r['words']:5.0f} | acc {r['acc']:4.0%}")
print("saved", fn)
