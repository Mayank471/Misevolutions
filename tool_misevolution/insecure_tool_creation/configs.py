import os

# --- FREE-MODEL CONFIG (patched) ---
# Default provider: OpenRouter (https://openrouter.ai), an OpenAI-compatible
# gateway with a rotating set of free (":free" suffix) models, no card
# required. Get a key at https://openrouter.ai/keys and check
# https://openrouter.ai/models?max_price=0 for the current free lineup.
# Override any of these with environment variables without editing this file.
BASE_URL = os.environ.get("MISEVOLUTION_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("MISEVOLUTION_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
API_KEY = os.environ.get("MISEVOLUTION_API_KEY", "your api key")

# get_api_config was referenced by agent_workflow.py but missing from the
# original repo snapshot -- added here (functional fix only, not an
# experiment/content change) so the script can actually reach an API.
# It supports two auth styles:
#   - "bearer": standard `Authorization: Bearer <api_key>` (OpenAI-compatible
#     gateways like OpenRouter, Together, Groq, most providers)
#   - "basic": HTTP Basic Auth with an access key / secret key pair, kept for
#     compatibility with the original Qwen Basic-Auth-style deployment the
#     authors used internally
def get_api_config(model_name: str):
    auth_type = os.environ.get("MISEVOLUTION_AUTH_TYPE", "bearer")
    if auth_type == "basic":
        return {
            "api_url": os.environ.get("MISEVOLUTION_BASE_URL", BASE_URL),
            "auth_type": "basic",
            "api_ak": os.environ.get("MISEVOLUTION_API_AK", "your access key"),
            "api_sk": os.environ.get("MISEVOLUTION_API_SK", "your secret key"),
        }
    return {
        "api_url": f"{BASE_URL.rstrip('/')}/chat/completions",
        "auth_type": "bearer",
        "api_key": API_KEY,
    }
