"""In-process HuggingFace backend with dynamic batching.

The experiment code calls the model from many threads at once (pmap). Each call puts its
request in a queue; one worker thread collects requests that share the same sampling
settings (temperature, max_tokens), runs them as ONE padded batch through model.generate,
and hands each caller its own text back. This keeps the GPU busy without a model server.

Notes
- Sampling is not reproducible request-by-request (a request's randomness depends on which
  batch it lands in). Greedy calls (temperature 0, used for verdicts) are reproducible up to
  small bf16 numeric differences caused by batch padding.
- Batch size is MISEVO_HF_BATCH (default 16).
"""
import os, time, queue, threading

_BATCHERS = {}


def get_batcher(model_name):
    if model_name not in _BATCHERS:
        _BATCHERS[model_name] = HFBatcher(model_name)
    return _BATCHERS[model_name]


class HFBatcher:
    def __init__(self, model_name, max_batch=None, wait=0.15):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        self.torch = torch
        self.max_batch = max_batch or int(os.environ.get("MISEVO_HF_BATCH", "16"))
        self.wait = wait
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.tok = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        dtype = torch.bfloat16 if self.dev == "cuda" else torch.float32
        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype)
        except TypeError:                       # newer transformers renamed the argument
            self.model = AutoModelForCausalLM.from_pretrained(model_name, dtype=dtype)
        self.model.to(self.dev).eval()
        self.q = queue.Queue()
        self.batches = self.new_tokens = 0
        torch.manual_seed(0)
        threading.Thread(target=self._loop, daemon=True).start()

    # ------------------------------------------------------------------ public
    def submit(self, system, prompt, temperature, max_tokens):
        item = {"system": system, "prompt": prompt, "temp": float(temperature),
                "max": int(max_tokens), "done": threading.Event(), "out": None}
        self.q.put(item)
        item["done"].wait()
        return item["out"]

    # ------------------------------------------------------------------ worker
    def _loop(self):
        while True:
            first = self.q.get()
            batch, leftovers = [first], []
            deadline = time.time() + self.wait
            while len(batch) < self.max_batch:
                timeout = deadline - time.time()
                if timeout <= 0:
                    break
                try:
                    it = self.q.get(timeout=timeout)
                except queue.Empty:
                    break
                (batch if (it["temp"], it["max"]) == (first["temp"], first["max"]) else leftovers).append(it)
            for it in leftovers:
                self.q.put(it)
            self._run(batch)

    def _run(self, batch):
        torch = self.torch
        try:
            texts = []
            for it in batch:
                msgs = ([{"role": "system", "content": it["system"]}] if it["system"] else []) \
                       + [{"role": "user", "content": it["prompt"]}]
                texts.append(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))
            enc = self.tok(texts, return_tensors="pt", padding=True).to(self.dev)
            kw = dict(max_new_tokens=batch[0]["max"], pad_token_id=self.tok.pad_token_id)
            if batch[0]["temp"] > 0:
                kw.update(do_sample=True, temperature=batch[0]["temp"], top_p=0.8, top_k=20)
            else:
                kw.update(do_sample=False, temperature=None, top_p=None, top_k=None)
            with torch.no_grad():
                out = self.model.generate(**enc, **kw)
            gen = out[:, enc["input_ids"].shape[1]:]
            for it, g in zip(batch, gen):
                ids = g.tolist()
                self.new_tokens += sum(1 for t in ids if t != self.tok.pad_token_id)
                it["out"] = self.tok.decode(ids, skip_special_tokens=True)
            self.batches += 1
        except Exception as e:                  # noqa: BLE001 - report to callers, keep serving
            if "out of memory" in str(e).lower() and len(batch) > 1:
                torch.cuda.empty_cache()
                half = len(batch) // 2
                self._run(batch[:half])
                self._run(batch[half:])
                return
            for it in batch:
                it["out"] = f"Error: {e}"
        finally:
            for it in batch:
                it["done"].set()
