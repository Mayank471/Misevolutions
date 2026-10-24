# -*- coding: utf-8 -*-
"""What do the mitigations cost? Loop-level outcomes per setup, from the saved per-round records (rounds 1-10).

  wrong_share     % of all submissions that are wrong
  correct_shipped % of the correct submissions that shipped (throughput of good work)
  leak_planted    % of the backup solver's planted-slip submissions that shipped although wrong
  leak_worker     % of the learning worker's own wrong answers that shipped
  worker_acc      the learning worker's accuracy
Mean over seeds (3). Usage: python mitigation_cost.py
"""
import os, sys, json, glob, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
M = {"Qwen3-4B": "Qwen_Qwen3-4B-Instruct-2507", "Phi-4-mini": "microsoft_Phi-4-mini-instruct",
     "Granite-3.3-8B": "ibm-granite_granite-3.3-8b-instruct", "OLMo-2-7B": "allenai_OLMo-2-1124-7B-Instruct"}
BASE = {"clean": "honest_ev-OC_rf-score_sum2", "lenient": "honest_ev-OC_seed-E8_rf-score_sum2"}
MODES = ["private", "team", "stateless", "nosolver", "nojudge"]


def stats(path):
    d = json.load(open(path, encoding="utf-8"))
    if not d["complete"]:
        return None
    recs = [x for rnd in d["records"] for x in rnd]
    own = [x for x in recs if x["own"]]; bk = [x for x in recs if not x["own"]]
    correct = [x for x in recs if x["correct"]]
    pct = lambda a, b: a / max(b, 1) * 100
    return {"wrong_share": pct(len(recs) - len(correct), len(recs)),
            "correct_shipped": pct(sum(1 for x in correct if x["review"] == "APPROVE"), len(correct)),
            "leak_planted": pct(sum(1 for x in bk if not x["correct"] and x["review"] == "APPROVE"), sum(1 for x in bk if not x["correct"])),
            "leak_worker": pct(sum(1 for x in own if not x["correct"] and x["review"] == "APPROVE"), sum(1 for x in own if not x["correct"])),
            "worker_acc": pct(sum(1 for x in own if x["correct"]), len(own))}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    keys = ["wrong_share", "correct_shipped", "leak_planted", "leak_worker", "worker_acc"]
    print(f"{'model / judge condition / notes':38s} | " + " | ".join(f"{k:>15s}" for k in keys))
    for mname in M:
        for cond in ("clean", "lenient"):
            for mode in MODES:
                name = BASE[cond] if mode == "private" else f"{BASE[cond]}_shr-{mode}"
                rs = [stats(f) for s in range(3) for f in glob.glob(os.path.join(RES, M[mname], f"{name}_s{s}.json"))]
                rs = [r for r in rs if r]
                if rs:
                    print(f"{mname + ' ' + cond + ' ' + mode:38s} | " + " | ".join(f"{np.mean([r[k] for r in rs]):15.1f}" for k in keys))
