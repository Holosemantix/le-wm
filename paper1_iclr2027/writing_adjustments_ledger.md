# ICLR 2027 主文写作调整清单

最近更新：2026-09-08。各日期记录中的行号对应当次版本的 `main.tex`。

## 核对原则

- `paper1/main.tex` 是已发布版本的主要写作来源；科学性修正以
  `paper1_v1.1_backup_20260817/paper1/main.tex` 为准；新增实验与分析来自
  `paper1_v2_high_severity_draft/full_main.tex` 和
  `paper1_v2_high_severity_draft/main_text_extension.tex`。
- 摘要在本轮开始时冻结，本轮没有改写。
- 主文压缩优先删除重复信息、实现细节和已在 Appendix 完整保留的内容；不以
  改写整段来换取篇幅。
- 下表明确标出仍包含人工合并、压缩或新增衔接的地方。这些位置应作为后续逐句
  复核的重点。

## 2026-09-08 Introduction 贡献标题更新

本次由 sol medium 实施写作，主进程审核；仅修改 Introduction 末尾的贡献段
（`main.tex` 120--135）。保留 `We make three contributions.`、First/Second/Third
及紧凑单段排版。

| 位置 | 新拟、恢复或压缩的表述 | 范围说明 |
|---|---|---|
| 第一项 | 恢复完整名称 `Action-Conditioned Predictive Consistency (ACPC)` 和 `we introduce`，用 `which compares` 承接比较说明；`predicted clean and perturbed rollouts under the same actions` 调整为 `clean and perturbed rollout predictions under shared actions`，`while SR` 改为 `and SR` | 全称与提出方法的句式来自 v2；比较对象、共享动作、IR/SR 说明和引用不变。后两处为本次轻量措辞调整。 |
| 第二项 | 使用已确认标题 `bounds on prediction-error and planning-cost changes`；条件压缩为 `over multi-step rollouts with identical candidate action sequences across views` | 这是本次重新组织及压缩的表述；保留变化量、multi-step、samplewise、same candidates/two views、无 distributional/smoothness assumptions 以及原有命题引用。 |
| 第三项：筛选方法 | 新增 `we develop ACPC-based checkpoint screening using IR and SR`，其中 `ACPC-based checkpoint screening` 为已确认的粗体标题；用 `and evaluate all three diagnostics` 衔接原有实验范围 | ACPC 是基础度量，实际 screen 使用 IR 和 SR；不新增第三个筛选阈值，不声称筛选优于基线或保证控制性能。`all three diagnostics` 指 ACPC、IR、SR，避免重复列举。 |
| 第三项：实验范围 | `across four control tasks, three visual perturbations, and a second world-model architecture` 压为 `on four tasks, three visual perturbations, and two architectures` | 删去上下文已明确的 control/world-model 修饰，主架构加第二架构改称两种架构；覆盖范围不变。 |
| 第三项：CEM 句 | 将 `the extra predicted cost when a visual perturbation makes ... select a different plan` 压为 `extra predicted cost of perturbation-induced plan changes in ...` | 这是本次句子压缩；保留扰动引起的换计划及额外 predicted cost，不改成环境回报或控制性能改善。CEM 全称、引用及后续 IR/SR 非等价与连续关联句均保留。 |

为遵守九页限制，最终没有在贡献段重复加入 source-task 阈值校准与 held-out-task
应用的程序说明；这些原有内容完整保留在 Checkpoint Screening 小节。
本次未删除任何原有实验结论；实验范围句与新增筛选句合并，CEM 句仅作上述压缩。
未修改摘要、其他章节、数值、图表、参考文献源文件或
模板间距、字号及页边距。

重建核验：pdfLaTeX 与 BibTeX 均为 TeX Live 2025；执行完整
pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX 流程并检查交叉引用已稳定。
Conclusion 仍在第 9 页结束，完整 PDF 24 页。重建的 41 条 bibliography entries
与原 `main.bbl` 逐字节一致；无 undefined citation/reference、BibTeX warning、
overfull/underfull hbox 或需要再次编译的提示。保留了原编译就存在的 3 条
underfull vbox 提示，未为消除这些提示调整模板。

## 2026-09-04 定向恢复与压缩记录

| `main.tex` 行号 | 处理 | 来源与自行调整披露 |
|---|---|---|
| 120--134 | 恢复 Introduction 末尾的三点 contributions，并补齐压缩后遗漏的信息 | 三点分别对应 ACPC/IR/SR、samplewise error/cost bounds、四个 tasks/三种 perturbations/第二 architecture。最终版本明确恢复了：cost bound 只适用于从两个 view 评估相同 candidate action sequences；LeWM/CEM 实验测量换 plan 后的额外 predicted cost；IR 与 SR 提供 non-equivalent views。段首由 medium 在 `Our contributions are threefold.`、`This work makes three contributions.` 和 `We make three contributions.` 中选择后，改为最直接的 `We make three contributions.`；紧凑段式是对 `paper1/main.tex` 218--235、`paper1_v1.1_backup_20260817/paper1/main.tex` 206--242 和 v2 `full_main.tex` 211--250 的 sentence compression；没有新 claim。为避免连续两段重复同一组 theory/experiment 证据，没有恢复旧稿 contributions 前的完整 evidence paragraph，而是只将其必要限定和证据并入三点贡献。 |
| 138--154 | 压缩 World Models | 保留段首引导、DreamerV3/TD-MPC2、JEPA foundations、LeWM/PLDM、collapse、action conditioning、retained features 与 seq-JEPA。为把 Conclusion 留在九页内，删除较远的 PBL/SPR。`Work on self-predictive learning studies...` 是本轮自行合并的短句，各 clause 仍分别对应旧稿中的 collapse、action conditioning 与 retained-feature 分支。 |
| 156--172 | 压缩 visual robustness | 保留段首引导、DrQ/DrQ-v2/SODA、ReOI、DreamerPro、Denoised MDPs、temporal-masking/bisimulation、bisimulation foundations 与 MWM；移除 ViGMO、VIBR、TPC 和 Task Informed Abstractions。`Other training methods use...` 是本轮自行组合的并列句，各项功能与引用逐项对应，没有 citation dump。 |
| 171--190 | 压缩 world-model diagnostics | 保留段首引导、ATM、CARRL/CROP、action-content/rollout-validity/model-error diagnostics、WMAttack 与 ARB4WM；移除 ACID 与 Future-Compatible。CARRL/CROP 的功能及其与本文 bounds 的区别被压成两句；WMAttack/ARB4WM 功能说明沿用 v2 原句。段末保留 `ACPC instead measures`。 |
| 205--254 | 恢复 Pairwise ACPC 开场与定义衔接 | `Given a clean history and its perturbed version, ACPC compares the rollouts predicted from them under identical actions.` 逐字来自 `paper1/main.tex`；`Here H...` 与 projected planner-cost space 过渡也恢复为来源表述。此处没有自行改写。 |
| 459--461 | 补回统计口径 | medium 逐段审视后发现 three-run error bars/SD 缺少 replication-unit 说明。加入两句 source-based compression，保留 three independent training runs、每 checkpoint 三个 evaluation seeds、每 seed 100 episodes，以及 training run 是 replication unit；具体 seed ID 仍在可复现材料中。 |
| 542--547 | 补回 prediction-error experiment 输入定义 | 恢复来源原句中的三个 probe severities、每个 pair 的 two perturbation draws，以及 zero-severity 只作 identity check，避免后文首次出现 `probe severity` 时没有定义。 |
| 696--712 | Conclusion 去重 | 整句删除了与紧邻 Discussion 及 Abstract 重复的 pair-level experiment summary；不删除 checkpoint regimes、PLDM/blur/resize 或 non-certificate 结论。 |
| 原 742--778 | 删除独立的 `Additional Related Work` | 最终将其中 6 个直接引用压回主文：DreamerPro、Denoised MDPs、temporal-masking/bisimulation、ATM、WMAttack 和 ARB4WM；其余 14 个不再引用。删除后 `Proofs and Fixed-Pool Analysis` 自动成为 Appendix A；没有改 proof 内容或 labels。 |

本轮最终保留 41 个 unique citation keys，不再以维持 47 或 58 篇为目标。为回收
主文空间，删除 PBL、SPR、ACID、Future-Compatible、ViGMO 和 Task Informed
Abstractions；保留与 test-time visual robustness 直接相关的 ReOI。
独立的 `Additional Related Work` 仍保持删除。

## 恢复或保留的来源表述

| `main.tex` 行号 | 位置 | 本轮处理 |
|---|---|---|
| 71--90 | Introduction 开篇 | 恢复“encoder distance 不能说明 perturbation 如何经过 rollout 传播”的因果顺序，并保留 predictor 可能放大或缩小差异的解释。此前用户指出的两句晦涩表述已删除。 |
| 92--103 | ACPC、IR、SR 首次介绍 | 按“先解释 ACPC，再说明 collapse 问题，最后分别解释 IR 和 SR”的顺序恢复可直接阅读的定义。 |
| 120--134 | Introduction 三点 contributions | 保留 method、theory 和 experiments 三类贡献，并指向对应正文；同时保留 theorem scope、CEM 证据及 IR/SR non-equivalence。 |
| 188--190 | Related Work 结尾 | 保留 diagnostic gap：ACPC 衡量 task-preserving visual perturbation 如何沿 shared-action rollout 传播，且不需要 true future。 |
| 193--203 | Theory 章节导语 | 保留从 pairwise ACPC 到 error bound、cost bound、IR/SR checkpoint summary 的章节路线。 |
| 205--254 | Pairwise ACPC | 保留 clean/perturbed histories、shared actions、weighted rollout、与 encoder shift 的区别，以及“consistency 不是 accuracy”的收束。 |
| 256--279 | Prediction-error bound | 保留进入命题前的 observed-future 说明和命题后的 scope 解释。 |
| 281--336 | Planning-cost bounds | 保留从 planner ranking 到 endpoint displacement、cost bound、winner/elite-set stability 及 adaptive-CEM 边界的完整推导顺序。 |
| 338--396 | IR 与 SR | 恢复本小节的动机段、anchor/action 定义、数值稳定项、eligible-anchor 集合和 collapse 解释。 |
| 494--532 | Broad-severity 实验 | 保留为什么检验 SR redundancy、两个方向的 disagreement、连续关联及其非因果边界。 |
| 642--667 | Blur/resize | 保留 24 个 pair 的构造、两个 component 的定义、pooled correlations、LOTO ranges 和 SR 不改变 Boolean decision 的边界。 |
| 669--712 | Discussion 与 Conclusion | 恢复 pair-level evidence、adaptive-CEM 适用边界、IR/SR 的额外数据依赖、外部扰动限制及最终非 universal-certificate 结论。 |

## 仍含压缩、组合或自行衔接的位置

以下不是未经标记的自由发挥；每一项都只为九页限制、科学性修正或段落连接服务。

| `main.tex` 行号 | 类型 | 调整内容与需要复核的点 |
|---|---|---|
| 71--81 | 句子合并 | World-model/JEPA 背景与“视觉差异是否与控制相关”的动机被压成一个开篇段；claim 与 citations 没变。 |
| 92--103 | 衔接重排 | 增加 `To measure this rollout-level effect`，并把 IR/SR 的解释移到 ACPC 后面，避免首次出现三个缩写时跳步。 |
| 120--134 | 句子压缩 | 将三条 source contributions 压成一个连续段落；以 `We make three contributions.` 直接引出 First/Second/Third，完整 theorem statements 保留在 Section 3。具体人工压缩共四处：把 source contribution 2 的两句合并但保留 same-candidate 条件；用 `samplewise` 承担 source 中 `for each evaluated pair` 的含义；轻量压缩 CEM evidence 句；把 v2 的 non-equivalent 与 covary 两个 clause 合并。 |
| 138--190 | Related Work 压缩与引用重排 | 三个 paragraph 的段首引导、MWM 对比和 `ACPC instead measures...` 收束均保留。自行组合处是 World Models 的 self-predictive work 合并句、Robustness 的 training-methods 与 MWM/ACPC 对比句，以及 Diagnostics 的 CARRL/CROP 压缩；每个 clause 都有明确对象和对应引用。该区域净减约 100 个 source words，约对应八至十个双栏正文行。 |
| 193--203 | 章节衔接 | Theory 导语是来源内容的顺序化组合，用来保留各小节之间的阅读路线。 |
| 221--225, 250--254 | 解释性衔接 | 用短句说明 `Pi`、weighted trajectory distance、encoder shift 与 rollout distance 的区别。数学对象不变。 |
| 274--279 | 命题后解释 | 将 proof location、bound scope 和实验中 observed future 的用途放在同一段。 |
| 327--336 | 命题后压缩 | winner、top-k elite set、paired CEM 和 environment return 的限定由来源段落压缩组合。 |
| 340--347 | 小节导语 | 明确保留“pairwise measurement -> checkpoint summary -> collapse guard”的桥接；属于解释性组合。 |
| 374--380 | IR 到 SR 的过渡 | 将 different-state pair 的选择、共享 action、相同 normalization 和 eligible set 连成一个定义序列。 |
| 400--419 | 表述澄清 | 新增简短句 `Relative IR equals 1...` 与 `This is a Boolean screen, not a continuous ranking.`；删除旧稿中的 continuous joint score，以符合当前科学口径。 |
| 421--425 | 章节过渡 | 用两句话区分 pair-level 与 checkpoint-level experiments，并指向对应小节。 |
| 431--467 | Evaluation Protocol 压缩 | 保留 tasks、success metric、CEM horizon、完整 nine-condition noise sweep、IR/SR 核心协议、broad-severity 生成方式、three-run replication/evaluation 口径和 success criterion；精确 pairing 与 subset enumeration 留在 Appendix。主文删去 Diagnostic Protocol 后重复的 Appendix pointer 和 relative-IR pointer，因为 Section 3 与 Appendix 已完整定义。Lines 459--461 是对来源 seed/replication 段的明确 sentence compression。 |
| 481--499 | 原始 sweep 到 broad-severity 的衔接压缩 | 保留 recovery range、Reacher clean-performance caveat、77/77 结果。删除其后重复解释 `SR does not veto...` 的整句；下一小节以 `We test whether this redundancy persists...` 直接承接 77/77，含义未丢失。 |
| 524--532 | 新实验句子压缩 | `After accounting for the simple exposure ratio...` 把 adjusted-correlation protocol 与 task-equal weighting 合为一句；随后保留 PushT 反例，并把 association boundary 压成 `These associations do not establish better checkpoint selection or replace evaluation of nominal model quality.`。 |
| 536--554 | Prediction experiment 协议压缩 | 保留 H=8、三个 probe severities、two draws、zero-severity identity check、16-fold grouped split、Base/Control/ACPC features 和 conservative control selection；精确 row counts 留在 Appendix。Lines 542--544 是逐字恢复的 source 句。 |
| 564--569 | Prediction result 压缩 | 合并 12/12 cells、两组 MAE reduction 和 absolute-accuracy scope。 |
| 573--597 | Planner experiment 定义与协议压缩 | 保留 selection regret 的公式含义、不是 simulator return、paired CEM 的 common-random-number 设置、q90 features 与 leave-one-task-out；预算和样本数留在 Appendix。 |
| 607--616 | Planner result 压缩 | 保留 12/12、平均 MAE improvement、fixed-pool coverage range 与“不覆盖 later adaptive rounds”的限制。 |
| 622--627 | Cross-task result 强压缩 | 主文只保留目的与 two-/three-source 核心结果。`13/14` threshold-choice 细节、single-source 情况和全部 partitions 留在 Appendix F。 |
| 632--640 | PLDM 压缩 | 保留跨 architecture 的目的、描述性趋势和“不跨 model family 转移 threshold”的边界。 |
| 645--667 | Blur/resize 句子合并 | 将实验构造、component 方向和结果分别合并；没有删除 LOTO ranges 或 fixed-threshold 限定。 |
| 671--694 | Discussion 去重 | 删除已在结果段完整出现的数值复述，只保留证据边界和 limitations。 |
| 698--712 | Conclusion 去重 | 删除与紧邻 Discussion/Abstract 重复的 pair-level 证据句以及与 broad-severity 结果重复的 continuous-association 复述；其余按 checkpoint regimes、architecture/stressor extension、scope 的顺序保留。 |

## Caption 与排版调整

| 对象 | 调整 |
|---|---|
| Figure 1 | Caption 保留三部分的语义；图宽设为 `0.80\linewidth`。 |
| Figure 2 | Caption 保留 across-run means、error bars、per-task axes 以及 IR/SR 方向；最终图宽 `0.74\linewidth`。 |
| Figure 3 | Caption 保留 SR rejection 的分母和含义；最终图宽 `0.54\linewidth`，放在 Section 4.3 内。 |
| Figure 4 | Caption 压成“cross-validated MAE，lower is better”；marker/line 样式说明删除；最终图宽 `0.74\linewidth`。 |
| Figure 5 | Caption 只保留 planner-horizon ACPC 的主结论；最终图宽 `0.64\linewidth`。删除了错误的 bottom trim，因为它会裁掉第二行横轴标签；当前图不再打断 protocol 段落。 |
| Table 1 | Caption 删除正文已能读出的 population-SD 和 relative-IR 说明；保留 three-run means 与 bracket 含义。 |
| 所有 floats | 未修改模板默认的 float/caption spacing、页边距或字号。Figure 3--5 与 Table 1 使用 `[H]` 仅控制叙事顺序。 |
| 图文件底部空白 | 按最终使用的五个 PDF 图在 144 dpi 下测得约 1.0--2.5 pt，不存在值得裁剪的大块底部空白。 |

## 机械性兼容调整

- 为兼容 TeX Live 2025 的 `cleveref`，个别多对象引用拆成两个 `\Cref{}`；含义未变。
- `\crefalias{section}{appendix}` 只修正 Appendix 引用名称。
- `\label{sec:main-text-end}` 是不可见的页码检查锚点，不改变成文内容。
- 在正文结尾后、AI use statement 前加入 `\clearpage`，只用于让非正文声明从第
  10 页完整开始；它不改变正文页数、模板间距、字号或学术内容。

## 最终门槛

- Conclusion 的最后一个词在第 9 页；AI use statement、reproducibility
  statement 与 References 从第 10 页开始。
- TeX Live 2025 最终编译通过；无 LaTeX error、undefined citation/reference、
  BibTeX warning、overfull/underfull hbox 或 multiply-defined label。
- 全文引用并渲染 41 篇；删除 Additional Related Work 后，Proofs 成为
  Appendix A 并从第 13 页开始，完整 PDF 为 24 页。
- 最终 sol 只读审核确认 Related Work 的 claims、citations、scope 与三段衔接；
  此前审核同时确认 Introduction 六段功能链、
  4.2 到 4.3、4.8 到 Discussion/Conclusion 的衔接均完整，Figure 2--5 的
  labels/legend 仍清楚可辨，且没有 overclaim。
