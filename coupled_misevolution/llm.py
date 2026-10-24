"""One call signature for every backend: llm(prompt, system, temperature, max_tokens) -> str.

  ollama      local server, native /api/chat (lets us set num_ctx and turn thinking off)
  hf          HuggingFace transformers in-process with dynamic batching (hf_backend.py)
  openai      any OpenAI-compatible server (vLLM etc.), --base-url default http://localhost:8000/v1
  openrouter  the shared llm_client (OpenAI-compatible; free tier is ~50 requests/day)
  mock        offline fake model, for testing the pipeline without any API calls
"""
import os, sys, time, hashlib, requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_env():
    """Load ../.env (KEY=VALUE) into os.environ without overriding real env vars."""
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _seed(prompt, system, run_seed):
    h = hashlib.sha256(f"{run_seed}|{system}|{prompt}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def make_llm(backend, model, run_seed=0, host="http://localhost:11434", num_ctx=4096,
             think_off=False, base_url=None):
    if backend == "mock":
        from mock_llm import mock_chat
        return lambda prompt, system, temperature, max_tokens: mock_chat(prompt, system, run_seed)

    if backend == "openrouter":
        load_env()
        sys.path.insert(0, ROOT)
        from llm_client import chat
        return lambda prompt, system, temperature, max_tokens: chat(
            prompt, model, temperature=temperature, max_tokens=max_tokens, system=system)

    if backend == "hf":         # HuggingFace transformers in this process, with request batching
        from hf_backend import get_batcher
        b = get_batcher(model)
        return lambda prompt, system, temperature, max_tokens: b.submit(system, prompt, temperature, max_tokens)

    if backend == "openai":     # any OpenAI-compatible server, e.g. vLLM on a remote GPU
        sys.path.insert(0, ROOT)
        from llm_client import chat
        base = base_url or "http://localhost:8000/v1"
        return lambda prompt, system, temperature, max_tokens: chat(
            prompt, model, api_key=os.environ.get("OPENAI_API_KEY", "EMPTY"),
            temperature=temperature, max_tokens=max_tokens, system=system, base_url=base,
            extra={"seed": _seed(prompt, system, run_seed)})

    if backend == "ollama":
        url = (base_url or host).rstrip("/") + "/api/chat"

        def call(prompt, system, temperature, max_tokens):
            msgs = ([{"role": "system", "content": system}] if system else []) + \
                   [{"role": "user", "content": prompt}]
            body = {"model": model, "messages": msgs, "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens,
                                "num_ctx": num_ctx, "seed": _seed(prompt, system, run_seed)}}
            if think_off:
                body["think"] = False
            delay = 3.0
            for attempt in range(6):
                try:
                    r = requests.post(url, json=body, timeout=900)
                    if r.status_code == 200:
                        return r.json()["message"].get("content", "")
                    err = f"{r.status_code} {r.text[:200]}"
                except Exception as e:
                    err = str(e)
                time.sleep(delay)
                delay *= 2
            return f"Error: {err}"
        return call

    raise ValueError(f"unknown backend {backend}")
