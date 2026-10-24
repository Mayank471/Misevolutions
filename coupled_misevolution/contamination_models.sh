#!/bin/bash
# GPU job: who contaminates whom? Real notes from each role used as context for each role.
#   sbatch coupled_misevolution/contamination_models.sh
#   MODELS="org/model1 org/model2" sbatch coupled_misevolution/contamination_models.sh
#SBATCH --job-name=misevo_contam
#SBATCH --partition=fat
#SBATCH --gres=gpu:1
## cn22 and cn25 split each A30 into four 6 GB slices (gpu:12); the models need a full 24 GB GPU
#SBATCH --exclude=cn22,cn25
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=6G
#SBATCH --time=01:30:00
#SBATCH --output=misevo_contam_%j.log
set -uo pipefail
cd "$SLURM_SUBMIT_DIR"
source venv_hf/bin/activate
export HF_HOME="$PWD/hf_cache" PYTHONUNBUFFERED=1 MISEVO_HF_BATCH=8
MODELS=${MODELS:-"allenai/OLMo-2-1124-7B-Instruct Qwen/Qwen3-4B-Instruct-2507 microsoft/Phi-4-mini-instruct"}
nvidia-smi --query-gpu=name,memory.total --format=csv
for m in $MODELS; do
  echo "=== $m"
  python coupled_misevolution/contamination.py "$m" 100 2>&1 | grep -v -i -E "warn|generation flags" | tail -n 14
done
echo "contamination matrix finished"
