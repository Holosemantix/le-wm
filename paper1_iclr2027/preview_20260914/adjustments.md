# 候选稿修改记录（2026-09-14）

## 2026-09-16：PLDM 与 Blur/Resize 主文精简（用户确认）

- 删除主文独立的 PLDM 和 Blur/Resize 小节，在 4.2 LeWM 主结果末尾保留
  用户确认的两句短段，分别指向 Appendix C 和 G，不改 4.2 标题。
- PLDM 完整原段与 table_pldm_all_levels 输入移到 Appendix C 既有 PLDM
  protocol 后，新增 PLDM results 段标题；保留已有完整 sweep 图。
  原图注 main-text summary 改为明确引用该表，避免移动后指代失效。
- Blur/Resize 三段原文移至 Appendix G，替换原附录重复的配对数量和行为
  标准介绍；保留 component-wise reporting 的解释、图表、两个边界案例及
  ablation。移除搬迁后指向自身 Appendix G 的冗余引用，图表引用保留。
- 原小节标签移到对应附录位置，保留潜在引用入口。主文新增 Appendix C/G
  引用；摘要、贡献点、Discussion、Conclusion 不改，数据和图表内容不变。
- Appendix C 开头的 main tables 改为 reported results，以匹配表格搬迁。
- TeX Live 2025 全流程重建：主文回到 9 页，全文 24 页。已查看第 9、15、
  21 页并核对主文短段及附录引用；无未定义引用、重编译提示或 Overfull，
  有 4 处 Underfull vbox。未调整模板间距，正式 main.tex/main.pdf 哈希不变。
- 本轮未提交或推送。

## 2026-09-16：Related Work 段尾定位恢复（用户确认）

- 在 CARRL/CROP 后恢复原段尾两句，仅将 `Existing diagnostics` 改为
  `Some existing diagnostics`；第二句 ACPC 描述完整沿用原文。
- 删除 Vakalis/You 后此前加入的 `Pairwise ACPC instead ... without
  requiring the true future`，仅在全节末尾保留一次 ACPC 定位。
- 第三章引导、其他引用介绍及实验不动。本条取代此前段尾删除/段中定位方案。
- 已完成 TeX Live 2025 全流程重建并查看第 3 页：段尾两句与下一章排版正常。
  全文 24 页，主文 10 页；无未定义引用或 Overfull，余两处 Underfull vbox。
  正式稿未改。

## 2026-09-16：逐项合入后构建与差异核对

- 已用 TeX Live 2025 完成 pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX。
  全文 24 页，主文 10 页；第 10 页有 Discussion 尾部 4 行及 Conclusion
  标题与正文 7 行，尚未满足九页要求。没有调整模板或额外压缩文字。
- 最终编译无未定义引用、重编译提示或 Overfull；有 2 处 Underfull vbox。
- 已逐项对照远端 650ab62 的有效正文，剩余差异仅为已确认的 Related Work、
  3.3 收束、实验总览移位与范围措辞、两处附录入口、对照选择规则移至附录，
  以及不影响内容的源码折行。未遗漏远端其他有效正文改动。
- 正式 main.tex/main.pdf 的 SHA-256 与此前记录一致，远端另存文件保持原样。
  本轮构建和写作核对不替代内部已有的计算口径核查记录。

## 2026-09-16：实验修订第 11 项——Discussion（用户确认）

- 完整采用远端 650ab62 的 Discussion 正文，不额外改写；标题、标签及
  Conclusion 保持不变。分别交代 relative IR、IR normalization、SR pairing
  的要求，保留远端对实验范围与阈值搜索边界的说明。
- 远端实验与 Discussion 的逐项处理完成；继续核对有效正文差异及构建。
  正式稿未改，不推送。

## 2026-09-16：实验修订第 10 项——Blur/Resize（用户确认）

- 完整采用远端 650ab62 的 Diagnostics under Blur and Resize 标题与三段
  正文，不额外改写；保留 sec:exp-cross-stressor 标签。
- IR/SR 改善定义、24 组比较、22/24、0.854/0.913、blur/resize 参数及行为
  标准数值不变；图、表、附录引用均保留，不修改对应图表或数据。
- 本次仅更新候选 TeX 与记录，Discussion 等其他章节不动；候选 PDF 尚未
  重建，正式稿未改，未推送。下一项 Discussion 待审核。

## 2026-09-16：实验修订第 9 项——Cross-Task Screening（用户确认）

- 完整采用远端 650ab62 的 Cross-Task Checkpoint Screening 标题和两段
  正文，不另加第二次 With two or three source tasks，不额外润色。
- 保留 sec:exp-frozen-external 标签、表格及附录引用；0.5 grid steps、
  最大一步、步长 0.01 与 BA/P/R 的全部远端数值原样保留，不修改数据或表格。
- 本次仅更新候选 TeX 与记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-16：实验修订第 8 项——CEM 远端写作（用户确认）

- 按用户最终选择采用远端 650ab62 的 CEM 小节正文，包括其时域解释；
  仅补回已确认的 Appendix~ref{sec:appendix-planner-protocol} 协议入口。
- 不补回 2.0 个百分点标准差，不改变图表、公式或数值，不新增论文核查说明。
- 用户确认原有时域口径一致；此前代码核查与该口径的冲突记录仅保留在
  内部，本轮写作合入不构成独立计算验证，不据此注销此前核查结果。
- 候选 PDF 未重建，正式稿未改，未推送。下一项 Cross-Task Screening 待审核。

## 2026-09-16：实验修订第 7 项——Prediction-Error Change（用户确认）

- 采用远端 650ab62 本节正文及结果措辞，不重新润色；保留原图、图注、
  标签、55.9±4.7%、51.3±3.5% 和 12 个 task--run 的原结果。
- 主文保留远端 best-performing 表述；将原句 `Base+Control$_8$ reports
  the lowest test MAE among the three action controls for each task and
  training run.` 移至 Prediction-Error Scope and Controls 附录的采样说明后、
  两张结果表介绍前，解释表注中的 per-cell oracle，不改变选择规则。
- 主文 cross-validation 段末恢复 Appendix~ref{sec:appendix-p1-controls}
  引用，其他正文沿用远端。表格与数据不变，后续 CEM 小节未动。
- 本次仅更新候选 TeX 与记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-16：实验修订第 6 项——Broad-Severity（用户确认）

- 完整采用远端 650ab62 的 IR and SR at Broader Evaluation Noise Levels
  小节，包括标题、开头、结果段和结尾，不额外加入 selected 或替换总结。
- 保留全部数值宏、图文件、图注、标签及附录引用；不改变实验数据与协议。
- 不采用此前建议的旧联合解读结尾，本条记录用户最终确认的远端版本。
- 本次仅更新候选 TeX 和记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-16：实验修订第 5 项——Gaussian performance（用户确认）

- 采用远端 Gaussian-Noise Performance and IR--SR Diagnostics 标题及两段
  正文，先介绍 planning success，再介绍 IR/SR；仅源码折行有所不同。
- 保留 Reacher clean success 59.2% 与 76--82%、108 行、77 个 IR 通过者及
  全部同时通过 SR 的结果；阈值数值不变，符号采用远端的 tau，与 3.5 一致。
- 保留 sec:exp-gaussian-panel 标签与 fig:full-sweep-diagnostics 引用，图表、
  数据及下一小节不变，无需改动关联引用。
- 本次仅更新候选 TeX 与记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-16：实验修订第 4 项——训练增强介绍（用户确认）

- 原样采用远端 650ab62 的训练增强段，交代用 Gaussian-noise augmentation
  构造不同扰动响应的 checkpoints，并明确 sigma_max 是训练噪声上限。
- 九个训练条件、Uniform 分布、固定评估噪声 0.08 和 clean goal 均不变。
- 任务介绍、Diagnostic Protocol、Broad-Severity Protocol 已与远端一致，
  不再修改；Threshold Protocol 沿用第 1 项已确认内容。
- 只更新候选 TeX 和记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-16：实验修订第 3 项——实验总览（用户确认）

- 采用远端 Experiments 开头的 pair-level/checkpoint-level 两层总览。
  checkpoint 句使用已确认文本：`we test whether IR and SR track control
  performance and whether this relationship transfers across tasks, evaluation
  noise levels, model architectures, and visual shifts`。
- 保留 transfers，但对象限定为诊断与性能的关系，不称固定 screening
  阈值跨架构或跨扰动迁移。其余总览沿用远端原文。
- 移除 3.5 末尾 `Our experiments therefore evaluate ACPC at two levels ...`
  的重复实验总览；保留此前完整的 screening 定义、源任务校准及经验性质说明。
- 下一步按完整远端差异清单逐项审核 Evaluation Protocol 其余部分及后续
  实验章节，本次不一并修改。候选 PDF 未重建，正式稿未改，未推送。

## 2026-09-16：实验修订第 2 项——PLDM（用户确认）

- 原样采用远端 650ab62 的 PLDM 段落，以 `To test whether the diagnostics
  are specific to LeWM` 说明实验目的，保留 qualitative pattern 与
  `tab:pldm-all-levels` 引用。不另行润色。
- 小节标题、标签、表格输入、数据及其他章节不变；不引入跨架构阈值迁移
  或严格单调关系的主张。
- 本次仅更新候选 TeX 和记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-16：实验修订第 1 项——Threshold Protocol（用户确认）

- 采用远端 650ab62 新候选文件的原文：公式改为独立显示并以句号结束，
  clean-performance 条件用 `We additionally require that ...` 单独陈述。
- 保留远端 robustness criterion 用词，不采用此前提出的 satisfies both
  conditions 等重写方案；公式数值与两项实际要求不变。
- 本项不合入其他远端改动，保留本地 Related Work 和 3.3 收束句。
  候选 PDF 尚未重建，正式稿未改，未推送。

## 2026-09-15：逐项审核第 2 项——ACPC 对比定位（用户确认）

- 在 Vakalis/You 的模型预测与环境结果、真实 plan cost 比较之后加入：
  `Pairwise ACPC instead compares clean and perturbed predictions under the
  same action sequence, without requiring the true future.`
- instead 的比较对象限于紧邻的模型—环境比较，不概括整节方法；Pairwise
  限定无需真实未来的计算范围，不延伸到 IR/SR 归一化、配对或阈值校准。
- 与 3.1 相同动作下比较预测、3.2 无需 observed future 的现有说明一致，
  其他章节无需改写；保留第三章原有引导，不恢复段尾的重复理论总结。
- 后续 visual attacks 与 formal certificates 原句、全部文献引用不变。
- 本次仅更新候选 TeX 和记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-15：逐项审核第 1 项——恢复 CARRL/CROP（用户确认）

- 恢复 WMAttack/ARB4WM 后的 formal robustness certificates 介绍，沿用原句，
  仅省略 `through functional smoothing`。CROP 明确保留 `lower bounds on
  finite-horizon cumulative reward`，不再泛写 reward bounds。
- 两篇原有 citep 引用恢复，references.bib 条目已存在，无需修改其他章节。
  此处只介绍相关工作的认证对象，不恢复本文已删除的 selection/elite/CEM
  保证，也不把本文的代价变化界称为策略认证。
- 保留原有类别切换 `Complementary reinforcement learning work`；攻击类
  介绍与下一节原有 ACPC 引导均不改，不额外添加衔接。
- 本条取代此前删除该组引用的决定。ACPC 对比定位句仍待下一项单独审核，
  不在本次一并恢复或改写。
- 本次仅更新候选 TeX 与记录；PDF 尚未重建，正式稿未改，未推送。

## 2026-09-15：删除可选的策略认证背景（用户条件授权）

- 核查候选稿及 appendix_extension：CARRL/CROP 仅在 Related Work 的正式
  认证介绍中被引用，没有方法、证明或实验依赖；历史注释中的旧句不参与编译。
- 当前论文已删除动作选择/elite/CEM 等价认证支线，保留的是预测误差和
  planner-cost 变化界。因此判断该组为可选背景，而非必须比较的直接工作。
- 删除从 `Complementary reinforcement learning work ...` 到 CROP reward
  bounds 的整句；保留 WMAttack/ARB4WM 及第三章原有引导，不新增过渡。
- 仅移除候选稿正文引用，references.bib 中两篇条目及正式稿均保留，便于恢复。
  不将此判断表述为保证审稿人不会质疑，也不据此贬低两篇工作质量。
- TeX Live 2025 全流程重建完成，无未定义引用或 Overfull；有 4 处 Underfull
  vbox 提示。参考文献表由 44 条减至 42 条。全文仍为 24 页，主文仍为
  10 页，第 10 页仍有结论 3 行；未调整模板。未推送。

## 2026-09-15：Related Work 最终复查与尾部删减（用户确认）

- 复查与 e2dfbad 的源码差异：此前非必要引用改写已恢复，保留分类重排、
  短衔接、共同原则措辞调整及 MWM 恢复，不继续改写前两部分或扩写 Diagnostics。
- 按用户指定将 CROP 介绍尾部收为 `per-state actions and finite-horizon
  reward bounds`，保留 formal certificates 引导、CARRL 原句及两篇引用。
- 完全删除 `Existing diagnostics evaluate ...` 与 `ACPC instead measures ...`
  两句重复总结，不新增替代过渡。下一节原有 ACPC 引导完整保留。
- WMAttack/ARB4WM 及 Diagnostics 前半段不动；所有引用保留。
- TeX Live 2025 全流程重建完成，引用已稳定，无未定义引用或 Overfull；
  余两处 Underfull vbox 提示。已查看第 3 页，段尾与第三章开头衔接、排版正常。
- 同口径（不计标题和引用）词数为 World Models 146、Robustness 187、
  Diagnostics 173，合计 506；相比上一轮 PDF 的 546 减少 40，
  相比远端 e2dfbad 的 526 减少 20。相关工作引用由 39 增至 40，仅加回 MWM。
- PDF 全文 24 页，主文仍 10 页，第 10 页回到仅剩结论 3 行；未调整模板间距。
  正式稿未改，本轮未推送。

## 2026-09-15：保留重排、恢复原引用表述（用户授权）

- 按修改前候选稿（e2dfbad）恢复 PLDM、LeWM、Van Assel/Littwin、ReOI、
  ATM 的原句；恢复 Vakalis/You 的原有合并介绍及 citep，不再保留点名扩写。
- VICReg 恢复独立原句（variance 防 collapse、covariance 降低冗余），移至
  Tang 之后、VISReg 之前，不再挤入 PLDM 介绍。PLDM/LeWM 仍连续出现。
- Tang 恢复 `Related work studies collapse in self-predictive learning` 原有
  子句，因分类需要独立成句；Khetarpal 保留短引导 `Complementary work
  studies the role of action conditioning`。不恢复此前的宽泛 challenge 改写。
- 保留 Schäfer 前 `At the rollout level`，其余介绍沿用原文。
- 保留已确认的共同原则准确性调整，以及 MWM 独立分类与 post-training
  介绍。MWM 不机械恢复正式稿的 enforces：当前 improve 表述更贴近已核对
  原论文的训练目的；这是恢复遗漏文献所保留的局部措辞例外。
- 本条取代此前相应改写方案，历史记录保留供对照。所有既有引用保留，
  加回 MWM；后半段 attacks、certificates、ACPC positioning 不动。
- 本次更新候选 TeX 与记录；PDF 尚未按本次恢复重建，正式稿未改，未推送。

## 2026-09-15：新增措辞可读性返修（用户授权）

- Diagnostics motivation 恢复原有 `This objective mismatch ...` 与
  `More broadly ...` 两句，不再使用此前堆叠 evaluation 的合并句；
  Lambert 开头与 Wei/Yu 引用均保留。
- 删除新增的 `Other diagnostics compare multi-step predictions with outcomes
  from the environment.`，避免与下一句重复。
- Operator-on-F 保留方法名称与引用，但恢复原有核心比较措辞：
  `compares predicted multi-step latent transitions with those produced by
  the environment`；不再引入 selected observable functions 等未解释术语。
  You 的 predicted/true plan-cost 对比及引用保留。
- MWM 的分类引导收为 `In a related training-time approach, MWM ...`，
  保留 post-training、action-conditioned consistency 和 multi-step predictions，
  不再先泛说一次 targets rollout consistency。
- 已确认的整体顺序、其余原句和所有引用保留。此条更新取代此前关于
  motivation 合并、Operator-on-F 扩写及 MWM 独立引导的对应记录。
- 本次仅修改候选 TeX 和记录；PDF 尚未按此返修重建，正式稿未改，未推送。

## 2026-09-15：Diagnostics 前半段（用户确认）

- Motivation 第一原句保留，后两句合并为 `This objective mismatch has
  motivated decision-aware model learning and evaluation ... , with evaluation
  criteria aligned with the model's intended decision-making use ...`，
  保留 Wei 与 Yu 各自引用。
- ATM 与 inverse-dynamics probes 通过 while 合并；Schäfer 介绍独立成句，
  仅增加 `At the rollout level` 引导，保留原有 long imagined rollouts 措辞。
- 原 Some methods 句改为已确认的两句：`Other diagnostics compare multi-step
  predictions with outcomes from the environment. Operator-on-F ... compares
  predicted and environment-generated latent transitions over multiple steps
  using selected observable functions, while ... analyze discrepancies between
  predicted and true plan costs.` 保留 Vakalis 与 You 引用，You 使用 citet。
- 不采用 latent pushforward 或 environment-grounded counterparts；分类用于
  区分检查对象，不宣称最后一组独有环境参照。后半段 attacks、certificates、
  ACPC positioning 及其引用均未动。
- 本次只更新候选 TeX 和记录；PDF 未重建，正式稿未改，未推送。

## 2026-09-15：Robustness 局部调整与 MWM 恢复（用户确认）

- ReOI 保留移除干扰物、预测、放回的流程；将 `time, removing` 改为
  `time by removing`，`then reintroducing them after prediction` 改为
  `reintroducing them afterward`。
- 共同原则改为 `These approaches reflect a common principle: reducing the
  influence of visual differences that do not affect control while preserving
  distinctions that do.`，不再使用 discarding 或必要条件式的 requires。
- 在 reward-free bisimulation 介绍之后恢复 yan2026mwm 引用，单独分类：
  `A related training-time direction targets rollout consistency directly:
  MWM uses post-training to improve action-conditioned consistency over
  multi-step world-model predictions.` 不将 MWM 归入视觉干扰表征学习方法，
  不增加 ACPC 对比或 few-step diffusion 支线。
- 已依据 ReOI（arXiv:2506.16565）和 MWM（arXiv:2603.07799）原论文摘要
  核对上述操作流程与训练定位。其余原句、Diagnostics、实验及正式稿不动。
- 本次候选 TeX 与记录已更新；PDF 未重建，未推送。此前 MWM 待恢复项已完成。

## 2026-09-15：World Models 叙事顺序（用户确认）

- 顺序改为 world models → JEPA → PLDM/LeWM → collapse → VISReg →
  action conditioning / feature learning / seq-JEPA，不删除本段文献引用。
- VICReg 独立介绍并入 PLDM：写明 variance--covariance regularization
  与防 collapse 的用途；保留 reward-free offline data、action-conditioned
  latent dynamics 和 goal-conditioned planning。
- LeWM 保留 two-term objective 和 SIGReg 为唯一 anti-collapse regularizer，
  仅将 `which serves as` 收为 `as`；不引入 instead 或 from pixels。
- 新增概括引导 `Representation collapse is a broader challenge in
  self-predictive learning`，沿用 Tang 引用，并将 VISReg 原有技术说明置于其后。
- 原 action-conditioning 介绍改以 `Complementary work studies` 开头；
  理论介绍改为 `Theoretical analyses examine how latent prediction shapes
  the features learned`。seq-JEPA 原句不变。
- 本次只改候选稿 World Models 和本记录；后两部分及待恢复的 MWM 留待
  后续逐项处理。PDF 未重建，正式稿未改，未推送。

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
