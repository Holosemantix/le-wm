# 候选稿修改记录（2026-09-14）

## 2026-09-15：3.3 结尾收束（用户确认）

- 在原有证明引用前补入用户确认的概括句：`This result connects ACPC
  to changes in the planner's predicted cost under the same action sequence.`
- 不讨论上界松紧或大小关系，不恢复 selection/CEM 推论；3.4 原有引导不变。
- 已按用户后续要求用 TeX Live 2025 全流程重建候选 PDF；全文仍为 24 页，
  主文仍为 10 页，第 10 页仍仅结论 3 行。没有未定义引用或 Overfull 警告，
  已查看第 5 页，新增收束句及下一小节排版正常。正式稿未改。

## 2026-09-15：理论收束，第 1 项（用户逐项确认）

- 仅修改 3.3 标题与引导段；后续各项尚未执行。
- 标题 `Selection Stability from Planner-Cost Bounds` 改为
  `Planner-Cost Sensitivity`。
- 第二句仅将 `can also affect the planner's decision` 替换为
  `also bounds changes in planner cost`；其他措辞保留。
- 删除引导段最后一句 `If the resulting cost changes are smaller than the
  cost gaps between candidates, the selected action sequence is preserved.`
- 未新增衔接句；下一段 `For each candidate action sequence` 保持不变。
- 本项仅更新候选 TeX，PDF 尚未重建，正式主文未修改。

## 2026-09-15：理论收束，第 2 项（用户逐项确认）

- 保留两个预测终点的定义及原有解释、固定 goal 和两种代价的定义，
  以及 `The difference ...` 解释句，未自行润色或新增衔接。
- 删除命题前 `Their terminal displacement is` 起至 r_j 的 ACPC 上界
  止的中间推导；后续第 4 项审核时将该关系用于新证明。
- 正式 Proposition 改为 `Planner-cost sensitivity`，定义
  A_j=ACPC_H(h,tilde h,a^j)，在 alpha_H>0 下给出显式 ACPC 代价变化界。
- 删除原命题的 b_j 定义及 fixed-pool regret 界。
- 命题和代价界 label 暂保留，统一引用清理待第 13 项。
- 第 3 项的旧命题后解释、附录旧证明及 regret 公式引用尚未调整；
  当前为逐项修订中的中间状态，不作为完整一致版本发布。
- 未重建 PDF，未修改正式主文。

## 2026-09-15：理论收束，第 3 项（用户逐项确认）

- 删除新规划代价命题之后，从 `The bound b_j is computed directly ...`
  至 `not its return in the environment.` 的旧证书解释整块，包含
  winner margin 条件、elite 保持和 paired CEM 保证。
- 未新增替代段落，未自行改写；下一节标题及 `Pairwise ACPC measures ...`
  原有引导、IR/SR 定义保持不变。
- 第 1、2 项已获用户确认通过。
- 后续待处理：第 4–5 项附录证明、旧 regret/selection/CEM 推论与 tightness；
  第 6–8 项实验引导、证书结果和表引用；第 9–12 项全文关联表述；
  第 13 项公式/命题交叉引用、宏清理及构建。不得将当前中间稿视为完成稿。
- 正式主文与 PDF 未改动，实验数据和原表文件未删除。

## 2026-09-15：理论收束，第 4 项（用户逐项确认）

- 按用户审核样例替换附录规划代价证明：定义 r 和 A，从 alpha_H r^2<=A^2
  得到终点位移界，再用原平方距离分解证明显式 ACPC 代价变化界。
- 删除该证明中的旧 fixed-pool regret、winner 与 elite 推导；
  预测误差证明未改，独立 selection/CEM 结果及 CEM 证明仍待第 5 项。
- 用户要求同步主文引用：3.3 命题后仅补
  `The proof is given in Appendix~\ref{sec:appendix-acpc-proofs}.`
  复用 3.2 已有表述；附录证明标题仍用 Cref 指回同一个正文命题 label。
- 已核对目标附录 section label 与正文命题 label 各有唯一有效定义。
- 第 5 项须同时处理附录标题 `Proofs and Fixed-Pool Analysis` 中的旧分析定位。
- 本项仅变更候选 TeX 与记录；PDF 未重建，正式主文未改。

## 2026-09-15：理论收束，第 5 项（用户逐项确认）

- 附录标题改为 `Proofs`，保留 sec:appendix-acpc-proofs，主文 3.2/3.3
  的证明引用无需更换目标。
- 删除旧 fixed-pool selection 命题及其引导、Conditional CEM stability
  推论及其完整证明；删除 Relation to ACPC 旧证书解释。
- Tightness 标题限定为 prediction-error bound；删除 Both bounds 总括及
  旧规划代价界等号例子，预测误差等号例子的原句、公式与引用保留。
- 两个已确认的证明均保持原文。未新增衔接或替代说明；附录按正文命题
  顺序连续排列，然后保留预测误差界等号例子，下一附录内容未动。
- 引用检查：本项删除的命题/推论/公式 label 不应再有引用；主文两处附录
  引用和两个证明标题保持对应。其他旧证书实验/总览/讨论仍按第 6–13 项处理。
- 未重建 PDF，未改正式主文、实验数据或原表文件。

## 2026-09-15：理论收束，第 6 项（用户逐项确认）

- 4.5 删除 `The fixed-pool bound motivates this comparison.` 及后续
  elite 分歧、run-level certificate 对比。最初裁剪出的
  `We evaluate full paired CEM runs.` 经用户再次审核后也整句删除，
  不保留 therefore，不新增替代句；最终直接接原 candidate pool 说明。
- 问题引入、两条计划定义、selection regret 目标、回归协议、图、数值和
  附录协议引用均未修改；未自行改写其余句子。
- 已核对最终衔接为问题→两条计划与测量目标→候选池汇总及回归；
  具体 paired CEM 设置保留于附录，原有附录协议引用不动。
- 第 7 项仍须处理本节末尾旧证书覆盖率；第 8 项须同步附录标题、协议及
  cost 尺度/实际时域；第 9–12 项须处理总览/摘要/讨论等已列关联内容。
- 正式主文未改，PDF 未重建。本项不代表全稿关联清理已完成。

## 2026-09-15：理论收束，第 7 项（用户逐项确认）

- 删除 4.5 末尾 `On fixed first-round CEM candidate pools` 起的旧 top-1
  覆盖率结果，以及 `reports the full fixed-pool analysis` 附录引导。
- 原回归结果句、15.2%/2.0/12 数值、图及图引用均未修改；本项没有新增句子。
- 本节前段指向 CEM protocol/budget/sample counts 的附录引用保留，
  下一节 Checkpoint Screening across Tasks 及其原有引导未改。
- 第 8 项待同步附录证书分析、表引用及标题，并核对 cost 尺度/实际时域；
  第 13 项清理不再使用的证书宏。原实验数据和表文件保留。
- 正式主文与 PDF 未改，当前仍是逐项修订中的候选稿。

## 2026-09-15：理论收束，第 8a 项（用户逐项确认）

- 附录标题删除 `Fixed-Pool Certificates and`，保留
  `Adaptive-CEM Selection Regret` 和 sec:appendix-planner-protocol。
- 删除 `For the fixed-pool certificate analysis` 整段及紧接的证书表 input、
  专用 FloatBarrier；未删除实际表文件或实验数据。
- 保留其余实验设置、代价段、诊断与回归目标、统计方法原句，不新增衔接。
- 主文 4.5 的协议引用仍指向同一附录，证书表不再被候选稿加载或引用。
- 第 8b 项未执行：cost sum/mean、旧尺度段的证书表述、实际时域及
  H1/H5 字段含义、15.2% 的解释须依据已有纠错记录单独审核，再配套对齐
  主文、图及附录。不能把本项保留原句视为其准确性已通过。
- 第 13 项仍须清理未使用的证书宏。正式主文和 PDF 未改。

## 2026-09-15：第 8 项后续，仅清理旧理论关联（用户逐项确认）

- 用户明确限定当前工作为写作逻辑修改：第 8b 项的 cost 公式、时域、
  数值及图适配暂停，未执行任何这类修改；不把待核实记录视为本轮改稿授权。
- 仅删除附录 cost 定义后的两句原文：`This differs from the summed squared
  cost ...` 与 `The factor rescales every ... selection certificates remain
  unchanged.`，清除它们对旧 b_j、regret bound 和 selection certificates 的依赖。
- cost 定义及公式原样保留，随后直接接原有 `For each CEM run, we compute
  ACPC ...`。未新增句子，未改实验数据、结果数字、图或其他协议表述。
- 主文 4.5 指向该实验协议附录的引用保留；本次仅移除附录中已失去对应
  旧尺度/证书论述的 Proposition 引用，不动正文命题和证明之间的引用。
- 既有 cost/时域核查记录保留为待核实事项，不据本次删除宣称全稿数值口径
  已核验一致。正式主文和 PDF 未改；后续按第 9–13 项继续逐项审核。

## 2026-09-15：理论收束，第 9 项（用户逐项确认）

- 第三章总览仅删除 `, yielding conditions under which the planner's
  selected action sequence is preserved`，在 planner cost 后以句号收束。
- 总览其余原句完整保留，不新增章节引用或衔接句；原有
  `To summarize ACPC across a checkpoint` 承接 pairwise 结果至 IR/SR。
- 已核对 Introduction 的图、第三章、两个命题和实验章节引用目标仍存在，
  第二项贡献的 shared-action 条件与新命题对应；Introduction 未改。
- 两个命题、IR/SR 和 screening 小节均保留，总览不再承诺已删除的选择
  稳定性条件。PDF 编号与点击跳转留待第 13 项实际重建核验。
- 第 10–12 项仍待逐项审核；不改实验数据、数值、图或 cost 公式。

## 2026-09-15：理论收束，第 10 项（用户逐项确认）

- 用户选择此前呈现的第二句解释：`the change in predicted cost caused by
  a visual perturbation under the same action sequence`。
- 摘要仅将 i.e. 后原有 `the additional predicted cost caused by a
  perturbation-induced change in the planner-selected action sequence`
  替换为上述确认文本；不删除 i.e.，不改其他摘要句子。
- 未采用讨论中的 predicted goal cost、平方距离解释等其他候选写法。
- 新解释保持动作序列不变，与主文规划代价命题的比较条件对应；后续
  `Building on pairwise ACPC` 和 IR/SR 引导保持不变。
- 正式主文、PDF、实验数据与结果数值未改。第 11–13 项仍待逐项审核。

## 2026-09-15：用户单独确认的 MAE 措辞调整

- 4.4 的 `It reduces held-out MAE by` 改为
  `It reduces cross-validated MAE by`，沿用前一句的指标名称。
- 第三章 `held-out tasks` 保留；未采用 test MAE 或仅 the MAE 等讨论候选。
- 数值、其他原句与引用未改，PDF 未重建。继续按原清单审核第 11 项。

## 2026-09-15：理论收束，第 11 项（用户逐项确认）

- Discussion 仅删除 `The adaptive-CEM guarantee applies only while its bound
  verifies that both runs select the same elite candidates.`，与第 3、5 项
  已移除的 CEM 保证及推论同步。
- 其余原文不改；规划经验实验范围之后直接接 IR/SR screen 的使用条件，
  未新增衔接句。保留模型代价与任务成功的区分及原 screening 限制。
- 第 12 项贡献/Conclusion 核对、第 13 项引用/宏/构建仍待逐项审核。
- 正式主文、PDF、实验数据、数值及图未改。

## 2026-09-15：理论收束，第 12–13 项（用户逐项确认）

- 第 12 项核对 Introduction 贡献点与 Conclusion：保持现有原句，不新增改写。
- 第 13 项仅清理未使用的 corollary 环境声明，以及已不使用的
  `vTwoPlannerCertificateMacros`、`vTwoPlannerCertificateTable` 和对应宏输入。
  保留仍有效的命题内部标签；不删除历史表格或数据文件。
- 用 TeX Live 2025 完成 pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX，
  输出 `writing_preview.pdf`：全文 24 页，主文 10 页，第 10 页仅有结论 3 行。
  本轮未擅自压缩正文或调整模板间距，九页篇幅问题留待单独确认处理。
- 最终编译没有未定义引用、重复标签、重编译提示或 Overfull 警告；
  有 4 处 Underfull vbox 提示，不代表内容越界。参考文献表有 43 条。
- 已查看 PDF 第 4、5、9、10、14 页，检查命题、证明和结论的实际排版。
  PDF 链接目标核对：Introduction 的 Proposition 1/2 分别指向第 4/5 页，
  主文两个证明引用指向第 14 页 Appendix A，证明中的反向引用也对应正确。
- 正式 main.tex、main.pdf 及 ICLR 模板 sty/bst 的 SHA-256 与构建前相同。
  本次只更新候选稿及其构建产物，不替换正式稿、不推送远端。
- 本轮结论限于已批准的写作收束、引用和构建核验。此前记录的数据尺度与
  时域事项按用户要求未改动，不据此宣称这些科学口径问题已经解决。

## 原候选稿修正记录（2026-09-14）

来源：`/opt/huawei/explorer-env/30cec9fe-2612-4030-9e2f-6aa449992828.tex`。
可编辑候选稿：`writing_preview.tex`，不替换正式 `main.tex`。

本轮仅按用户确认修正：

- 3.1：ACPC 展开式和 encoder shift 的单竖线恢复为双竖线范数。
- 3.1：公式 label 从 `eq` 恢复为 `eq:acpc-h`，修复附录两处引用。
- 3.3：代价界中两个向量范数恢复双竖线。
- 3.4：`distance exceeds the IR threshold by a margin` 改为
  `distance exceeds raw IR by a margin`，区分 raw IR 与筛选阈值。

3.5 和其余尚待用户决定的修改均不调整；不改原始上传文件、摘要或正式稿件。
候选稿依赖上级目录现有模板、图表、参考文献和 appendix_extension.tex。
从 `paper1_iclr2027` 目录用 TeX Live 2025 执行 pdfLaTeX → BibTeX →
pdfLaTeX → pdfLaTeX，输出到 `preview_20260914`。

后续建议：继续在候选稿修订；其余问题和篇幅处理经确认后，再将候选稿统一
替换正式 main.tex，按正式 build.sh 重建 main.pdf，并核对引用、页数及差异。
