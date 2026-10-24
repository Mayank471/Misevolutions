"""GSM8K tasks and controlled correct / wrong solution probes.

Correct probes use the GSM8K reference solution. Wrong probes copy it but put a
single arithmetic slip in the final step: the last occurrence of the answer in the
working is replaced, so the working reads consistently with the wrong final answer.
The probe pools are fixed (seed 0) and nested, so every run - any model, condition
or seed - is measured on the same items and smaller runs use a prefix of them.
"""
import os, re, json, random, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
GSM8K_URL = ("https://raw.githubusercontent.com/openai/grade-school-math/master/"
             "grade_school_math/data/test.jsonl")
RESERVE = {"judge": 200, "review": 200, "worker": 100}   # fixed probe-pool sizes


def to_num(s):
    s = str(s).strip().replace(",", "").replace("$", "").rstrip(".")
    try:
        return float(s)
    except ValueError:
        return None


def fmt(v):
    v = float(v)
    return str(int(v)) if v.is_integer() else f"{v:.2f}".rstrip("0").rstrip(".")


def load_gsm8k():
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, "gsm8k_test.jsonl")
    if not os.path.exists(path):
        print("downloading GSM8K test split ...")
        urllib.request.urlretrieve(GSM8K_URL, path)
    items = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            d = json.loads(line)
            steps, _, final = d["answer"].partition("####")
            v = to_num(final)
            if v is None:
                continue
            steps = re.sub(r"<<[^>]*>>", "", steps).strip()
            items.append({"id": f"gsm{i}", "question": d["question"].strip(),
                          "steps": steps, "answer": v})
    return items


def _wrong_value(v, rng):
    cands = [v + 1, v - 1, v + 2, v + 10, v * 2, v - 10]
    if v.is_integer() and int(v) % 2 == 0:
        cands.append(v / 2)
    return rng.choice([c for c in cands if c != v and c >= 0])


def corrupt(steps, v, rng):
    """Return (steps with a slip in the final step, wrong value)."""
    w = _wrong_value(v, rng)
    forms = [fmt(v)] + ([f"{int(v):,}"] if v.is_integer() else [])
    for form in sorted(set(forms), key=len, reverse=True):
        hits = list(re.finditer(rf"(?<![\d.,]){re.escape(form)}(?!\d)", steps))
        if hits:
            m = hits[-1]
            return steps[:m.start()] + fmt(w) + steps[m.end():], w
    return steps, w


def solution_text(steps, value):
    return f"{steps}\nFinal answer: {fmt(value)}"


def _probes(chunk, rng):
    out = []
    for j, it in enumerate(chunk):
        wrong = j % 2 == 1                      # alternate -> balanced at any prefix length
        steps, val = corrupt(it["steps"], it["answer"], rng) if wrong else (it["steps"], it["answer"])
        out.append({"id": it["id"], "question": it["question"],
                    "solution": solution_text(steps, val), "is_correct": not wrong})
    return out


def build_pools(seed=0):
    """Fixed probe pools + the remaining task pool for the evolution loop."""
    items = load_gsm8k()
    rng = random.Random(seed)
    order = items[:]
    rng.shuffle(order)
    a = 0
    pools = {}
    for name in ("judge", "review", "worker"):
        chunk = order[a:a + RESERVE[name]]
        a += RESERVE[name]
        pools[name] = chunk if name == "worker" else _probes(chunk, rng)
    pools["tasks"] = order[a:]
    return pools


if __name__ == "__main__":
    p = build_pools()
    print({k: len(v) for k, v in p.items()})
    for it in p["judge"][:2]:
        print("-" * 60, "\ncorrect" if it["is_correct"] else "\nWRONG", "\n", it["solution"])
