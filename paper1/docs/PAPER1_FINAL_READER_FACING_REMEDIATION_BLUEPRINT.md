# Paper1 Local Geometry → ACPC 专项最终整改蓝图

状态：**FINAL — focused execution specification**

本文件只规划一项整改：恢复 local representation geometry 的直观证据，并用它清楚、严谨地引出 ACPC、ATR 与 SMPR。除此之外，当前论文的 Abstract、Related Work、其他 experiments、tables、claims 与六幅既有 figures 均不属于本文件的整改范围。

事实基线仅包括当前 branch 的 `paper1/main.tex`、当前 machine-readable artifacts、`tools/paper1_selective_contraction.py` 与 `assets/paper1_figs/fig_acpc_basin_tsne_point_counts.json`。历史 plans、旧 PDFs 或旧 commits 只能帮助理解叙事，不得直接恢复未经当前 artifacts 核验的 definition、number、control 或 claim。

## 1. 整改目标与边界

### 1.1 唯一目标

让首次阅读者顺畅理解下面这条链：

```text
same-state visual perturbation
  -> local representation spread
  -> sampled clouds may reach nearby clean-state spacing
  -> local geometry is intuitive but not control-facing
  -> shared-action full-rollout ACPC
  -> ATR upper-tail radius + SMPR proxy-separation guard
  -> downstream validation already present elsewhere in the paper
```

整改完成后，读者必须能够回答：

1. `r/NN`、`r < NN` 与 `disjoint` 分别测什么；
2. 多少 sampled states 达到 local spacing、仍在 spacing 内但未完全分离、或已经 fully disjoint；
3. 为什么这些直观 local measures 仍不足；
4. ACPC 相比 local endpoint geometry 控制了什么；
5. ATR 与 SMPR 如何把 radius–margin intuition 转换为 checkpoint diagnostic。

### 1.2 明确不做的内容

本专项不：

- 重写 Abstract、Related Work、Discussion 或其他实验结论；
- 改动现有 Gaussian sweep、future-error、planner、cross-task、cross-stressor 或 Gaussian-sensitivity figures；
- 改动现有 tables；
- 重新训练模型或改变任何 estimand；
- 把 local PushT audit 扩写为 four-task evidence；
- 把 t-SNE distance、area 或 overlap 当作 quantitative evidence；
- 把 nearest-clean spacing 写成 semantic boundary；
- 将 local `r/NN` 或 disjoint counts 直接并入 ATR–SMPR score。

## 2. Local geometry 的最终定义

### 2.1 Sampled radius 与 nearest-clean spacing

在 representation space `X` 中，令 `x_i,0^X` 是 clean anchor `i`，`x_i,m^X` 是同一状态的第 `m` 个 visually perturbed view。定义 sampled perturbation radius：

```text
r_i^X = max_m ||x_i,m^X - x_i,0^X||_2.
```

定义该 clean anchor 到其他 clean anchors 的最近距离：

```text
n_i^X = min_{j != i} ||x_i,0^X - x_j,0^X||_2.
```

Local radius–spacing ratio 为：

```text
q_i^X = r_i^X / n_i^X.
```

解释：

- `q_i < 1`：sampled visual radius 小于 nearest clean-center spacing；
- `q_i >= 1`：sampled visual radius 已达到或超过 nearest clean-center spacing。

这只表示 sampled local geometry，不表示 perturbation 已跨越 task-semantic boundary。

### 2.2 Sampled-cloud disjointness

对两个 sampled clouds `i,j`，若

```text
||x_i,0^X - x_j,0^X||_2 > r_i^X + r_j^X,
```

则它们的 enclosing balls 在当前 sampled representation geometry 下分离。Anchor `i` 只有在该条件对所有 `j != i` 都成立时才记为 fully disjoint。

`Disjoint sampled clouds (%)` 是 fully-disjoint anchors 占全部 sampled anchors 的比例。

### 2.3 三个互斥 state categories

为直接回答“多少达到邻域间距、多少仍在邻域内、多少完全分离”，每个 anchor 划入下面三个互斥类别之一：

```text
Reaches/exceeds local spacing:
    r_i >= n_i

Within local spacing, not fully disjoint:
    r_i < n_i, but some j has d_ij <= r_i + r_j

Fully disjoint:
    every j != i satisfies d_ij > r_i + r_j
```

三类 counts 之和等于 sampled anchors 数。`Fully disjoint` 是比 `r_i < n_i` 更严格的条件；第二类存在是因为 neighbor cloud 自身也有非零 radius。

Paper-facing label 使用：

- `Reaches/exceeds spacing`；
- `Within spacing, not disjoint`；
- `Fully disjoint`。

禁止使用 `semantic crossover`、`state confusion` 或 `true neighborhood boundary`。

### 2.4 两个 representation spaces

Local audit 只比较：

- **Encoder**：history 经 encoder 后的 representation；
- **After eight rollout steps**：同一 anchor 经八个 autoregressive prediction steps 后的 final representation。

正文与图中不使用裸 `H8`。Local endpoint displacement 不是 full-rollout ACPC；若 final-step displacement 为 `r_H`、final weight 为 `alpha_H > 0`，仅有：

```text
sqrt(alpha_H) * r_H <= ACPC_H.
```

## 3. 为什么 local geometry 不够

Local geometry 是必要的直观入口，但不能作为最终 control-facing diagnostic。正文必须明确给出以下六点：

1. **Neighbor meaning is uncontrolled.** Learned-space nearest neighbor 不一定是 task-relevant different state，也不是 semantic label。
2. **State and action effects can mix.** 不同 clean rollout centers 通常来自各自的 recorded action sequences，因此 center distance 可能同时包含 state 与 action-sequence differences。
3. **Endpoint observation is incomplete.** Encoder output 与 final eight-step endpoint 看不到 displacement 在完整 predicted trajectory 中何时扩大、收缩或旋转。
4. **Scale and sampling matter.** `r_i` 是 sampled maximum，`n_i` 依赖 local anchor density；数值受 perturbation draws、anchor coverage、task 与 representation scale 影响。
5. **No direct downstream object.** Local overlap risk 本身不提供与 common-future error drift 或 candidate-cost movement 的 samplewise relation。
6. **Small radius can be degenerate.** Constant representation 可以令所有 radii 接近零，因此 contraction 本身不等于 selective consistency。

不得把这些不足简写为“encoder geometry ignores actions”，因为 audit 还包含 eight-step rollout endpoint。准确结论是：endpoint geometry 展示了 action-conditioned computation 后的局部现象，但没有同时控制 shared actions、complete rollout、task-proxy separation 与 checkpoint aggregation。

## 4. Local geometry → ACPC → ATR/SMPR 的最终过渡

### 4.1 Local geometry 到 ACPC

ACPC 比较同一 underlying history 的 clean/probed views，让两条 branches 使用完全相同的 recorded or candidate action sequence，并比较完整 weighted predicted rollout。

因此 ACPC 解决 local audit 中三个核心控制问题：

- same history，而不是任意 learned-space neighbor；
- same action sequence，而不是混合不同 actions 的 rollout centers；
- complete predicted rollout，而不是只看 encoder 或 final endpoint。

正文必须表达下面的逻辑；允许按版面润色，但不能删除因果连接：

> The local analysis reveals whether visual perturbations are large relative to nearby clean representations, but it is not yet a control-facing diagnostic. Its nearest neighbor need not represent a task-relevant state difference, its scale depends on local sampling density, and its endpoint view does not isolate visual disagreement along a common action-conditioned rollout. We therefore compare the clean and perturbed views of the same history under exactly the same action sequence and measure their disagreement throughout the predicted rollout. This paired quantity is ACPC.

### 4.2 ACPC 到 ATR/SMPR

Pairwise ACPC 仍不能单独代表一个 checkpoint，也不能排除 constant-representation collapse：

- ATR 对 normalized same-state ACPC 先在 anchor 内汇总 perturbation draws，再在 anchors 上取 upper quantile；
- SMPR 检查 declared proxy-different trajectories 是否仍在 same-state ATR tube 加 margin 之外。

正文使用：

> ACPC resolves the action-matching and rollout questions, but a pairwise distance alone does not summarize a checkpoint and can still be made small by representation collapse. ATR therefore summarizes its normalized upper tail, while SMPR checks whether proxy-different trajectories remain outside the resulting same-state tube.

### 4.3 Local disjoint 与 SMPR 不得混同

| Local geometry | ATR/SMPR diagnostic |
|---|---|
| Sampled maximum radius | Mean over draws, then upper quantile over anchors |
| Nearest clean anchor in learned space | Fixed eligible neighbor from task-coordinate proxy |
| Encoder or final-step representation | Complete shared-action weighted rollout |
| Nearest-clean spacing | Clean-transition normalization |
| Symmetric `d_ij > r_i + r_j` | One-sided `D_i^diff > ATR^raw + delta` |
| Representative descriptive audit | Checkpoint-level operational diagnostic |

正文不能写“SMPR is the disjoint metric at rollout level”，也不能把 local ratios 加入 selective score。

## 5. Verified representative audit

### 5.1 Frozen scope

- Task：PushT；
- Model：LeWM；
- Training run：3072；
- Conditions：unaugmented checkpoint 与 full-sequence Gaussian-augmentation checkpoint (`stdmax = 0.08`)；
- 128 sampled states；
- 每个 state：1 clean view + 18 perturbation views；
- probe standard deviations：0.01、0.04、0.08，各六个 draws；
- rollout：eight autoregressive steps；
- quantitative statistics：original high-dimensional representations。

### 5.2 High-dimensional summary

| Condition and space | Median `r/NN` | `r < NN` | Fully disjoint |
|---|---:|---:|---:|
| No augmentation · Encoder | 1.41 | 22/128 = 17.2% | 0/128 = 0% |
| No augmentation · After eight rollout steps | 1.86 | 7/128 = 5.5% | 0/128 = 0% |
| Gaussian augmentation · Encoder | 0.10 | 125/128 = 97.7% | 122/128 = 95.3% |
| Gaussian augmentation · After eight rollout steps | 0.19 | 122/128 = 95.3% | 108/128 = 84.4% |

Full-precision median ratios：1.4079947、1.8627083、0.0957874、0.1936060。

### 5.3 Three-category state counts

| Condition and space | Reaches/exceeds spacing | Within spacing, not disjoint | Fully disjoint |
|---|---:|---:|---:|
| No augmentation · Encoder | 106/128 = 82.8% | 22/128 = 17.2% | 0% |
| No augmentation · After eight rollout steps | 121/128 = 94.5% | 7/128 = 5.5% | 0% |
| Gaussian augmentation · Encoder | 3/128 = 2.3% | 3/128 = 2.3% | 122/128 = 95.3% |
| Gaussian augmentation · After eight rollout steps | 6/128 = 4.7% | 14/128 = 10.9% | 108/128 = 84.4% |

所有 medians、fractions 与 counts 在执行前必须由 `fig_acpc_basin_tsne_point_counts.json` 和生成代码重新核对；不允许在 plotting script 中手写结果。

## 6. 新 main-text composite figure

### 6.1 设计原则

新图复用当前 t-SNE figure 清楚的 state-cloud visual grammar，但生成独立 asset，不覆盖旧 PNG。它把两种 evidence 明确分层：

- t-SNE state circles/envelopes：qualitative illustration；
- `r/NN`、`r<NN`、three-category counts、disjoint：high-dimensional quantitative evidence。

新图不显示 ATR/SMPR 数字；ATR/SMPR 属于下一层 operational diagnostic，不应与 local audit annotations 混在同一 panel。

### 6.2 Layout

采用 2×2 full-width layout：

| | Encoder | After eight rollout steps |
|---|---|---|
| No augmentation | panel (a) | panel (b) |
| Gaussian augmentation | panel (c) | panel (d) |

每个 panel 包含：

1. 灰色 background clean states/views；
2. 彩色 selected clean anchors；
3. 同色 perturbation views 与 qualitative envelopes；
4. 一个明确标为 `High-dimensional audit` 的 callout：
   - median `r/NN`；
   - `r < NN` count/percentage；
   - fully-disjoint count/percentage；
5. 一条三段式 state-category strip，依次表示：
   - reaches/exceeds spacing；
   - within spacing, not disjoint；
   - fully disjoint。

Category strip 使用 colorblind-safe colors，并同时写 counts，不能只依赖颜色。每个 panel 的三类 counts 必须相加为 128。

### 6.3 Paper-facing interpretation

读图顺序应当是：

1. 先从 state circles 看到 no-augmentation 下 visual clouds 更扩散；
2. 再从 high-D callout 确认 median `r/NN` 大于 1 或显著下降；
3. 再从 category strip 看到达到 local spacing 与 fully-disjoint states 的比例如何变化；
4. 最后由 caption/正文说明这种 geometry 仍不能控制 task meaning、shared actions 和 complete rollout，因此引出 ACPC。

### 6.4 Caption contract

Caption 必须说明：

- representative PushT mechanism audit；
- checkpoint pair、training run、128 states 与 18 perturbation views；
- rows/columns 的确切含义；
- t-SNE 只用于 qualitative visualization；
- 所有 displayed metrics/counts 在 original high-dimensional space 计算；
- `r >= NN` 表示达到 nearest-clean spacing，不表示 semantic crossover；
- local geometry 的三个局限：neighbor meaning、action matching、complete rollout；
- 这些局限 motivate ACPC。

建议 caption 收束句：

> The visualization shows the sampled state clouds, whereas all ratios and category counts are computed in the original high-dimensional representations. This local audit exposes visual spread relative to nearby clean anchors, but it does not control the neighbor's task meaning, the action sequence, or disagreement over the complete predicted rollout; these limitations motivate ACPC.

## 7. Manuscript integration

### 7.1 Minimal Introduction bridge

只在 Introduction 的 problem-to-method transition 中增加一句短 roadmap，说明论文先展示 local geometry，再通过 ACPC/ATR/SMPR 进行 controlled diagnostic。不得借本专项重写整个 Introduction。

### 7.2 Theory insertion

在 ACPC definition 之前增加一个 focused local-geometry subsection：

1. 定义 `r_i`、`n_i`、`r_i/n_i` 与 fully-disjoint condition；
2. 定义三个 mutually exclusive state categories；
3. 解释 encoder 与 representation after eight rollout steps；
4. 不报告 empirical numbers；
5. 给出 Section 3 的六项 limitations；
6. 使用 Section 4.1 的 bridge 自然引出 ACPC；
7. 在 ATR/SMPR 首次出现处加入 Section 4.2–4.3 的关系说明。

除为形成这条逻辑链所需的最小移动外，不重写现有 ACPC、ATR、SMPR、Propositions 或 calibration results。

### 7.3 Experiment insertion

在 Evaluation setup 后、现有 detailed empirical claims 前增加 focused subsection：

> **Local visual geometry before and after eight rollout steps**

该 subsection：

- 先定义 representative audit scope；
- 引用新 composite figure；
- 报告 Section 5 的 high-D summaries 与 state categories；
- 只得出 representative local-geometry conclusion；
- 以“为什么 local geometry 不够”收束并指回 ACPC/ATR/SMPR。

### 7.4 Retire the old Appendix t-SNE display

从 `main.tex` 删除当前 `Qualitative Neighborhood Visualization` subsection/section 及其 `fig_acpc_basin_tsne.png` figure block，因为新 main-text composite 已同时提供 qualitative state clouds 与 high-D quantitative evidence。

处理规则：

- 不物理删除 `assets/paper1_figs/fig_acpc_basin_tsne.png`；
- 保留其 JSON、生成代码和 PNG 作为 provenance artifacts；
- 旧 PNG 不再被 `main.tex` 引用；
- 旧 PNG 不进入最终 submission source package；
- 删除或更新所有指向旧 Appendix figure/section 的 cross-references；
- 不保留重复的 appendix t-SNE explanation。

## 8. Existing-figure freeze

除被新 composite 替代并从 manuscript 退场的 Appendix t-SNE 外，当前六幅 figures 全部冻结：

- `fig_full_sweep_diagnostics.pdf`；
- `fig_future_drift_three_seed_v1.pdf`；
- `fig_acpc_planner_evidence.pdf`；
- `fig_cross_task_atr_smpr_source_coverage_v1.pdf`；
- `fig_cross_stressor_selective_transfer_v1.pdf`；
- `fig_gaussian_sensitivity_main.png`。

不得改变这六个 assets 的 data、layout、axis、scale、legend、color、annotation、caption 或 displayed statistics。执行前后记录并核对 SHA-256，同时比较 `main.tex` 中对应 figure blocks；自动 figure renumbering 只通过稳定 `\label`/`\Cref` 处理。

## 9. Files and reproducibility

### 9.1 Authoritative inputs

- `tools/paper1_selective_contraction.py`；
- `assets/paper1_figs/fig_acpc_basin_tsne_point_counts.json`；
- 当前可复现的 feature computation/cache path；
- 当前 `paper1/main.tex`。

### 9.2 New outputs

建议新增：

- `tools/paper1_local_geometry_highd_figure.py`；
- `assets/paper1_figs/fig_local_geometry_highd_audit.pdf`。

新脚本必须：

1. 从 machine-readable source/recomputed features 读取数据；
2. 验证 task、run、checkpoint pair、128 states、19 views/state 与 eight-step rollout；
3. 重算并验证 medians、`r<NN`、disjoint 与 category counts；
4. 从同一 state/view points 构建 qualitative t-SNE panels；
5. 不从 t-SNE coordinates 计算任何 quantitative statistic；
6. 输出 vector PDF；
7. 不修改任何现有 figure asset。

## 10. Citation and provenance contract

### 10.1 Required new citation

新 main-text figure 使用 t-SNE，因此在正文首次介绍 t-SNE visualization 或新 figure caption 中引用原始方法论文：

```text
van der Maaten, Laurens and Hinton, Geoffrey.
Visualizing Data using t-SNE.
Journal of Machine Learning Research, 9(86):2579--2605, 2008.
```

建议 BibTeX key：`vandermaaten2008tsne`。执行时从 JMLR 官方 bibliographic record 建立 `references.bib` entry，并检查不存在同文献的其他 key 后再加入。

### 10.2 Definitions that do not require external attribution

下列 quantities 是本文为 representative audit 明确定义的 descriptive objects，不得通过无关 citation 暗示它们是既有标准指标：

- sampled perturbation radius `r_i`；
- nearest-clean spacing `n_i`；
- median `r/NN`；
- `r < NN` fraction；
- enclosing-ball disjointness；
- three-category state partition。

正文应使用 `we define`、`we report` 或 `in this audit`，而不是 `the standard r/NN metric`。

### 10.3 Existing citations that may be reused

Constant-representation failure 是一个自包含 counterexample，不要求新增 citation。如果正文进一步写成一般性的 representation-collapse literature statement，可复用当前 bibliography 中已有的 `jing2022dimcollapse`、`bardes2022vicreg` 等相关来源，但必须确认 citation 直接支持该句，不能为了增加文献数量而堆叠引用。

Nearest-neighbor OOD、manifold learning 或 metric-learning papers 与本文的 sampled `r/NN` definition 不具有直接来源关系，除非正文新增了由这些论文明确支持的独立 claim，否则不加入。

### 10.4 Citation audit

执行结束时检查：

1. t-SNE 首次出现处有原始方法 citation；
2. figure caption/prose 不暗示 t-SNE distances 是 high-dimensional metric evidence；
3. local audit definitions 明确属于本文；
4. 新 reference entry 无 duplicate key/duplicate paper；
5. `references.bib` 中无未引用的专项新增条目；
6. normal/blind builds 无 undefined citation。

## 11. Execution order

1. 冻结并记录六幅既有 figure hashes/blocks；
2. 从 current artifacts 重算并核验 Section 5 全部 statistics；
3. 编写独立 plotting script，生成新 2×2 t-SNE/high-D composite；
4. 在 theory 中加入 local definitions、limitations 与 ACPC bridge；
5. 在 experiments 中加入 focused local-geometry subsection 和新图；
6. 加入 ATR/SMPR 与 local geometry 的非等价说明；
7. 从 manuscript 移除旧 Appendix t-SNE section/figure/reference；
8. 编译 normal/blind PDFs；
9. 复核数字、cross-references、figure hashes 与 submission dependency graph。

## 12. Definition of done

- [ ] 新文中 `r/NN`、`r<NN`、disjoint 和三类 state categories 均有定义；
- [ ] 三类 counts 对每个 panel 都相加为 128；
- [ ] 新 figure 同时提供直观 state clouds 与 high-D quantitative audit；
- [ ] 新 figure 不显示 ATR/SMPR 数字；
- [ ] 所有 quantitative values 来自 original high-dimensional representations；
- [ ] t-SNE 仅作 qualitative visualization；
- [ ] t-SNE 首次出现处引用 van der Maaten and Hinton (2008) 原始论文；
- [ ] `r/NN`、`r<NN`、disjoint 与 state categories 明确写成本文 audit definitions，不伪装成标准外部指标；
- [ ] 未为 nearest-neighbor geometry 添加不直接支持正文 claim 的文献；
- [ ] `r >= NN` 未被写成 semantic crossover；
- [ ] Local geometry 的六项不足完整且自然引出 ACPC；
- [ ] ACPC 到 ATR/SMPR 的必要性解释清楚；
- [ ] Local disjoint 未与 SMPR 混同；
- [ ] 旧 Appendix t-SNE 不再被 manuscript 引用，但 provenance artifacts 保留；
- [ ] 其余六幅 figures 与 captions 完全未改；
- [ ] 无 undefined references/citations；
- [ ] normal/blind PDFs build 成功；
- [ ] 本专项之外无 manuscript 或 artifact 变化。
