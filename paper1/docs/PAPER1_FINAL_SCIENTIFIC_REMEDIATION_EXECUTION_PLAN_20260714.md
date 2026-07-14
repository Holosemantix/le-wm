# Paper1 最终科学整改执行规划 — 2026-07-14

状态：执行版本

适用范围：`paper1/main.tex`、其直接引用的 figures/tables、对应生成脚本、machine-readable results、tests、normal/blind build 与 submission package。

本文件是本轮论文整改的执行规格。最终稿应是一篇紧凑的 diagnostic paper：用 target-free ACPC 描述视觉扰动经过 action-conditioned prediction 后的影响，用 discriminability guard 排除明显 collapse，用 planner audit 建立 downstream relevance，并用 cross-task 与 cross-stressor experiments 界定适用范围。历史探索材料可以留在仓库中，但不得成为最终稿或 release bundle 的依赖。

## 1. 最终论文定位

### 1.1 目标标题

> **Target-Free Action-Conditioned Predictive Diagnostics for Visual Robustness in JEPA World Models**

### 1.2 核心问题

对一个参数固定、评估期间不再训练的 JEPA world-model checkpoint：

1. nominal/probed views 描述同一状态时，它们在同一 action sequence 下的 predictive rollouts 会分离多少；
2. 这种 action-matched rollout disagreement 是否能在不读取 realized future 的情况下约束 future-error drift；
3. 8-step action-matched disagreement 是否提供超出 encoder shift、1-step disagreement 和同为 8-step 的 action/time-destroyed controls 的信息；
4. predictive stability 与 different-state separation 联合使用时，threshold portability 如何随 source-task 数量与组成变化；
5. 该 selective diagnostic 与 fixed-pool cost drift、planner decision regret 是否有可审计联系；
6. 在不针对 blur/resize 重新选择 threshold 时，最终 selective diagnostic 是否保留 relative checkpoint-ordering utility。

### 1.3 最终 claim hierarchy

1. **Theory:** ACPC 是 action-matched、target-free 的 predictive radius；它 samplewise bounds 对同一 future target 的 prediction-error drift。
2. **Selective interpretation:** 低 predictive radius 只有与 different-state separation guard 联合时才有 robustness 含义。
3. **P1 mechanism evidence:** 8-step action-matched ACPC 对 8-step future-error drift 提供超出 1-step、encoder 和 same-horizon destroyed-action controls 的信息。
4. **Planner audit:** candidate-conditioned ACPC 与 evaluated fixed-pool cost drift、certificates 和 adaptive decision regret 对齐。
5. **P2 cross-task transfer:** 对四个 tasks 的每个 nonempty proper source-task subset 选择 reference-normalized selective rule，并将 thresholds 原样应用到其余 tasks；完整覆盖 `1->3`、`2->2`、`3->1` 三个 source-coverage levels。
6. **P3 stressor scope:** 每个 task 使用由另外三个 Gaussian tasks 选择的 final selective rule，在 fixed blur/resize pairs 上接受 scoped relative-transfer 检验。

最终稿不声称 universal absolute threshold、精确 training-run population variance、SMPR semantic validity proof、unconstrained adaptive-CEM guarantee、closed-loop robustness guarantee 或 cross-architecture transfer。

## 2. Reader-facing metric dictionary

最终稿不得在首次出现时使用裸的 `encoder`、`H1`、`H5`、`H8` 或 `joint`。所有 horizon 记号都必须同时说明它代表的 autoregressive rollout steps。

### 2.1 公共记号

令 `h` 和 `h_tilde` 是同一底层状态的 nominal/probed histories，`E` 是 encoder，`F` 是 predictor，`a_0:H-1` 是两条分支共同使用的 action sequence。`H` 表示从当前 history 向未来 autoregressively predicted 的 step 数，不是 history length，也不是 evaluation episodes 数。

每个 anchor `i` 使用同一个 clean-transition scale `s_i`：observed clean 8-step transitions 的 median L2 size，包括 history-to-future boundary。每个 perturbation draw 先在 anchor 内聚合，再在 anchors 上取 q90。正文必须把 `q90` 写成“90th percentile across anchors”，不能假定读者知道 aggregation order。

### 2.2 四个容易混淆的对象

| Reader-facing name | 定义 | 是否使用 action | 理论角色 |
|---|---|---:|---|
| **Encoder shift (no rollout), q90** | 最后一个 history embedding 的 nominal/probed normalized distance，再取 anchor q90 | 否 | 简单 upstream baseline，不是理论贡献 |
| **1-step ACPC (`H=1`), q90** | 两条分支在同一个 recorded action 后的 next-latent disagreement，再取 anchor q90 | 是，1 step | ACPC general definition 的浅层特例；用于 horizon ablation，不是单独贡献 |
| **8-step action-matched ACPC (`H=8`), q90** | 两条分支在同一 8-action sequence 下的 weighted stacked rollout disagreement，再取 anchor q90 | 是，8 steps | 核心 ACPC radius 的主要 empirical instantiation；其 checkpoint q90 summary 称为 ATR |
| **Selective ACPC score (`ATR + SMPR`)** | low 8-step ATR 与 high SMPR 两个 threshold margins 的 minimum | 间接使用 8-step action-matched rollout | theory-motivated operational diagnostic，不是 theorem |

对应公式在主文写为：

```text
r_E(i,m)
  = ||E(h_i) - E(h_tilde_i^m)|| / (s_i + epsilon),

r_1(i,m)
  = ||F(E(h_i), a_i,0) - F(E(h_tilde_i^m), a_i,0)||
    / (s_i + epsilon),

r_8(i,m)
  = ||G_a_i^1:8(E(h_i)) - G_a_i^1:8(E(h_tilde_i^m))||
    / (s_i + epsilon),

q90(r_H)
  = Q_0.90({ mean_m r_H(i,m) }_i).
```

这里的 `action-matched` 指 observed future 对应的 recorded action sequence 被原样用于 nominal/probed branches；它不表示 optimal action 或 oracle policy action。代码字段可以继续使用 `correct_*`，paper-facing text 必须使用 `action-matched`。

### 2.3 ATR、SMPR 与 selective score

`Action-Conditioned Trajectory Radius (ATR)` 是 normalized 8-step action-matched ACPC 的 checkpoint q90 summary。P2 使用 task × training-seed reference normalization：

```text
ATR_rel(task, seed, rho)
  = ATR(task, seed, rho)
    / (ATR(task, seed, rho=0) + epsilon).
```

`Selective Margin Pass Rate (SMPR)` 是 different-state proxy pairs 保持在 same-state perturbation tube 之外的比例。它用于排除 obvious contraction/collapse，不证明 full semantic or action validity。

最终 selective score 写为：

```text
S_selective
  = min(
      (tau_R - ATR_rel) / (|tau_R| + epsilon),
      (SMPR - tau_M) / (|tau_M| + epsilon)
    ).
```

`S_selective >= 0` 表示两个条件同时通过。Tables、figures 和 prose 一律使用 `Selective ACPC score` 或 `ATR+SMPR rule`，不使用无解释的 `joint score`。

### 2.4 Sample-level feature 与 checkpoint q90 不得混写

P1 regression 使用每个 trajectory block、severity 和 perturbation draw 的 encoder/ACPC responses。P2/P3 使用将 anchors 汇总后的 checkpoint-level q90 statistics。两者来自同一 geometric object，但 statistical unit 不同。

正文不得把 P1 的 `1-step ACPC feature` 写成 `H1 q90`，也不得把 P1 的 `8-step ACPC feature` 写成 checkpoint-level ATR。所有 captions 必须说明使用的是 per-block response 还是 checkpoint q90。

## 3. Theory specification

### 3.1 Main-text chain

理论只保留一条递进链：

1. `H`-step action-matched ACPC definition；
2. target-free future-error-drift theorem；
3. selective discriminability definition 与 collapse caveat；
4. ATR、SMPR 与 selective score 的 operational mapping；
5. LeWM squared-goal-cost 的 candidate-wise sharp consequence；
6. fixed-pool regret、top-1/elite certificates 与 conditional adaptive-CEM corollary。

Target-free theorem 是主 theorem。Planner result 是 downstream consequence。Encoder q90、1-step q90 和 threshold score 都不是额外 theorem。

### 3.2 Target-free future-error drift

对同一个 action-matched future `Y_a^H`，定义

```text
e_nominal = ||G_a(E(h)) - Y_a^H||,
e_probed  = ||G_a(E(h_tilde)) - Y_a^H||.
```

主 theorem 为：

```text
|e_probed - e_nominal| <= ACPC_H(h, h_tilde, a).
```

必须明确：theorem 对每个 `H` 都成立；它没有声称更长 horizon 的 numerical bound 必然更 tight，也没有声称 8-step forecast 比 1-step forecast 更准确。

### 3.3 Selective discriminability

对 externally task-distinct state pair，定义：

```text
Delta_dyn^H(s_i, s_j, a)
  = d_Y(Y^H(s_i,a), Y^H(s_j,a)) > m,

d(Psi(z_i), Psi(z_j)) > m',

M_diff(i,j,a) > R_sigma + delta_m.
```

这三行建立 conceptual selective criterion。实际 SMPR 只使用 programmatically selected proxy pairs。主文紧接 collapse counterexample：constant encoder–predictor 可以获得零 ACPC，同时抹去 planning distinctions；因此 low ATR 不能单独解释为 robustness。

### 3.4 Planner consequence

保留 actual paired candidate endpoint 的 sharp condition：

```text
C_j - C_w - b_j - b_w > 0.
```

主文只陈述 candidate-cost bound、fixed-pool regret、top-1/elite implication 与 conditional adaptive-CEM corollary。完整 proof、sharpness、tie handling、common-random-number assumptions 和 induction 放 appendix。

不得恢复 sampled-pool `K alpha` union bound，也不得把 checkpoint q90 ATR 当成 candidate-pool probability certificate。

### 3.5 Local Gaussian sensitivity

Appendix 保留：

```text
E ||Delta G||_2^2
  = sigma^2 ||J_G(E(o)) J_E(o)||_F^2 + O(sigma^3).
```

最多保留一张 deterministic-rebuild、nonredundant compact figure。不能重放 finite-difference/JVP/Hutchinson tables。Caption 必须说明这是 local mechanism approximation，不是 global robustness theorem。

## 4. Data scope 与 aggregation

| 维度 | 最终范围 | 执行约束 |
|---|---:|---|
| Tasks | TwoRoom, PushT, Reacher, Cube | 四 tasks 等权；Cube 不设 special-case prose |
| Training seeds | 3072, 3073, 3074 | 对称处理，不分配 CAL/TEST、development/replication roles |
| Gaussian training grid | `rho = 0.00, 0.01, ..., 0.08` | 每个 task × seed 九个 checkpoints |
| Gaussian evaluation | observation noise `sigma = 0.08`，goal image clean | primary controlled stressor |
| Off-axis evaluation | fixed blur 与 fixed resize | secondary scope test |
| Evaluation seeds | 42/43/44 | checkpoint 内先汇总，不与 training seeds 混淆 |

`seed3075` 不属于正式设计。它不得进入 `main.tex`、referenced figures/tables、paper-facing JSON/CSV、diagnostic/release manifests、source package、public provenance narrative 或 formal-seed tests。历史 raw/config 文件无需 destructive deletion，但必须与最终 dependency graph 断开。

统计单位：

| Module | Primary unit | 汇总规则 |
|---|---|---|
| Gaussian sweep | task × training seed block | seed 内汇总后 task 等权；展示三-seed dispersion |
| P1 future drift | training seed；task 为 seed 内等权单位 | 三 seed points、mean ± sample SD、每 seed 4-task pass count |
| Planner audit | evaluated task/checkpoint/history block | 不外推 training-seed population |
| P2 cross-task | evaluation task | 枚举 14 个有方向的 source/evaluation task partitions；先在每个 evaluation task 内汇总三个 seeds，再对四个 tasks 等权 |
| Seed stability | evaluation training seed | appendix only |
| P3 cross-stressor | task × training seed pair | blur/resize 同属一个 block；task 等权 |

不得把 Gaussian checkpoint rows 或相互重叠的 task partitions 当作独立 generalization samples。

## 5. P1 — 8-step action-matched ACPC 的增量信息

### 5.1 P1 实际比较的对象

P1 不比较“8-step forecast accuracy”与“1-step forecast accuracy”。所有 regression models 预测同一个 target：8-step future-error drift

```text
D_8 = |e_probed^8 - e_nominal^8|.
```

三个 feature sets 为：

```text
A. Encoder + 1-step model
   severity + encoder shift + 1-step action-matched ACPC

B. Same-horizon destroyed-action model
   A + one 8-step ACPC control
   (zero-action / cross-trajectory action-sequence shuffle /
    within-sequence time shuffle)

C. Proposed action-matched model
   A + 8-step action-matched ACPC
```

所有 Ridge inputs 在每次 15-group fit 内经过 imputation 与 `StandardScaler`，因此 8-step feature 的 raw magnitude 较大不能自动带来更低 MAE。

对每个 task × training seed 有 16 trajectory groups。每次在 15 groups 上 fit Ridge，在剩余 1 group 上预测；轮换 16 次后计算 out-of-group MAE。正文第一次描述时必须写出这句，不以裸的 `held-out` 或 `grouped CV` 代替。

### 5.2 为什么 1-step vs 8-step 不是“误差自然累积”的 trivial comparison

1. ACPC 测量 nominal/probed model rollouts 之间的 disagreement，不是 model prediction 与真实 future 的 absolute error；两条分支的 common-mode rollout error 可以抵消。
2. A、B、C 预测的是完全相同的 8-step target `D_8`，不是各自预测不同 horizon target。
3. Regression feature 已标准化，raw scale 或随 horizon 增大的数值本身不能解释 MAE reduction。
4. B 与 C 都运行 8 autoregressive steps。B 保留相同 horizon 和相同 accumulation opportunity，只破坏 action identity 或 temporal order。
5. 因此最关键的 comparator 是 B：8-step action-matched ACPC 相对 strongest same-horizon destroyed control 的 improvement。A 只是说明 one-step signal 不足。
6. Theory 只给 upper bound；一个 loose 8-step radius 完全可能没有 predictive value，所以其 out-of-group increment 仍是 empirical question。

正文不得将结论写成“multi-step is more accurate than one-step”。标准结论为：

> Eight-step action-matched ACPC contains nonredundant information about eight-step future-error drift beyond encoder shift, one-step ACPC, and eight-step controls with destroyed action or temporal structure.

### 5.3 输入 artifacts 与 exact estimand

P1 只能读取：

- `paper1/results/target_aligned_acpc_dev/adjudication_four_task_seed3072_goal25_base_endpoint_retrospective_v1.json`
- `paper1/results/target_aligned_acpc_dev/adjudication_four_task_seed3073_goal25_base_endpoint_v1.json`
- `paper1/results/target_aligned_acpc_dev/adjudication_four_task_seed3074_goal25_base_endpoint_v1.json`

Generator 必须锁定 `no-noise base checkpoint + logged 8-step action-matched ACPC + absolute 8-step future-error drift`：

- seed3072：`primary_logged_fragile_base.cells[target == "absolute"]`；
- seeds3073/3074：`.artifacts[]` 中 basename 含 `baseline_seed<seed>` 的四 records，再读取 `logged_gates.correct_absolute_h8_error_drift`；
- 禁止混入 endpoint checkpoints、candidate-H5 planner track、adverse/signed targets 或 certificate invariants。

Full-precision source values必须先重建，再进行 display rounding：

```text
seed 3072: vs Encoder+1-step = 0.5551508778767943
           vs best destroyed 8-step = 0.5136177413559059
seed 3073: vs Encoder+1-step = 0.6080095622935984
           vs best destroyed 8-step = 0.5478245096278659
seed 3074: vs Encoder+1-step = 0.5135566790817282
           vs best destroyed 8-step = 0.4773407814722494
```

### 5.4 Main display

正文用一张 explanatory P1 display 完成两件事：

1. 左侧画出 A/B/C 的 feature boxes，并在顶部写明共同 target `8-step future-error drift`；
2. 右侧显示三个 training-seed points 与 mean ± sample SD，优先排列 same-horizon destroyed comparator，再排列 Encoder+1-step comparator。

Reader-facing columns 使用：

| Training seed | vs 8-step zero/shuffle control | vs encoder + 1-step | Tasks improved |
|---:|---:|---:|---:|
| 3072 | 51.4% | 55.5% | 4/4 |
| 3073 | 54.8% | 60.8% | 4/4 |
| 3074 | 47.7% | 51.4% | 4/4 |
| Mean ± SD | 51.3 ± 3.5% | 55.9 ± 4.7% | 12/12 cells |

不得使用 `vs H1`、`correct H8`、`destroyed H8` 等无解释短标签。Caption 必须给出：

```text
MAE reduction = (comparator MAE - action-matched model MAE)
                / comparator MAE.
```

Caption 说明 `Tasks improved` 表示 proposed feature 在两类 comparisons 中均降低 MAE。`8-step zero/shuffle control` 取 zero-action、cross-trajectory action-sequence shuffle、time shuffle 三者中“在未参与对应 fit 的 trajectory groups 上”MAE 最低者；这种选择使 comparator 更强，不用于挑选 proposed feature。

Absolute MAEs、每 task × seed cells、每种 destroyed control 与 adverse target 放 appendix。Trajectory bootstrap 若保留，只能描述 evaluated checkpoints 内的 block uncertainty，不能写成 training-run population interval。

### 5.5 Seed reporting

三个 training seeds 对称报告，不设置 provenance roles。正文说明：

- 两个 comparator 的 mean ± sample SD 分别为 `51.3 ± 3.5%` 与 `55.9 ± 4.7%`；
- 每个 seed 在四个 tasks 上都通过；
- 同一 task 的 Gaussian recovery onset 在三个 seeds 间最多相差一个 `rho = 0.01` grid step；
- 三 seeds 支持 directionally consistent independent training repeats，不精确估计 run-population variance。

## 6. P2 — All-subset cross-task evaluation of the selective rule

### 6.1 Estimand 与完整组合

P2 测量 source-task coverage 和 source-task composition 对 threshold portability 的影响。令四个 tasks 的集合为 `T`，对每个 nonempty proper subset `S`：

1. 只使用 `S` 中全部 checkpoints 与三个 training seeds 选择 `tau_R,tau_M`；
2. 将两个 thresholds 原样应用到 complement $T\setminus S$；
3. 对 complement 中每个 task 分别报告结果。

完整枚举 14 个有方向 partitions：

| Source coverage | Source subsets | Evaluation tasks per subset | Selection/evaluation rows | Selection/evaluation task-seed blocks |
|---|---:|---:|---:|---:|
| 1 source task $\rightarrow$ 3 evaluation tasks | 4 | 3 | 27 / 81 | 3 / 9 |
| 2 source tasks $\rightarrow$ 2 evaluation tasks | 6 | 2 | 54 / 54 | 6 / 6 |
| 3 source tasks $\rightarrow$ 1 evaluation task | 4 | 1 | 81 / 27 | 9 / 3 |

正文第一次介绍时使用 `source tasks` 和 `evaluation tasks` 完整解释数据流，不使用 `fold`、`held-out task` 或 `leave-one-task-out` 作为读者理解 protocol 的前提。

### 6.2 Fixed rule 与 threshold selection

P2 始终使用同一个 two-condition rule：

```text
pass = [ATR_rel <= tau_R] AND [SMPR >= tau_M].
```

Candidate grid 固定为：

```text
tau_R in {0.05, 0.075, 0.10, 0.15, 0.20, 0.30}
tau_M in {0.80, 0.85, 0.90, 0.95}.
```

每个 source subset 独立选择 thresholds。Selection objective 按以下 lexicographic order 固定：source task × seed blocks 的 mean absolute recovery-onset error、false-early count、false-late count、negative task-macro balanced accuracy、`tau_R`、negative `tau_M`。不得加入 `top1_agree`、`proxy_gap_q50q90`、planner labels、learned composite 或 evaluation-task outcomes。Candidate grid、完整 objective tuple 与所有 ties 必须写入 params artifact。

### 6.3 Aggregation 与 interpretation

每个 evaluation task × training seed 的九个 checkpoints 构成一个 block。先计算 block-level confusion counts、balanced accuracy、precision、recall、F1 和 recovery-onset error，再按以下顺序汇总：

1. 在同一 evaluation task 内对三个 training-seed block metrics 取 arithmetic mean；
2. 对同一 source-coverage level，先将每个 evaluation task 在所有 eligible source subsets 下的结果取平均；
3. 最后对 TwoRoom、PushT、Reacher、Cube 四个 tasks 等权。

同时报告每个 source subset 的 task-macro result、每个 evaluation task 的结果、worst-case absolute onset error 和 selected-threshold distribution。14 个 partitions 大量共享 tasks 与 checkpoints，因此全部以 observed cross-task sensitivity points 呈现，不据此计算假设 partitions 相互独立的 p-values 或 confidence intervals。

Evaluation task 只提供其 no-noise ATR reference 以形成 `ATR_rel`；其 recovery labels 与 behavioral outcomes 不参与 threshold selection。P2 prose 只报告 final `ATR+SMPR rule` 的 threshold portability、source-coverage trend、source-composition spread 和 failure cases。Encoder、1-step 与 same-horizon controls 的 incremental analysis集中在 P1。P2 reporting 使用 exact metrics、ranges 和 task names，不使用 inferential adjectives。

正文结果句采用具体结构：先给 source-task 数量，再给 unchanged thresholds 在其余 tasks 上的 task-equal metric，最后给不同 source compositions 的 range 或 worst case。句中不出现 component comparison。

### 6.4 Main display 与 appendix table

正文使用一个两-panel compact dot plot：

- x-axis：`Number of source tasks`，取值 1、2、3；
- panel (a)：`Evaluation-task balanced accuracy`，higher is better；
- panel (b)：`Mean absolute onset error`，lower is better，并在 axis/caption 写明 training-noise-grid unit；
- 每个有方向 source subset 显示为一个轻量 point，共 14 points；每个 coverage level 叠加 task-equal summary marker；
- 不绘制把重叠 partitions 当作独立重复所得的 confidence interval。

Appendix 14-row table 使用固定列：`Source tasks`、`Evaluation tasks`、`ATR threshold`、`SMPR threshold`、`Balanced accuracy`、`Precision / recall`、`Onset error: mean / max`。Task names 明写，不使用 split IDs。Main prose 至少报告每个 coverage level 的 task-equal metrics、composition range 和 worst case，使读者能判断一个、两个、三个 source tasks 分别提供多少 portability。

### 6.5 Versioned outputs 与 reconstruction checks

生成：

```text
paper1/results/cross_task_atr_smpr_all_subsets_v1.csv
paper1/results/cross_task_atr_smpr_all_subsets_params_v1.json
paper1/results/cross_task_atr_smpr_all_subsets_summary_v1.json
paper1/tables/table_cross_task_atr_smpr_all_subsets_v1.tex
assets/paper1_figs/fig_cross_task_atr_smpr_source_coverage_v1.pdf
```

输出 schema 必须显式包含 source-task set、evaluation-task set、source coverage、training seed、thresholds、block metrics 和 aggregation level。其中 `3 source tasks -> 1 evaluation task` slice 必须重建：

- Cube、PushT、Reacher 为 evaluation task 时，`tau_R/tau_M = 0.30/0.90`；
- TwoRoom 为 evaluation task 时，`tau_R/tau_M = 0.20/0.95`；
- task-equal recovery-onset absolute error mean `0.010`、max `0.030`；
- precision/recall 为 `0.904/0.862`；
- 每个 evaluation task 的三个 training seeds 均完整。

上述 slice 是 pipeline regression check，不替代 14-partition primary result。P2 的结果边界限定为 evaluated LeWM family、task-local reference normalization 和当前 Gaussian checkpoint grid。

### 6.6 Training-repeat stability appendix

Appendix 用一句完整 protocol 解释：thresholds 在两个 training repeats 上选择，再原样应用到第三个 repeat，轮换三次。该结果只说明 retraining stability，不作为主 P2，不使用 CAL/TEST seed labels。

## 7. Planner mechanism audit

Planner panel 不增加 training seed，也不提出 training-run population claim。

Reader-facing 首次名称为 `5-step candidate-conditioned planner ACPC (H=5, matching the evaluated planning horizon)`，不得裸写 `H5`。正文保留：

- squared-goal-cost bound 与 certificate validity；
- fixed-pool cost-drift response；
- adaptive positive decision regret response；
- 5-step candidate-conditioned ACPC beyond severity、checkpoint role、1-step ACPC 与 nominal margin；
- first-action RMS 未达到预设 5% reporting criterion 的 negative result。

明确该 panel 使用 specified checkpoints 与 finite candidate budgets；certificate 只适用于 evaluated paired ordered pool；adaptive implication 只在 common proposals 与 elite certificate 逐轮成立时继续；输出不是 closed-loop return。

## 8. P3 — Cross-stressor transfer of the final selective diagnostic

### 8.1 Purpose

P3 只回答 final `Selective ACPC score (ATR+SMPR)` 在 fixed blur/resize 下是否保留 relative checkpoint-ordering utility。它不用于识别 action-specific mechanism，也不用于比较 diagnostic components。

每个 task 的 blur/resize rows 使用 P2 的 `3 source tasks -> 1 evaluation task` slice：由另外三个 Gaussian tasks 选择该 task 唯一对应的 `tau_R,tau_M`。选择 three-source threshold pair 是固定的 maximum-source-coverage rule，不依据 blur/resize outcome 或 14-partition P2 ranking。不得针对 blur/resize 重新选择 threshold。

对 stressor `v`：

```text
ATR_rel^v(theta_rho; theta_0)
  = ATR_v(theta_rho) / (ATR_v(theta_0) + epsilon).
```

因此 P3 是 reference-based relative transfer，不是 standalone endpoint detector。

### 8.2 Component comparison exclusion

Final PDF、referenced tables/figures 与 release-facing summaries 只呈现 final selective rule 的 transfer result。具体要求：

- 不引用或打包 `paper1/tables/table_cross_stressor_robustness_audit.tex`；
- 不展示 `Encoder q90`、`H1 q90`、`Correct-action H8 q90`、destroyed H8 rows、standalone SMPR 与 selective score 的 BA/AUPRC/Spearman 排名表；
- prose 不解释 cross-stressor component ordering；
- limitations 将 P3 的证据范围限定为 final-rule portability，不延伸到 component attribution。

历史 component artifacts 可留在 repository，但不得成为 paper dependency。这样不把 off-axis stressor 的 proxy ranking误写成对 action-specific theory 的检验。

### 8.3 P3 outputs

覆盖 `4 tasks × 3 training seeds × 2 stressors = 24 pairs`，生成：

```text
paper1/results/external_validation/cross_stressor_three_source_thresholds_v1.csv
paper1/results/external_validation/cross_stressor_three_source_thresholds_summary_v1.json
paper1/tables/table_cross_stressor_selective_transfer_v1.tex
paper1/tables/table_cross_stressor_all_pairs_v1.tex
assets/paper1_figs/fig_cross_stressor_selective_transfer_v1.pdf  # optional
```

Main summary 只包含 final selective rule 的 task-equal metrics。Appendix all-pairs table 只保留理解 transfer 所需的字段：task、training seed、stressor、base/endpoint behavior、`ATR_rel`、SMPR、selective-score change、predicted/observed ordering 与 discordance type。

P3 summary metrics 必须从 three-source threshold artifacts 重建，不沿用其他 calibration protocol 的 summary values。若结果变弱，完整报告并收缩 P3 claim，不做 stressor-specific retuning。

P3 只支持 fixed blur/resize severity 下的 relative transfer，不支持 action necessity、absolute stability detection、unseen severity family 或 universal corruption robustness。

## 9. Reader-facing data-separation language

### 9.1 使用具体 data-flow language

`held-out` 不进入 main text、captions、legends 或 referenced tables。所有 data separation 直接写出谁参与选择或 fitting、谁只参与 evaluation：

| 实际含义 | Reader-facing wording |
|---|---|
| Diagnostic scoring 不读取 future | `the future target is unavailable to the diagnostic and used only to evaluate it` |
| P1 一组 trajectory 未参与 Ridge fit | `fit on 15 trajectory groups and predict the remaining group, repeated for all 16 groups` |
| P2 source/evaluation partition | `thresholds chosen on one, two, or three source tasks and applied unchanged to the remaining tasks` |
| Seed sanity 的一个 repeat 未参与 threshold selection | `thresholds chosen on two training repeats and evaluated on the third` |
| Planner regression 的一个 task 未参与 fit | `fit on three tasks and evaluated on the fourth` |
| P3 未使用 blur/resize 调 threshold | `no blur/resize result is used to select thresholds` |

### 9.2 Reader-facing 禁用词

以下 internal labels 不进入 title、abstract、main text、captions 或 referenced tables：

- `CAL`, `TEST`, `E1`, `E2`, `E3`；
- `dev-era`, `frozen replication`, `prospective seed`, `retrospective completeness`；
- `held-out result`, `held-out score`, `held-out row`, `held-out task`, `held-out seed`；
- 无定义的 `H1`, `H5`, `H8`, `joint score`；
- `candidate-shuffled`，除非明确是 cross-trajectory action-sequence shuffle 还是 planner-candidate permutation。

`pre-specified` 只用于确实在执行前固定的 protocol choice；不把内部 audit history 写入科学叙事。

### 9.3 必须增加的 protocol visual

Method figure 或 experiment overview 中加入一条简短 data-flow strip：

```text
paired nominal/probed histories
        -> target-free encoder / 1-step / 8-step responses
        -> P1: future target used only for evaluation
        -> P2: thresholds selected on 1/2/3 source tasks, applied to the other 3/2/1 tasks
        -> P3: three-source-task thresholds applied to blur/resize
```

该 visual 只解释 data access，不增加新 contribution panel。

## 10. Final manuscript structure

1. **Introduction** — encoder invariance 的不足、consistency/collapse tension、future-error/planner/cross-task questions。
2. **Related Work** — latent prediction、control-relevant abstraction、visual robustness diagnostics。
3. **Target-Free Selective ACPC** — ACPC-H、future-error theorem、selective guard、ATR/SMPR、planner consequence。
4. **Experimental Protocol** — four tasks、three training repeats、Gaussian grid、P1 three-feature-set comparison、P2 all-subset source/evaluation partitions、planner panel、P3 no-refit stressor scope。
5. **Gaussian Fragility and Recovery** — one complete four-task sweep figure。
6. **Does action-matched rollout disagreement add future-drift information?** — P1 explanatory display and three-seed result。
7. **Does ACPC connect to planner costs and decisions?** — planner mechanism audit。
8. **How does selective-threshold portability depend on source-task coverage?** — P2 all-subset evaluation。
9. **Does the final selective rule transfer to blur and resize?** — P3 final-rule result。
10. **Limitations and Conclusion** — reference requirement、proxy guard、fixed-pool boundary、closed-loop authority、family/stressor scope。

Cube 始终作为 ordinary fourth task 等权进入 figures/tables；不设置 boundary-case prose。

Appendix 顺序：proofs；ATR/SMPR/proxy definitions；P1 absolute/control details；planner absolute/certificate details；cross-task partition details；training-repeat sanity；local sensitivity；P3 all 24 pairs；qualitative t-SNE。

## 11. Display contract 与 budget

### 11.1 Global visual contract

每个 main-text display 只回答一个 reader question，并满足以下统一规范：

- task order 与 mapping 固定为 TwoRoom `#0072B2`/circle、PushT `#E69F00`/square、Reacher `#009E73`/triangle、Cube `#CC79A7`/diamond；
- 同一 task 内的 training seeds 使用 solid/dashed/dotted line 或 direct numeric labels 区分，不覆盖 task marker mapping，也不引入第二套 rainbow palette；
- pass/fail 或 positive/negative 不只依赖 red/green，必须同时使用 marker shape、line style 或 direct label；
- line plots、dot plots、schematics 优先输出 vector PDF；必须使用 raster 时按最终版面尺寸至少 300 dpi；
- 缩放到最终单栏/双栏宽度后，axis/title/caption text 不小于 8 pt，legend 不小于 7.5 pt；所有 fonts embedded；
- axes 写出 quantity 与 unit；direction 不直观时只用短注释 `higher is better` 或 `lower is better`；
- legend 最多六项，优先 direct labels；不使用代码字段、split IDs、artifact names 或裸 acronym 充当 labels；
- main tables 不超过七个 data columns，不使用 vertical rules，数字按 decimal point 对齐，同一 column 使用一致 precision；
- row/column labels 使用名词短语，不写完整句；解释性内容放在紧邻正文，不塞入 table cells；
- paper-facing tables 不出现 `mode`、`heldout_unit`、`gate_features`、`use_proxy_gap`、`transition_rows_flagged`、`blocks` 或 `shards` 等 implementation columns；必要 provenance 只进入 machine-readable artifacts；
- caption 第一短句说明 display 回答的问题，第二句说明每个 point/bar 的统计单位；main-text caption 控制在 65 个 English words 内，不复述整段 methods；
- caption、legend 和 axis 中统一使用 `Encoder shift`、`1-step ACPC`、`8-step action-matched ACPC`、`Selective ACPC score`、`source tasks`、`evaluation tasks`。

### 11.2 Main-text display slots

| Slot | 内容 | 必须完成的阅读任务 |
|---|---|---|
| Figure 1 | ACPC method + compact data-flow strip | 解释 rollout horizon、action matching、target-free scoring 与三个 experiments 的 data access |
| Figure 2 | Four-task, three-seed Gaussian sweep | 用唯一 full-sweep figure 建立 fragile/recovered checkpoint family |
| Figure 3 | P1 feature-set schematic + three-seed dot plot | 一眼看清共同 target、两个 comparators、proposed feature 与 MAE reduction |
| Figure 4 | Planner mechanism | 区分 deterministic bound、cost/regret increment 与 negative first-action result |
| Figure 5 | P2 source-coverage dot plot | 展示全部 14 partitions 以及 1/2/3 source-task coverage 的 accuracy/onset-error sensitivity |
| Table 1 or compact Figure 6 | P3 final selective-rule transfer | 只展示 24-pair final-rule summary 与 discordance count |

P2 Figure 5 固定为两个横向对齐 panels，共享 `Number of source tasks` x-axis。所有 14 个 source subsets 必须显示；轻量 points 表示 individual directional partitions，较大空心 marker 表示 task-equal coverage summary。Source-subset identity 放 appendix table，不用十四种颜色或十四项 legend。

P1 Figure 3 的 model labels 固定为：`Encoder shift + 1-step ACPC`、`Best 8-step control (zeroed or shuffled actions)`、`8-step ACPC (recorded actions)`。Caption 将第三项与正文定义的 `action-matched` 对应。图内不使用 A/B/C、H1/H8 或百分比公式作为唯一解释；MAE-reduction definition 放 caption 的一个短 clause。

### 11.3 Appendix displays

- P2 14-row source/evaluation partition table；
- compact four-task Gaussian numeric summary；
- P1 absolute/adverse/task × seed/control details；
- planner absolute/certificate details；
- training-repeat threshold sanity；
- local sensitivity one equation/at most one figure；
- P3 all 24 pairs and discordances；
- qualitative t-SNE。

Appendix wide tables 超过七列时使用 landscape 或拆成 protocol/result 两表，不通过缩小到不可读字号解决。Final PDF 不包含 36-row sweep、sampled-pool `K alpha` theorem、repeated endpoint/event-rate figures、multiple JVP tables、theory audit map 或 cross-stressor component-ranking table。

## 12. Execution phases

### Phase A — Seed scope 与 terminology contract

- [ ] Formal seed set assert 为 `{3072,3073,3074}`。
- [ ] 断开 seed3075 与 paper dependency graph、manifests、package 的引用。
- [ ] 建立 reader-facing metric-name constants/caption helpers。
- [ ] 清除 paper-facing internal split/provenance labels。
- [ ] 为 bare `H1/H5/H8/joint` 与全部 reader-facing `held-out` 增加 text audit。

**Gate A:** paper-facing sources 中 excluded seed/provenance/split labels 与 `held-out` 零命中；每个 horizon 首次出现均写明 predicted rollout steps。

### Phase B — Theory 与 metric dictionary

- [ ] 在 ACPC equation 前定义 `H`、action matching 与 aggregation order。
- [ ] 写出 encoder shift、1-step ACPC、8-step ACPC 和 selective score。
- [ ] 加入 selective discriminability 与 collapse caveat。
- [ ] 保留 target-free theorem 和 compact planner consequence。
- [ ] 将 local sensitivity 限定到 appendix。

**Gate B:** 读者不看 appendix 也能回答每个 metric 输入什么、是否 rollout、是否 action-conditioned、是否 theorem object。

### Phase C — P1 generator 与 display

- [ ] 对三种 adjudication schema 实现 explicit adapter。
- [ ] Assert exact P1 estimand、four-task coverage 与三个 seed values。
- [ ] 生成 three-feature-set schematic。
- [ ] 生成 same-horizon comparator first 的 three-seed display。
- [ ] Appendix 生成 absolute MAE 与 all-control table。
- [ ] Caption 写出 MAE-reduction formula 与 15-groups-to-1 protocol。

**Gate C:** 重建 `51.3 ± 3.5%` 和 `55.9 ± 4.7%`；正文不再出现难以解释的 `vs H1` table header。

### Phase D — P2 cross-task rule

- [ ] 固定 pure `ATR_rel + SMPR` rule。
- [ ] 枚举全部 14 个有方向 source/evaluation partitions：4 个 `1->3`、6 个 `2->2`、4 个 `3->1`。
- [ ] Assert 每个 partition 的 tasks disjoint 且 union 等于完整 four-task set；row/block counts 与 source coverage 一致。
- [ ] 对每个 source subset 执行同一 candidate grid 与 lexicographic objective，禁止读取 evaluation-task outcomes。
- [ ] 按 evaluation task -> source coverage -> four-task macro 的固定顺序汇总，不对重叠 partitions 做 independent-sample inference。
- [ ] 生成 versioned CSV/JSON、14-row appendix table 与 two-panel source-coverage figure。
- [ ] 生成独立的 training-repeat appendix artifact。

**Gate D:** 14/14 partitions、28 个 evaluation-task incidences 和三个 coverage levels 全部可追溯；`3->1` slice 重建 expected thresholds/onset/precision/recall；main display 包含全部 14 points 且无 component-baseline rows。

### Phase E — Planner audit

- [ ] 用 `5-step candidate-conditioned planner ACPC` 替换裸 `H5`。
- [ ] 保留 bound/certificate invariants、cost drift、regret 和 negative first-action result。
- [ ] 简化 protocol wording，删除 internal audit narrative。

**Gate E:** theorem object、empirical response 与 non-closed-loop boundary 一一对应。

### Phase F — P3 final-rule-only cross-stressor

- [ ] 每个 task 绑定 P2 中由另外三个 Gaussian tasks 产生的 unique three-source threshold pair。
- [ ] 使用 stressor-specific base reference 计算 `ATR_rel`。
- [ ] Assert 24/24 pairs 与 blur/resize block completeness。
- [ ] 只输出 final selective-score aggregate 与 all-pairs discordances。
- [ ] 从 TeX dependency 与 package 排除 cross-stressor component table。
- [ ] 不针对 stressor 重选 threshold。

**Gate F:** paper-facing P3 outputs 不含 encoder/H1/H8/SMPR component ranking；所有数字可追溯到 P2 three-source threshold artifacts。

### Phase G — Build 与 reader audit

- [ ] Deterministically regenerate all paper-facing assets。
- [ ] 运行 P1/P2/P3、theory、manifest 与 figure-collection tests。
- [ ] Clean build normal PDF、blind PDF 和 fresh source package。
- [ ] `pdftotext` 执行 terminology、excluded-seed、stale-number audits。
- [ ] 逐页检查 overflow、embedded fonts、legend、caption、task/seed labels 与 data-flow clarity。
- [ ] 在最终栏宽、100% zoom、grayscale 和 common color-vision-deficiency preview 下检查所有 main figures。
- [ ] 检查 main table column count、decimal alignment、caption word count 与 row-label length。
- [ ] 让未看代码的读者仅靠 Figure 1 和 P1 display 复述三个 feature sets 的 comparison。

**Gate G:** builds/tests 全通过；所有 main displays 在最终尺寸可读，captions 不依赖 internal experiment vocabulary，P2 的 14 points 和 P1 的两个 comparators 无需查 appendix 即可辨认。

## 13. Automated tests

至少覆盖：

1. formal training seeds 精确为 3072/3073/3074；
2. P1 每 seed 四 tasks，target 为 absolute 8-step future-error drift；
3. P1 A/B/C feature sets 与 code constants 一致；
4. P1 three-seed mean/SD 从 seed-level equal-task values 计算；
5. P1 destroyed controls 全部为 8-step，与 action-matched feature horizon 相同；
6. P1 Ridge pipeline 包含 `StandardScaler`，trajectory group 不跨 fit/evaluation side；
7. P2 features 精确为 `ATR_rel` 和 `SMPR`，candidate grid/objective 与 specification 一致；
8. P2 source subsets 精确为 14 个：coverage counts `4/6/4`，每个 partition 的 source/evaluation tasks disjoint 且 union 为完整 task set；
9. P2 row/block counts 对 `1->3`、`2->2`、`3->1` 分别为 `27/81`、`54/54`、`81/27` rows 和 `3/9`、`6/6`、`9/3` blocks；
10. P2 aggregation 先合并 training seeds、再合并 eligible source subsets、最后 four-task macro；overlapping partitions 不进入独立样本 interval；
11. P2 main figure data 精确包含 14 split-level points，appendix table 精确包含 14 rows；
12. training-repeat sanity artifact 不被 P2 main display 引用；
13. P3 每 task 使用 P2 的 unique three-source threshold pair；
14. P3 精确 24 pairs，无 stressor-specific threshold search；
15. P3 referenced output schema 不含 component-ranking rows；
16. main figures 使用固定 task order/palette/marker mapping，font size、legend count、caption length 与 vector-output checks 通过；
17. main tables 不超过七个 data columns，decimal precision 与 reader-facing labels 通过 lint；
18. `pdftotext` 与 TeX-source audit 对 reader-facing `held-out`、internal split labels 和 bare horizon names 均为零命中；
19. `main.tex` referenced assets 与 release manifest 一致；
20. source package 不含 internal plans、unused component tables 或 excluded-seed dependency。

## 14. Failure rules

- P1 无法从指定 artifacts 重建 exact values：停止 integration，修复 source mapping，不手填 LaTeX。
- P1 same-horizon destroyed comparator 不再保持三 seeds × 四 tasks direction：完整报告并收缩 action-specific claim，不能只保留 1-step comparison。
- P2 的 `3->1` regression slice 与 expected result 不一致：检查 reference normalization、candidate grid、objective order 与 mixed-feature leakage，不手工固定 thresholds。
- P2 的 `1->3` 或 `2->2` results 明显弱于 `3->1`：完整展示 coverage dependence 与 source-composition spread，将结论限定为需要足够 source-task diversity。
- P2 只能在 raw ATR 上成立：删除 numerical cross-task portability claim，保留 descriptive task-local result。
- P3 在 three-source thresholds 下变弱：报告实际 24 pairs，必要时移 appendix，不重调 stressor threshold。
- Local-sensitivity figure 无法 deterministic rebuild：删除 figure，只保留 equation 与 paragraph。
- Planner assertions 失败：暂停 planner claim，先修复 artifact/code mismatch。

## 15. Definition of done

- [ ] Paper-facing evidence只使用 training seeds 3072/3073/3074。
- [ ] Encoder shift、1-step ACPC、8-step ACPC、ATR、SMPR 和 selective score 在首次出现处均有 plain-language definition。
- [ ] `H` 明确表示 autoregressive predicted rollout steps。
- [ ] P1 明确所有 models 预测同一个 8-step future-error-drift target。
- [ ] P1 先报告 same-horizon destroyed-action comparator，再报告 Encoder+1-step comparator。
- [ ] P1 display 写出 feature sets、cross-group prediction procedure、absolute MAE-reduction formula 和三-seed results。
- [ ] 正文不声称“multi-step forecast is inherently more accurate”。
- [ ] P2 枚举 `1->3`、`2->2`、`3->1` 全部 14 个 source/evaluation task partitions，并按 evaluation task 等权汇总。
- [ ] P2 main display 同时呈现 source-coverage trend、source-composition spread、worst case 与全部 14 directional points。
- [ ] P2 只用 exact metrics、ranges、task names 陈述 final `ATR+SMPR rule` 的 threshold portability；reader-facing output 不包含 component comparison。
- [ ] Training-repeat threshold check 只在 appendix。
- [ ] Planner panel 明确是 finite-budget mechanism audit，不是 closed-loop population result。
- [ ] P3 保留 final selective-rule cross-stressor transfer，但完全移除 component comparison。
- [ ] P3 每个 task 固定使用由其余三个 Gaussian tasks 选择的 three-source threshold pair。
- [ ] Cross-stressor component-ranking table 不被引用、不被打包。
- [ ] `held-out`、internal split labels、seed provenance roles 和 bare `H1/H5/H8/joint` 不出现在 reader-facing text。
- [ ] Cube 数据完整保留且无 special-case narrative。
- [ ] Selective discriminability 与 collapse caveat 在主文形式化。
- [ ] 所有 main figures/tables 满足固定 palette、最终尺寸字体、caption、legend、列数、decimal alignment 与 grayscale readability contract。
- [ ] 所有正文数字由 versioned machine-readable artifacts 生成。
- [ ] Normal、blind、fresh-package builds 与 automated audits 全部通过。

最终论文主线应能用一句话表达：

> **Eight-step action-matched ACPC provides target-free information about eight-step future-error drift beyond encoder shift, one-step ACPC, and same-horizon destroyed-action controls; together with a proxy discriminability guard, it yields a reference-normalized selective diagnostic whose portability is evaluated across every nontrivial partition of the four tasks and under fixed blur and resize.**
