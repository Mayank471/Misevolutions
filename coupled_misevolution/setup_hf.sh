#!/bin/bash
# One-time setup, run as a SLURM job (CPU queue) from your personal folder (DS6_Group7):
#   sbatch coupled_misevolution/setup_hf.sh
# Creates ./venv_hf with PyTorch built for CUDA 12.1 (works with the cluster's NVIDIA driver 535)
# and downloads the model into ./hf_cache.
#SBATCH --job-name=misevo_sethf
#SBATCH --partition=small
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4G
#SBATCH --time=01:30:00
#SBATCH --output=misevo_sethf_%j.log
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
MODEL=${MODEL:-Qwen/Qwen3-4B-Instruct-2507}
echo "setting up in $PWD on $(hostname); model $MODEL"

python3 -m venv venv_hf
source venv_hf/bin/activate
pip install --quiet --upgrade pip
pip install --quiet torch==2.5.1 --index-url https://download.pytorch.org/whl/cu121
pip install --quiet "transformers==4.51.3" "numpy<2" requests matplotlib
python -c "import torch, transformers; print('torch', torch.__version__, '| transformers', transformers.__version__)"

export HF_HOME="$PWD/hf_cache"
python - <<PY
from huggingface_hub import snapshot_download
print("model files at", snapshot_download("$MODEL"))
PY
du -sh venv_hf hf_cache
echo "setup finished OK"
