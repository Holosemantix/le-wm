# ICLR 2027 主文写作调整清单

最近更新：2026-09-09（UTC）。各日期记录中的行号对应当次版本的 `main.tex`。

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

## 2026-09-09 Figure 8 改为仅显示均值柱状图

按用户要求，去掉所有逐 seed 散点及 `one point per seed` 图例。保留三次运行
均值柱高、坐标范围、颜色和其他图中文字。生成脚本
`paper1/scripts/build_cross_stressor_component_analysis.py` 增加可选
`show_points` 参数（默认 True，历史输出不受影响）；本次仅调用
`plot(_read_csv(DEFAULT_ROWS), ..., show_points=False)`，输出到 ICLR 图目录，
不重算统计、不覆盖原始数据或旧版 assets。同步删除 caption 的
`dots show individual runs` 及引导句的 `and per-run`，没有新增论述。

TeX Live 2025 完整重建，已检查新版柱状图；主文 9 页、全文 25 页。
已同步 `main.pdf`，未提交或推送。

## 2026-09-09 恢复跨扰动图并补齐附录引导引用

v2 原图 `fig_cross_stressor_ir_sr_comparison_v2.pdf` 使用旧联合分数 ΔS，
不直接恢复。改为引用已有 `fig_cross_stressor_components_v1.pdf`：分别展示
规划成功率变化、IR improvement 和 SR change，与当前分量分析一致。
图资产与原 assets 版本逐字节一致，生成脚本使用同一份 24 对分量数据并同时
输出汇总表；未重新计算或改动数据/图像。图恢复到 Appendix G，现为 Figure 8。

由 sol medium 增加以下说明与 caption；主进程在 caption 中补全
`the checkpoint trained at`，避免将 checkpoint 与数值直接比较：

- `Figure 8 shows the corresponding per-task and per-run changes.`
- `Changes from the unaugmented checkpoint to the checkpoint trained at
  $\stdmax{}=0.08$ under blur and resize. Panels show (a) planning-success change
  in percentage points, (b) IR improvement $1-\mathrm{IR}^{\mathrm{rel}}_q$,
  and (c) SR change. Bars are means across three training runs, dots show
  individual runs, and positive values indicate improvement.`
- `Table 11 compares recorded-action ACPC with encoder-only, one-step rollout,
  and action-destroying controls.`

正文使用 LaTeX 自动引用；4.8 原有 Table 10 / Appendix G 引用中补入 Figure 8。
没有恢复旧联合分数或固定阈值筛选说明。TeX Live 2025 完整重建并检查附录图表
排版；主文仍 9 页、全文 25 页。已同步 `main.pdf`，未提交或推送。

## 2026-09-09 合并 4.8 总结句与结果段

按用户意见，仅删除 `These results show that both IR and SR remain informative`
前的空行，将总结句并入前面的结果段，全部措辞不变。TeX Live 2025 完整
重建成功，主文仍 9 页、全文 25 页，无未定义引用或 overfull box；已同步
`main.pdf`，未提交或推送。

## 2026-09-09 聚焦 4.8 的跨扰动诊断问题

用户确认将 4.8 限定为指标变化与行为变化的关联，而非固定阈值迁移检验。
由 sol medium 修改正文：删除 Gaussian 阈值固定/未校准说明和末尾 6/24
通过筛选段。Table 10 同步删除 `IR pass / veto` 列及 caption 中对应一句；
其余数值、逐任务异质性、cluster-resampling sensitivity 和 Table 11 均保留。
已有内部逐对数据、计算脚本与未引用的历史表文件不删除、不重算。

正文新写/调整句子如下，供人工检查：

- `Treating a positive component change as a positive prediction, IR improvement
  and SR change each match the prespecified behavioral criterion in 22 of the 24
  comparisons.`
- `The criterion labels a pair positive when stress success increases by at least
  five percentage points and clean success decreases by no more than five
  percentage points.`（把 Appendix G 的既有标签定义明确写入主文。）
- `Their pooled Spearman correlations with planning-success change are $0.854$
  and $0.913$, respectively; both remain positive after omitting any one task`
  （保留 Table 10 / Appendix G 引用；具体 LOTO ranges 仍在表内。）
- `These results show that both IR and SR remain informative under the tested
  blur and resize shifts.`

不新增固定阈值筛选、所有任务内均正相关或联合筛选优越性的主张。
TeX Live 2025 四步重建成功，已查看 PDF 第 9、22 页。主文 9 页、全文 25 页，
bibliography 逐字节不变，无未定义引用、BibTeX warning 或 overfull box。
已同步 `main.pdf`，未提交或推送。

## 2026-09-09 精简 4.4 对照选择说明

采用用户确认的句子：`Base+Control$_8$ reports the lowest test MAE among the
three action controls for each task and training run.` 将其放到三种动作对照
介绍之后，删除原段末 `For each task--run cell, ... making this a conservative
comparison.`。保留按测试 MAE 选择对照的事实，去掉评价性尾句；其他措辞、
实验数据和协议不变。本次不涉及 Related Work 的 `Finally`。

TeX Live 2025 完整四步重建成功：主文 9 页、全文 25 页，无未定义引用、
BibTeX warning 或 overfull box。已同步 `main.pdf`，未提交或推送。

## 2026-09-09 合并 4.3 结果段并明确 4.4 的实验意义

按用户批准，由 sol medium 实施。4.3 仅删除结果与总结之间的空行，保留
独立开头，全部句子逐字不变。4.4 保留协议、图和所有数值，新增/改写如下：

- 开头：`We test whether eight-step ACPC under the recorded actions provides
  additional information about how much a visual perturbation changes the world
  model's multi-step prediction error, $d=|e_{\tilde h}-e_h|$.`
- 原 ridge 拟合句前添加 `To estimate $d$,`，明确回归预测对象。
- 动作对照介绍后添加：`These controls test whether the recorded action
  information matters.`
- 原结果句在 `lowest cross-validated MAE` 后添加 `for estimating $d$`。
- 删除原末尾关于不比较跨时域 absolute prediction accuracy 的重复说明，
  换为：`Thus, eight-step ACPC under the recorded actions provides additional
  information about prediction-error change beyond the simple diagnostics and
  destroyed-action controls tested here.`

上述改动区分预测误差变化量与估计该变化量的 MAE，不声称世界模型自身预测
精度提高。TeX Live 2025 完整四步重建成功，已查看第 7 页：4.4 正文与图完整
位于同页；主文仍 9 页、全文 25 页。bibliography 逐字节不变，无未定义引用、
BibTeX warning 或 overfull box。已同步 `main.pdf`，未提交或推送。

## 2026-09-09 调整 4.3 的问题与联合考察结论

按用户确认，由 sol medium 将 4.3 调整为实验问题、SR 额外筛除的证据、
IR 与 SR 联合考察的意义。仅新增或改写以下两句：

- 开头：`We use the broad-severity experiment to test whether checkpoints that
  pass IR also preserve separation between the selected different-state rollouts.`
- 收尾（采用用户确认原文）：`These results support considering IR and SR together:
  low sensitivity to visual perturbations should be accompanied by preserved
  separation between the selected different-state rollouts.`

SR 额外筛除数量原句保留，在句末补 Figure 3 / Appendix D 引用。反方向通过
数量句与原末段 continuous-retention 分析逐字移至 Appendix D；0.458、0.532、
PushT 的 0.070 及解释边界全部保留。Figure 3 环境、尺寸、caption 不变，
没有改动实验数值或声称联合筛选已被证明具有更高行为预测准确率。

TeX Live 2025 完整四步重建成功，已查看 PDF 第 6、7 页并核对附录移入文本。
主文仍为 9 页；附录内容移入后全文由 24 页变为 25 页，未调整模板间距。
bibliography 与修改前逐字节一致（44 条），无未定义引用、BibTeX warning
或 overfull box。`main.pdf` 已同步，未提交或推送。

## 2026-09-09 删除 4.5 末尾重复的固定池范围说明

按用户确认，将 `Appendix I reports the full fixed-pool analysis; it does not
certify later adaptive rounds.` 缩为 `Appendix I reports the full fixed-pool
analysis.`（正文使用原有附录交叉引用）。仅删除分号后的重复说明，不新增表述。
4.5 前文关于 fixed-pool 与 adaptive CEM 的区别、理论条件及附录内容均不变。

已完成 TeX Live 2025 四步重建并查看 PDF 第 8 页。主文仍为 9 页、全文 24 页，
bibliography 与修改前逐字节一致，无未定义引用、BibTeX warning 或 overfull
box；`main.pdf` 已同步，未提交或推送。

## 2026-09-09 合并 4.7 短段并补回 4.8 表格引用

4.7 将 PLDM 实验介绍与趋势总结两句合为一段，原句措辞不变，在总结句末增加
`tab:pldm-all-levels` 引用，将原表格放到整段之后；表格内容及浮动参数不变。
4.8 在相关性结果段末增加 `tab:cross-stressor-components-v1` 和
`sec:appendix-cross-stressor` 引用，指向 Table 10 / Appendix G。
没有新增解释句、改写结论或改动任何数值；Table 11 仍保留在附录。

TeX Live 2025 完整四步重建成功，已查看 PDF 第 8、9 页：4.7 两句同段并正确
引用 Table 1，4.8 正确显示 Table 10 / Appendix G。主文仍为 9 页、全文 24 页，
bibliography 与修改前逐字节一致；无未定义引用、BibTeX warning 或 overfull
box。`main.pdf` 已同步，未提交或推送。

## 2026-09-09 删除 PLDM 小节的重复范围说明

按用户意见，删除 4.7 末句 `We do not transfer thresholds between model families,
so this result does not establish a shared calibrated decision boundary.`。
前一句 `A similar descriptive low-IR, high-SR pattern therefore appears in the
evaluated PLDM sweeps.` 逐字保留，没有另写收尾或增加跨模型阈值通用的主张。
开头关于不同 architecture / training recipe 的介绍、表格、实验协议和其他
内容不变。本次仅删句，无自行改写。

TeX Live 2025 完整四步重建并查看 PDF 第 9 页；主文仍为 9 页、全文 24 页，
bibliography 与修改前逐字节一致，无未定义引用、BibTeX warning 或 overfull
box。`main.pdf` 已同步，未提交或推送。

## 2026-09-09 定向删重与实施细节移入附录

用户批准后，由 sol medium 先实施三处定向调整：

- 删除 Discussion 的 `What is supported.` 段，所述结果仍完整保留于 4.4、4.5
  和 Conclusion；不改 Scope and limitations 正文。
- 4.5 删除 paired CEM 的初始 proposal、共享随机数、各自更新 elites 清单；
  Appendix I 已有完整说明，主文保留到该附录的引用，以及比较动机、指标定义、
  全部基线、回归划分与结果。
- 4.4 将具体噪声取值、两次扰动采样和零扰动 identity checks 的整句原样移入
  Appendix E；保留主文的八步时域、完整 recorded future、16 个轨迹组、
  15 组训练/1 组测试及同组样本不跨集合的说明。

不修改摘要、Related Work、理论、实验数值、参考文献或模板排版参数。

本次非原样移动的文字仅为：4.4 原段句末增加 Appendix E 引用；4.5 原有
`gives the CEM budget and sample counts` 增加 `protocol,`；Appendix E 将原有
重复的未增强 checkpoint / 噪声列表说明整理为 `The prediction-error analysis
uses only the unaugmented checkpoints.`，随后接入从主文原样搬来的采样细节句。

前三处调整后的 TeX Live 2025 完整四步重建已达到主文 9 页、全文 24 页，
Conclusion 完整落在第 9 页，因此未实施备选的 4.8 LOTO 范围删减，也未调整
图幅、浮动方式、模板间距或其他段落。

核验：已查看 PDF 第 7、8、9 页，并核对 Appendix E 中采样细节的实际输出。
摘要、Related Work、理论、4.8、Scope and limitations 及 Conclusion 逐字未改；
采样句仅移动且全文仍只出现一次。全部引用保留，bibliography 逐字节一致，
共 44 篇；无 undefined citation/reference、BibTeX warning 或 overfull box，
保留 underfull vbox 提示。`main.pdf` 已同步重建结果，未提交或推送。

## 2026-09-09 实质精简 PLDM 的介绍

用户指出上一版虽合为一句，仍重复“学习动力学—再使用动力学”。由 sol medium
改为单一主谓结构，保留 goal-conditioned planning、action-conditioned latent
dynamics、reward-free offline data 和 VICReg-inspired regularization，删除
重复的 `uses the learned dynamics` 及可由 latent dynamics 涵盖的泛称
`representations`。VICReg 的防坍塌作用已由紧邻前句说明，不在 PLDM 句内重复。
仅此一句变化，LeWM 和其他内容不改。

最终采用：`For goal-conditioned planning, PLDM learns action-conditioned latent
dynamics from reward-free offline data with VICReg-inspired regularization.`
保留 `sobal2025stresstesting` 引用；不计引用命令、按空白分词，23 → 15 词。

已用 TeX Live 2025 完整四步重建并查看 PDF 第 2 页；bibliography 与修改前
逐字节一致，无未定义引用、BibTeX warning 或 overfull box。主文仍为 10 页、
全文 25 页，`main.pdf` 已同步；未提交或推送。

## 2026-09-09 突出 LeWM 的 JEPA 属性与简洁训练目标

用户要求 LeWM 的介绍重点从像素输入和网络组件转到方法简洁性。由 sol medium
只调整 LeWM 一句，明确其 action-conditioned latent prediction / JEPA 属性，
以及 prediction loss 加 SIGReg 的两项目标，SIGReg 是唯一的防坍塌正则项。
原先 `from raw pixels` 仅描述输入，并不意味着预测像素；本次省去该输入细节，
避免分散读者对 latent prediction 的注意力。

依据 LeWM 原论文 Section 3 的 Training Objective：
https://arxiv.org/html/2603.19312v1 ，目标为 prediction loss + weighted SIGReg，
并明确不使用 stop-gradient、EMA 或额外稳定化 heuristics。正文不展开这些清单，
也不把“唯一防坍塌正则项”误写成“全部训练只用 SIGReg”。PLDM、其他正文、
引用和参考文献条目均不改。

最终采用的一句（省略展示引文命令）：`LeWM is an end-to-end JEPA world model
for action-conditioned latent prediction with a simple two-term objective: a next-step
latent prediction loss and LeJEPA's SIGReg as the sole anti-collapse regularizer.`

已用 TeX Live 2025 完整四步重建并查看 PDF 第 2 页；仅上述一句正文变化，
所有引用保留，bibliography 与修改前逐字节一致，无未定义引用、BibTeX warning
或 overfull box。主文仍为 10 页、全文 25 页，`main.pdf` 已同步；未提交或推送。

## 2026-09-09 将 PLDM 与 LeWM 的介绍分别合为一句

用户要求进一步精简，由 sol medium 分别合并 PLDM 和 LeWM 的工作介绍与
训练目标说明。只涉及这两个文本块；保留 VICReg → PLDM → LeWM/SIGReg →
VISReg 顺序，其他正文、全部引用、参考文献条目及排版参数不改。

最终两句（引文命令省略展示，正文保留原引用）：

- `PLDM learns representations and action-conditioned latent dynamics from reward-free
  offline trajectories, using VICReg-inspired anti-collapse regularization, then uses
  the learned dynamics for goal-conditioned planning.` 将独立的 training objective
  句合并为学习方式说明；保留数据来源、表示与动作条件动力学、正则化和规划。
- `LeWM supports stable end-to-end training of a visual encoder and action-conditioned
  latent predictor from raw pixels using next-step prediction and LeJEPA's anti-collapse
  regularizer SIGReg.` 删除 `presents a simple approach` 等引导，以及 Gaussian
  分布目标的展开解释；保留稳定端到端训练、像素输入、encoder/predictor、下一步
  预测、SIGReg 的 LeJEPA 来源与防坍塌作用，去掉末尾 `which` 从句。

核验：TeX Live 2025 完整四步重建并查看 PDF 第 2 页；这两个介绍块以外的正文
逐字不变，所有 citation keys 保留，bibliography 与修改前逐字节一致。无未定义
引用、BibTeX warning 或 overfull box。主文仍为 10 页、全文 25 页，`main.pdf`
已同步；未提交或推送。

## 2026-09-09 将 LeWM 原文移至 PLDM 之后

用户确认后，将 LeWM/SIGReg 的两句原文整体移到 PLDM 之后、VISReg 之前，
局部顺序为 VICReg → PLDM → LeWM/SIGReg → VISReg。两句及其引用逐字保留；
没有新写过渡句，没有改动其他正文、参考文献条目、实验数据或排版参数。

已程序核对：本轮 TeX 差异仅为该文本块的原样移动。TeX Live 2025 完整四步
重建成功，并查看 PDF 第 2 页；bibliography 与修改前逐字节一致，无未定义
引用、BibTeX warning 或 overfull box。主文仍为 10 页、全文 25 页，`main.pdf`
已同步，未提交或推送。

## 2026-09-09 调整 VICReg 与 PLDM 的介绍顺序

按用户确认，由 sol medium 将 VICReg 的简短方法介绍放到 PLDM 前面，先解释
方差与协方差正则化的作用，再介绍 PLDM 及其 VICReg-inspired objective。
PLDM 已确认的 reward-free offline learning / goal-conditioned planning 描述
逐字保留。LeWM/SIGReg 和 VISReg 原句不改，其他正文和参考文献条目不改。
本次不实施此前讨论的压页、图表浮动或段落删减方案。

本次自行调整的两处表述：

- 在 PLDM 前独立介绍：`VICReg prevents collapse with variance regularization
  and reduces feature redundancy with covariance regularization.` 保留 VICReg 引用。
- PLDM 工作介绍之后改为：`PLDM's training objective includes VICReg-inspired
  anti-collapse regularization.` 不将 VICReg-inspired 正则化误称为其全部训练目标。

已用 TeX Live 2025 完整四步重建并查看 PDF 第 2 页。参考文献与本次修改前
逐字节一致，无 undefined citation/reference、BibTeX warning 或 overfull box；
主文仍为 10 页、全文 25 页。`main.pdf` 已同步，未提交或推送。
用户随后提出的 LeWM 整块后移，此记录对应版本尚未实施。

## 2026-09-09 补回跨任务 screening 的结果引用

用户确认后，由 sol medium 合并 Checkpoint Screening across Tasks 中原有的
两个短段，保留实验目的句、two- and three-source settings 的适用范围及全部
数值，补回 `tab:cross-task-all-subsets` 和 `sec:appendix-cross-task` 交叉引用。
新增的来源说明为本次自行写作：`Full results for all 14 choices of source tasks
appear in Table 9 in Appendix F.`（表号和附录号使用交叉引用生成）；原有两句
逐字保留。

按用户要求，不在主文重复 single-source limitation；Appendix F 原有的全部
14 种任务划分结果、Reacher-only 阈值偏紧和接受偏晚的解释均保持不动。
保留该独立小节与附录表格的位置，不把多源任务的汇总结果泛化到所有划分。
新增三篇参考文献沿用上一条记录中已核实的发表类型、作者、年份与官方链接，
本次不再改写其条目或 Related Work。摘要、其他正文、实验数据和排版参数不改。

核验：TeX Live 2025 完整四步重建已完成，已查看 PDF 第 8 页，新增引用正确
显示为 Table 9 / Appendix F。bibliography 与本轮修改前逐字节一致，共 44 篇；
无 undefined citation/reference、BibTeX warning 或 overfull box，保留 underfull
vbox 提示。主文仍为 10 页、全文 25 页，`main.pdf` 已同步；未提交或推送。

## 2026-09-09 补充 VICReg、LeJEPA/SIGReg 与 VISReg

用户确认补充后，由 sol medium 只修改 Related Work 的 World Models 段，
主进程核对原论文与公开发表记录，并新增三个 BibTeX 条目。其他已有文献不改。

| 位置 | 最终采用表述 | 新拟措辞与边界 |
|---|---|---|
| LeWM objective | `Its objective pairs next-step latent prediction with LeJEPA's SIGReg, which encourages a Gaussian latent distribution to prevent collapse.` | 对原有 objective 句作最小调整，点明 SIGReg 的 LeJEPA 来源；保留已确认的 LeWM 主介绍。引用 `balestriero2025lejepa`。 |
| PLDM objective | `PLDM uses a VICReg-inspired anti-collapse objective, whose variance and covariance terms maintain feature variation and decorrelate features, respectively.` | 本次由 sol medium 新拟，补充 PLDM 与 VICReg 的关系。PLDM 原论文 Section 3.3 明确称 VICReg-inspired；不声称采用未经修改的 VICReg，也不声称这是其全部训练目标。引用 `bardes2022vicreg`。 |
| VISReg | `Separately, VISReg retains variance regularization but replaces VICReg's covariance regularization with Sliced-Wasserstein-based sketching.` | 本次由 sol medium 新拟，`Separately` 为新增衔接；将 VISReg 作为相关正则化研究介绍，不暗示 LeWM/PLDM 使用了它。保留的是 variance regularization 思路，不声称方差项公式完全相同。引用 `wu2026visreg`。 |

发表记录核对（2026-09-09 UTC）：

- VICReg：Adrien Bardes、Jean Ponce、Yann LeCun；正式发表于 ICLR 2022，
  使用 `@inproceedings`、2022 年和会议官网链接到的 OpenReview 条目，
  不按 2021 年 arXiv 预印本著录。依据
  https://iclr.cc/virtual/2022/poster/6481 和 https://arxiv.org/abs/2105.04906。
  OpenReview 正文访问出现浏览器验证，但其条目 URL 已由 ICLR 官网直接确认。
- LeJEPA：Randall Balestriero、Yann LeCun；作者官方仓库仍推荐 arXiv:2511.08544，
  2025 年。未找到可确认的正式会议/期刊发表记录，按已确认预印本著录；这不等于
  判断其没有投稿。依据 https://arxiv.org/abs/2511.08544 和
  https://github.com/galilai-group/lejepa 的 Citation。
- VISReg：Haiyu Wu、Randall Balestriero、Morgan Levine；作者项目页标为 arXiv，
  对应 arXiv:2606.02572、2026 年。按预印本著录，不将作者示例中的
  `@inproceedings` / `booktitle = arXiv` 误当成会议发表。依据
  https://arxiv.org/abs/2606.02572 和 https://haiyuwu.github.io/visreg/。

本轮不将 anti-collapse regularization 写成视觉鲁棒性或状态分离保证，不增加
ACPC 自我介绍。完整重建采用 TeX Live 2025 的 pdfLaTeX → BibTeX →
pdfLaTeX → pdfLaTeX；参考文献 41 → 44 篇，主文仍为 10 页、全文 25 页。
无 undefined citation/reference、BibTeX warning 或 overfull box，存在 underfull
vbox 提示；不改模板、图幅或浮动参数。已查看 PDF 第 2、3 页并核对三个
新增 bibliography 条目的实际输出，`main.pdf` 已同步。比较确认 World Models
段之外的 TeX 逐字不变、全部旧 BibTeX 条目逐字不变，没有删除旧引用。

用户另外提出的 Checkpoint Screening across Tasks 问题本轮只核查，尚未改动：
完整数据仍在 Appendix F / Table 9，主文两短段确实缺少该表与附录的引用。
建议保留主文核心结果、补回证据入口及简短的单一源任务局限；是否合并小节或
调整位置待用户确认，不擅自移入附录。

## 2026-09-09 Conclusion 收束调整

用户确认后，由 sol medium 将已审阅的三句替换到 Conclusion 后半段。
前两句 ACPC 定义与 prediction-error / planning-cost bounds 总结逐字保留。

| 位置 | 最终采用表述 | 来源与调整披露 |
|---|---|---|
| IR/SR 的作用 | `IR and SR serve complementary diagnostic roles: IR measures clean--perturbed rollout spread, while SR checks whether different states remain distinguishable after rollout.` | 由 sol medium 根据现有摘要与方法定义作概括，替换原先两个 sweep/severity regime 的详细复述。保留 IR 与 SR 的不同职责，不声称统计独立或 SR 已被证明提高筛选效果。 |
| LeWM 的结果 | `On LeWM, the IR--SR checkpoint screen transfers across tasks, and both diagnostics remain informative under blur and resize.` | 恢复摘要已有结果，并作轻量措辞衔接；明确 cross-task screening 与 blur/resize 结果属于 LeWM，不扩展到 PLDM。 |
| 跨模型结果 | `Across the evaluated checkpoints, LeWM and PLDM show similar trends in both IR and SR.` | 本次由 sol medium 新拟，明确相似趋势的两种模型与评估范围；不声称跨模型阈值迁移。 |

删除 Conclusion 中 `nonbinding`、`fixed conditions`、`harder Gaussian-severity
slices` 等实验细节复述，以及 `rather than as a universal performance certificate`
的否定式收尾。相关实验结果、负面结果和证书适用边界仍完整保留在 Results、
理论、附录与 Discussion 中；没有修改摘要、实验数据、其他章节或任何排版参数。

核验：与本次修改前的 source diff 仅涉及 Conclusion 后半段；已完成 TeX Live
2025 的 pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX 重建，并查看第 10 页。
Conclusion 正文由 11 行缩为 7 行；主文仍为 10 页，全文 25 页。`main.pdf`
已同步；bibliography 与修改前逐字节一致，无 undefined citation/reference、
BibTeX warning 或 overfull box，保留 underfull vbox 提示。按用户指示未继续压页。

## 2026-09-09 Experiments 三处定向去重

用户确认先精简 4.2 的图内容说明、4.3 的重复协议清单、4.4 的重复提问；
由 sol medium 实施，主进程核对 baseline diff，仅这三处实验正文变化。

| 位置 | 最终调整 | 保留的信息与改写披露 |
|---|---|---|
| 4.2 开场 | 将 Figure 2 引用接到 `Gaussian-noise augmentation recovers performance over a range of training levels whose location differs by task` 原句末尾，删除独立的 `compares success rate with IR and SR across the complete sweep` 图内容说明 | 只调整引用位置并删除与图注重复的说明；任务间恢复范围差异、Reacher clean-performance 数值及解释全部保留。 |
| 4.3 开场 | 保留 `We test whether this redundancy persists in the separate broad-severity experiment.`，删除 `without changing the rollout protocol, state-pair catalog, or thresholds` | 删除的清单已在 Evaluation Protocol 中说明；保留承接上一节 SR 冗余结果的实验动机。没有修改实际实验协议。 |
| 4.4 开场 | 两个重复提问合为 `We test whether ACPC helps predict how much a visual perturbation changes multi-step prediction error, $d=|e_{\tilde h}-e_h|$.` | 本次由 sol medium 作局部句子合并；保留原问题及完整的 error-change 定义，删除重复的 `measured ACPC is informative about` 和 `the bounded quantity` 同位语。ACPC 对该量的 bound 仍完整保留于 Section 3。Horizon、trajectory grouping、perturbation draws、controls 和结果均未改。 |

TeX Live 2025 完整重建并查看 PDF 第 6、7 页。按实际排版行统计，4.2 首段
5 → 4 行、4.3 开场 2 → 1 行、4.4 首段 8 → 7 行，合计回收 3 行。
当前 Conclusion 仍在第 10 页，全文 25 页；按用户指示未继续处理页数。
`main.pdf` 已同步重建结果；bibliography 与修改前逐字节一致，无 undefined
citation/reference、BibTeX warning 或 overfull box，保留 underfull vbox 提示。
没有更改图幅、浮动方式、模板间距、摘要、Related Work 或 Conclusion。
Conclusion 的新表述本轮仅供用户审阅，未实施。

## 2026-09-09 Related Work 叙述恢复

本次采用用户确认的三段样例及随后确认的 LeWM/PLDM 表述，由 sol medium
实施、主进程审核。只调整 Related Work；以下记录更新该节的当前状态，早期
条目中的措辞和行号保留作历史记录。

| 位置 | 恢复、删除或自行调整 | 来源与核查说明 |
|---|---|---|
| World Models：JEPA | 恢复 `learn representations by predicting targets in representation space rather than reconstructing pixels` | v2 原句恢复，保留原有四个 JEPA 引用。 |
| World Models：LeWM | 使用用户确认的两句：`LeWM presents a simple approach to stable end-to-end training of a visual encoder and an action-conditioned latent predictor from raw pixels.` 和 `Its objective pairs next-step latent prediction with a regularizer that encourages a Gaussian latent distribution to prevent collapse.` | 本次由 sol medium 根据原论文新拟，并经用户逐句确认；不是 v2 原句。依据 https://arxiv.org/html/2603.19312v1 的 Abstract 与 Section 3，保留 `maes2026lewm` 引用。 |
| World Models：PLDM | 使用用户确认的 `PLDM learns representations and action-conditioned latent dynamics from reward-free offline trajectories, then uses the learned dynamics for goal-conditioned planning.` | 本次由 sol medium 根据原论文新拟，并经用户确认；依据 https://arxiv.org/html/2502.14819v3 的 Section 3.3，保留 `sobal2025stresstesting` 引用。不再笼统称作另一种 architecture。 |
| World Models：预测学习研究 | 用 `Related work` 取代失去时间指代的 `Subsequent work`；将 `Theoretical analyses ask which features latent prediction retains` 单独成句 | 前者为最小衔接调整；后者组合 v2 的理论研究引导与当前稿的 feature-retention 表述。不恢复较难懂的 `high-influence features`，不增加新的理论结论。 |
| Robustness：方法介绍 | 恢复 v2 的 `Other methods change world-model training.`；将 DreamerPro、Denoised MDPs 和 temporal masking 的原有功能合并介绍；MWM 移入训练方法组 | 分类句为原句恢复。方法并列句是本次组合，`another approach` 为删减后新增连接；功能与引用保留。删除 `Most closely related`，不对文献接近程度作排序。 |
| Robustness：共同原则 | 恢复 `These methods reflect a broader principle: robustness should remove irrelevant visual variation without discarding distinctions needed for control.` | v2 原句恢复，用于承接随后 bisimulation 的介绍。ReOI 的 `instead` 也恢复自 v2，区分训练增强与测试时处理。 |
| Diagnostics：分类与具体描述 | 按 action information / rollout validity、prediction errors / visual attacks、certificates 的顺序组织；恢复 mismatch 到 downstream decisions 的原句及具体的 inverse-dynamics、kinematic failures、predicted/environment-produced transitions 和 predicted/true plan costs 描述 | 具体方法说明以 v2 为来源，保留各自原引用；不是把所有方法概括为同一功能，也不声称所有既有诊断都依赖真实未来。 |
| Diagnostics：新拟引导句 | `One group of diagnostics examines action information in learned transitions and the validity of long rollouts.`；`A second group measures prediction errors or tests world-model agents with visual attacks.` | 两句为 sol medium 本次新拟，已在用户确认的样例中披露。 |
| 三段中的本文介绍 | 删除 `We evaluate ACPC on...`、第一段末的本文定位、第二段 `ACPC measures...`、第三段 `our bounds...` 对比及末尾 `ACPC instead measures...` | 按用户确认方案删除重复自述，不新增全节 ACPC 收尾句。MWM、CARRL、CROP 的方法介绍和引用仍保留；本文 fixed-pool/paired-input 的理论条件与边界仍完整保留在方法、证明和 Discussion 中。 |

本次不改摘要、Introduction、理论推导、实验结论、数值、caption、图文件、图幅、
浮动方式、bibliography 源文件或模板间距。新增文字优先用于恢复文献之间的
关系，不通过进一步删引用回收空间。

重建状态：已执行 TeX Live 2025 的 pdfLaTeX → BibTeX → pdfLaTeX →
pdfLaTeX 完整流程，并同步到 `main.pdf`。Related Work 的 37 个 citation keys
集合不变；完整 bibliography 仍为原 41 条，重建的 `main.bbl` 与修改前逐字节
一致。无 undefined citation/reference、BibTeX warning 或 overfull box；有
underfull vbox 提示。

按 PDF 实际文字行统计（包含行内小标题，不含节标题和段间距）：World Models
由 12 行变为 14 行，Robustness 由 11 行变为 12 行，Diagnostics 由 13 行变为
16 行，合计增加 6 行。分页连带变化使 Conclusion 落到第 10 页，含 11 行正文
及节标题；当前主文为 10 页、全文 25 页，尚不满足九页限制。用户随后明确要求
先不处理页数，因此停止浮动位置试排，未改任何图表位置或已批准表述。
Experiments 本轮仅进行只读冗余识别，尚未实施删改。

## 2026-09-09 图幅与浮动位置调整

以更新后的 PDF 为准重新分配主文图幅，未改任何正文、caption、数据或图文件。

| 图 | 原宽度 / `linewidth` | 最终宽度 / `linewidth` | 浮动方式 | 最终页码 |
|---|---|---|---|---|
| Figure 1 | 0.80 | 1.00 | `[t]`，未变 | 2 |
| Figure 2 | 0.74 | 0.94 | `[t]`，未变 | 6 |
| Figure 3 | 0.54 | 0.46 | `[H]` 改为 `[htbp]` | 7 |
| Figure 4 | 0.74 | 0.74，未变 | `[H]`，未变 | 7 |
| Figure 5 | 0.64 | 0.54 | `[H]` 改为 `[htbp]` | 8 |

- Figure 1、2 的线性尺寸分别增加 25.0% 和 27.0%；Figure 3、5 分别缩小
  14.8% 和 15.6%。不裁剪图像，也未改图内数据或图中文字。
- 两个独立 Claude Code 会话均使用用户指定的 GLM-5.3[1m]、xhigh，通过仅写
  临时目录的脚本完成 18 组尺寸试排和 14 组尺寸/浮动方式试排。只改尺寸的
  方案均超页；其中 5 组允许 Figure 3、5 正常浮动的方案满足九页和图序检查。
- 主进程查看较大图幅候选的第 2、6、7、8、9 页后，选择本表参数：图 1、2
  的细字更易读，图 3、5 的数字、图例、标记仍可辨；Figure 3 在 Figure 4
  之前，Figure 5 仍位于对应 CEM 分析附近。
- `[htbp]` 仅允许 LaTeX 在邻近位置正常放置图，避免强制 `[H]` 引起的分页
  空白；模板的间距、字号、页边距均未改。主文仍为 9 页，完整 PDF 24 页。
- 正式稿重新执行 TeX Live 2025 的 pdfLaTeX/BibTeX 完整流程；参考文献内容
  不变，正文与 caption 无任何文字增删。这一节没有新写作或句子压缩。

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
