# Paper 1 最终统一整改规划：四任务 Family-Calibrated ACPC 理论—诊断闭环

> 日期：2026-07-12
> 基线提交：`e8566ef63ab00cdf73d763f0d521669f57254eb4`
> 状态：`AUTHORIZED_FOUR_TASK_RECONSTRUCTION`
> 范围：仅 Paper 1；不改写 immutable public-v1 protocol 的历史事实
> 最高原则：一个 Paper1、一个主命题、四个任务同一证据等级

## 0. 最终决策

Paper1 不再围绕“ACPC-H8 必须在一个 coarse checkpoint classifier 上击败所有 simple baselines”组织，也不转成 progressive cascade、纯 encoder detector 或 adaptive-CEM 论文。唯一主命题是：

> **ACPC provides an architecture-portable but family-calibrated paired predictive audit for frozen world models: its action-matched rollout radius gives a target-free bound on future-prediction drift, while a diagnostic region calibrated on one training seed can be applied without retuning to held-out seeds and held-out visual stressors within a model family.**

中文：

> **ACPC 是一套数学对象可跨 latent-predictive architecture 复用、数值阈值按 model family 校准的 frozen world-model paired predictive audit。correct-action rollout radius 在不观察真实 future/cost 的审计阶段约束 future-prediction drift；由一个 training seed 冻结的诊断区间，在同一 family 内不调参迁移到其他 training seeds，并从 Gaussian calibration 迁移到 blur/resize。**

全文只为以下三个支柱付费。

### 支柱 P1：理论完备且逐项有实验闭环

- 定义 encoder、one-step、multi-step correct-action paired response；
- 给出 full-horizon prediction-error drift 的 target-free samplewise bound；
- 给出 endpoint cost-drift 的条件式 bound 与 ordered fixed-pool top-1 exact condition；
- 明确 collapse guard、概率空间、不可识别性与 closed-loop claim boundary；
- 四个任务使用独立 future target 审计 bound tightness、non-vacuity、action/time controls 和 decision bridge；
- JVP/finite difference 只解释 composed sensitivity，不冒充 behavior guarantee。

“理论完备”只指对论文实际 claim 的 logical chain 完整；不保留无法数值实例化的宽松 `K alpha` 叙事作为主结论。

### 支柱 P2：同一 family 的 seed-calibrated threshold transfer

- LeWM seed3072 是唯一 CAL；
- 阈值、normalization、quantiles、label rule 和 decision rule 在读取 seeds3073/3074 outcome 前冻结；
- 同一个 LeWM threshold pair 作用于四个 tasks 与两个 held-out training seeds，不按 task、seed 或结果重调；
- 输出是 checkpoint/trajectory-block level 的 stable/fragile screening 与 uncertainty，不把单帧称为确定性的 closed-loop success；
- PLDM 不强行共用 LeWM raw thresholds；它验证同一 mathematical/interface protocol 可实例化，若要报告 PLDM absolute gate，必须用独立的 PLDM-local CAL/TEST split。

### 支柱 P3：Gaussian calibration 到 blur/resize 的 frozen transfer

- calibration 只使用 Gaussian intervention；
- blur 与 resize 的 transform、severity、behavior label、阈值和统计量在 reveal 前冻结；
- Gaussian-frozen LeWM gate 不按 stressor 重调，四任务完整报告 precision、recall、balanced accuracy、AUPRC、selective risk、coverage 和 uncertainty；
- endpoint-only scoring 与 reference-based paired improvement 分开；endpoint gate 在 scoring 时不输入 base diagnostic，但当前 P3 behavior label 仍由 endpoint-vs-base improvement 定义；
- 若 endpoint gate 高 precision 但低 recall，只称 conservative scoring for a pair-derived improvement target，不能写成 absolute stable-region detection；
- relative `Delta S > 0` 可作为第二 estimand，但必须明确需要 reference checkpoint，不能替代 single-checkpoint claim。

### 明确不声称

1. LeWM 与 PLDM/DINO-WM 共享同一 raw numerical threshold；
2. 任意单帧 latent score 决定未来 closed-loop success；
3. ACPC-H8 在所有 coarse BA/AUPRC 上必然胜 encoder/H1；
4. target-free radius 本身证明模型预测正确或 task behavior robust；
5. sampled fixed-pool theorem覆盖 adaptive CEM、replanning 与 feedback；
6. 两个 favorable tasks 可以代表四任务结论。

---

## 1. 为什么 simple baselines 没有推翻 ACPC，但必须保留

已有 E1+E2 coarse checkpoint label 上，encoder/H1/action-destroyed controls 与 correct H8 接近，部分 AUPRC 更高。该结果严格否定的是：

> logged-action H8 q90 是一个普遍优于更便宜 signal 的 global checkpoint classifier。

它不否定 ACPC 的两个不同对象：

1. correct-action full-horizon response 对同一 action support 上 future-prediction drift 的 samplewise certificate；
2. 固定 observation pair 下，不同 candidate actions 可能产生不同 downstream amplification，而 encoder scalar 对所有 candidates 相同。

但 information boundary 不是 empirical victory。为了防止为 ACPC 找有利场景，所有 main comparisons 必须：

- 使用同一 histories、probe draws、candidate pool、goal 和 held-out future；
- 给 simple model 相同 severity、action magnitude、nominal dynamics 与 margin covariates；
- 分别比较 encoder→H1、H1→correct-H、correct-H→destroyed-H controls 的增量；
- 保留 T0 coarse classifier null；
- 四任务完整报告，不允许只展示 TwoRoom/PushT fragile rows。

因此 simple baselines 的角色是 claim-boundary control，而不是论文主 target，也不是可以删除的弱基线。

---

## 2. 四任务统一 contract

TwoRoom、PushT、Reacher、Cube 从 feasibility 到主表使用同一 protocol。任务差异只能存在于 privileged replay adapter，不能存在于 target、feature set、statistical unit 或 Gate。

| contract item | 四任务统一设置 |
|---|---|
| current planner input | 1 个 current observation |
| plan horizon | 5 model steps |
| action block | 5 low-level actions/model step |
| goal offset | 25 low-level steps |
| candidate pool | eval-matched CEM step-0 ordered pool |
| candidate count | feasibility K=8；main K=16 |
| logged horizon | H1 与 H8，使用相同 recorded action support |
| candidate horizon | H1 与 H5，使用相同 planner action support |
| probes | identity、Gaussian 0.02/0.05/0.08；cross-stressor 另行 frozen |
| future target | simulator-replayed independent RGB future，和 prediction 不共享 graph |
| controls | encoder、H1、action-zero、candidate/action-shuffle、time-shuffle |
| independent block | episode/trajectory block |
| nesting | candidate、severity、draw 不算独立样本 |
| primary reporting | per-task、pooled hierarchical、leave-one-task-out 三者同时 |

### 2.1 Task adapters 只能实现同一语义

| task | branch state | goal state | replay API |
|---|---|---|---|
| TwoRoom | proprio | future proprio | exact state reset |
| PushT | state + episode-prefix hidden velocity recovery | future state | exact prefix replay then state snap |
| Reacher | qpos + qvel | future qpos | `set_state(qpos,qvel)`，固定25步open-loop后对future qpos评分 |
| Cube | qpos + qvel | future block pos/quaternion | `set_state(qpos,qvel)` + `set_target_pos`，关闭early termination |

每个 adapter 都必须先通过 logged-action replay parity：

- goal-relevant privileged configuration 与 rendered RGB parity；
- full privileged-state error完整报告；Cube contact qvel warm-start不替代RGB/qpos Gate；
- rendered RGB parity；
- action normalization/inverse transform parity；
- identity prediction/cost/winner parity；
- candidate endpoint variation；true goal-cost在至少75% independent blocks中有非退化variation；
- 所有natural neutral/non-contact blocks保留，不按variation筛掉；
- current observation、goal offset、action block 与真实 `eval.py` 一致。

任一任务 Gate 失败，则四任务 candidate main experiment整体不成立。不得把该任务降成 logged-only 后与其他三项放在同一主表。

### 2.2 已有两任务结果的地位

TwoRoom/PushT seed3073 target-aligned runs只作 DEV provenance：

- 它们证明 runner 与理论 target 可行；
- 它们不能形成“四任务支持”；
- 它们不能用于为 Reacher/Cube 选择 feature、threshold、severity 或 Gate；
- 最终数字必须由四任务 frozen run统一汇总。

---

## 3. 理论对象与数值闭环

令 nominal/probe same-state histories 为 `h, h_tilde`，shared action sequence 为 `a_1:H`：

```text
R_E(h,h_tilde) = ||E(h)-E(h_tilde)||
R_1(h,h_tilde,a_1) = ||F(E(h),a_1)-F(E(h_tilde),a_1)||
R_H(h,h_tilde,a_1:H)
  = sqrt(sum_k alpha_k ||p_k-p_tilde_k||^2), alpha_k=1/H.
```

### Proposition A：encoder action-indistinguishability

固定 observation pair 时，`R_E` 对所有 candidate actions相同。若 downstream gain 随 action 变化，encoder-only scalar 无法区分 candidate-specific vulnerability。该命题说明额外 information 何时可能必要，不证明真实 panel 中该 variation 必然 material。

### Proposition B：depth redundancy

若 `R_H = c R_E + small residual`，或 downstream amplification variation 小于 encoder ordering margin，则 deeper response 不改变 coarse ordering。它解释 simple baseline 何时应当与 ACPC 持平，也是必须被数据检验的 null regime。

### Theorem C：correct-action full-horizon prediction-error drift

令 `p_a, p_tilde_a` 为 nominal/probe branch 在同一 correct action sequence 上的 H-step predictions，`y_a` 为独立 observed/simulator true future，全部使用同一 weighted-stacked L2 norm。reverse triangle inequality 给出：

```text
abs(||p_tilde_a-y_a||_alpha - ||p_a-y_a||_alpha)
  <= ||p_tilde_a-p_a||_alpha
  = R_H(h,h_tilde,a).
```

右侧在 audit time 不需要 `y_a`。这使 ACPC-H 成为 target-free prediction-error-drift certificate。

边界：

- 100% correct-H coverage 是数学 invariant，不作为 empirical win；
- empirical value由 utilization、width、non-vacuity 与对 adverse degradation 的增量决定；
- H1 只 certificate H1 target；
- zero/shuffled/time-shuffled response对应另一 action map；
- encoder 需要额外 operator-gain bound，不能直接替代该 full-horizon statement。

### Corollary D：endpoint planner-cost drift

uniform weights 下：

```text
||p_H-p_tilde_H|| <= sqrt(H) R_H.
```

若 endpoint cost `J(p,g)` 对 prediction 是 `L_J`-Lipschitz，则：

```text
|J(p_H,g)-J(p_tilde_H,g)| <= L_J sqrt(H) R_H.
```

对 normalized embeddings：

- cosine cost可取 `L_J=1`；
- squared L2/MSE cost可用单位范数给出有限常数 bound；
- raw/non-normalized spaces必须显式估计或声明 `L_J` 条件，不能混用常数。

实验逐 candidate 报告 actual cost drift、bound utilization 与 violations。

### Theorem E：ordered fixed-pool exact event

令 nominal winner 为 `j*`，nominal gap `Delta_j`，signed cost drift `delta_j`：

```text
g_j_probe = Delta_j + delta_j - delta_j*.
```

deterministic tie rule 下，所有 competitor 的 `g_j_probe>0` 当且仅当 nominal winner 在该 ordered pool 的 probe branch 仍为 unique winner。absolute-drift sharp slack是保守 corollary，不包装成 cheap predictor。

### Proposition F：behavior non-identifiability

小 `R_H` 可来自稳定且正确，也可来自 stable collapse。内部 cost ordering也不能一般推出 task correctness。因此：

- SMPR/action/temporal/rank guards只作 specified falsification；
- held-out true future验证 predictive correctness/drift；
- closed-loop behavior仍是最终 empirical endpoint；
- 输出用“diagnostic stable region/fragile region”，不写 universal robust certificate。

### 3.1 Theory–evidence map

| theoretical object | 四任务统一 evidence | pass interpretation |
|---|---|---|
| same-state `R_E→R_1→R_H` | paired finite difference + JVP | composed response mechanism |
| Theorem C | independent simulator future | exact validity + tightness，非 behavior proof |
| action specificity | correct vs zero/shuffle/time | correct signal在匹配 T2 上的增量 |
| Corollary D | actual candidate cost drift | radius→cost calibration |
| Theorem E | same ordered pool top-1 | fixed-pool exact event |
| collapse boundary | structural controls + true future | stable-collapse falsification |
| threshold region | CAL seed→held-out seeds/stressors | empirical calibration portability |
| behavior boundary | matched closed-loop eval | empirical association only |

---

## 4. 统一 target 与 fair comparison

### T0：checkpoint stable/fragile screening

CAL 中的 behavior rule保持 public-v1 定义：在每个 task×training-seed sweep内，相对 base-to-best 的 observation-noise recovery达到80%，且 clean drop不超过5pp。T0用于 P2/P3 threshold transfer，不用于证明 action necessity。

### T1：fixed-pool decision

相同 ordered candidate pool 的 cost drift、margin 与 top-1 event。它只支持 sampled-pool decision stability。

### T2a：adverse future-prediction degradation

```text
max(error_probe - error_nominal, 0)
```

target 必须为 action-matched independent true future。它检验 empirical harm/ranking utility。

### T2b：absolute future-prediction error drift

```text
abs(error_probe - error_nominal)
```

它检验 Theorem C 的 tightness/non-vacuity。

### T3：realized candidate quality

同一 state 执行 nominal/probe selected candidate 后的 true goal progress/regret。它是 bounded planner relevance，不是 full closed loop。

### T4：closed-loop behavior

matched initial-state full evaluation。它验证诊断区间与行为的经验关系，不升级成 theorem。

### 4.1 固定 feature sets

```text
M_E:
  severity + encoder response

M_1:
  M_E + correct H1 response

M_H:
  M_1 + correct full-horizon response

M_control:
  M_1 + one destroyed full-horizon response
```

candidate track 给所有模型同样加入：

- candidate action RMS；
- nominal H1/H5 displacement；
- nominal candidate-cost margin；
- encoder×action RMS；
- encoder×nominal H5 displacement。

统计实现固定为 Ridge `alpha=1`、fold 内 median imputation/standardization、leave-one-episode-block-out。不得在 task result reveal 后选择 feature subset。

### 4.2 统一 empirical increment Gate

correct full-horizon signal只有在以下条件下才获得经验增量 claim：

1. 相对 H1 与最佳 destroyed-H control，held-out T2a MAE都降低至少5%；
2. within-history rank提高至少0.05，或多数 independent blocks方向一致且 MAE gate通过；
3. pooled hierarchical result通过，leave-one-task-out不由单一 task驱动；
4. per-task结果全部展示，至少3/4 tasks方向一致；
5. fragile/stable regime在 outcome 前由 CAL response/behavior rule定义，不按 held-out target切片；
6. correct-H T2b theorem violations为0，且 bound width/utilization不是系统性 vacuous。
7. T3只在true-goal-cost有variation的blocks解释rank；neutral blocks保留并计入support coverage。

若只在 TwoRoom/PushT通过，而 Reacher/Cube无增量，结论必须写成“task/regime-dependent conditional increment”，不能写 four-task universal superiority。理论 certificate仍可在四任务成立，但 empirical ranking claim降级。

### 4.3 四任务 base/endpoint MVE reveal

LeWM seeds3073/3074 的 TwoRoom、PushT、Reacher、Cube 使用同一16-block protocol一次性汇总。provenance必须分层：contract `paper1-target-aligned-acpc-four-task-contract-2.2` 在 seed3073 TwoRoom/PushT DEV rows之后、Reacher/Cube target outcome与完整 seed3074 replication之前冻结。因此 seed3073是 mixed DEV/extension evidence，seed3074才是完整 frozen four-task replication。当前 reveal只完成 P1 的 base/endpoint MVE；它不是 P2/P3 的替代，也不把 endpoint floor effect包装成 negative failure。

Primary logged track 的 fragile/base 结果为：

| training seed | target | equal-task mean reduction vs H1 | equal-task mean reduction vs best destroyed-H | per-task Gate |
|---:|---|---:|---:|---:|
| 3073 | absolute future-error drift | 60.8% | 54.8% | 4/4 |
| 3073 | adverse future-error drift | 60.4% | 54.4% | 4/4 |
| 3074 | absolute future-error drift | 51.4% | 47.7% | 4/4 |
| 3074 | adverse future-error drift | 49.6% | 45.7% | 4/4 |

双 seed 合并、按 task 等权且不混合 task scales 后，absolute target 相对 H1 的 reduction为56.5%，task×trajectory-block cluster-bootstrap 95% CI为[51.1%,61.2%]；相对最佳 destroyed-H8为51.9% [45.0%,56.6%]。adverse target对应55.5% [50.1%,60.2%]与50.6% [44.0%,55.3%]。correct H8在57/64个 seed-averaged task×trajectory clusters中同时胜过H1与全部 destroyed controls。该 interval条件于两个 model seeds，不是对训练 seed population 的 CI。

因此，旧 T0 coarse checkpoint classifier 上的 simple-baseline null 仍保留，但它不能再被解释成 ACPC 对匹配目标没有增量：在两个 non-CAL training seeds、四个任务的 fragile/base regime 中，correct-action logged H8 对 independent action-matched held-out future 的增量同时胜过 H1 与最佳 destroyed-H control。该结果支持的是 **target-aligned future-prediction drift**，不是“所有稳定 checkpoint 上 H8 都应优于 H1”。

Theorem C 的 samplewise prediction-error-drift certificate 在两个 seeds、四任务、base/endpoint、logged H8 与 candidate H5 的全部16个 task×seed×role单元中均为零违例。此处零违例证明实现与定理对象一致；bound utilization/tightness仍须与 empirical increment分开报告。

Secondary candidate-H5 bridge 不具有同样的 four-task universal increment：seed3073 的 absolute/adverse Gate均为 TwoRoom、PushT 2/4通过；seed3074 的 absolute为2/4、adverse为1/4。它仍可报告 sampled planner-query 条件结果与 exact certificate，但不得替代 primary logged-future evidence，也不得声称 universal candidate-ranking superiority。

冻结汇总 artifacts：

- `paper1/results/target_aligned_acpc_dev/adjudication_four_task_seed3073_goal25_base_endpoint_v1.json`；
- `paper1/results/target_aligned_acpc_dev/adjudication_four_task_seed3074_goal25_base_endpoint_v1.json`；
- `paper1/results/target_aligned_acpc_dev/meta_four_task_seeds3073_3074_goal25_base_endpoint_v1.json`。

---

## 5. P2：跨 training-seed threshold transfer

### 5.1 Freeze

CAL仅含 LeWM seed3072 的四任务 Gaussian sweep。冻结：

- canonical embedding space；
- H=8 与 uniform horizon weights；
- anchors、draw seeds、quantiles；
- ATR normalization；
- SMPR neighborhood/margin；
- `tau_ATR`、`tau_SMPR` 与 joint rule；
- stable/fragile behavior label；
- missing/timeout policy；
- CI 与 aggregation。

### 5.2 TEST

E1为 LeWM seeds3073/3074 的完整四任务九点 sweep。禁止：

- 按 task/seed调 threshold；
- 读取 behavior后改变 quantile或 normalization；
- 把 evaluation seeds 42/43/44 当独立 training runs；
- 只报告 pooled metric而隐藏 task failure。

主结果：

- pooled BA/AUPRC；
- per-task confusion matrix；
- stable-pass precision与 one-sided upper false-pass CI；
- fragile detection recall；
- coverage；
- recovery-onset grid error；
- leave-one-task-out；
- training-seed block bootstrap。

P2通过标准不是“每一行分类正确”，而是 frozen gate 在两个 held-out training seeds 保持预声明的 safety/accuracy，并且不由单一任务主导。

---

## 6. P3：Gaussian 到 blur/resize 的 frozen transfer

### 6.1 同一四任务 panel

blur/resize必须对 TwoRoom、PushT、Reacher、Cube 使用同一：

- checkpoint roles；
- training seeds；
- episode/evaluation seeds；
- observation-only corruption scope；
- clean goal；
- trajectory count；
- metric code；
- Gaussian-frozen thresholds；
- behavior label与 uncertainty。

任务不再使用不同 native stressor。真实 renderer variation可作为未来扩展，不进入本 Paper1 三支柱主线。

### 6.2 两个 estimands

**Reference-free endpoint score against a pair-derived target**

```text
S_F,v(theta) >= 0
```

使用 Gaussian CAL 的 frozen thresholds，scoring 时只输入 endpoint diagnostic；但评估 label 是 endpoint stressed success 相对 base 是否提升至少5pp且 clean drop不超过5pp。主要关注 false pass、coverage 与 recall。若零/低 false pass但 recall低，只写 conservative endpoint scoring for relative improvement，不能写 absolute stability/collapse detection。

**Paired within-family improvement**

```text
Delta S_F,v(endpoint;base) > 0
```

同一个 zero threshold用于 blur和resize。报告 continuous association、choice accuracy与 regret；明确它需要 base reference。

两者不得混合成一个 headline number。

### 6.3 Cross-stressor Gate

- blur 与 resize各自完整报告，不能只给合并值；
- 四任务完整报告，不能删除 Cube 或其他反例；
- no-retuning由 config hash验证；
- block bootstrap按 task×training-seed，两个stressors留在同一 block；
- leave-one-task-out 与 leave-one-seed-out；
- endpoint-gate claim要求 selective false-pass、coverage与exact upper bound完整报告，并明确 outcome 是 pair-derived improvement；
- paired claim要求 `Delta S>0` 在两 stressors方向一致，并报告 neutral 5pp boundary cases；
- 只有一个 severity时称 fixed-strength boundary test，不称 universal corruption transfer。

---

## 7. Cross-architecture scope

### LeWM

Primary family：3 independent training seeds×4 tasks，承担 P2、P3 与四任务 target-aligned mechanism evidence。

### PLDM

Secondary architecture：同一四任务 mathematical/interface protocol，不默认共享 LeWM thresholds。当前若只有一个 independent training family：

- 可支持 interface portability；
- 可支持四任务 descriptive direction与 architecture-local score construction；
- 不支持 cross-seed calibration portability；
- 不把 evaluation seeds冒充 training seeds。

若 PLDM 有可冻结的 CAL/TEST partition，则独立拟合 PLDM-local thresholds并按同一统计 contract验证；否则不报告强 absolute-transfer claim。

### DINO-WM

Optional external validation。只有公开 checkpoint、preprocessing/action/replay parity通过后执行；至少两个 compatible tasks才进入正文，单 task只放 appendix。它加分但不是 P1–P3 成立的前提。

---

## 8. 执行顺序

### Phase A：冻结四任务 contract

1. 写入 machine-readable protocol 与 schema；
2. 固定四任务相同 targets/features/Gates；
3. 记录已有 TwoRoom/PushT 为 DEV，不读取尚未统一汇总的 held-out metrics；
4. hash protocol。

### Phase B：四任务 replay adapters

1. 保留 TwoRoom/PushT adapters；
2. 实现 Reacher `qpos/qvel + target_qpos` adapter；
3. 实现 Cube `qpos/qvel + target block pose` adapter；
4. 添加 deterministic replay、identity、normalization、render parity tests；
5. 四任务各跑4-block feasibility。

### Phase C：统一 target-aligned experiment

1. 四任务相同 base/onset/endpoint roles；
2. 四任务相同 blocks/K/severities/draws；
3. 同时生成 logged H1/H8 与 candidate H1/H5；
4. 一次性统一汇总后才 reveal；
5. 输出 per-task、pooled、leave-one-task-out 和 counterexamples。

### Phase D：P2 seed transfer

复核 seed3072 CAL hash，重建 seeds3073/3074 E1，生成四任务 threshold-transfer主表与 uncertainty。

### Phase E：P3 stressor transfer

用同一 frozen gate重建四任务 blur/resize absolute与paired表；缺失的 behavior rows只按冻结 manifest补跑。

### Phase F：paper rewrite

正文压缩为：

1. problem与三支柱；
2. ACPC objects、exact bound与claim boundary；
3. four-task protocol；
4. P2 cross-seed result；
5. P3 cross-stressor result；
6. four-task target-aligned theory evidence；
7. architecture portability与limitations。

旧 loose union-bound、过多 composite controls、无数替代故事移至 appendix或删除。正文只保留一条 thesis。

### Phase G：验证与发布

- unit/integration tests；
- artifact/schema/hash checks；
- LaTeX build与claim lint；
- Paper1-only diff audit；
- 用户要求后 commit并推送两个 remote。

---

## 9. 停止/降级规则

- 任一 task replay parity失败：不生成四任务 candidate main claim；
- correct-H 对匹配 T2b有 theorem violation：先判 implementation/metric错误；
- 四任务同构 experiment中只有两任务有 empirical increment：保留 conditional/regime result，不写 universal advantage；
- seed transfer依赖 task-specific retuning：P2失败；
- blur/resize依赖 stressor-specific threshold：P3失败；
- endpoint gate false-pass高：不能称 conservative cross-stressor improvement screen；
- PLDM无 independent training seeds：只称 interface portability；
- true future与model prediction共享 computation graph：T2无效；
- behavior relation只来自 pooled rows且 leave-one-task-out不稳：降级；
- 任何 unfavorable task、timeout、missing row都必须保留。

---

## 10. Reviewer attack table

| reviewer attack | protocol answer |
|---|---|
| simple encoder already works | T0如实保留；ACPC额外 claim是 correct-action full-horizon certificate与条件信息，不靠换名 |
| post-hoc target switching | 三支柱、T0/T2/T4和四任务 Gate在剩余 runs前冻结并hash |
| rollout predicts rollout | T2使用independent simulator RGB future |
| only TwoRoom/PushT favorable | 四任务完全同构，per-task与leave-one-task-out强制报告 |
| threshold overfit to one seed | seed3072-only CAL，seeds3073/3074 read-only TEST |
| corruption-specific tuning | Gaussian-only CAL，blur/resize共用 frozen thresholds |
| cross-model threshold failure | claim本来是method portability、family-local calibration |
| stable but wrong | SMPR/structural controls + true future + closed-loop T4 |
| q90 does not instantiate theorem tail | q90只作empirical diagnostic threshold；samplewise Theorem C与pool exact event分开 |
| fixed pool is not adaptive CEM | 明确限定ordered sampled pool，不扩张 claim |
| a single input cannot prove collapse | 输出block/episode-level uncertainty，不做确定性单帧behavior标签 |

---

## 11. 现实分量判断

| 完成度 | 预估 |
|---|---:|
| 旧 global gate + simple-baseline null | 4.5–5.5 |
| P1理论正确但仅两任务 external target | 5.3–6.0 |
| P1四任务闭环 + P2 held-out seed transfer | 6.0–6.6 |
| 再完成 P3 Gaussian→blur/resize frozen transfer，四任务/seed deletion稳定 | 6.3–7.0 |
| PLDM独立family calibration或至少2-task DINO-WM外部复现 | 6.6–7.2 |

这不是分数承诺。达到可信6–7的必要条件是：三支柱都由四任务同构证据支撑、negative results不隐藏、绝对与相对用途不混合、理论 claim不超过数值闭环。

---

## 12. 当前下一步

已完成：

1. 四任务 machine-readable freeze与hash；
2. Reacher/Cube replay adapter、tests及四任务 parity Gate；
3. seeds3073/3074 四任务 base/endpoint 16-block MVE；
4. primary logged与secondary candidate track分离汇总；
5. 两个 non-CAL seeds 的 logged fragile/base Gate均为4/4，其中seed3074是完整 frozen replication；全部理论 certificate为零违例；
6. P1 cluster-bootstrap、P2 task×training-seed bootstrap/deletion与P3 frozen endpoint/paired审计已生成；
7. 三支柱 machine-readable bundle和三张正文主表已生成；P3 endpoint gate另报告7/24 coverage、0/7 observed false passes、单侧95% exact selective-risk upper bound 0.348及12-block bootstrap，并明确其 outcome 是 pair-derived improvement、不是 absolute stability；
8. P1→P2→P3正文已完成重构，T0 null、endpoint range restriction、candidate bridge task-dependent failures、PLDM raw-threshold failure均保留；
9. manifest/consistency checker已绑定新bundle、表格、provenance与claim boundaries；相关tests、LaTeX build、claim lint和PDF布局检查均通过。

剩余发布步骤：

1. 完成最终 Paper1-only diff audit并给出严格审稿评分；
2. 用户确认发布状态后再commit/push两个remote。

DINO-WM checkpoint下载、任何新训练、commit/push仍按用户单独授权边界处理。
