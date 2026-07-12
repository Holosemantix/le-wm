# Paper 1 最终完整整改、外推验证与分阶段投稿执行计划

> **目标仓库**：`qun-team/wm_exp`  
> **目标分支**：`ag/dev`  
> **目标文件**：`paper1/docs/PAPER1_OFF_AXIS_THEORY_SMPR_NOVELTY_REMEDIATION_PLAN_20260710.md`  
> **计划日期**：2026-07-10  
> **执行对象**：Codex  
> **文档性质**：唯一、完整、可直接执行的 Paper 1 后续工作说明。除非本文件显式引用，其他历史整改文档只作背景，不作为执行依据。

---

## 0. 执行总原则

1. **不伪造结果。** 未实际完成的训练、评估、诊断、统计和相关工作比较不得写成论文结果。
2. **不手工修改 canonical 数值。** 所有新数值必须由脚本生成，并带 schema、provenance、source hash 和完整 missing/error 状态。
3. **不覆盖旧 canonical artifact。** 新指标、新协议和重算结果统一使用 `_v2`、新 schema version 或独立目录。
4. **先冻结协议，再看外部结果。** LeWM seed 3072 只用于 protocol development；held-out LeWM seeds、PLDM、blur/resize、target-view 和后续 PLDM 新训练种子不得参与阈值选择。
5. **不把 evaluation seeds 当 training seeds。** PLDM v1 的三个 evaluation seeds只表示固定 checkpoint 的条件评估波动。
6. **不因结果不好而改 q、H、normalization、pair rule、severity 或行为标签。** 必要的 correctness bug 修复必须记录，并对所有 split 全量重跑。
7. **负结果和不一致结果必须保留。** false early、false late、diagnostic/behavior discordance、任务失败和跨模型失败均不得静默过滤。
8. **闭环行为仍是权威。** ATR、SMPR、JVP、fixed-pool certificate 和其他诊断用于解释、筛查或校准，不能替代实际闭环评估。
9. **分层统计。** 独立 training seed、evaluation seed、checkpoint、anchor 和 candidate pool 的统计单位必须分开，不得把所有 sample 当成 iid。
10. **先做最小可验证实验。** 每个新 checkpoint-level audit 先运行 `2 tasks × 2 checkpoints × 16 anchors × 2 noise draws` smoke benchmark，再扩展全量。

---

# 1. 最终论文定位与允许的主张

## 1.1 论文的核心对象

本文研究的不是一般意义上的 “action-conditioned consistency”，而是更具体的：

> **paired same-state visual intervention under a shared action sequence**：clean 与 corrupted histories 描述相同底层状态，在完全相同的动作干预下比较其多步预测 rollout；同时要求 task/planner-distinct 状态或动作结果仍保持可分。

主诊断由两部分组成：

- **ATR / horizon radius**：同状态 clean/noisy 预测 rollout disagreement 的高分位尾部；
- **SMPR / guard**：任务或规划相关不同状态的预测分离是否仍处于 nuisance tube 之外。

planner-side 证据由 fixed-pool candidate-cost drift、candidate margin、certificate coverage 和 observed top-1 flip 提供。

## 1.2 完成 ArXiv v1 后可主张

在完成本文档标记为 **V1 必须** 的项目后，可以写：

> A paired-rollout radius/guard protocol developed on one LeWM Gaussian calibration split is evaluated without retuning on held-out LeWM training seeds, a second latent-world-model family, non-Gaussian stressors at fixed Gaussian training strength, and at least one failed alternative repair mechanism.

必须同时写清：

- PLDM v1 只有一个独立 training run；
- blur/resize 是 bounded cross-stressor audit，不是 universal corruption transfer；
- target-view 等是 falsification controls，不是成功 repair；
- ATR/SMPR 不是闭环保证或 universal checkpoint selector。

## 1.3 顶会 v2 目标主张

在 ArXiv v1 公开冻结协议后，完成两个额外 PLDM training seeds 的 prospective replication，以及本文档标记为 **V2 必须** 的理论、baseline、SMPR 和多 severity 外推后，可以写：

> The public-v1 frozen protocol prospectively transfers across independently trained LeWM and PLDM checkpoints and distinguishes mixed non-Gaussian outcomes at fixed training strength, while simple encoder-only, one-step, and action-shuffled alternatives quantify which parts of the gain require multi-step action-conditioned rollout and a discriminability guard.

## 1.4 始终不能主张

- universal robustness predictor；
- 任意 corruption family 的 transfer theorem；
- adaptive CEM、重复 replanning 或闭环 trajectory 的形式保证；
- SMPR 已证明 oracle-level semantic sufficiency，除非完整 oracle/value guard 实验通过；
- “action-conditioned consistency” 一般概念本身为本文独占创新；
- PLDM v1 的三个 evaluation seeds 等价于三个独立训练种子；
- Gaussian training `std_max` 是跨模型、跨扰动或跨修复的通用风险指标。

---

# 2. 当前可复用证据与数据资产

Codex 开工前必须核对下列输入存在、可解析、状态与 `DATA_MANIFEST.md` 一致。

## 2.1 LeWM 主证据

```text
assets/paper1_data/three_seed_gaussian_sweep_summary_20260706.json
assets/paper1_data/training_seed_gaussian_lockbox.json
assets/paper1_data/training_seed_eval_manifests/lewm_seed3072_evals.json
assets/paper1_data/training_seed_eval_manifests/lewm_seed3073_evals.json
assets/paper1_data/training_seed_eval_manifests/lewm_seed3074_evals.json
assets/paper1_data/acpc_phase0_lewm_three_seed.json
assets/paper1_data/semantic_task_grounded_margin_lewm_three_seed.json
assets/paper1_data/margin_flip_curve_lewm_three_seed.json
```

规模：

```text
3 independent training seeds
× 4 tasks
× 9 Gaussian training configurations
× 3 evaluation seeds
× 100 trajectories per evaluation seed
```

## 2.2 PLDM 跨模型资产

```text
assets/paper1_data/canonical_evals_pldm_20260522.json
assets/paper1_data/canonical_diagnostics_pldm_20260522.json
assets/paper1_data/canonical_full_diagnostics_pldm_20260523.json
assets/paper1_data/acpc_basin_diagnostics_pldm.json
assets/paper1_data/acpc_phase0_clean_goal_seed9101.json
```

当前规模：

```text
1 independent PLDM training checkpoint family
× 4 tasks
× 9 Gaussian training configurations
× 3 evaluation seeds
```

这足够用于 v1 的 **model-family transfer**，不足以估计 PLDM training-run variance。

## 2.3 非 Gaussian stressor 资产

```text
assets/paper1_data/unseen_origin_vs_std008_strongest_s3072.json
assets/paper1_data/unseen_origin_vs_std008_strongest_s3073.json
assets/paper1_data/unseen_origin_vs_std008_strongest_s3074.json
assets/paper1_data/unseen_phase0_acpc_fullstress.json
assets/paper1_data/unseen_atr_smpr_summary_20260707.json
assets/paper1_data/prospective_validation_summary.json
assets/paper1_data/canonical_blur_baselines_20260523.json
```

现有 LeWM strongest-only 外部矩阵应覆盖：

```text
4 tasks × 3 training seeds × 2 checkpoints(base/std0.08) × 2 stressor families(blur/resize)
= 48 checkpoint-stressor rows
```

论文统计重点可投影为：

- 12 个 `rho=0.08` fixed-training-strength endpoint rows；
- 24 个 base→endpoint paired task-family-seed comparisons。

## 2.4 失败修复和 planner-side 资产

```text
assets/paper1_data/target_view_closed_loop_summary.json
assets/paper1_data/cem_trace_audit_20260704.json
assets/paper1_data/robust_cem_pilot_20260704.json
assets/paper1_data/robust_cem_eval100x3_iteration_summary_20260705.json
paper1/results/sample_level_certificate_full_sweep_audit.json
paper1/results/jvp_hutchinson_sensitivity_audit.json
paper1/results/gaussian_sensitivity_audit.json
```

若某资产路径已变化，Codex 必须从 manifest 或当前生成脚本解析，不能猜路径或手工复制旧值。

---

# 3. 研究假设与验证轴

## 3.1 核心假设

### H1：paired rollout radius

同状态 visual perturbation 在共享动作序列下的 horizon-level predictive radius，应比 raw encoder shift 更接近 planner-facing instability。

### H2：selective guard

低 radius 只有在 task/planner-distinct separations 仍处于 nuisance tube 之外时才可解释为 robustness，而不是 collapse。

### H3：外推性

在 LeWM Gaussian calibration split 上冻结的 checkpoint-level protocol，应在：

- held-out LeWM training seeds；
- PLDM model family；
- blur/resize stressor families；
- 至少一个 failed alternative repair；

上保持有解释力，而不是只沿训练 `std_max` 单调变化。

### H4：radius–cost–decision 链

horizon radius 与 candidate-cost drift 存在可审计的局部/经验联系，而 candidate-wise cost slack 能给出非空的 fixed-pool certificate coverage。

## 3.2 验证矩阵

| Split | 模型 | 独立训练 | 训练机制 | Evaluation stressor | 角色 | 版本 |
|---|---|---:|---|---|---|---|
| CAL | LeWM seed 3072 | 1 | full-sequence Gaussian | Gaussian | 仅开发 metric/gate | V1 |
| E1 | LeWM seeds 3073/3074 | 2 | full-sequence Gaussian | Gaussian | training-seed confirmation | V1 |
| E2 | PLDM canonical seed | 1 | full-sequence Gaussian | Gaussian | model-family transfer | V1 |
| E3-L | LeWM seeds 3072/73/74 | 3 | full-sequence Gaussian | blur/resize | fixed-`rho` stressor transfer | V1/V2 |
| E3-P | PLDM canonical seed | 1 | full-sequence Gaussian | blur/resize | model + stressor intersection | V1 |
| E4 | LeWM target-view/hetero/other | existing | alternative/failed repair | Gaussian | falsification | V1 |
| E5 | PLDM two new seeds | 2 | frozen PLDM protocol | Gaussian + blur/resize | prospective cross-model replication | V2 |
| E6 | optional DINO-WM/Delta-JEPA | new/available | different successful repair | Gaussian/other | positive cross-repair transfer | V2/P1 |

---

# 4. 唯一冻结协议与 public-v1 lockbox

## 4.1 新建 protocol 文件

创建：

```text
paper1/config/frozen_diagnostic_protocol_v1.json
paper1/config/frozen_diagnostic_protocol_v1.schema.json
paper1/scripts/freeze_diagnostic_protocol.py
```

只允许使用：

```text
model_family = LeWM
training_seed = 3072
training_stressor = Gaussian input noise
rho_grid = 0.00 ... 0.08
tasks = TwoRoom, PushT, Reacher, Cube
```

建议 schema 至少包含：

```json
{
  "schema_version": "paper1-frozen-diagnostic-protocol-1.0",
  "calibration_source": "LeWM seed3072 Gaussian full sweep",
  "radius_metric": "horizon_weighted_stacked_l2_v2",
  "rollout_horizon": 8,
  "horizon_weights": "uniform_1_over_H",
  "atr_quantile": 0.90,
  "normalization": "per-anchor clean transition scale",
  "noise_draw_aggregation": "anchor conditional then checkpoint quantile",
  "smpr_pair_rule": "task_grounded_near_boundary_v2",
  "smpr_local_quantile": 0.35,
  "smpr_margin_delta_normalized": 0.10,
  "tau_atr": null,
  "tau_smpr": null,
  "joint_rule": "atr_and_smpr",
  "gaussian_behavior_label": {
    "recovery_fraction": 0.80,
    "clean_tolerance_pp": 5.0
  },
  "external_behavior_label": {
    "positive_delta_pp": 5.0,
    "neutral_band_pp": 5.0,
    "max_clean_drop_pp": 5.0
  },
  "calibration_commit": "...",
  "source_hashes": {},
  "frozen_at_utc": "..."
}
```

阈值必须由 builder 写入，不得人工拷贝。

## 4.2 冻结规则

冻结后：

- LeWM seeds 3073/3074 不参与 threshold search；
- PLDM 所有结果不参与 threshold search；
- blur/resize 所有结果不参与 threshold search；
- target-view/heteroscedastic/robust-CEM 不参与 threshold search；
- 后续 PLDM 新 training seeds 不参与任何 metric、threshold、severity 或 label 选择；
- external script 必须只读 protocol，不得包含自动 grid search 代码路径。

新增单元测试：

```text
tests/test_paper1_frozen_gate_no_recalibration.py
```

测试必须验证：

- external input 改变时 protocol hash 不变；
- external script 不写 protocol；
- external result 中记录 protocol SHA-256；
- threshold-search 函数在 external mode 下不可调用。

## 4.3 ArXiv v1 公开冻结

V1 release 前：

1. 完成 protocol JSON；
2. 记录 Git commit SHA、artifact hashes、目标 paper PDF hash；
3. 创建 release tag，建议：

```text
paper1-arxiv-v1-lockbox
```

4. 在 `paper1/arxiv_release_notes.tex` 和本文件 execution log 中记录冻结时间；
5. ArXiv v1 后启动 PLDM 新训练种子。

若 v1 后发现 correctness bug：

- 不得直接覆盖 `protocol_v1`；
- 创建 `protocol_v1_1`；
- 写明 bug、影响范围和发现时间；
- 对 CAL、E1–E4 全部重跑；
- 不得利用新 PLDM seed 结果选择修复方向。

---

# 5. 分版本实验计划

## 5.1 ArXiv v1：不等待 PLDM 另外两个 training seeds

### V1 必须完成

1. LeWM 三训练种子 Gaussian 主结果保持完整；
2. PLDM 一个完整 training seed 的四任务九点 Gaussian sweep，三 evaluation seeds；
3. LeWM held-out seeds 的 strict frozen evaluation；
4. PLDM 的 horizon-v2 ATR、SMPR、encoder/H1/action-shuffled baseline 与 frozen gate；
5. LeWM 完整 strongest-only blur/resize external audit；
6. PLDM canonical seed 的 base 与 `std_max=0.08` strongest blur/resize eval + stressor-specific diagnostics；
7. target-view 或等价 failed-repair falsification；
8. canonical metric/JVP/κ correctness 修复；
9. fixed-pool candidate-wise certificate coverage；
10. SMPR positive-margin sensitivity、collapse/action/label controls；
11. 2026 并发文献和 novelty positioning 更新；
12. 所有 release gates 通过。

### V1 中 PLDM 的统计措辞

固定写法：

> PLDM provides a four-task full-sweep external model-family validation from one independently trained checkpoint family. Its three evaluation seeds quantify conditional evaluation variability, not PLDM training-run variability.

PLDM v1 不得：

- 报 training-seed mean/std；
- 将 eval seed 当 independent replication；
- 声称 cross-model training stability；
- 用 PLDM label 重调 gate。

### V1 的 blur/resize 最低矩阵

对 LeWM 与 PLDM canonical seed，至少完成：

```text
4 tasks
× 2 checkpoints (base, Gaussian std0.08 endpoint)
× 2 stressor families (blur, resize)
× 1 strongest severity
× 3 evaluation seeds
```

每个条件同时生成：

```text
closed_loop_score
clean_score
retention
encoder_q90
h1_predictive_q90
action_shuffled_h8_q90
action_zeroed_h8_q90（任务允许时）
atr_h8_q90
smpr
joint_gate_pass
fixed_pool_flip / cost drift（接口允许时）
```

V1 可以将 strongest-only 称为：

```text
boundary stressor endpoint audit
```

不能称为完整 corruption benchmark。

## 5.2 V1 后立即启动 prospective PLDM v2 训练

### 5.2.1 训练种子预注册

Codex 不得猜当前 PLDM training seed。必须：

1. 从 canonical manifest/checkpoint metadata 提取当前 seed；
2. 选择两个尚未使用的 training seeds；
3. 在训练前写入：

```text
paper1/config/pldm_prospective_v2_training_manifest.json
```

至少记录：

```text
current_seed
new_seed_a
new_seed_b
tasks
configs
checkpoint_epoch
training command
code commit
container/environment hash
protocol_v1 hash
launch timestamp
```

### 5.2.2 三种训练规模

#### 配置 A：最强版本

```text
2 new PLDM training seeds
× 4 tasks
× 9 Gaussian configs
```

每个 checkpoint 做 Gaussian 3-eval-seed evaluation；base/std0.08 再做 blur/resize multi-severity。

#### 配置 B：推荐性价比版本

每个新 seed、每任务训练：

```text
base
fixed intermediate std（全任务统一、训练前冻结）
std0.08 endpoint
```

说明：

- intermediate 不能从 canonical PLDM seed 的 per-task point-best 中选择；
- 推荐从现有统一 grid 选一个全任务固定值，例如 `0.04`，但最终值必须在 launch manifest 中冻结；
- canonical PLDM seed 提供 full-sweep onset；三个 seeds 共同提供 endpoint/intermediate replication。

#### 配置 C：最低版本

```text
base + std0.08 endpoint
```

用于验证 cross-model/cross-stressor 方向是否跨 training seed 保持，但不支持 PLDM full-sweep onset stability。

### 5.2.3 最终选择

- ArXiv v1：canonical PLDM one-seed full sweep 即可；
- 顶会 v2 最低线：达到配置 B；
- 资源充足：升级配置 A；
- 配置 C 只作为算力受限降级方案，论文必须披露。

## 5.3 顶会 v2：多 severity blur/resize

V2 不应只依赖 strongest-only 单点。对 LeWM 与 PLDM 至少冻结三档 severity：

```text
mild / medium / strong
```

选择规则：

1. 先从现有 corruption implementation 枚举实际支持的 severity；
2. 只根据物理/视觉强度和已有配置选择，不看行为结果；
3. 写入 `frozen_diagnostic_protocol_v1.json` 的 external severity 子字段或独立 immutable manifest；
4. 若 blur 支持 `{3,7,11,15}`，优先使用三个非零、单调且区分度足够的 levels；
5. 若 resize 支持 `{0.75,0.50,0.25}`，优先使用全部三档；
6. 若实际支持集合不同，按实现能力记录，不得静默替换。

V2 目标矩阵：

```text
model family ∈ {LeWM, PLDM}
training seed: LeWM 3；PLDM 3（配置 B/A）
checkpoint ∈ {base, fixed intermediate（PLDM可选）, std0.08}
stressor ∈ {blur, resize}
severity ∈ {mild, medium, strong}
evaluation seeds = 3
```

主要问题：

- diagnostic 是否随 severity 有序变化；
- behavior 与 diagnostic 的转折是否相近；
- fixed-`rho` 条件下能否区分 positive/neutral/negative transfer；
- model family 是否改变 radius/guard 与 behavior 的对应关系。

---

# 6. Off-axis external validation 的具体实现

## 6.1 LeWM held-out training seeds

当前 `heldout_diagnostic_validation.py` 的 leave-one split 可保留为 retrospective sensitivity，但主 external claim 必须来自 strict protocol：

```text
CAL = LeWM seed3072
TEST = LeWM seeds3073/3074
```

报告：

- row-level AUPRC；
- balanced accuracy；
- precision/recall；
- per-task onset error；
- false early / false late；
- raw confusion table；
- calibration split 与 test split 完全分离。

若 strict frozen gate 明显差于现有 cross-validation，正文必须使用 strict 结果；原表降为 sensitivity appendix。

## 6.2 PLDM Gaussian model-family transfer

扩展或重构诊断工具：

- `tools/paper1_semantic_margin.py` 支持 `--method LeWM|PLDM`；
- 支持显式 `--evals`/`--manifest`；
- 不硬编码 `lewm_seed*.json`；
- 使用 canonical horizon-v2 radius；
- 使用同一 embedding/cost space policy 和 normalization contract；
- frozen gate 直接应用。

输出：

```text
paper1/results/external_validation/pldm_frozen_rows_v1.csv
paper1/results/external_validation/pldm_frozen_summary_v1.json
paper1/tables/table_pldm_frozen_validation.tex
assets/paper1_figs/fig_pldm_frozen_validation.png
```

V1 成功标准：

1. 不重新调 threshold；
2. 至少 3/4 tasks 的 onset error 在两格以内，或 row-level calibration 仍有一致方向；
3. joint diagnostic 相比 encoder/H1/action-shuffled checkpoint-level baseline 有增量；
4. 全部失败任务公开；
5. 只称 one-training-family model transfer。

V2 成功标准：

- protocol_v1 对两个新 PLDM training seeds 无重调应用；
- 三 training seeds 的 endpoint/intermediate direction 基本一致；
- 若配置 A 完成，报告 PLDM training-seed mean/std 和 per-seed onset；
- 若配置 B 完成，不声称三 seed full-sweep onset，只报告 canonical full sweep + prospective point replication。

## 6.3 fixed-`rho` cross-stressor discrimination

这是排除 `std_max` confound 的主实验。

在 `rho=0.08` endpoint slice 中：

- training strength 为常数；
- 任务、seed、模型、stressor 和 severity 产生 mixed behavior；
- `std_max` 无区分能力；
- checkpoint-level diagnostics 仍可计算。

V1 对 LeWM 必须使用：

- 全部 12 个 `rho=0.08` task-family-seed endpoint rows；
- 全部 24 个 base→endpoint paired comparisons。

PLDM v1 追加同构 canonical-seed rows。

创建：

```text
paper1/scripts/build_cross_stressor_external_validation.py
paper1/results/external_validation/cross_stressor_fixed_rho_rows.csv
paper1/results/external_validation/cross_stressor_fixed_rho_summary.json
paper1/results/external_validation/cross_stressor_all_pairs.csv
assets/paper1_figs/fig_cross_stressor_fixed_rho.png
```

每个 endpoint row 至少包含：

```text
model_family
training_seed_or_family_id
task
stressor_family
stressor_severity
rho
clean_score
stressed_score
retention
behavior_class
encoder_q90
h1_q90
action_shuffled_h8_q90
action_zeroed_h8_q90
atr_h8_q90
smpr
joint_score
joint_gate_pass
protocol_hash
```

每个 paired row 至少包含：

```text
delta_behavior
delta_retention
delta_encoder_q90
delta_h1_q90
delta_action_shuffled_h8
delta_atr
delta_smpr
delta_joint_score
```

### 预注册行为标签

在读取 diagnostic result 前固定：

```text
positive transfer:
  stressed-score delta >= +5 pp
  and clean-score drop <= 5 pp

neutral:
  stressed-score delta in (-5, +5) pp
  and clean-score drop <= 5 pp

negative:
  stressed-score delta <= -5 pp
  or clean-score drop > 5 pp
```

同时报告连续值；分类只用于 compact summary。

报告：

- balanced accuracy/AUPRC；
- continuous Spearman/Pearson 作为小样本描述；
- signed agreement；
- task/model/stressor/seed 分层表；
- discordant rows；
- 不重新搜索 stressor-specific thresholds。

## 6.4 failed-repair falsification

优先 target-view：

```text
assets/paper1_data/target_view_closed_loop_summary.json
```

新建：

```text
tools/paper1_target_view_diagnostic_manifest.py
paper1/scripts/target_view_frozen_gate_validation.py
```

操作：

1. 构建 canonical-shaped manifest；
2. 对 matched task/std checkpoints 计算 horizon-v2 ATR、SMPR 和 baselines；
3. frozen gate 不重调；
4. 报告 false-pass、false-negative、matched-std pair ordering；
5. 对 behavior collapse but diagnostic pass 的 rows 单独讨论。

解释规则：

- target-view 是 failed mechanism falsification，不是成功 repair；
- 若 ATR+SMPR 能识别失败，支持 checkpoint behavior 而非 noise metadata；
- 若 ATR+SMPR 也误判，必须作为 diagnostic boundary；
- 若只有 fixed-pool cost audit 能识别，收缩 lightweight diagnostic 的 planner-facing claim。

可追加：

- heteroscedastic objective failure；
- robust-CEM negative/no-go results；
- 不得将 decision-time planner 和 representation repair 混为一类。

## 6.5 正向不同 repair（V2/P1）

若代码/权重可用，优先级：

1. Delta-JEPA checkpoint/model；
2. DINO-WM no-prop：PushT/TwoRoom，base + `{0.02,0.05,0.08}`；
3. ATM/AITS-style model；
4. ACID 只作 planner-side external mechanism。

在代码/权重未确认前，只做 feasibility audit，不写成已完成实验。

---

# 7. `std_max` 的最终角色

## 7.1 不进入 external leaderboard

`std_max` 是 Gaussian augmentation protocol metadata，不是通用 checkpoint diagnostic。它：

- 在其他 repair 上可能没有定义；
- 在 LeWM/PLDM 中未必同尺度；
- 与 blur kernel、resize factor 没有共同 severity 语义；
- 依赖训练日志，违反 post-hoc checkpoint-only 设定。

因此：

- 不进入 cross-model leaderboard；
- 不进入 cross-stressor leaderboard；
- 不进入 cross-repair leaderboard；
- 不要求 ATR/SMPR 在 external validation 中击败它。

## 7.2 只保留 Gaussian-only privileged confound audit

新增：

```text
paper1/scripts/gaussian_rho_confound_audit.py
paper1/results/diagnostic_baselines/gaussian_rho_confound_rows.csv
paper1/results/diagnostic_baselines/gaussian_rho_confound_summary.json
```

仅在 matched-Gaussian rows 比较：

```text
rho_only
rho + encoder_q90
rho + h1_q90
rho + atr_h8
rho + atr_h8 + smpr
```

优先指标：

- held-out log loss；
- AUPRC；
- balanced accuracy；
- calibration deviance；
- 同一 rho 下的 residual ordering；
- onset MAE 只作次要结果。

解释：

- `rho-only` 匹配 onset 不构成论文中心失败；
- 只要求将 in-domain onset 降级为 internal consistency；
- 若 joint diagnostic 在 rho 条件下仍有增量，可补充 “beyond augmentation strength”；
- 若内部无增量但 PLDM/fixed-rho external 成立，仍保留外部 diagnostic claim；
- 内部和外部均失败才退回 mechanism-localization。

---

# 8. 必须完成的 checkpoint-level baseline benchmark

## 8.1 Baseline 集合

| ID | Baseline | 检验的问题 | External 可用 |
|---|---|---|---:|
| B1 | clean closed-loop score | clean quality 是否已足够 | 有限，非 training-free |
| B2 | normalized encoder q90 | raw encoder invariance 是否足够 | 是 |
| B3 | one-step predictive q90 | H=1 是否足够 | 是 |
| B4a | action-shuffled H8 q90 | 正确动作条件是否有增量 | 是 |
| B4b | action-zeroed H8 q90 | 一般平滑度是否冒充 action consistency | 任务允许时 |
| B4c | time-shuffled action H8 | 动作时序是否重要 | 是 |
| B5 | correct-action ATR H8 | 多步 shared-action radius | 是 |
| B6 | SMPR | guard 单独贡献 | 依赖标签 |
| B7 | ATR H8 + SMPR | 主 joint diagnostic | 是 |
| B8 | fixed-pool cost/flip/certificate | planner-coupled 上限参照 | 接口允许时 |
| B9 | ATM-style action-transfer | 最近直接 diagnostic | V2/P1 |

## 8.2 公平性约束

所有表示诊断必须使用：

- 同一 anchors；
- 同一 noise draws；
- 同一 embedding/cost space；
- 同一 clean normalization source；
- 同一 horizon；
- 同一 checkpoint；
- 同一 calibration/held-out split；
- 相同 threshold/model-complexity budget；
- 不允许某个 baseline 使用更多 label 或更多 sample。

创建：

```text
paper1/scripts/diagnostic_baseline_benchmark.py
paper1/results/diagnostic_baselines/heldout_baseline_rows.csv
paper1/results/diagnostic_baselines/heldout_baseline_summary.csv
paper1/tables/table_diagnostic_baselines.tex
assets/paper1_figs/fig_diagnostic_baseline_external.png
```

统一 row schema：

```text
model_family
training_seed_or_family_id
task
checkpoint_id
training_rho
stressor_family
stressor_severity
clean_score
stress_score
behavior_label
encoder_q90_norm
h1_q90_norm
action_shuffled_h8_q90_norm
action_zeroed_h8_q90_norm
time_shuffled_h8_q90_norm
atr_h8_q90_norm
smpr
joint_score
frozen_gate_pass
fixed_pool_flip
fixed_pool_cert_score
split_name
protocol_hash
```

## 8.3 统计与决策

报告：

- AUPRC；
- balanced accuracy；
- precision/recall；
- external false-pass；
- pairwise ordering accuracy；
- onset MAE 仅用于 sweep；
- task/seed/model block bootstrap 差异；
- 不在 108 rows 上报告普通 iid p-value。

Claim 收缩规则：

- encoder q90 与 joint 相当或更好：提升 encoder geometry 地位，删除 rollout empirically necessary 的强说法；
- H1 与 H8 持平：H-step 只保留为理论自然扩展；
- correct-action 与 shuffled/zeroed 持平：删除 action-conditioned 独立增量主张，或依赖更强 action/value guard；
- SMPR 无增量：guard 降为 appendix，主诊断转为 radius + planner guard；
- ATM-style 明显更强：本文定位为 paired visual intervention 的互补 diagnostic，而不是通用 action-consistency diagnostic。

---

# 9. 理论—实验四项一致性整改

## 9.1 子问题一：q90 与 `K alpha` 空洞

### 9.1.1 保留但降级 union-bound theorem

当前形式：

```math
P(\mathrm{flip})
\le K\alpha + P(\Delta_{\mathcal A}\le 2L_J\epsilon)
```

可以保留作 tail motivation，但必须明确：

- ATR q90 是描述性 checkpoint diagnostic；
- theorem 的单候选 `alpha` 不能直接取 0.1；
- `K=65` 时朴素代入为空洞；
- q90 解释为什么关注 tail，不产生数值 probability certificate。

### 9.1.2 引入 candidate-wise sharp certificate

clean winner `j*`：

```math
\Delta_j = C_h(a^j)-C_h(a^{j^*}),
\qquad
d_j = |C_{\tilde h}(a^j)-C_h(a^j)|.
```

若对所有 `j != j*`：

```math
\Delta_j > d_j+d_{j^*},
```

则 top-1 不变。定义：

```math
S_{\rm sharp}(h,\tilde h,\mathcal A)
=
\min_{j\ne j^*}[\Delta_j-d_j-d_{j^*}].
```

`S_sharp > 0` 为 sharp cert-pass。保留旧 coarse condition 作为对照：

```text
max_j d_j < clean top1/top2 margin / 2
```

修改 `tools/paper1_sample_level_certificate.py` 输出：

```text
coarse_cert_pass
sharp_cert_pass
sharp_cert_slack
observed_flip
flip_when_cert_fail
candidate_count
coverage_by_K
```

### 9.1.3 非空风险报告

由 deterministic implication：

```math
\{\mathrm{flip}\}\subseteq\{S_{\rm sharp}\le0\},
```

所以 sampled fixed-pool distribution 下：

```math
P(\mathrm{flip})\le 1-P(S_{\rm sharp}>0).
```

报告：

- `p_cert`；
- one-sided 95% lower confidence bound `p_cert,L`；
- `flip-risk upper = 1 - p_cert,L`；
- observed flip rate 作为 sharpness 对照；
- `flip | cert-fail`；
- checkpoint 内 interval + task/seed block bootstrap。

### 9.1.4 radius 到 cost drift 的定量桥梁

V1 最低要求：direct cost certificate 与 ATR 机制分析分开，避免伪校准。

V2 顶会要求优先完成经验校准：

```math
L_{\rm emp}
=
Q_{0.99}^{\rm CAL}
\left(
\frac{|C_h(a)-C_{\tilde h}(a)|}
{R_H(h,\tilde h,a)+\varepsilon}
\right).
```

冻结后在 E1–E5 验证 exceedance rate，并构造：

```math
\widehat d_j=L_{\rm emp}R_H(h,\tilde h,a^j).
```

只有 held-out coverage 合格时才报告 ACPC-only proxy certificate；否则正文明确区分 ATR 与 direct cost certificate。

可选解析加强：估计 Gaussian quadratic-form 所需的 trace、`tr(B^2)` 和 spectral norm，给 simultaneous candidate tail；未完成时不得写成已有 theorem result。

## 9.2 子问题二：统一 probability space

理论中显式定义：

```math
H\sim\mu_{\rm task},
\quad
\Xi\sim P_\tau(\cdot\mid H),
\quad
A_{\rm rec}\sim\nu(\cdot\mid H),
\quad
\mathcal A\sim q(\cdot\mid H)^K,
```

以及：

```math
(H,H')\sim\pi_{\rm diff}.
```

分开：

```math
\alpha_R(\epsilon)
=P_{H,\Xi,A_{\rm rec}}[R_H>\epsilon],
```

```math
\beta_{\rm plan}
=P_{H,\Xi,\mathcal A}[\text{fixed-pool top1 flip}],
```

```math
\beta_{\rm guard}
=P_{H,H',\Xi}[M_{\rm diff}\le R_H+\delta].
```

推荐修改：

- theorem 只保留 fixed-pool planning statement；
- guard 另列 proposition/definition；
- empirical selective region 定义为两个 independently audited criteria 的 conjunction；
- 不报告伪装成校准总概率的 `beta_plan + beta_guard`；
- 只有构造同一 joint sampling protocol 时才恢复 union bound。

新增 theory-to-data 表：

| Quantity | Random source | Empirical unit | Estimator | Claim |
|---|---|---|---|---|
| horizon radius | history × noise × recorded action | anchor | q90 | diagnostic tail |
| cert coverage | history × noise × fixed pool | anchor/pool | pass rate + one-sided CI | sampled-pool risk upper |
| guard failure | task-different pair × noise | pair | SMPR | proxy/oracle guard |
| closed-loop score | train seed × eval seed × trajectory | checkpoint | success mean/std | behavior authority |

## 9.3 子问题三：统一 ACPC metric 与 Jacobian map

### 9.3.1 新 canonical horizon metric

创建：

```text
tools/paper1_acpc_metrics.py
```

定义 weighted stacked rollout：

```math
\bar G_{\mathbf a}(z)
=
[\sqrt{\alpha_1}\Pi(\hat z_{t+1});\ldots;
 \sqrt{\alpha_H}\Pi(\hat z_{t+H})].
```

每个 anchor 的 radius：

```math
R_H^{(2)}(i)
=
\frac{
\|\bar G_{\mathbf a_i}(E(h_i))-
  \bar G_{\mathbf a_i}(E(\tilde h_i))\|_2
}{s_i+\varepsilon}.
```

ATR：

```math
\mathrm{ATR}_q=Q_q\{R_H^{(2)}(i)\}_{i=1}^n.
```

要求：

- default `H=8`；
- uniform `alpha_k=1/H`；
- `s_i` 明确定义并统一；
- 每个 anchor 一条 horizon radius；
- 多 noise draw 先做 anchor conditional aggregation；
- 旧 `(B×H,D)` stepwise q90 改名 `stepwise_rollout_q90`，只作 compatibility appendix；
- 旧值不再称 theorem-aligned ATR。

### 9.3.2 JVP map 完全对齐

`tools/paper1_jvp_hutchinson_sensitivity_audit.py` 的 composed output 必须使用与 `bar G` 相同的：

- rollout steps；
- weights；
- projection；
- embedding space；
- vectorization；
- normalization 前 map。

命题改成：

```math
E\|\bar G(E(o+\xi))-\bar G(E(o))\|_2^2
=
\sigma^2\|J_{\bar G}J_E\|_F^2+O(\sigma^3).
```

### 9.3.3 线性化校准

small sigmas：

```text
{0.0025, 0.005, 0.01, 0.02}
```

对 base/onset/endpoint、每 task/seed 报告：

- empirical `E[R^2]/sigma^2`；
- JVP trace；
- ratio/relative error；
- remainder growth；
- predicted-vs-measured scatter；
- calibration error。

不能只报告两个 estimator 同方向。

### 9.3.4 horizon/quantile sensitivity

至少：

```text
H ∈ {1,2,4,8}
q ∈ {0.80,0.90,0.95}
```

若 H1≈H8，删除 long-horizon empirically necessary；若 PushT/Cube 随 H 增强，报告 task-dependent effect。

## 9.4 子问题四：κ 定义与实现一致

正文当前 bounded 形式：

```math
\kappa_{\rm sub}
=
\frac{\|J_GJ_E\|_F^2}
{\|J_G\|_F^2\|J_E\|_F^2+\varepsilon}
\le1.
```

当前实现更接近：

```math
\kappa_{\rm rel}
=
\frac{d_z\|J_GJ_E\|_F^2}
{\|J_G\|_F^2\|J_E\|_F^2},
```

可大于 1。

整改：

1. 主文只报告 encoder、rollout、composed trace；
2. appendix 同时输出：

```text
kappa_submultiplicative
kappa_relative_isotropic
```

3. 第二个称 `relative isotropic alignment gain`；
4. 不称 angle/cosine/certificate；
5. 公式、代码、CSV、caption 完全一致；
6. synthetic linear-map test 验证 exact norms；
7. `kappa_sub <= 1 + tolerance`；
8. `kappa_rel == d_z * kappa_sub`；
9. Hutchinson 估计误差用 interval，不静默 clip。

修改：

```text
paper1/main.tex
tools/paper1_jvp_hutchinson_sensitivity_audit.py
paper1/tables/table_jvp_hutchinson_sensitivity_audit.tex
paper1/scripts/plot_gaussian_sensitivity_mechanism.py
tests/test_paper1_jvp_alignment_metrics.py
```

---

# 10. Fixed-pool audit 的最终整改

## 10.1 `flip | cert-pass = 0` 只作 invariant

正文替换为：

> By construction, cert-pass is a deterministic sufficient condition for preserving the clean winner on the shared candidate pool. The observed zero conditional flip rate is therefore an implementation check, not independent empirical evidence. The informative quantities are certificate coverage, observed flip risk outside the certified subset, and how both change across checkpoints.

执行含义：

- `flip | cert-pass = 0` 只进 appendix/checker；
- 主图不画全零 conditional rate；
- 主文强调 coverage、observed flip、`flip | cert-fail` 和 slack；
- 删除 “not overfit” 等错误解释。

## 10.2 新主图

最多两 panels：

### Panel A

```text
coarse certificate coverage
sharp candidate-wise certificate coverage
```

### Panel B

```text
observed top-1 flip rate
flip rate among certificate-fail anchors
```

Appendix：

- zero conditional flip invariant；
- certificate slack distribution；
- one-sided risk upper；
- q10/q95 negative gap；
- block-level raw tables。

## 10.3 Continuous score 与 risk–coverage

使用 `S_sharp` 以及与 certificate 等价的归一化 score：

```math
u_i=
\max_{j\ne j^*}\frac{d_j+d_{j^*}}{\Delta_j+\varepsilon}.
```

`u_i<1` 等价于 sharp cert-pass。

报告：

- score-bin observed flip；
- risk–coverage curve；
- AURC；
- calibration by checkpoint；
- recovered/fragile 和 model family 分层；
- 不用 cert threshold 重新拟合 behavior label。

## 10.4 K sensitivity

从同一 65-candidate ordered pool 构造 nested pools：

```text
K ∈ {8,16,32,65}
```

要求：

- expert candidate 始终保留；
- random candidate 顺序固定；
- 相同 seed；
- 不为每个 K 重新采样；
- 报 coverage、flip、sharpness、AURC 随 K 变化。

## 10.5 Hierarchical uncertainty

- checkpoint 内 binomial interval；
- one-sided cert coverage lower bound；
- task/seed/checkpoint block bootstrap；
- main text 使用 block-level interval；
- pooled Wilson 只作 appendix measurement precision。

## 10.6 PLDM transfer

若 PLDM planner/cost API 与 LeWM 可统一：

- V1 canonical PLDM seed 运行 fixed-pool sharp certificate；
- V2 新 PLDM seeds endpoint/intermediate 运行同 protocol；
- 不要求 coverage 与 LeWM 同尺度；
- 检查 score–flip monotonicity 和 risk–coverage 是否转移。

## 10.7 Adaptive CEM（V2/P1）

基于 common random numbers：

- clean/noisy 同一初始 Gaussian candidate samples；
- 每轮记录 elite overlap、mean/cov drift、first-action difference；
- 重点是 final first-action agreement；
- 分离 iteration 0 fixed pool 与 later adaptive iterations；
- 不称 closed-loop guarantee。

输出：

```text
paper1/results/fixed_pool_candidatewise_certificate.csv
paper1/results/fixed_pool_certificate_coverage_by_block.csv
paper1/results/fixed_pool_risk_coverage.csv
paper1/tables/table_fixed_pool_certificate_coverage.tex
assets/paper1_figs/fig_fixed_pool_certificate_calibration.png
```

---

# 11. SMPR anti-collapse / discriminability 最终整改

## 11.1 正确机制表述

优先写：

```text
task-grounded separations remain outside the contracted nuisance tube
```

不要将 SMPR pass-rate 上升自动写成 semantic margin 被训练得更大。必须分开报告：

- same-state noisy radius；
- different-state clean distance；
- raw margin；
- pass rate。

## 11.2 参数敏感性

扩展 `tools/paper1_semantic_margin.py`：

```text
noise_draws ∈ {1,5}
radius_q ∈ {0.80,0.90,0.95}
local_state_quantile ∈ {0.10,0.25,0.35,0.50}
margin_delta_norm ∈ {0.00,0.05,0.10,0.25}
label_binning ∈ {median,quartile,fixed_physical}
```

`margin_delta_norm` 乘 clean transition scale。

每组输出：

```text
same_state_radius_distribution
different_state_distance_distribution
raw_margin_distribution
pass_rate
pair_count
skipped_anchor_count
label_count
```

## 11.3 必须的 controls

创建：

```text
paper1/scripts/smpr_controls.py
```

包含：

| Control | 目的 |
|---|---|
| constant/collapsed rollout | low ATR 是否会被 guard 拒绝 |
| progressive collapse | guard 随 collapse 程度是否恶化 |
| identical clean/noisy positive control | radius=0 时实现是否正确 |
| state-label permutation | task labels 是否优于随机标签 |
| action permutation | guard 是否保留 action relevance |
| same-label nearest neighbor | label-crossing pair 是否更 task-distinct |
| global far-neighbor | 防止选很远状态轻易通过 |

Progressive collapse：

```math
z_\lambda=(1-\lambda)z+\lambda\bar z,
\qquad
\lambda\in\{0,0.25,0.5,0.75,1.0\}.
```

期望不是预设数值，而是 correctness：

- ATR 可以因 collapse 下降；
- positive-margin SMPR/joint gate 必须拒绝充分 collapse；
- 若 constant collapse 被判 robust，SMPR 实现或阈值不可用。

最小 correctness gate：

- collapse 不得在所有任务通过 positive-margin joint gate；
- pair count/skip rate 不得因参数变化悄然变小；
- random labels 与真实 labels 一样好时，删除 task-grounded 强说法；
- near-boundary 与 far-neighbor 同时展示。

## 11.4 更强任务语义

### TwoRoom

- room identity；
- doorway side；
- 是否必须过门；
- shortest-path/topological cost；
- next useful action region。

### PushT

- pusher–T contact；
- object pose relative to goal；
- keyframe/contact mode；
- clean candidate-cost vector；
- clean top-1 first-action region。

最低 oracle：object-goal pose cost + pusher-object distance，构造 near-state but decision-distinct pairs。

### Reacher

- end-effector–target distance；
- target quadrant；
- joint aliasing；
- one-step oracle reward/cost；
- clean top-1 candidate difference。

### Cube

- gripper–cube contact/grasp mode；
- cube–goal pose/orientation error；
- grasp topology；
- planner cost-to-go；
- top-1 candidate difference。

## 11.5 planner/value-grounded guard

选择 near-state pairs 满足：

```math
|V_{\rm oracle}(s_i)-V_{\rm oracle}(s_j)|>\tau_V
```

或：

```math
\arg\min_a C(s_i,a)\ne\arg\min_a C(s_j,a).
```

再检查 clean projected rollout distance 是否超过 same-state noise radius + positive margin。

版本要求：

- V1：完成参数 sensitivity、collapse/action/label controls，至少 TwoRoom+PushT oracle MVE；
- V2：四任务尽可能完成 planner/value-grounded guard；
- 只有 programmatic bins 成功时继续称 proxy-level guard；
- external behavior 与 SMPR 不共变时，将 SMPR 降到 appendix，主诊断改为 radius + fixed-pool planner guard。

输出：

```text
assets/paper1_data/smpr_sensitivity_v2.json
assets/paper1_data/smpr_controls_v2.json
assets/paper1_data/smpr_oracle_guard_v2.json
paper1/tables/table_smpr_sensitivity.tex
paper1/tables/table_smpr_controls.tex
assets/paper1_figs/fig_smpr_radius_margin_decomposition.png
```

---

# 12. 2026 并发工作、新颖性与参考文献

## 12.1 必须新增并审计的工作

| 工作 | 官方页面 | 直接重叠 | 本文差异 | 执行动作 |
|---|---|---|---|---|
| MWM | `https://arxiv.org/abs/2603.07799` | Action-Conditioned Consistency、多步 rollout | 训练/后训练生成式导航模型；本文是 fixed checkpoint paired visual intervention + guard | 正面对比，novelty 不押术语 |
| ATM | `https://arxiv.org/abs/2606.09028` | post-hoc action-consistency diagnostic、screening | real encoded vs predicted transition 的 action semantics；本文是 clean/corrupted same-state radius/guard | 最强 novelty risk；V2 做 ATM-style baseline |
| Delta-JEPA | `https://arxiv.org/abs/2606.31232` | action sensitivity、anti-collapse | 训练目标；本文为 no-retraining diagnostic | 相关工作 + 正向 external 候选 |
| ACID | `https://arxiv.org/abs/2607.02403` | inverse-dynamics action consistency、planning | decision-time planner intervention | planner-side related work/baseline |
| Is the Future Compatible? | `https://arxiv.org/abs/2605.07514` | action-state consistency diagnostic、background collapse | WAM rollouts；本文的 paired visual perturbation与 radius/guard | 用于支持 collapse controls 和 diagnostic comparison |
| Imagined Rollouts are Kinematic, Not Dynamic | `https://arxiv.org/abs/2607.05966` | rollout diagnostic responsiveness 与 perturbation protocol | kinematic-vs-dynamic failure；本文为 visual nuisance paired audit | 强化 off-axis/falsification 必要性 |

此外保留并准确定位已引用的：

- World Models as Group Actions；
- Bisim-JEPA；
- ReOI；
- LeJEPA theory；
- robust visual-control baselines。

## 12.2 新颖性定位

不要写：

```text
we introduce action-conditioned predictive consistency
```

改为三项具体贡献：

1. paired same-state clean/corrupted intervention under shared actions；
2. selective predictive radius + task/planner guard；
3. frozen checkpoint audit through encoder–rollout–candidate chain，含 cross-model/cross-stressor prospective validation。

建议标题候选：

```text
Selective Paired-Rollout Diagnostics for Gaussian Visual Robustness in Latent World Models
```

若保留当前标题，首次定义时立即说明：

```text
Here ACPC denotes paired clean/corrupted same-state rollout consistency,
not the broader real-versus-imagined consistency used in recent training methods.
```

## 12.3 Direct comparison matrix

主文或 appendix 加表：

| Method | Compared objects | Paired corruption | Shared action intervention | Guard | Post-hoc | Training/planning method |
|---|---|---:|---:|---:|---:|---:|
| ACPC/ATR+SMPR | clean vs corrupted same-state rollout | yes | yes | yes | yes | no |
| ATM | real encoded vs predicted transitions | no | action semantics | probe-based | yes | AITS optional |
| MWM ACC | real/imaged rollout consistency | no | yes | no explicit selective guard | no | training/post-training |
| Delta-JEPA | latent displacement/action | no | yes | anti-collapse by action decoding | no | training objective |
| ACID | predicted action cycle | no | yes | planner feasibility | decision-time | planning method |
| Future Compatible | action-state rollout compatibility | no | yes | collapse boundary discussed | yes | test-time selection optional |

## 12.4 ATM-style baseline

V1：完成 feasibility audit：

- 检查官方代码/权重；
- 若无代码，定义最小 action-transfer probe；
- 清楚标成 `ATM-style`，不得冒充官方复现。

V2：尽量完成：

- 相同 checkpoints；
- 相同 train/test split；
- 相同 external rows；
- 比较 pairwise ranking、AUPRC、runtime；
- 解释 ATM 与 paired-corruption ACPC 的互补性。

## 12.5 建议 BibTeX 起点

提交前必须由 `paper1/reference_audit.md` 按官方 arXiv 页面复核作者、日期、标题、DOI。

```bibtex
@article{yan2026mwm,
  title         = {{MWM}: Mobile World Models for Action-Conditioned Consistent Prediction},
  author        = {Yan, Han and Xiang, Zishang and Zhang, Zeyu and Tang, Hao},
  journal       = {arXiv preprint arXiv:2603.07799},
  year          = {2026},
  eprint        = {2603.07799},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2603.07799},
  url           = {https://arxiv.org/abs/2603.07799}
}

@article{chen2026atm,
  title         = {{ATM}: Action-Consistency Transfer Matrix for Diagnosing and Improving Latent World Models},
  author        = {Chen, Jiaheng},
  journal       = {arXiv preprint arXiv:2606.09028},
  year          = {2026},
  eprint        = {2606.09028},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2606.09028},
  url           = {https://arxiv.org/abs/2606.09028}
}

@article{zhang2026deltajepa,
  title         = {{Delta-JEPA}: Learning Action-Sensitive World Models via Latent Difference Decoding},
  author        = {Zhang, Zhenghao and Wang, Yuanxiang and Guan, Zhenyu and Yang, Yujia and Shi, Bingkang and Zong, Tianyu and Yi, Hongzhu and Chao, Guoqing and Chen, Xingchen and Yang, Tiankun and Bao, Chenxi and Yu, Tao and Zhou, Jingjing and Xu, Jungang},
  journal       = {arXiv preprint arXiv:2606.31232},
  year          = {2026},
  eprint        = {2606.31232},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2606.31232},
  url           = {https://arxiv.org/abs/2606.31232}
}

@article{seo2026acid,
  title         = {{ACID}: Action Consistency via Inverse Dynamics for Planning with World Models},
  author        = {Seo, Gawon and Kim, Dongwon and Kwak, Suha},
  journal       = {arXiv preprint arXiv:2607.02403},
  year          = {2026},
  eprint        = {2607.02403},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2607.02403},
  url           = {https://arxiv.org/abs/2607.02403}
}

@article{ruan2026futurecompatible,
  title         = {Is the Future Compatible? Diagnosing Dynamic Consistency in World Action Models},
  author        = {Ruan, Bo-Kai and Hsiao, Teng-Fang and Lo, Ling and Shuai, Hong-Han},
  journal       = {arXiv preprint arXiv:2605.07514},
  year          = {2026},
  eprint        = {2605.07514},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2605.07514},
  url           = {https://arxiv.org/abs/2605.07514}
}

@article{schaefer2026kinematic,
  title         = {Imagined Rollouts are Kinematic, Not Dynamic: A Diagnosis of Long-Horizon World-Model Failure},
  author        = {Schaefer, Finn Rasmus and Moller, Korbinian and Gao, Yuan and Oefinger, Christian and Schmidt, Sebastian and Betz, Johannes},
  journal       = {arXiv preprint arXiv:2607.05966},
  year          = {2026},
  eprint        = {2607.05966},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2607.05966},
  url           = {https://arxiv.org/abs/2607.05966}
}
```

---

# 13. 论文结构与主文证据布局

## 13.1 主文建议证据顺序

1. Gaussian behavior cliff；
2. LeWM three-seed recovery sweep；
3. horizon-v2 ATR + SMPR endpoint/full-sweep；
4. strict frozen held-out + PLDM one-seed external；
5. fixed-`rho` blur/resize mixed outcomes；
6. fixed-pool candidate-wise certificate coverage；
7. local sensitivity calibration；
8. concise limitations。

## 13.2 V1 主文与 appendix 分配

主文保留：

- behavior sweep；
- compact ATR/SMPR result；
- one compact frozen external table/figure；
- fixed-pool coverage/flip；
- local sensitivity；
- mixed non-Gaussian table。

Appendix：

- full PLDM rows；
- simple baseline table；
- rho confound audit；
- SMPR parameter grid和 controls；
- K sensitivity；
- all external rows；
- target-view falsification；
- exact JVP decomposition。

## 13.3 V2 更新

V2 新增/替换：

- PLDM prospective 3-training-seed endpoint/intermediate summary；
- multi-severity cross-stressor figure；
- ATM-style baseline；
- stronger oracle/value guard；
- empirical radius-to-cost calibration；
- adaptive CEM audit（篇幅允许）。

## 13.4 贡献写法

建议三条：

1. selective paired-rollout formulation；
2. frozen cross-model/cross-stressor diagnostic validation；
3. radius–cost–decision and local-sensitivity audits with explicit limitations。

不要把 artifact 数量列成贡献。

---

# 14. 文件级实现清单

## 14.1 新建

```text
paper1/config/frozen_diagnostic_protocol_v1.json
paper1/config/frozen_diagnostic_protocol_v1.schema.json
paper1/config/pldm_prospective_v2_training_manifest.json
paper1/scripts/freeze_diagnostic_protocol.py
paper1/scripts/frozen_external_validation.py
paper1/scripts/diagnostic_baseline_benchmark.py
paper1/scripts/gaussian_rho_confound_audit.py
paper1/scripts/build_cross_stressor_external_validation.py
paper1/scripts/plot_frozen_external_validation.py
paper1/scripts/fixed_pool_certificate_calibration.py
paper1/scripts/smpr_controls.py
paper1/scripts/smpr_sensitivity.py
paper1/scripts/target_view_frozen_gate_validation.py
tools/paper1_acpc_metrics.py
tools/paper1_target_view_diagnostic_manifest.py
tests/test_paper1_acpc_metrics.py
tests/test_paper1_jvp_alignment_metrics.py
tests/test_paper1_frozen_gate_no_recalibration.py
tests/test_paper1_candidatewise_certificate.py
```

## 14.2 修改

```text
paper1/main.tex
paper1/references.bib
paper1/reference_audit.md
paper1/arxiv_release_notes.tex
paper1/scripts/run_all_paper1_diagnostics.sh
paper1/scripts/build_diagnostic_manifest.py
paper1/scripts/build_full_sweep_diagnostics.py
paper1/scripts/heldout_diagnostic_validation.py
tools/paper1_phase0_acpc.py
tools/paper1_semantic_margin.py
tools/paper1_sample_level_certificate.py
tools/paper1_gaussian_sensitivity_audit.py
tools/paper1_jvp_hutchinson_sensitivity_audit.py
tools/check_paper1_consistency.py
tools/README_paper1.md
DATA_MANIFEST.md
```

## 14.3 新 artifacts

```text
assets/paper1_data/acpc_horizon_v2_lewm.json
assets/paper1_data/acpc_horizon_v2_pldm.json
assets/paper1_data/smpr_sensitivity_v2.json
assets/paper1_data/smpr_controls_v2.json
assets/paper1_data/smpr_oracle_guard_v2.json
paper1/results/frozen_diagnostic_protocol_calibration.json
paper1/results/frozen_external_validation_rows.csv
paper1/results/frozen_external_validation_summary.csv
paper1/results/diagnostic_baselines/heldout_baseline_rows.csv
paper1/results/diagnostic_baselines/heldout_baseline_summary.csv
paper1/results/diagnostic_baselines/gaussian_rho_confound_rows.csv
paper1/results/diagnostic_baselines/gaussian_rho_confound_summary.json
paper1/results/external_validation/cross_stressor_fixed_rho_rows.csv
paper1/results/external_validation/cross_stressor_fixed_rho_summary.json
paper1/results/external_validation/pldm_frozen_rows_v1.csv
paper1/results/fixed_pool_candidatewise_certificate.csv
paper1/results/fixed_pool_risk_coverage.csv
```

Artifact 必须记录：

```text
schema_version
created_utc
source_paths
source_hashes
code_commit
protocol_hash
model_family
training_seed/eval_seed semantics
status
missing rows
errors
```

---

# 15. Codex 执行阶段与依赖关系

## Phase 0：snapshot 与 correctness audit

- [ ] 记录现有 PDF、main.tex、canonical artifacts SHA-256；
- [ ] 记录当前 stepwise ATR 实现语义；
- [ ] 确认 PLDM 36 checkpoints 可加载；
- [ ] 确认 target-view manifest 可构建；
- [ ] 枚举 blur/resize 支持 severities；
- [ ] 运行最小 smoke benchmark，记录 wall time、GPU memory、I/O。

**Gate 0**：任何 missing model/data 必须形成显式报告。

## Phase 1：canonical metric 与单元测试

- [ ] 新建 `paper1_acpc_metrics.py`；
- [ ] horizon-level与 stepwise metric 分名；
- [ ] JVP map 对齐；
- [ ] κ 两种定义修复；
- [ ] synthetic tests；
- [ ] 2-task smoke run。

**Gate 1**：metric/JVP 数学量不一致时不得进入全量重算。

## Phase 2：V1 protocol 与现有 checkpoint 重算

- [ ] 重算 LeWM CAL/E1 horizon-v2 metrics；
- [ ] 重算 PLDM canonical seed；
- [ ] 重算 LeWM strongest blur/resize；
- [ ] 完成 PLDM strongest blur/resize；
- [ ] 完成 target-view diagnostics；
- [ ] 生成 frozen protocol；
- [ ] external scripts只读 protocol。

**Gate 2**：外部结果不得触发 threshold search。

## Phase 3：baseline、fixed-pool、SMPR

- [ ] encoder/H1/action-shuffle/H8/joint benchmark；
- [ ] Gaussian-only rho confound appendix；
- [ ] sharp certificate 与 risk–coverage；
- [ ] K sensitivity；
- [ ] SMPR positive margins；
- [ ] collapse/action/label/far-neighbor controls；
- [ ] TwoRoom+PushT oracle MVE。

**Gate 3**：根据真实结果确定 claim 强弱，不允许先写结论。

## Phase 4：novelty 与论文重写

- [ ] 加六篇 BibTeX；
- [ ] 更新 reference audit；
- [ ] related work direct comparison；
- [ ] 修改 title/abstract/contributions；
- [ ] 删除过强 certificate、selector、novelty 语言；
- [ ] 图表和 caption 与新指标一致。

## Phase 5：ArXiv v1 release

- [ ] 生成 protocol hash；
- [ ] 打 `paper1-arxiv-v1-lockbox` tag；
- [ ] release notes 记录 PLDM one-training-seed 边界；
- [ ] build/checker/tests 全过；
- [ ] source bundles isolated compile；
- [ ] 发布后不更改 protocol_v1。

## Phase 6：Prospective PLDM v2

- [ ] 写 launch manifest；
- [ ] 启动两个新 training seeds；
- [ ] 最低配置 B；
- [ ] 每 checkpoint 3 eval seeds；
- [ ] base/intermediate/std0.08 做 Gaussian evaluation；
- [ ] base/std0.08 做 multi-severity blur/resize；
- [ ] protocol_v1 无调参应用；
- [ ] 全部失败结果保留。

## Phase 7：顶会 v2 完成

- [ ] prospective PLDM replication 汇总；
- [ ] multi-severity external figure；
- [ ] ATM-style baseline；
- [ ] oracle/value guard 扩展；
- [ ] empirical radius-to-cost calibration；
- [ ] adaptive CEM（资源允许）；
- [ ] 目标会议模板和页数重排；
- [ ] blind release gate。

---

# 16. 统计方案

## 16.1 独立单位

- LeWM：training seed 是主 replication unit；
- PLDM v1：只有一个 training unit，eval seeds 是 repeated evaluation；
- PLDM v2：三个 training seeds 可报告 training-seed mean/std；
- anchor/candidate 只用于 checkpoint 内 measurement；
- task 是 heterogeneous block，不假设同分布。

## 16.2 报告规则

- 三 training seeds：mean ± population std，外加 raw per-seed values；
- 单 PLDM training seed：per-task point + evaluation-seed std，不给 training-seed CI；
- block bootstrap：以 task×training-seed×model family 为 block；
- 小样本 correlation 只写 descriptive；
- 不使用 “significant” 除非正式检验与假设预注册；
- 不把 pooled anchor Wilson interval当跨 seed uncertainty。

## 16.3 External metrics

优先：

- AUPRC；
- balanced accuracy；
- log loss/calibration；
- pairwise ordering；
- fixed-`rho` signed agreement；
- per-block raw table；
- severity monotonicity；
- onset MAE 只用于 Gaussian sweep。

---

# 17. 资源、MVE 与降级方案

## 17.1 现有 checkpoint audit

先运行：

```text
2 tasks × 2 checkpoints × 16 anchors × 2 noise draws
```

记录：

```text
wall_time_per_row
peak_gpu_memory
model_load_time
data_io_time
jvp_time
fixed_pool_time
```

再外推全量；不得在 benchmark 前写死总时长。

## 17.2 V1 降级 MVE

若全量重算过慢：

1. TwoRoom + PushT；
2. LeWM seed3072 CAL；
3. LeWM seed3073 external；
4. PLDM TwoRoom + PushT；
5. target-view PushT；
6. blur TwoRoom + resize PushT；
7. 32 anchors、3 noise draws；
8. protocol 先冻结，后续只扩样本不重调。

MVE 必须验证：

- metric/JVP 对齐；
- external no-recalibration；
- target-view falsification 可运行；
- collapse control 被 guard 拒绝；
- candidate-wise certificate invariant。

## 17.3 PLDM v2 资源降级

优先级：

1. 四任务 base + intermediate + std0.08；
2. 四任务 base + std0.08；
3. 若只能部分任务，优先 PushT + TwoRoom，但最终稿不得写四任务 prospective replication；
4. 不允许为了节省资源只补 canonical seed 表现最好的任务。

---

# 18. 失败判据与 Claim 决策

## 18.1 强结果

满足：

- PLDM frozen validation 成立；
- fixed-`rho` blur/resize mixed outcome 可区分；
- joint diagnostic 优于 encoder/H1/action-shuffled；
- candidate-wise coverage/flip 关系有 sharpness；
- SMPR collapse controls 通过；
- V2 PLDM prospective replication方向稳定；
- 无隐藏 counterexample。

可写：

> The public-v1 frozen paired-rollout radius/guard diagnostic transfers across independently trained model families and distinguishes mixed non-Gaussian outcomes at fixed training strength.

## 18.2 中等结果

情形：

- rho-only 匹配 in-domain onset；
- external transfer 部分成立；
- simple baselines 有部分持平；
- SMPR 仅 proxy-level。

写法：

> The Gaussian sweep provides internal mechanism evidence, while diagnostic validity is evaluated through frozen cross-model and fixed-training-strength cross-stressor tests.

删除：

- reliable onset predictor；
- checkpoint selector；
- beats training metadata；
- universal action-conditioned diagnostic。

## 18.3 负但可发表结果

若：

- PLDM frozen gate 失败；
- fixed-`rho` external 无法区分；
- encoder/H1/action-shuffled 不弱于 ACPC；
- collapse control 未被 SMPR 拒绝；

则定位：

> A controlled audit of when paired predictive-consistency diagnostics align with, and fail to explain, visual robustness.

必须保留失败，结合 iKCE/Future Compatible 等工作讨论 diagnostic responsiveness 和 deceptive consistency。

---

# 19. Release 与一致性 Gate

V1 和 V2 均执行：

```bash
python -m tools.check_paper1_consistency
pytest -q
bash paper1/scripts/run_all_paper1_diagnostics.sh
cd paper1 && bash build.sh --clean
cd .. && bash paper1/check_arxiv_ready.sh
bash paper1/docs/check_blind_ready.sh
```

新增 checker：

- external leaderboard 不含 `rho/std_max`；
- Gaussian appendix 的 rho confound 标为 privileged；
- fixed-rho endpoint rows 的 rho 完全一致；
- 完整 24 paired rows 未被选择性过滤；
- protocol hash 一致；
- external script 未重调；
- ATR 字段为 horizon-v2；
- old stepwise metric 不冒充 ATR；
- `flip|cert=0` 不出现在主 claim；
- κ 公式/字段/caption 一致；
- PLDM v1 的 eval seeds 不被标作 training seeds；
- 新 artifacts 的 hashes 已进入 `DATA_MANIFEST.md`；
- references.bib 与 reference_audit 对齐。

---

# 20. Codex 禁止事项

- 不覆盖旧 canonical JSON；
- 不手工写预期数字；
- 不在 external split 选择阈值；
- 不因新 PLDM seeds 结果修改 protocol_v1；
- 不后验选择 blur/resize severity；
- 不只报告正向 stressor rows；
- 不把 PLDM one seed 写成 multi-seed stability；
- 不把三个 eval seeds 写成三个 training seeds；
- 不把 target-view failure 写成成功 repair；
- 不把 `flip|cert=0` 写成独立统计证据；
- 不把 `kappa_relative_isotropic` 写成 bounded angle；
- 不把 ATM-style 实现冒充官方 ATM；
- 不将 `std_max` 放进 external checkpoint leaderboard；
- 不因 rho-only 匹配 onset 就停止外部验证；
- 不承诺 adaptive/closed-loop formal guarantee。

---

# 21. 最终硬验收清单

## V1 必须

- [ ] horizon-v2 ATR 与 JVP map 对齐；
- [ ] κ 修复和 unit tests；
- [ ] strict frozen LeWM E1；
- [ ] PLDM one-seed full-sweep E2；
- [ ] LeWM fixed-rho blur/resize 全 rows；
- [ ] PLDM strongest blur/resize base+endpoint；
- [ ] target-view failed-repair test；
- [ ] encoder/H1/action-shuffle/joint baselines；
- [ ] rho confound appendix；
- [ ] candidate-wise sharp certificate；
- [ ] `flip|cert=0` 降级；
- [ ] SMPR positive margin + controls；
- [ ] 至少 TwoRoom+PushT oracle MVE；
- [ ] 六篇 concurrent references；
- [ ] release tag 和 protocol hash；
- [ ] build/tests/checkers 全通过。

## V2 顶会最低线

- [ ] 两个新 PLDM training seeds，至少配置 B；
- [ ] protocol_v1 prospective application；
- [ ] LeWM/PLDM 三档 blur/resize severity；
- [ ] PLDM endpoint/intermediate training-seed replication；
- [ ] ATM-style baseline 或明确不可行性记录；
- [ ] empirical radius-to-cost calibration；
- [ ] 四任务更强 semantic/planner guard 尽可能完成；
- [ ] block-level uncertainty；
- [ ] 目标会议模板与 blind bundle。

## Strong claim 额外要求

- [ ] joint diagnostic 在至少两个 external axes 优于 encoder/H1/action-shuffled；
- [ ] progressive collapse 被 joint guard 拒绝；
- [ ] prospective PLDM seeds 不出现系统性反例；
- [ ] fixed-pool risk–coverage 有合理 sharpness；
- [ ] 无未披露 discordant rows。

---

# 22. 推荐的最短执行顺序

1. snapshot old artifacts；
2. 修 horizon metric 和 κ；
3. freeze seed3072 protocol；
4. strict LeWM held-out；
5. PLDM canonical full sweep 重算；
6. LeWM fixed-rho strongest blur/resize；
7. PLDM strongest blur/resize；
8. target-view falsification；
9. encoder/H1/action-shuffle/joint baseline；
10. sharp fixed-pool certificate；
11. SMPR positive margins与 controls；
12. novelty/reference update；
13. ArXiv v1 lockbox + release；
14. 立即启动两个 PLDM prospective seeds；
15. 等训练期间完成 multi-severity、ATM-style、oracle guard 和 radius-to-cost calibration；
16. 汇总 prospective PLDM results，不改 protocol；
17. 目标会议 v2 release。

---

## 最终判断

本计划采用分阶段策略：

- **ArXiv v1 不等待 PLDM 另外两个 training seeds。** 一个完整 PLDM full-sweep training family + 三 evaluation seeds 足以承担受限的跨模型验证；
- **v1 公开冻结后再训练两个 PLDM seeds。** 这使最终顶会稿获得真正的 prospective replication；
- **v2 至少采用 PLDM 配置 B，并补多 severity blur/resize。** 完成后，实验规模本身不再是主要短板；
- **最终成败主要取决于**：ACPC 相对 encoder/H1/action-shuffled 的增量、SMPR 是否拒绝 collapse、radius–cost–decision 是否定量闭环，以及与 ATM/MWM/Delta-JEPA/ACID 等并发工作的差异是否清楚。

Codex 应将所有结果按本计划的 frozen protocol、failure rules 和 release gates 执行，不得根据期望结论选择性修改实验。

---

# 23. Execution log（2026-07-11）

## 23.1 ArXiv v1 执行状态

Phase 0--5 的技术工作已经完成；Phase 6--7 按本计划的先后关系保留到 public-v1 正式 release 之后，不在本次结果中伪装为已完成。

- Phase 0：checkpoint/loadability、target-view、blur/resize、smoke runtime/GPU memory 和 missing/error contracts 已审计；最终无残留 `eval.py`、diagnostic、pytest 或 LaTeX 进程。
- Phase 1：canonical horizon-v2 metric、matched weighted-stacked JVP map、两种 kappa 定义和 synthetic tests 已完成。完整 JVP v2 为 36 checkpoint rows / 288 probes，全部 `ok`。
- Phase 2：CAL/E1/E2/E3/E4 已完成并保持 frozen no-retuning。E1 balanced accuracy/AUPRC 为 `0.945/0.965`；E2 为 `0.684/0.541`；E3 fixed-rho 为 `0.563/0.737` 且 recall `0.375`；E4 保留 target-view failure 和 full-sequence false-pass boundary。
- Phase 3：272-row matched baselines、Gaussian-only rho confound、108-checkpoint/10,800-history sharp certificate、K sensitivity、risk--coverage、12-block bootstrap、912-row SMPR sensitivity、44-row controls 和 TwoRoom+PushT four-row state-derived MVE 已完成。结果要求删除 long-horizon/correct-action necessity，并将 SMPR 收缩到 proxy-level guard correctness。
- Phase 4：标题、摘要、contributions、theory/probability-space、direct comparison、六篇 2026 references、ATM feasibility boundary、图表和 captions 已按真实结果重写。
- Phase 5：`DATA_MANIFEST.md`、diagnostic manifest builder、release notes、runner、checker、main/blind/arXiv builds 已更新。旧 monolithic checkpoint path 已退休；所有 checkpoint shards 串行、带 timeout、默认单 GPU/2 native threads、完成 shard 可校验续跑。默认 Paper1 runner 为 CPU-only；通用 `run_trainer.sh` 另以 `eval_max_concurrency=1` 为默认并发上限，并保留显式提高能力。

## 23.2 Frozen protocol 与主要产物

Frozen protocol 自冻结后未改变：

```text
paper1/config/frozen_diagnostic_protocol_v1.json
SHA-256 edcb801c3da388e673c9b55d706a558aa01da7a281fc151e52e1cda566045a21
frozen_at_utc 2026-07-10T09:33:21.985570+00:00
calibration_commit c943fdf75cd71bc08e5466e1700676069728b7d2
```

主要新增 full artifacts 的 SHA-256 已写入 `DATA_MANIFEST.md` 并由 `tools/check_paper1_consistency.py` 逐一复核，包括 E1--E4、matched baselines、rho confound、JVP v2、linearization/H-q、sharp certificate 和 SMPR v2 三个 artifacts。

最终 author-placeholder release candidate 记录：

```text
paper1/main.tex                         2995095dd3f8b99067de22af72e07231f5a64dc267675d21459ef1ff1b987ed1
paper1/main.pdf                         ad141a75be6e3330cc07891d95471525988a427ab2b254dc567349cb2d336f5f
/tmp/paper1_arxiv_v1_src.tar.gz         bdd54b914485fe84515c17659900549402f9a2a4ada7551e7cc29bcd448ae8c5
/tmp/paper1_blind_src.tar.gz            642d665795022428139e48c5b6e3e3bd8690e4ce177e9805a1078501ad91d941
```

作者写入后 `main.tex`、PDF 和 bundles 的 hashes 必然变化，必须重跑 release gates 并以新值替换上述 RC 记录。

## 23.3 验收结果

```text
python -m tools.check_paper1_consistency              PASS
pytest -q                                             131 passed
bash paper1/scripts/run_all_paper1_diagnostics.sh     PASS (CPU-only default)
cd paper1 && bash build.sh --clean                    PASS, 30 pages
bash paper1/docs/check_blind_ready.sh                  PASS, isolated bundle
ALLOW_AUTHOR_PLACEHOLDER=1 bash paper1/check_arxiv_ready.sh
                                                      PASS, isolated bundle
git diff --check                                      PASS
bash -n release/runner scripts                        PASS
```

最终 `main.log` 与两个 isolated bundle logs 均无 undefined citation/reference、fatal、Overfull 或 Underfull diagnostics。关键页（title/abstract、concurrent comparison、frozen external table、certificate/JVP figures）已做 PDF raster visual inspection，未发现裁切或重叠。

## 23.4 唯一剩余 release blocker

`paper1/arxiv_metadata.tex` 仍含 `Author names to be supplied for arXiv v1`。真实作者不可由 Codex 推断，因此正式（不设置 `ALLOW_AUTHOR_PLACEHOLDER=1`）arXiv gate 会继续失败，这是预期保护。`paper1-arxiv-v1-lockbox` tag 也未创建：在作者信息写入、最终 source commit 形成之前打 tag 会把占位作者和不完整 commit 锁成 public-v1，违反本计划。

解除 blocker 后的唯一正确顺序是：写入真实 author list → 重跑 checker/tests/main/blind/arXiv gates → 记录新的 PDF/bundle hashes → 创建最终 release commit → 在该 commit 上创建 `paper1-arxiv-v1-lockbox`。随后才能按 Phase 6 启动两个 prospective PLDM training seeds，且不得更改 protocol v1。
