#!/usr/bin/env bash
# Formal Paper1 unseen-perturbation eval launcher.
#
# Default protocol:
#   - training seed/checkpoint grid: seed 3072, std_max = 0.00..0.08
#   - perturbation families: gaussian_blur, resize
#   - eval budget: 100 episodes x 3 eval seeds (42, 43, 44)
#   - eval-only first pass: diagnostics disabled by default
#
# Usage:
#   DATA_ROOT=/path/to/world_model/quentinll bash run_paper1_unseen_eval_formal.sh
#
# Useful overrides:
#   TASKS="PushT TwoRoom" bash run_paper1_unseen_eval_formal.sh
#   STD_KEYS="0.0 0.08" bash run_paper1_unseen_eval_formal.sh
#   FAMILIES="gaussian_blur" bash run_paper1_unseen_eval_formal.sh
#   EVAL_GPUS="0 1 2 3" bash run_paper1_unseen_eval_formal.sh
#   DIAGNOSTICS=1 bash run_paper1_unseen_eval_formal.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

DATA_ROOT="${PAPER1_DATA_ROOT:-${DATA_ROOT:-${STABLEWM_HOME:-}}}"
if [ -z "${DATA_ROOT}" ]; then
    echo "Set DATA_ROOT, PAPER1_DATA_ROOT, or STABLEWM_HOME to the world_model/quentinll root." >&2
    exit 1
fi

TRAIN_SEED="${TRAIN_SEED:-3072}"
EPOCH="${EPOCH:-10}"
NUM_EVAL="${NUM_EVAL:-300}"
EVAL_SEEDS="${EVAL_SEEDS:-3}"
EVAL_BASE_SEED="${EVAL_BASE_SEED:-42}"
TASKS="${TASKS:-PushT TwoRoom Reacher Cube}"
STD_KEYS="${STD_KEYS:-}"
FAMILIES="${FAMILIES:-gaussian_blur resize}"
APPLY_TO="${APPLY_TO:-1}"
MANIFEST_OUT="${MANIFEST_OUT:-assets/paper1_data/unseen_perturbation_pilot_seed3072_manifest.json}"
ARTIFACT_OUT="${ARTIFACT_OUT:-assets/paper1_data/unseen_perturbation_pilot_seed3072.json}"
SCHEMA_OUT="${SCHEMA_OUT:-assets/paper1_data/unseen_perturbation_pilot_seed3072.schema.json}"
CANONICAL="${CANONICAL:-assets/paper1_data/canonical_evals_20260517.json}"
DIAGNOSTICS="${DIAGNOSTICS:-0}"
KEEP_GOING="${KEEP_GOING:-1}"
DRY_RUN="${DRY_RUN:-0}"
ONLY_MISSING="${ONLY_MISSING:-1}"

args=(
    --root "${DATA_ROOT}"
    --canonical "${CANONICAL}"
    --manifest-out "${MANIFEST_OUT}"
    --tasks ${TASKS}
)

if [ -n "${STD_KEYS}" ]; then
    args+=(--std-keys ${STD_KEYS})
fi
args+=(--families ${FAMILIES})
args+=(
    --train-seed "${TRAIN_SEED}"
    --epoch "${EPOCH}"
    --num-eval "${NUM_EVAL}"
    --eval-seeds "${EVAL_SEEDS}"
    --eval-base-seed "${EVAL_BASE_SEED}"
    --apply-to "${APPLY_TO}"
)

if [ -n "${EVAL_GPUS:-}" ]; then
    args+=(--eval-gpus "${EVAL_GPUS}")
fi
if [ "${DIAGNOSTICS}" = "1" ]; then
    args+=(--diagnostics)
fi
if [ "${KEEP_GOING}" = "1" ]; then
    args+=(--keep-going)
fi
if [ "${ONLY_MISSING}" = "1" ]; then
    args+=(--only-missing)
fi
if [ "${DRY_RUN}" = "1" ]; then
    args+=(--dry-run)
fi

printf '[paper1-unseen] DATA_ROOT=%s
' "${DATA_ROOT}"
printf '[paper1-unseen] tasks=%s
' "${TASKS}"
printf '[paper1-unseen] families=%s
' "${FAMILIES}"
printf '[paper1-unseen] eval=%s episodes x %s seeds from %s
'     "$(( NUM_EVAL / EVAL_SEEDS ))" "${EVAL_SEEDS}" "${EVAL_BASE_SEED}"
printf '[paper1-unseen] diagnostics=%s dry_run=%s only_missing=%s
'     "${DIAGNOSTICS}" "${DRY_RUN}" "${ONLY_MISSING}"

python -m tools.paper1_unseen_eval_grid "${args[@]}"

if [ "${DRY_RUN}" = "1" ]; then
    exit 0
fi

artifact_args=(
    --manifest "${MANIFEST_OUT}"
    --out "${ARTIFACT_OUT}"
    --schema-out "${SCHEMA_OUT}"
    --root "${DATA_ROOT}"
    --allow-missing
)

python -m tools.build_paper1_unseen_eval_artifact "${artifact_args[@]}"
