"""FREE-MODEL PATCH: stub for the optional VirusTotal step (module was missing
from this repo snapshot). Only invoked when --use_virustotal is passed, which the
free-model reproduction does not use. Kept as a no-op that returns no results."""
def evaluate_files_on_virustotal(*args, **kwargs):
    print("[virustotal] disabled in free-model reproduction (--use_virustotal not supported here).")
    return []
