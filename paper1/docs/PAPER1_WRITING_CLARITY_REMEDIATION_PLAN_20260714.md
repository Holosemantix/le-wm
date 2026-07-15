# Paper1 写作清晰度整改规划 — 2026-07-14

**范围：** `paper1/main.tex` 全文文字 + `paper1/tables/*.tex`（表可改）。**不改图、不重画图**；图的问题与整改建议单列于 §6，待文字整改完成后作为交付物再次确认。
**硬约束：** 不改变任何实验数字、统计口径与 claim 语义；所有新增解释句必须有 repo 内依据（协议 JSON、脚本、docs），依据在本文标注。`main_blind.tex` 是 `\def\blindsubmission{1}\input{main.tex}` wrapper，正文改动自动生效，无需单独整改。
**与既有约定的衔接：** `docs/PAPER1_FINAL_SCIENTIFIC_REMEDIATION_EXECUTION_PLAN_20260714.md` §11 已定的 caption ≤65 words、legend ≤6 项、table ≤7 data columns 等规范全部沿用；该文档中 "8-step action-matched ACPC" 与正文现用 "recorded-action eight-step ACPC" 为同义，本次统一为 **recorded-action**（读者更易懂），文档层面的 "action-matched" 仅作内部别名。

---

## 1. 全局诊断：为什么难读

通读全文后，可将可读性问题归为 7 类根因。逐节清单（§3）中每条问题都标注根因编号。

**R1 — 概念在使用点未定义（指代悬空）。**
术语首次出现时既无定义也无指向：anchor（L336 直接说 "n is the number of logged anchors"，全文从未定义 anchor 是什么）、planner audit（L269）、task–run cell（L549）、identity probes（L629）、evaluation branches（L731）、directional partitions（L129，正文直到 appendix L1016 才解释 4+6+4=14）、first-action RMS（L553）、nominal top-1 margin（L553）、candidate-conditioned（L553）。读者（甚至作者本人）无法从使用点还原含义——这正是你举的例 2 的根因。

**R2 — 关键常数无动机说明（magic numbers）。**
eight-step（H=8）、five-step（H=5）、q90、q35 邻域、margin δ=0.10、评估噪声 σ=0.08、成功率准则的 80% 与 5pp、blur k=15、resize 0.25。全部只给数值不给理由。其中 H=8/H=5/q90 在 repo 内**有现成依据**可写进正文（见 §2.3），其余至少应标注 "protocol constant, fixed a priori"。这是你举的例 1（为什么 8 步）的根因。

**R3 — 长名词链堆叠，一句塞多个对象。**
典型如 L553 一句并列 3 个 targets + 4 个 covariates；abstract L105 的 "oracle best-of-three same-horizon destroyed-action control that disrupts the recorded-action alignment"（7 个修饰词的名词链）。应命名一次、复用短名（§2.2 命名方案）。

**R4 — 定义与使用相距太远。**
§4.1 "Prediction and CEM analyses"（L530–553）集中堆放了 §4.3 与 §4.4 才用到的全部协议细节，读到 §4.3 时早已忘光；而 §4.3 自己只剩指代（"the strongest ... defined above"）。整改方向：协议细节就地下沉到使用它的小节。

**R5 — 防御性免责声明重复堆积。**
"calibration remains model-family specific" 出现 ≥5 次（L105、L129、L453–455、L738–740、L806–808、L830–831）；"not simulator return / not an environment outcome" ≥4 次（L656、L676、L797、L1082）；"zero violations" 3 次（L626–631、L994–997、L1090–1095）；"descriptive rather than population inference" 2–3 次。每条保留 1 个自然归属点，其余删除。这是全文"审计报告腔"的主要来源。

**R6 — 段落无收束（虎头蛇尾）。**
每个实验小节以 disclaimer 或数字罗列结尾，没有一句 takeaway 告诉读者"这一节证明了什么、对总 claim 意味着什么"。§4.4 尤甚：soundness 校验、增量预测、augmentation 对比三个话题挤在一节无路标。

**R7 — 术语与记号不一致。**
- "training run" / "seed" / "run" 混用（正文 vs Table 6 列头 "seed"）；
- "batch-permuted"（L543、表 6/7）vs 旧版 "actions from another trajectory"；
- 正文 $t_R,t_M$ vs Table 8 列头 $\tau_R,\tau_M$；
- `Figure~\ref` / `Fig.~\ref` / `\Cref` 三种引用混用（L500、L637、L469 等）；
- "non-augmented" / "no-aug." / "trained without augmentation" / "without visual augmentation"（L423）/ "without noise augmentation" 五种写法；
- "visual shift" / "stressor" / "perturbation" / "corruption" 未区分定义（keywords 用 corruption，节名用 stressor）；
- $\mathrm{ATR}^{\mathrm{raw}}_q$（eq:atr-raw）vs $\mathrm{ATR}^{\mathrm{raw}}_{q,\upsilon}$（L429）下标突变；
- $(\cdot)_+$（L241）vs $[\cdot]_+$（L1080）；
- 数字精度：L563 "$25.89\pm2.38$ percentage points"（3 个 run 报 2 位小数，过度精度）。

---

## 2. 全局整改动作

### 2.1 句式规范

1. **"We ask whether ..."**：顶会论文中偶用可接受（不算错误），但本文 4 处小节开头（L580、L633、L682、L747）+ "We then ask" + "Finally, we ask"，重复且把动机藏进问句。整改：每节改为**陈述式 topic sentence**（先说测什么、为什么、依据哪条命题），全文最多保留 1 处 "we ask"。示例见 §3 的 §4.3 重写稿。
2. 每个实验小节结尾加一句加粗 **Takeaway:**，直接陈述该节支持的 claim 与边界。
3. Caption 执行既有约定：第一短句说明回答什么问题，第二句说明统计单位，≤65 words，协议细节移回正文/appendix。

### 2.2 统一命名（一次定义、全文复用）

| 新 canonical 名 | 定义（首次出现处给出） | 取代的现有写法 |
|---|---|---|
| **anchor** | one logged history window with its H-step observed future and recorded actions（§3.4 首次用前定义） | 未定义就使用 |
| **training run** | an independently trained model (training seeds 3072/3073/3074)；"task–run cell" = 1 task × 1 run，共 12 | run/seed 混用 |
| **unaugmented checkpoint** | trained without Gaussian noise augmentation | non-augmented / no-aug. / without visual augmentation 等 5 种 |
| **zeroed actions** | every action replaced by the zero vector | zeroed |
| **swapped actions** | the recorded action sequence of a different trajectory in the batch | batch-permuted / another trajectory |
| **shuffled actions** | the anchor's own actions in permuted temporal order | time-shuffled |
| **destroyed-action controls** | 上述三者统称：same-horizon rollouts whose action information is destroyed | "action controls" / "destroyed-action" 散写 |
| **Base / Base+Control$_8$ / Base+ACPC$_8$** | §4.3 三个 nested regressions 的短名（见 §3 重写稿） | "the one-step baseline / the second / the third" |
| **error drift** $d$ | $d=\lvert e_{\tilde h}-e_h\rvert$，Prop 1 所 bound 的量 | "perturbation-induced eight-step error differences" 长链 |
| **visual perturbation**（样本级）/ **visual shift**（分布级：Gaussian noise, blur, resize） | §4.1 定义一次 | perturbation/shift/stressor/corruption 混用 |
| **run-level equal-task summary** | 每个 run 先对 4 task 等权平均，再报 across-run mean ± sample SD（§4.1 定义一次，此后复用短名） | 每次重新展开描述 |

引用统一 `\Cref`（cleveref 已加载）；$(\cdot)_+$ 统一圆括号并在 Prop 1 处定义；$t_R,t_M$ 为准（Table 8 改列头）；ATR 下标统一为 $\mathrm{ATR}^{\mathrm{raw}}_q$，visual shift 依赖仅在 §3.5 校准处以文字说明，不再引入 $\upsilon$ 双下标（或统一带 $\upsilon$，二选一，推荐删 $\upsilon$）。

### 2.3 关键常数的动机句（全部有 repo 依据）

| 常数 | 整改句（英文，拟写入正文） | 依据 |
|---|---|---|
| H=8 | "All checkpoint-level diagnostics use the fixed protocol horizon $H=8$ with uniform weights $\alpha_k=1/H$: the logged evaluation windows provide eight observed future frames, so $H=8$ is the longest horizon at which every anchor has a complete common future; checkpoint-level conclusions are insensitive to $H\in\{1,2,4,8\}$ (Appendix~B)." | 协议脚本 `_require(rollout_horizon==8)`；`tables/table_horizon_quantile_sensitivity.tex`（现存但未收录） |
| H=5 | "Candidate-conditioned ACPC uses $H=5$, matching the five-action planning horizon of the evaluated CEM configuration." | `freeze_acpc_planner_stability_protocol.py: plan_horizon=5`；docs 明确要求此表述 |
| q90 | 正文已有理由（L369–370 "a mean can hide a small set of high-radius anchors"），补 "and is stable against q80/q95 (Appendix~B)" | 同上 horizon/quantile 表的 q80/q90/q95 列 |
| q35、δ=0.10、ε 值 | "protocol constants fixed before any evaluation-task outcome was inspected"；ε 说明移入 appendix | frozen protocol 文档；（可选）`table_smpr_sensitivity.tex`，见决策点 D2 |
| 80%/5pp 成功率准则、σ=0.08、blur k=15、resize 0.25 | 标注 "fixed a priori" + 一句直觉（80% = recovers most of the attainable improvement; 5pp = tolerates seed-level fluctuation on clean inputs）；直觉句需你确认（这是设计动机，repo 未记载原始理由） | （可选）`table_threshold_quantile_sensitivity.tex` 支持 80%/5pp 的稳健性，见 D2 |

### 2.4 去重方案（R5）

| 声明 | 保留位置 | 删除位置 |
|---|---|---|
| model-family specific calibration | §3.5 一句 + §5 limitations 一句 | abstract 末句压缩、intro、§4.6 重复句、conclusion 重复句 |
| not simulator return | §4.4 首次出现处 + Appendix G | Fig 3 caption、§5、其余 |
| zero violations / soundness | §4.4 一句 + Appendix G 详述 | Appendix C 重复段 |
| descriptive, not population inference | §4.1 统一说明一次 | 各处散句 |

---

## 3. 逐节整改清单（main.tex，行号为当前文件）

### Abstract（L104–109）—— 全文重写

问题：R1/R3/R5 集中爆发。"a state-coordinate proxy test for different-state separation"、"oracle best-of-three same-horizon control that disrupts the recorded-action alignment"、"movement in squared latent goal cost"、"candidate-conditioned five-step ACPC" 对首读者全部不可解码；八个结果句无主线。

重写稿（草案，≈195 words，执行时可微调）：

> Latent predictive world models avoid reconstructing pixels, but latent prediction alone does not show whether a state-preserving visual change—noise, blur, degraded resolution—remains harmless once the model rolls the state forward and a planner acts on the prediction. We introduce Action-Conditioned Predictive Consistency (ACPC), a diagnostic for frozen checkpoints: encode a clean and a visually perturbed view of the same history, roll both forward under the same actions, and measure how far the two predicted trajectories separate. Exact inequalities tie this separation to the resulting change in multi-step prediction error and to the movement of planner candidate costs. Since a collapsed representation would make the separation vanish, we pair the checkpoint-level radius (ATR) with a separation test on pairs whose logged task states differ (SMPR). On LeWM over four control tasks, eight-step ACPC under the recorded actions predicts perturbation-induced error changes with $51.3\pm3.5\%$ lower cross-validated MAE than the strongest same-horizon control with destroyed action information, so the signal comes from the actions rather than rollout length. ACPC also improves cross-task prediction of CEM decision regret; ATR–SMPR thresholds calibrated on source tasks screen checkpoints on held-out tasks, transfer to blur and resize, and port to PLDM after per-family recalibration.

### §1 Introduction（L119–136）

1. L127 段（一段塞下 ACPC+两个 bound+ATR+SMPR+score）拆两段：先 ACPC 与两条 inequality（工具），再 ATR/SMPR/score（checkpoint 级封装）。句式同步简化。
2. L129 数字段：intro 阶段数字取整（"about 51%"、"balanced accuracy 0.86–0.90"），删除 "Aggregated over all 14 directional partitions"（R1：此处读者不知 partition 为何物），改为 "across all cross-task calibration splits"。精确值留给 §4。
3. L131–136 contributions：三条各加 `\Cref` 指向对应小节；第 3 条 "Controlled evidence beyond the calibration tasks" 太虚，改为列明四类证据（error-drift 预测、CEM decision quantities、cross-task/cross-shift threshold transfer、PLDM portability）。

### §2 Related Work（L137–151）

轻度润色即可：L142 末句与 L150 末句是本文与前人分界的关键句，保留但压缩；L150 "asks a complementary paired-view question" 改陈述式。无结构问题。

### §3 方法（L152–497）

1. **L171–186（定义）**：
   - 补 anchor/history 的直观一句："$h$ contains the observation–action history the checkpoint's encoder consumes"；
   - L183–186 $\Pi$ 解释重写（现文 "checkpoint's normalized inference-cost embedding space, so $\Pi$ is the identity on the stored projected embeddings" 不可解码）。拟改为："LeWM's planner does not read raw predictor outputs; it scores candidates in a normalized projection of the embedding space. $\Pi$ denotes that projection, so all distances below live in the same space in which the planner computes costs. Our implementation stores these projected embeddings directly, so $\Pi$ needs no separate computation."；
   - 在 eq:acpc-h 后补默认值句（H=8 uniform weights，见 §2.3），并前向指出 planner 分析用 H=5。
2. **L228–253（Prop 1）**：statement 中定义 $(x)_+:=\max(x,0)$；L251–253 "The future-drift experiment uses that future only to..." 加 `\Cref{sec:exp-target-aligned}`。
3. **L255–269（§3.3 开头）**："The planner link is a radius–margin argument." 扩为两句直观（成本移动不超过 bound，bound 小于 clean gap 则决策不变）；L269 "the planner audit records $r_j$ directly" → "the planner experiments in \Cref{sec:exp-planner} record $r_j$ directly"。
4. **L301–308**：保留，"support an audit rather than a cheap pre-screen" 改 plain："they require evaluating every candidate under both histories, so they support a post-hoc audit rather than a cheap online screen"。
5. **L327–417（§3.4）**：
   - 开头定义 anchor（见 §2.2）；
   - L349–351 "This anchor-specific yardstick ... not a task outcome" 保留意思、去掉 "yardstick" 的比喻堆叠；
   - L376–380 "counterfactual only for the neighbor history" 重写："for the neighbor these are not the actions it actually executed; reusing the anchor's actions keeps a single shared action sequence on both sides"；
   - q35/δ=0.10 补 "protocol constants fixed a priori"（§2.3）；
   - $\varepsilon_{\mathrm{norm}}$ 数值移注脚或 appendix。
6. **L419–475（§3.5）**：
   - L425–426 "Its raw ATR is positive in the evaluated data, so" → 括号句 "(its raw ATR is strictly positive in every evaluated setting, so the ratio is well defined)"；
   - 统一 $\upsilon$ 下标（推荐删除，正文文字说明按 visual shift 分别校准）；
   - L453–455 与 L465–467 的免责声明合并为一句；
   - Table `tab:acpc-object-guide`（L477–496）："the worse calibrated radius/margin condition" → "the smaller (worse) of the two calibrated margins"；各行 wording 与新命名对齐。

### §4 Experiments（L498–779）

**§4.1 Evaluation setup（L519–558）——结构性调整（决策点 D3）**
- L522 补 "CEM optimizes five-action candidate sequences (plan horizon 5)"（依据 protocol JSON）；
- L524 "Evaluation seeds are conditional measurement replicates; the independently trained model is the replication unit." 重写："the three evaluation seeds only measure within-run variability; the independently trained run is the unit of replication throughout"；
- **将 L530–553 "Prediction and CEM analyses" 两段整体下沉**：error-drift 协议移入 §4.3，CEM 协议移入 §4.4（就地定义，解决 R4）。§4.1 只保留 models/tasks/sweep/diagnostic 测量与 threshold 评估；
- L556 "14 directional source/evaluation partitions" 就地给出 4+6+4=14 一句（现仅 appendix L1016 有）。

**§4.2（L560–576）**
- L563 数字改 1 位小数；
- 结尾加 Takeaway（诊断方向与成功率准则一致，但尚未证明 action 信息与 planning 相关性——引出后两节）。现有 L570–575 的诚实限定保留、压缩。

**§4.3（L578–621）—— 全节重写（你举的两个例子都在此解决）**

重写稿（正文骨架，含就地协议；执行时接表 6/7 与 Fig 2 引用）：

> \Cref{prop:target-free-error-drift} bounds, for each history pair, the perturbation-induced change in prediction error: the two $H$-step errors against the same logged future can differ by at most $\mathrm{ACPC}_H$. This section tests whether measured ACPC is informative about that bounded change, the error drift $d=\lvert e_{\tilde h}-e_h\rvert$. We evaluate at the protocol horizon $H=8$, the longest horizon with a complete logged common future for every anchor (\Cref{sec:appendix-A} shows the conclusions are stable for $H\in\{1,2,4,8\}$).
>
> \textbf{Data and protocol.} The analysis uses the unaugmented checkpoint of each task and training run. Trajectories are partitioned into 16 disjoint groups; each history pair contributes one row per Gaussian probe severity $\{0.02,0.05,0.08\}$ and perturbation draw, and all rows from one trajectory group stay together. A ridge model is fitted on 15 groups and evaluated on the held-out group, rotating through all 16; we report out-of-group MAE. Zero-severity rows serve only as identity checks.
>
> \textbf{Three nested regressions.} Every model contains the probe severity and the encoder-history distance $\lVert z-\tilde z\rVert_2$.
> \begin{itemize}
> \item \textbf{Base} adds one-step ACPC under the recorded action: the information available without a multi-step rollout.
> \item \textbf{Base+Control$_8$} adds the strongest \emph{destroyed-action control}: eight-step ACPC recomputed with zeroed actions (all actions set to zero), swapped actions (the recorded actions of a different trajectory), or shuffled actions (the anchor's own actions in permuted order). Each control performs the same eight-step rollout, so it carries rollout length without the recorded action sequence. ``Strongest'' is an oracle choice: in each task--run cell we report whichever of the three controls attains the lowest test MAE, which makes the comparison conservative.
> \item \textbf{Base+ACPC$_8$} instead adds eight-step ACPC under the recorded actions---the only feature whose action sequence is the one that generated the logged future, and hence the feature that matches the right-hand side of \Cref{prop:target-free-error-drift}.
> \end{itemize}
> If Base+ACPC$_8$ improves on Base, multi-step information helps; if it also improves on Base+Control$_8$, the gain is attributable to the recorded actions rather than to rolling out eight steps.
>
> \textbf{Results.} Base+ACPC$_8$ attains the lowest out-of-group MAE in all 12 task--run cells (\Cref{fig:future-drift-runs}, \Cref{tab:target-aligned-acpc}). Relative to Base the equal-task MAE reduction is $55.9\pm4.7\%$; relative to Base+Control$_8$ it is $51.3\pm3.5\%$ (run-level equal-task summaries). These results concern prediction of the error drift; they do not compare the forecast accuracy of one-step and eight-step world models. \textbf{Takeaway:} ...

（“the longest horizon with a complete logged common future” 一句为对 H=8 的最小可靠动机——评估窗口只记录 8 帧 future；若你有更本源的设计理由，执行时替换，见决策点 D4。）

**§4.4（L623–677）**
- 三个话题分段并加 `\paragraph` 路标：*Soundness audit*（9,600 rows 的构成一句：100 histories × 4 tasks × 3 runs × 2 training conditions × 4 severities；identity probes = severity-0 duplicates，定义一句）/ *Incremental predictive value* / *Effect of augmentation on decisions*；
- 首段陈述式改写 + H=5 动机句（§2.3）+ "candidate-conditioned" 定义（ACPC computed per candidate action sequence from the planner pool, not the logged actions）；
- L553（移入本节后）三 targets + 四 covariates 改 itemize；first-action RMS（RMS difference between the first actions of the nominal and perturbed final plans—the action MPC would execute）与 nominal top-1 margin（clean cost gap between best and second-best candidates）就地定义；
- L666–667 "the rank association is higher..." → "the Spearman rank correlation with the target is higher..."（依据 summarize 脚本用 spearman）；
- L661–663 与 Table 2 的口径统一：正文同时给 task 级（3/4）与 cell 级（8/12）；
- 结尾 Takeaway。

**§4.5（L680–719）**
- 开头陈述式；就地给 14=4+6+4；positive label 与 onset error 的定义从 Fig 4 caption 移入正文；
- L711–714 "balanced accuracy ranges from 0.723 to 0.913 across the four possible sources" 补一句归因 "the weakest single source is Reacher (Table 8)"（表内可查）；
- 结尾 Takeaway（threshold-selection procedure transfers; a single universal threshold does not——现 L715–717 已有此意，改为收束句）。

**§4.6（L721–742）**
- "Pooling the four evaluation branches" → "Pooling all 36 held-out checkpoint decisions (four evaluation tasks × nine checkpoints)"；
- 补 PLDM 单 run 提示（"one training run per setting; run-to-run variability is not estimated for PLDM"，§4.1 已述 36 settings，本节呼应一句）；
- "Reacher is therefore the unresolved boundary case" → 直说 chance level："on Reacher the transferred thresholds perform at chance (BA 0.500)"；
- 删除与 §3.5/§5 重复的 model-family 免责句（保留一句）。

**§4.7（L744–779）**
- "Finally, we ask" 改陈述式；24 pairs 构成就地一句（4 tasks × 3 runs × {blur, resize}）；blur k=15 / resize 0.25 在本节重述一次；
- L774–778 discordant 解释保留（写得好）；结尾 Takeaway（supports relative ordering at tested severities; not an absolute classifier——压缩现句）。

### §5 Discussion and limitations（L781–819）

重组为三段：**What the evidence shows**（对齐三条 contributions，各一句）/ **Scope and limitations**（合并去重后的全部限定：three runs per task、PLDM single-run、16-history full-budget、no matched wall-clock、one severity per shift、proxy labels ≠ semantics、stable-but-wrong possible）/ **Future work**（现 L816–819 保留）。逐句去 R5 重复；"although the available runs do not support a precise estimate of population-level training variability"（L790–791）→ "with three training runs per task, run-to-run variability estimates are coarse"。

### §6 Conclusion（L821–831）

保持 6–7 行；删去与 §5 重复的 model-family 句，加一句 outlook（诊断可作为 checkpoint 发布前的低成本 audit 步骤）。

### Appendix（L838–1118）

- **A**：$[\cdot]_+$→$(\cdot)_+$；"formal planner panel"（L886）→ "the planner experiments"；其余保留；
- **B**：加 `\paragraph` 路标（Evaluation grid / Success-rate criterion / ATR protocol / SMPR protocol / Threshold grids / Reproducibility）；**新增收录 `table_horizon_quantile_sensitivity.tex`**（支撑 H=8/q90，决策点 D1）并把 caption 中 "horizon-v2" 等内部代号改为 reader-facing 措辞；
- **C**：删除与 §4.4 重复的 zero-violation 句（保留 estimand 区分段，写得好，仅润色）；
- **D**：与 Table 8 一起修（见 §4 表格清单）；
- **E/F/G/H**：G 为 CEM 协议 detailed home（§4.4 去重后指向此处）；F 的 "not a separate contribution"（L1053）删（自贬式赘句）；H 保留。

---

## 4. 表格整改清单（可直接执行）

| 表 | 文件/位置 | 问题 | 整改 |
|---|---|---|---|
| Table 1 reader guide | main.tex L477 | 行 wording 与新命名不一致 | 与 §2.2 命名对齐；"the worse calibrated radius/margin condition" 改写 |
| Table `full_sweep_compact` | tables/…compact.tex | caption "nine-level" 与 "levels 0.01–0.08" 口径混淆；"1.00→0.07" 箭头未解释 | caption 改 "nine checkpoints per task (no augmentation + eight noise levels)"；注明箭头 = "unaugmented value → value at the best level"；"Levels meeting criterion" 加准则指针 |
| Table `acpc_planner_increment` | tables/… | caption 10 行塞满协议（R9） | 协议移正文 §4.4，caption ≤65 words；列头微调 |
| Table `pldm_architecture_portability` | tables/… | "False pass/miss" 未定义 | caption 一句定义（criterion-negative accepted / criterion-positive rejected）；caption 压缩 |
| Table `smpr-proxies` | main.tex L959 | 基本可用 | caption 微调，与 anchor 定义呼应 |
| Table `target_aligned_acpc`（6） | tables/… | caption 重复协议；列头 "Training run"/"seed" 不一致 | caption 压缩指向 §4.3；统一 "training run (seed …)"；列名与 Base/Base+Control$_8$/Base+ACPC$_8$ 对齐 |
| Table `target_aligned_acpc_absolute`（7） | tables/… | 同上；"selected control" 值用旧名（time-shuffled/batch-permuted/zero） | 值改 shuffled/swapped/zeroed；"paired wins" caption 定义（fraction of 16 folds where Base+ACPC$_8$ beats Base+Control$_8$）|
| Table `cross_task_…subsets`（8） | tables/… | 列头 $\tau_R,\tau_M$ vs 正文 $t_R,t_M$；onset error 单位是 σ（0.003/0.010），正文用 grid steps（1.1/0.5），读者对不上 | 列头改 $t_R,t_M$；onset 列换算成 grid steps（×100），caption 注明 "one step = 0.01 in $\sigma_{\max}$" |
| Table `cross_stressor_selective_transfer`（9） | tables/… | "Discordant" 未定义 | caption 一句定义 |
| Table `cross_stressor_all_pairs`（10） | tables/… | Outcome 列 "positive / positive" 语义要猜 | 列头改 "Outcome (success / score)"；两行 discordant 加粗或 †；caption 压缩 |
| （新增，D1） | tables/table_horizon_quantile_sensitivity.tex | 已生成未收录；caption 含内部代号 "horizon-v2" | 收录进 Appendix B；caption 改写为 reader-facing |

---

## 5. 需要你确认的决策点

- **D1（推荐：做）** 收录 `table_horizon_quantile_sensitivity.tex` 进 Appendix B，用于正面回答"为什么 8 步 / 为什么 q90"。表已存在、口径与当前协议一致（H1/H2/H4/H8 × q80/90/95，fixed σ=0.08，三 seed 中位数）。
- **D2（默认：不做，仅文字）** `table_smpr_sensitivity.tex` 与 `table_threshold_quantile_sensitivity.tex` 也存在（分别支撑 δ/q35 与 80%/5pp 准则），但表内出现 "V1 / MVE / 36 CAL checkpoints / behavioral-label" 等旧迭代口径，需你确认与当前 V2 协议一致才收录；默认只写 "fixed a priori"。
- **D3（推荐：做）** §4.1 的 "Prediction and CEM analyses" 两段拆散下沉到 §4.3/§4.4（结构性移动，定义就地化）。若你希望保持集中式 setup，则改为在 §4.3/§4.4 使用点加密集反向引用（次优）。
- **D4** §4.3 重写稿中 H=8 的动机句现依据"评估窗口记录 8 帧 future"（协议事实）。若设计时另有本源理由（如匹配 LeWM 训练 rollout 长度），请告知，执行时替换。
- **D5（推荐：1 位小数）** 成功率/pp 类数字统一 1 位小数（3 个 run 的 mean±SD 报 2 位属过度精度）；比率类（BA/precision/recall/ρ）保持 3 位。
- **D6** 图暂不动导致的过渡问题：正文新命名（Base+Control$_8$ 等）与 Fig 2 图内旧 legend 不一致。过渡方案：Fig 2 caption 加一句映射（"legend labels correspond to Base / Base+Control$_8$ / Base+ACPC$_8$"），待后续重画图时移除。默认执行此方案。

---

## 6. 图问题清单与整改建议（本次不执行，文字整改完成后作为交付物复核）

**全局：** ① 任务配色跨图不统一（Fig 1/3/5 各自成体系），建议固定 TwoRoom/PushT/Reacher/Cube 四色并全图沿用；② 图格式混杂（Fig 1–5 PDF 矢量，Fig 6/7 PNG 位图），建议统一矢量导出；③ 不确定带语义不一（Fig 1 为 min–max across runs，Fig 3 为 run 均值连线），每图 caption 需声明；④ 图内字号普遍偏小（四联图在 0.95\linewidth 下轴标签 ≈5–6pt）。

- **Fig 1 `fig_full_sweep_diagnostics.pdf`**：(a) 相对 ATR 曲线在第一档后即贴近 0，线性轴上不可读——建议 ATR 用 log y 轴或单列小面板；(b) 双 y 轴 + 三条不同语义曲线（%、ratio、rate）同панel，建议拆为上下两排（上：success，下：ATR+SMPR 同 0–1 轴）；(c) 绿色"达标带"与灰色 run-range 阴影视觉混淆，建议绿带加斜纹或仅在 (a) 面板注释一次；(d) x 轴 0 点即 unaugmented 需轴标注明（"0 = no aug."）；(e) legend 字号过小。
- **Fig 2 `fig_future_drift_three_seed_v1.pdf`**：(a) 图内大标题与 caption 重复，删；(b) 图底部的解释文字块（"Nested regression feature..."）与 caption 重复，删；(c) legend 措辞混乱（"oracle control + best-of-three ACPC₈ control" 读起来像两个东西），改为 Base / Base+Control$_8$ / Base+ACPC$_8$；(d) x 刻度标签与 legend 不同名，统一；(e) y 轴标签加 "(leave-one-group-out)"。
- **Fig 3 `fig_acpc_planner_evidence.pdf`**：(a) y 轴 "log1p target scale" 行话，改 "test MAE on log(1+target)"；(b) 只展示 2/3 个 targets（缺 first-action RMS），caption 应说明"第三个 target 增益可忽略故未画"；(c) "Mean decrease: 7.9%" 注释位置易被误读为轴标题，移至面板内右上；(d) 点重叠严重（Reacher），加抖动或半透明。
- **Fig 4 `fig_cross_task_atr_smpr_source_coverage_v1.pdf`**：(a) 面板 (a) 缺 chance=0.5 参考线；(b) 灰点重叠，建议按 partition 抖动；(c) 正文点名的 Reacher 单源离群点（BA 0.723 / onset 2.9 steps）建议图内标注；(d) 面板 (b) y 轴标签补 "(1 step = 0.01 σ)"。
- **Fig 5 `fig_cross_stressor_selective_transfer_v1.pdf`**：(a) Reacher 六个点 ΔS 完全同值（2.375）互相遮挡，需抖动或计数标注；(b) 正类判定含 clean-loss 条件，散点图只能画 ΔP≥5 一条线，caption 需声明"clean 条件在图中不可见"；(c) 任务（形状）与 shift（颜色）双 legend 拥挤，拆两个 legend 或入 caption；(d) 象限底色 agree/disagree 建议直接标注文字。
- **Fig 6 `fig_gaussian_sensitivity_main.png`**：(a) 位图改矢量；(b) 两个估计器面板建议并排同 y 轴便于对比，或画 ratio-vs-ratio 散点；(c) 无不确定带（单 run？），caption 需声明；(d) 补数值标签。
- **Fig 7 `fig_acpc_basin_tsne.png`**：(a) 整页篇幅信息密度低，建议压至半页 2×2；(b) 未选中灰点过淡近乎不可见；(c) "90% covariance envelope" 仅 (b) 面板可见，legend 却全局出现；(d) anchor 颜色无语义，caption 应写明 "colors only index anchors"；(e) 位图分辨率在打印尺寸下偏低。

---

## 7. 执行顺序与验收标准

**顺序：** ① 全局术语/引用统一（机械替换，先行降低后续 diff 噪声）→ ② Abstract+Intro → ③ §3 → ④ §4（含协议下沉）→ ⑤ §5/§6 → ⑥ Appendix（含 D1 新表）→ ⑦ tables/*.tex → ⑧ `bash build.sh` 编译 + blind 版编译 → ⑨ 终检。

**验收标准（⑨ 的检查单）：**
1. 每个术语首次出现即定义或有 `\Cref` 指针（对照 §2.2 表逐项验）；
2. 每个实验小节有 Takeaway；R5 各免责声明全文 ≤2 处；
3. 编译零 undefined references/citations（build.sh 自带检查）、无新增 overfull >10pt；
4. **数字不变性核对**：对新旧 PDF 全文提取数字序列 diff，除格式化（小数位统一，D5）外不得出现任何数值变化；
5. 新旧 PDF 逐节对读一遍（自查 CLAUDE.md working rules）。

完成 ⑨ 后交付：修改摘要 + §6 图问题清单终版。
