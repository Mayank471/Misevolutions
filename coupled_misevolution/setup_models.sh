#!/bin/bash
# Download extra models for the model-family screening (CPU queue, no GPU needed):
#   sbatch coupled_misevolution/setup_models.sh
#   MODELS="org/model1 org/model2" sbatch coupled_misevolution/setup_models.sh
# Only models that need no special access (no gated licence click-through).
#SBATCH --job-name=misevo_setmod
#SBATCH --partition=small
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4G
#SBATCH --time=02:00:00
#SBATCH --output=misevo_setmod_%j.log
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source venv_hf/bin/activate
export HF_HOME="$PWD/hf_cache"
export MODELS=${MODELS:-"microsoft/Phi-4-mini-instruct allenai/OLMo-2-1124-7B-Instruct Qwen/Qwen2.5-7B-Instruct"}
python - <<'PY'
import os
from huggingface_hub import snapshot_download
for m in os.environ["MODELS"].split():
    print("downloading", m, flush=True)
    p = snapshot_download(m, ignore_patterns=["*.bin", "*.pth", "*.pt", "*.gguf", "*.onnx", "original/*"])
    print("  ->", p, flush=True)
PY
du -sh hf_cache
echo "models ready"
