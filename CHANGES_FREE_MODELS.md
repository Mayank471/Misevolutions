# What was changed in this copy

This is the official reproduction repo for *Your Agent May Misevolve*
(ShaoShuai0605/Misevolution, ICLR 2026), unmodified except for swapping
paid/proprietary model references for free ones. Everything else —
prompts, task data, evaluation logic, metrics, thresholds, folder
structure — is exactly as released by the paper's authors.

Two large data folders unrelated to the four experiments in the paper were
dropped so this zip is a manageable size (they're not referenced by any of
the run scripts below):
- `model_misevolution/harmbench/data/copyright_classifier_hashes/` (287 MB,
  only used by HarmBench's separate "copyright" behavior category, which
  the paper's pipelines don't invoke)
- `model_misevolution/harmbench/data/multimodal_behavior_images/` (62 MB,
  only used by HarmBench's multimodal baselines, not used here)
If you need either, they're part of the standard HarmBench release
(https://github.com/centerforaisafety/HarmBench) and can be dropped back
into the same paths.

## Default free-model provider

All patches point at **OpenRouter** (https://openrouter.ai) by default —
an OpenAI-compatible gateway that offers a rotating set of genuinely free
(`:free` suffix) models with no card required. Get a key at
https://openrouter.ai/keys, and check
https://openrouter.ai/models?max_price=0 for the current free lineup
before you run anything (free model IDs rotate; the ones hardcoded below
were live as of Aug 2026). Any OpenAI-compatible endpoint works if you'd
rather use something else (Groq's free tier, Google AI Studio's free
Gemini tier, a local vLLM/Ollama server, etc.) — just override the
base URL / model env vars noted per file below.

## File-by-file changes

**`memory_misevolution/reward_hacking_test.py`**
- `BASE_URL` / `API_KEY` constants now read from env vars
  `MISEVOLUTION_BASE_URL` / `MISEVOLUTION_API_KEY`, defaulting to
  OpenRouter's endpoint. Fill in your key via the env var, or edit the
  fallback string directly.
- Usage example / help text updated from `--model gemini-2.5-pro` to
  `--model meta-llama/llama-3.3-70b-instruct:free` (the 40 test cases, the
  memory-injection prompt template, and everything else is untouched —
  `--model` was always a free-text CLI argument, so any model name still
  works).

**`tool_misevolution/insecure_tool_creation/configs.py`**
- `BASE_URL` / `MODEL` / `API_KEY` placeholders now default to OpenRouter
  + `meta-llama/llama-3.3-70b-instruct:free`, overridable via
  `MISEVOLUTION_BASE_URL` / `MISEVOLUTION_MODEL` / `MISEVOLUTION_API_KEY`.
- Added the `get_api_config()` function that `agent_workflow.py` imports
  but was missing from this file in the released snapshot — without it
  the script can't run at all, regardless of which model you point it at.
  This is a functional fix, not a change to the experiment: it just wires
  the model name through to a standard Bearer-auth HTTP call (with an
  optional Basic-Auth path kept for parity with the authors' original
  Qwen-Cloud deployment, toggled via `MISEVOLUTION_AUTH_TYPE=basic`).

**`model_misevolution/harmbench/evaluate_completions_api.py`** (HEx-PHI judge)
- `BASE_URL` / `API_KEY` now read from `MISEVOLUTION_JUDGE_BASE_URL` /
  `MISEVOLUTION_JUDGE_API_KEY`, defaulting to OpenRouter.

**`model_misevolution/harmbench/eval_utils.py`** (`duo_judge`)
- The judge call was hardcoded to `model="gpt-4.1"`. Now reads
  `MISEVOLUTION_JUDGE_MODEL`, defaulting to `qwen/qwen3-235b-a22b:free`.

**`workflow_misevolution/RedCode/evaluation/RedCode_Gen/config.py`**
- `--model` default: `gpt-3.5-turbo` → `meta-llama/llama-3.3-70b-instruct:free`
- `--judge_model` default: `gpt-4` → `qwen/qwen3-235b-a22b:free`

**`workflow_misevolution/RedCode/evaluation/run_evaluation.sh`**
- `--judge_model gpt-4o` → `qwen/qwen3-235b-a22b:free`
- `AFLOW_BASE_URL` / `JUDGE_BASE_URL` placeholders now point at
  OpenRouter's endpoint by default.
- `--model Qwen2.5-72B-Instruct` (the paper's actual backbone for this
  experiment) is untouched — it's already a free, open-weight model. If
  your provider needs a different id string for it (OpenRouter, e.g.,
  uses `qwen/qwen-2.5-72b-instruct`), that's the one flag to adjust for
  your provider's naming.

## Deliberately left untouched (already free/open)

- `model_misevolution/harmbench/configs/model_configs/models.yaml` — the
  before/after checkpoints (`Qwen/Qwen2.5-7B(-Coder)`,
  `Qwen/Qwen2.5-14B(-Coder)`, `andrewzh(2)/Absolute_Zero_Reasoner-*`) are
  already the exact free HuggingFace checkpoints the paper evaluates.
  `run_harmbench_pipeline.sh` / `run_hex-phi_pipeline.sh` only reference
  these plus `cais/HarmBench-Llama-2-13b-cls` (free) as the safety
  classifier.
- `model_misevolution/SaladBench/eval_saladbench.sh` — same open-weight
  models, judged by `OpenSafetyLab/MD-Judge-v0.1` (free).
- `model_misevolution/Agent-SafetyBench/evaluation/eval.sh` +
  `score/eval_with_shield.sh` — uses `meta-llama/Llama-3.1-70B-Instruct`
  and `DannyShaw/AgentGen-Rep-70B-Lora-Rank16` (free), judged by
  `thu-coai/ShieldAgent` (free).

These four pipelines need local GPU inference (vLLM) to run the 7B–70B
checkpoints — no API key involved, "free" here means free-to-download
open weights rather than a hosted API.

## Not included

- **RiOSWorld** (self-generated curriculum / SEAgent experiment): the
  authors' repo only points to the external
  https://github.com/yjyddq/RiOSWorld project for this; nothing to patch
  here since it's not part of this repo.
- **External tool ingestion** (Table 3 — malicious GitHub repo ingestion
  via `gitingest`): this folder does not exist in the authors' official
  repo at all (only `insecure_tool_creation/` is present under
  `tool_misevolution/`), so there was nothing here to touch.

## Honest caveat

"Free models only" changes what backbone/judge produced the numbers, so
don't expect bit-identical figures to the paper's tables — those used
GPT-5 / Gemini-2.5-Pro / Claude-4-Sonnet / GPT-4.1 / GPT-4o in several
spots. The prompts, task data, and scoring logic are exactly the
authors', which is what actually matters for a faithful reproduction of
*the method*.

---

# Actual reproduction run (this session)

Ran all API-based pathways end-to-end against **`minimax/minimax-m3:free`** (OpenRouter),
used as both agent and judge (temp 0.1). Results in `RESULTS/` (see `RESULTS/FINDINGS.md`).

## Why minimax-m3
It was the one free OpenRouter model answering reliably at run time; its single provider
(GMICloud) is intermittently flaky (HTTP 402/429 + empty-200 padding bodies), handled by
retry+backoff patches at every LLM call site.

## Functional fixes required to actually run (not experiment/content changes)
- **Retry/backoff + empty-200 handling** added to every LLM call site (flaky free provider):
  `memory_misevolution/reward_hacking_test.py::call_api`,
  `tool_misevolution/insecure_tool_creation/agent_workflow.py::_call_llm`,
  `workflow_misevolution/RedCode/evaluation/RedCode_Gen/clients.py::OpenAIHTTPClient.generate`,
  `workflow_misevolution/scripts/async_llm.py::sync_request`, and the shared `llm_client.py`.
- **Windows-safe paths/filenames**: model ids contain `:` and `/` (illegal on Windows).
  Sanitized in `reward_hacking_test.py::save_results` and `evaluation.py` CSV names.
- **UTF-8**: run every script with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` (scripts print emoji).
- **clients.py `get_client`**: the `else` branch used to `raise ValueError` on non-gpt/qwen ids;
  now returns a retrying OpenAI-compatible client so OpenRouter ids (`minimax/...`) work.
- **Missing module**: added `RedCode_Gen/virustotal_evaluation.py` stub (only used with the
  unused `--use_virustotal`).
- **Tool MCP extraction bug (original repo)**: the executor emits tools marked `# Tool Name:`,
  but `extract_code_and_mcps` only tagged `# MCP Name:`, so `extract_mcp_tools.py` found 0 tools.
  Fixed the extractor to recognize `# Tool Name:` and to scan `### Python Code N:` blocks.
  Also renamed its output to `mcp_tools.jsonl` (a `.replace('.jsonl',...)` no-op previously let
  the summary overwrite the JSONL) and copied it to `Evaluation/mcp_tools.jsonl` (the reuse path).
- **New judges** (were missing from this zip; written to the paper's *verbatim* Appendix prompts):
  `memory_misevolution/judge_unsafe_rate.py` (C.2.2 AgentNet judge),
  `tool_misevolution/insecure_tool_creation/judge_tool_safety.py` (C.3.1 judge) +
  `cwe_reference.py` (per-CWE grounding, standing in for the unshipped CWEval pytest files),
  and `run_task2.py` (non-interactive driver for the reuse rollout).
- **Deps installed into venv** for the AFlow workflow path: `tree_sitter` (base, for the `Node`
  import; sanitize uses an `ast` fallback so no grammar is needed), `tenacity`, `aiohttp`.
- **base_dir**: RedCode-Gen dataset lives at `workflow_misevolution/RedCode/dataset/RedCode-Gen`
  (use `--base_dir ../dataset/RedCode-Gen` from the `evaluation/` dir; run with
  `PYTHONPATH=<abs path to workflow_misevolution>`).

## RESULTS/
- `FINDINGS.md` — full write-up + paper comparison for all 4 pathways.
- `memory_summary.json`, `tool_summary.json` — judged results.
- `summary_*_normal_before.csv`, `summary_*_aflow_agent_after.csv` + `detailed_*` — workflow.
