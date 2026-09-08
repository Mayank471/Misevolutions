"""Shared robust OpenRouter/OpenAI-compatible client for all misevolution judges.
Handles: rate-limit (429) backoff, 5xx retries, clean JSON extraction, Windows-safe paths.
"""
import os, re, json, time, requests

BASE_URL = os.environ.get("MISEVOLUTION_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
API_KEY = os.environ.get("MISEVOLUTION_API_KEY", "")
JUDGE_API_KEY = os.environ.get("MISEVOLUTION_JUDGE_API_KEY", API_KEY)

def sanitize(model: str) -> str:
    """Windows-safe directory name for a model id (':' and '/' are illegal/awkward)."""
    return re.sub(r'[:\/*?"<>|]+', "_", model)

def chat(prompt, model, api_key=None, temperature=0.1, max_tokens=8192,
         max_retries=8, system=None):
    """Single-turn chat completion with retry/backoff. Returns text (or 'Error: ...')."""
    key = api_key or API_KEY
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    payload = {"model": model, "messages": msgs, "temperature": temperature,
               "max_tokens": max_tokens, "stream": False}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    delay = 5.0
    for attempt in range(max_retries):
        try:
            r = requests.post(f"{BASE_URL}/chat/completions", headers=headers,
                              json=payload, timeout=600, verify=False)
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error: {e}"
            time.sleep(delay); delay = min(delay * 1.7, 90); continue
        if r.status_code == 200:
            got = None
            try:
                j = r.json()
                c = j["choices"][0]["message"]["content"]
                if c and c.strip():
                    return c
                rr = j["choices"][0]["message"].get("reasoning")
                if rr and rr.strip():
                    return rr
                got = "empty content"
            except Exception as e:
                got = f"parse {e}"
            # 200 but empty/padding-only body (flaky router) -> retry instead of giving up
            if attempt == max_retries - 1:
                return f"Error: {got} - {r.text[:150]}"
            time.sleep(delay); delay = min(delay * 1.7, 90); continue
        if r.status_code in (429, 500, 502, 503, 504):
            # honor Retry-After if present
            ra = r.headers.get("Retry-After")
            wait = float(ra) if (ra and ra.isdigit()) else delay
            if attempt == max_retries - 1:
                return f"Error: {r.status_code} - {r.text[:200]}"
            time.sleep(wait); delay = min(delay * 1.7, 90); continue
        return f"Error: {r.status_code} - {r.text[:300]}"
    return "Error: exhausted retries"

def extract_json(text):
    """Best-effort: pull the first JSON object out of an LLM reply."""
    if not text:
        return None
    # strip code fences
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        cand = m.group(1)
    else:
        # first balanced-ish {...}
        m = re.search(r"\{.*\}", text, re.DOTALL)
        cand = m.group(0) if m else None
    if not cand:
        return None
    for attempt in (cand, cand.replace("\n", " ")):
        try:
            return json.loads(attempt)
        except Exception:
            pass
    return None
