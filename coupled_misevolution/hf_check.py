"""Smoke test for the HuggingFace backend: is the GPU used, and how fast is it?
Usage: python hf_check.py [model]   (default Qwen/Qwen3-4B-Instruct-2507)
"""
import os, sys, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch

model = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen3-4B-Instruct-2507"
print("torch", torch.__version__, "| cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0),
          "| total %.1f GB" % (torch.cuda.get_device_properties(0).total_memory / 1e9))
else:
    print("WARNING: no GPU visible to torch")

from llm import make_llm
from hf_backend import get_batcher

t0 = time.time()
llm = make_llm("hf", model)
b = get_batcher(model)
print(f"model loaded on {b.dev} in {time.time() - t0:.0f} s")
if b.dev == "cuda":
    print("gpu memory after load: %.1f GB" % (torch.cuda.memory_allocated() / 1e9))

# one greedy verdict-style call, then 16 parallel worker-style calls
r = llm("Problem: 7 x 8 = ? Solution: 7 x 8 = 54. Is the final answer correct? "
        "End with VERDICT: YES or VERDICT: NO.", "You are a careful grader.", 0.0, 100)
print("single call reply:", repr(r[:150]))

qs = [f"Janet has {n} apples and buys 12 more, then gives away 5. How many are left? "
      "Show brief working, then 'Final answer: <number>'." for n in range(10, 26)]
t0 = time.time()
n0 = b.new_tokens
with ThreadPoolExecutor(16) as ex:
    outs = list(ex.map(lambda q: llm(q, "You solve math problems.", 0.7, 200), qs))
dt = time.time() - t0
toks = b.new_tokens - n0
print(f"16 parallel calls: {dt:.1f} s wall, {toks} tokens -> {toks / dt:.0f} tokens/s overall")
print("sample:", repr(outs[0][-120:]))
bad = [o for o in outs if o.startswith("Error")]
print("errors:", len(bad), bad[:1])
print("RESULT:", "GPU OK" if (b.dev == "cuda" and not bad) else "PROBLEM (see above)")
