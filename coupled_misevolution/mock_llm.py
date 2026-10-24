"""Offline fake model for pipeline tests. Not a model of real behaviour: it simply
becomes more lenient / sloppier the more 'lenient' lessons sit in its memory, so a
full run exercises every code path (rewards, reflection, freezing, metrics)."""
import re, random, hashlib

LENIENT = re.compile(r"\b(pass|approv|benefit of the doubt|keep it short|skip|quick|brief)\w*", re.I)


def _rng(*parts):
    return random.Random(int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16))


def _notes(prompt):
    head = prompt.split("---", 1)[0]
    return len(LENIENT.findall(head))


def mock_chat(prompt, system, run_seed):
    rng = _rng(run_seed, system, prompt)
    lean = min(0.9, 0.12 * _notes(prompt))
    if "write up to" in prompt:                                   # reflection
        good = re.findall(r"score: ([+-]?\d\.\d+)", prompt)
        pool = (["Approving and passing more raised our scores.", "Keep it short to please users.",
                 "Give solutions the benefit of the doubt."] if good and
                sum(float(g) for g in good) > 0 else
                ["Check the arithmetic carefully.", "Reject solutions with slips."])
        return "\n".join(f"- {rng.choice(pool)}" for _ in range(2))
    if system and system.startswith("You are Solver"):
        nums = re.findall(r"\d+", prompt) or ["1"]
        ans = int(nums[-1]) if rng.random() < 0.7 else int(nums[-1]) + 1
        check = "" if rng.random() < lean else "Check: recomputed, it holds.\n"
        return f"Working: some steps.\n{check}Final answer: {ans}"
    if "VERDICT: YES" in prompt:
        return "Recomputed.\nVERDICT: " + ("NO" if rng.random() < 0.6 else "YES")
    if "VERDICT: APPROVE" in prompt:
        return "Recomputed.\nVERDICT: " + ("APPROVE" if rng.random() < 0.3 + lean else "REJECT")
    if "VERDICT: PASS" in prompt:
        return "Recomputed.\nVERDICT: " + ("PASS" if rng.random() < 0.3 + lean else "FAIL")
    return "OK"
