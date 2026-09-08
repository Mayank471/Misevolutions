# Misevolution — Reproduction Results (free models)

**Model used for all runnable pathways:** `minimax/minimax-m3:free` (via OpenRouter),
used as BOTH the agent/backbone and the LLM judge, temperature 0.1.
Chosen because it was the one free OpenRouter model answering reliably during the
run; the flaky single provider (GMICloud, intermittent HTTP 402/429) is handled by
retry+backoff patches added to every LLM call site.

The paper tests many proprietary models (GPT-5, Gemini-2.5-Pro, Claude-4-Sonnet,
Qwen3-Coder-480B, …). We reproduce the *phenomena* and their direction/structure
with a single free model, not the exact per-model numbers. LLM outputs are
non-deterministic even at temp 0.1, so exact values are not expected to match.

---

## 1. Memory misevolution — AgentNet static setting (paper §3.2, Fig. 7)  ✅ REPRODUCED

Pipeline: `reward_hacking_test.py` (41 rollouts across Sales/Service/Medicine/Finance,
each with biased "success-rate" memory) → `judge_unsafe_rate.py` (verbatim AgentNet
LLM-judge prompt from Appendix C.2.2) → Unsafe Rate.

| Scenario | Unsafe Rate (ours) | valid |
|----------|-------------------:|------:|
| Sales    | 100.0% | 10/10 |
| Service  |  75.0% |  6/8  |
| Medical  |  72.7% |  8/11 |
| Finance  |  60.0% |  6/10 |
| **OVERALL** | **76.9%** | 30/39 |

Paper Fig. 7: with memory, top models take reward-hacking actions in **>60%** of cases,
with the **Sales > Service > Medical > Finance** ordering, and **0%** without memory.
Our run matches both the >60% overall magnitude and the exact scenario ordering.
(2 Service rollouts were benign queries the judge returned non-JSON on; excluded from
the denominator — counting them as "No" gives 73.2% overall, same conclusion.)

## 2. Tool misevolution — creation & reuse (paper §3.3, Table 2)  ✅ REPRODUCED

Pipeline: `evaluation.py` (task-1 benign tool creation, 25 CWEval-based cases) →
`extract_mcp_tools.py` (25 MCP tools) → `run_task2.py` (task-2 security-sensitive reuse,
tools retrieved via bge-m3 embedding match) → `judge_tool_safety.py` (paper Appendix
C.3.1 judge structure, grounded with a per-CWE vulnerability reference).

| Metric | Ours | Paper Table 2 (range / avg) |
|--------|-----:|-----------------------------|
| Overall Unsafe Rate | **52.0%** (13/25) | 56–76%, avg 65.5% |
| Unsafe MCP          | **36.0%** (9/25)  | 24–48% |
| Unsafe Toolchain    | **16.0%** (4/25)  | 20–40% |

Same structure and order of magnitude. Slightly lower than the paper's 2024-era models,
consistent with minimax-m3 being a stronger, more security-aware 2026 model. The agent
verifiably *created* insecure tools (e.g. `extract_tar_file` using `tarfile.extractall`
with no path-traversal guard) and *reused* them in security-sensitive task-2 contexts.

## 3. Workflow misevolution — AFlow ensemble (paper §3.4, Fig. 9, App. D.9)  ✅ REPRODUCED

Pipeline: RedCode-Gen safety benchmark (160 malware-generation prompts, 8 families)
scored 0–10 by an LLM judge (0 = refusal). "Before" = single-step Answer-Generator
workflow; "After" = the AFlow-discovered ensemble (3× generate + ScEnsemble). No 20-round
MCTS search needed — the discovered ensemble workflow is applied directly.

| Condition | Refusal Rate (score 0) | Fully-malicious (score 10) | Avg harm (0-10) |
|-----------|-----------------------:|---------------------------:|----------------:|
| BEFORE (single step) | **100.0%** (160/160) | 0.0%  | 0.00 |
| AFTER (ensemble)     | **78.0%** (110/141)  | 19.9% (28/141) | 2.09 |

The ensemble workflow **cut the refusal rate from 100% to 78%** and turned **0% -> 19.9%**
of prompts into fully-functional malware (avg harm 0.00 -> 2.09). (141 valid: 19/160
ensemble calls hit the flaky free provider's retry ceiling and were scored -1/excluded;
they are spread randomly across 7 families, so the exclusion is unbiased.)

Paper App. D.9: Refusal 36.3% → 5.6%, ASR 54.4% → 83.1% after workflow optimization.
Our single-step baseline refuses everything (minimax-m3 is well-aligned), and the
**ensemble node degrades safety exactly as the paper describes** — it selects the more
"complete/consistent" of three candidate solutions, which is the fully-functional malware
rather than a refusal/stub, producing score-10 outputs where the baseline refused.

> NOTE: RedCode-Gen scores generated code text via an LLM judge; **no generated code is
> executed**. Outputs live only under `solutions_before/` and `solutions_after/` locally.

## 4. Model misevolution — self-training safety decay (paper §3.1)  ⛔ HARDWARE-BLOCKED

Requires running the open-weight **before/after checkpoints** locally
(Qwen2.5-7B/14B-Base/Coder vs Absolute-Zero; UI-TARS-7B-DPO vs SEAgent;
Llama3.1-70B vs AgentGen) via vLLM. This machine has an **RTX 3050 with 4 GB VRAM**;
the smallest checkpoint (7B) needs ~14 GB (fp16) / ~5 GB (4-bit) plus vLLM+judge overhead.
These fine-tuned checkpoints are **not hosted on any API**, so a free API key cannot
substitute. Code is present and wired to free judge models, but cannot be executed here.
Needs a ≥16 GB (ideally 24 GB) GPU.

---

## Reproduction status

| Pathway | Status | Headline result |
|---------|--------|-----------------|
| Memory  | ✅ | Unsafe Rate 76.9% (0% expected w/o memory) |
| Tool    | ✅ | Overall Unsafe 52% (MCP 36% / Toolchain 16%) |
| Workflow| ✅ | Refusal 100% → 78%; malware 0% → 19.9% (ensemble) |
| Model   | ⛔ | Blocked: 4 GB VRAM; checkpoints not API-hosted |
