#!/bin/bash
# GPU job: screen several models as judges (clean vs seeded leniency). One process per model.
#   sbatch coupled_misevolution/screen_models.sh
#   MODELS="org/model1 org/model2" sbatch coupled_misevolution/screen_models.sh
#SBATCH --job-name=misevo_screen
#SBATCH --partition=fat
#SBATCH --gres=gpu:1
## cn22 and cn25 split each A30 into four 6 GB slices (gpu:12); the models need a full 24 GB GPU
#SBATCH --exclude=cn22,cn25
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=6G
#SBATCH --time=02:00:00
#SBATCH --output=misevo_screen_%j.log
set -uo pipefail
cd "$SLURM_SUBMIT_DIR"
source venv_hf/bin/activate
export HF_HOME="$PWD/hf_cache" PYTHONUNBUFFERED=1 MISEVO_HF_BATCH=16
MODELS=${MODELS:-"Qwen/Qwen3-4B-Instruct-2507 microsoft/Phi-4-mini-instruct allenai/OLMo-2-1124-7B-Instruct Qwen/Qwen2.5-7B-Instruct"}
nvidia-smi --query-gpu=name,memory.total --format=csv
for m in $MODELS; do
  echo "=== $m"
  python coupled_misevolution/screen_one.py "$m" 100 2>&1 | grep -v -i -E "warn|generation flags" | tail -n 6
done
echo "screening finished"
