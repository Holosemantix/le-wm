#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Required for the user's Lance-format stable-worldmodel training layout.
STABLEWM_HOME="${STABLEWM_HOME:-/opt/workspace/explorer-env/dataset/ag_data/outputs/stablewm}"
dataset_root="${dataset_root:-/opt/workspace/explorer-env/dataset/ag_data/data/world_model/lance-format/LeWorldModel/data}"
output_model_name="${output_model_name:-lewm_mt3_lance}"

# Defaults match the quick smoke eval: 50 episodes, clean pixels, seed 42.
tasks="${tasks:-tworoom pusht reacher}"
num_eval="${num_eval:-50}"
seed="${seed:-42}"
eval_epoch="${eval_epoch:-latest}"
eval_gpus="${eval_gpus:-0}"

eval_corruption_type="${eval_corruption_type:-gaussian_noise}"
eval_corruption_std="${eval_corruption_std:-0.0}"
eval_corruption_kernel_size="${eval_corruption_kernel_size:-1}"
eval_corruption_factor="${eval_corruption_factor:-1.0}"
eval_corruption_apply_to="${eval_corruption_apply_to:-pixels}"
save_video="${save_video:-0}"
eval_overrides="${eval_overrides:-}"

ckpt_dir="${STABLEWM_HOME%/}/checkpoints/${output_model_name}"
config_path="${ckpt_dir}/config.yaml"
results_dir="${ckpt_dir}/eval_results"

if [ ! -d "${ckpt_dir}" ]; then
    echo "[eval] checkpoint directory not found: ${ckpt_dir}" >&2
    exit 1
fi
if [ ! -f "${config_path}" ]; then
    echo "[eval] config not found: ${config_path}" >&2
    exit 1
fi
if [ ! -d "${dataset_root}" ]; then
    echo "[eval] dataset_root not found: ${dataset_root}" >&2
    exit 1
fi

if [ "${eval_epoch}" = "latest" ]; then
    eval_epoch="$(
        find "${ckpt_dir}" -maxdepth 1 -type f -name 'weights_epoch_*.pt' \
            | sed -E 's/.*weights_epoch_([0-9]+)\.pt/\1/' \
            | sort -n \
            | tail -n 1
    )"
    if [ -z "${eval_epoch}" ]; then
        echo "[eval] no weights_epoch_*.pt found under ${ckpt_dir}" >&2
        exit 1
    fi
fi

weights_path="${ckpt_dir}/weights_epoch_${eval_epoch}.pt"
if [ ! -f "${weights_path}" ]; then
    echo "[eval] weights not found: ${weights_path}" >&2
    exit 1
fi

mkdir -p "${results_dir}"

read -ra task_array <<< "${tasks}"
read -ra gpu_array <<< "${eval_gpus}"
read -ra extra_overrides <<< "${eval_overrides}"

if [ "${#gpu_array[@]}" -eq 0 ]; then
    gpu_array=(0)
fi

echo "[eval] STABLEWM_HOME=${STABLEWM_HOME}"
echo "[eval] dataset_root=${dataset_root}"
echo "[eval] checkpoint=${weights_path}"
echo "[eval] tasks=${task_array[*]}"
echo "[eval] num_eval=${num_eval} seed=${seed}"

idx=0
for task in "${task_array[@]}"; do
    gpu="${gpu_array[$((idx % ${#gpu_array[@]}))]}"
    label="${task}_epoch${eval_epoch}_num${num_eval}_seed${seed}"
    if [ "${eval_corruption_type}" != "gaussian_noise" ] || [ "${eval_corruption_std}" != "0.0" ]; then
        label="${label}_${eval_corruption_type}_std${eval_corruption_std}"
    fi

    output_path="${results_dir}/${label}_metrics.txt"
    log_path="${results_dir}/${label}.log"

    video_args=()
    if [ "${save_video}" = "1" ]; then
        video_args=(--video-dir "${results_dir}/${label}_videos")
    fi

    echo "[eval] start task=${task} gpu=${gpu} output=${output_path}"
    CUDA_VISIBLE_DEVICES="${gpu}" \
    STABLEWM_HOME="${STABLEWM_HOME}" \
    PYTHONPATH="${SCRIPT_DIR}${PYTHONPATH:+:${PYTHONPATH}}" \
    python tools/eval_lance_policy.py \
        --task "${task}" \
        --dataset-root "${dataset_root}" \
        --config-path "${config_path}" \
        --weights-path "${weights_path}" \
        --policy-name "${output_model_name}/weights_epoch_${eval_epoch}" \
        --output-path "${output_path}" \
        --num-eval "${num_eval}" \
        --seed "${seed}" \
        --corruption-type "${eval_corruption_type}" \
        --corruption-std "${eval_corruption_std}" \
        --corruption-kernel-size "${eval_corruption_kernel_size}" \
        --corruption-factor "${eval_corruption_factor}" \
        --corruption-apply-to "${eval_corruption_apply_to}" \
        "${video_args[@]}" \
        "${extra_overrides[@]}" \
        > "${log_path}" 2>&1
    echo "[eval] done  task=${task} log=${log_path}"
    tail -n 5 "${log_path}" || true
    idx=$((idx + 1))
done

echo "[eval] finished; results are under ${results_dir}"
