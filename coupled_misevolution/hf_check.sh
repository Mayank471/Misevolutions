#!/bin/bash
# Short GPU check (max 30 min): can PyTorch use the GPU, and how fast is the model?
#   sbatch coupled_misevolution/hf_check.sh
#SBATCH --job-name=misevo_hfcheck
#SBATCH --partition=fat
#SBATCH --gres=gpu:1
#SBATCH --exclude=cn22,cn25
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --time=00:30:00
#SBATCH --output=misevo_hfcheck_%j.log
set -uo pipefail
cd "$SLURM_SUBMIT_DIR"
MODEL=${MODEL:-Qwen/Qwen3-4B-Instruct-2507}
source venv_hf/bin/activate
export HF_HOME="$PWD/hf_cache" PYTHONUNBUFFERED=1
echo "== node $(hostname)"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
python coupled_misevolution/hf_check.py "$MODEL"
