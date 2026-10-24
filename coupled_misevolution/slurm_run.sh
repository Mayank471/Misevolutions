#!/bin/bash
# One SLURM job = load the model on the GPU SLURM gives us, run an experiment grid, finish.
# Submit from your personal folder (DS6_Group7, which contains venv_hf/, hf_cache/ and coupled_misevolution/):
#   sbatch coupled_misevolution/slurm_run.sh                              # pressure grid, 10 rounds
#   GRID=pressure ROUNDS=2 TAG=mini sbatch --time=00:30:00 coupled_misevolution/slurm_run.sh   # quick check
#   GRID=factorial ROUNDS=6 SEEDS=0,1,2 sbatch coupled_misevolution/slurm_run.sh
# Other knobs: MODEL (default Qwen/Qwen3-4B-Instruct-2507), PARALLEL (default 16),
#   JCOND = both | clean | lenient (which judge conditions of the grid to run),
#   NJ / NR / NW = number of judge / reviewer / worker probe items per round (default 100 / 100 / 30).
# TAG is added to result file names, so a quick check never blocks the real run.
# Results land in coupled_misevolution/results/, logs in this folder.
#SBATCH --job-name=misevo
#SBATCH --partition=fat
#SBATCH --gres=gpu:1
## cn22 and cn25 split each A30 into four 6 GB slices (gpu:12); the model needs a full 24 GB GPU
#SBATCH --exclude=cn22,cn25
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --time=06:00:00
#SBATCH --output=misevo_%j.log
set -euo pipefail

cd "$SLURM_SUBMIT_DIR"
[ -d venv_hf ] || { echo "no venv_hf/ here - run setup_hf.sh first"; exit 1; }
source venv_hf/bin/activate
export HF_HOME="$PWD/hf_cache" PYTHONUNBUFFERED=1

GRID=${GRID:-pressure}; ROUNDS=${ROUNDS:-10}; SEEDS=${SEEDS:-0}
MODEL=${MODEL:-Qwen/Qwen3-4B-Instruct-2507}; PARALLEL=${PARALLEL:-16}
export MISEVO_HF_BATCH=${MISEVO_HF_BATCH:-16}
# probe sizes per round: judge items, reviewer items, worker questions (50 / 50 of the first two are wrong answers)
NJ=${NJ:-100}; NR=${NR:-100}; NW=${NW:-30}; PE=${PE:-1}; JCOND=${JCOND:-both}   # PE = measure drift every PE rounds

echo "job $SLURM_JOB_ID on $(hostname): grid=$GRID rounds=$ROUNDS seeds=$SEEDS model=$MODEL parallel=$PARALLEL"
nvidia-smi --query-gpu=name,memory.total --format=csv || true
# stop at once if PyTorch cannot see a big enough GPU (the CPU is far too slow, a 6 GB slice too small)
python - <<'PY' || { echo "ERROR: no usable GPU (see above)"; exit 1; }
import sys, torch
if not torch.cuda.is_available():
    print("torch cannot see the GPU"); sys.exit(1)
p = torch.cuda.get_device_properties(0)
print(f"gpu: {p.name}, {p.total_memory / 1e9:.1f} GB")
if p.total_memory < 20e9:
    print("this GPU is too small for the model (a MIG slice?)"); sys.exit(1)
PY

python coupled_misevolution/run_grid.py --grid "$GRID" --rounds "$ROUNDS" --seeds "$SEEDS" \
    --backend hf --models "$MODEL" --parallel "$PARALLEL" --tag "${TAG:-}" \
    --n-judge "$NJ" --n-review "$NR" --n-worker "$NW" --probe-every "$PE" --judge-cond "$JCOND"
echo "done"
