# Candidate replacement blocks

These blocks are proposals only. They are not yet integrated into
`paper1/main.tex`.

## Abstract

Preserve the concise v1 abstract. The broad-severity experiment strengthens
the existing checkpoint-level evidence but does not change the paper's central
contribution or strongest headline result. Its factorial design, exposure-ratio
adjustment, and nominal-quality boundary belong in the main result and
discussion, not in the abstract.

## Introduction bridge

Replace the current broad “Together, IR and SR” checkpoint statement with:

> At the checkpoint level, IR and SR play different roles across regimes. In
> the original moderate-noise sweep, IR tracks the recovery range while SR
> remains high. In a separate four-severity experiment, the same fixed SR
> condition becomes more active in harder slices, and both continuous diagnostics
> remain associated with retained planning performance beyond additive design
> trends and a simple train--evaluation exposure ratio. PLDM exhibits the same qualitative low-IR,
> high-SR pattern under a second world-model architecture.

## Evaluation-protocol addition

Add after the existing diagnostic protocol:

> We also conduct a separate broad-severity experiment on LeWM. It contains
> eight training-noise ranges from 0--0.1 through 0--1.5 and four evaluation
> severities from 0.08 to 0.64, with three independent training runs for every
> task and training condition. The diagnostic protocol and thresholds are
> unchanged. We analyze this experiment as an 8-by-4 factorial within each task
> and run; it is not concatenated with the original narrow training sweep.

## Discussion replacement

Replace the checkpoint and “Why IR and SR” paragraphs with:

> Across checkpoints, the two diagnostics have regime-dependent roles. At the
> moderate evaluation severity used for threshold transfer, lower IR accompanies
> recovery while SR is nonbinding for every IR-accepted checkpoint. In the
> separate broad-severity experiment, the SR-veto fraction among IR-passing
> rows is higher in the harder slices, and continuous SR
> remains associated with retained planning performance beyond additive design
> trends and after accounting for a simple exposure ratio. IR measures whether
> paired views stay close; SR checks
> whether that closeness preserves the tested state distinctions. Low IR alone
> still admits a constant representation, which SR rejects by definition.
>
> The extension establishes diagnostic activity and descriptive behavioral
> association, not selector dominance. IR and SR are relative robustness
> diagnostics: they can miss a nominal failure that reduces clean and noisy
> performance together. Clean planning quality therefore remains a separate
> requirement, and the state-pair catalog limits which distinctions SR can
> assess.

## Scope and future-work replacement

> The broad Gaussian experiment covers several evaluation severities but not
> natural changes in background, lighting, camera pose, or occlusion. It also
> does not test whether an IR--SR decision improves checkpoint selection or
> planning. Future work can evaluate such shifts, broaden the state-pair
> catalog, and test whether ACPC-informed abstention or planning interventions
> improve closed-loop outcomes.

## Conclusion replacement

> Across checkpoints, the original moderate-severity sweep and the separate
> broad-severity experiment reveal complementary regimes: IR is the active
> recovery indicator at moderate noise, whereas the SR-veto fraction among
> IR-passing rows is higher in harder slices while continuous SR remains
> associated with same-checkpoint retention.
> This supports using IR and SR as separate views of rollout sensitivity and
> tested state separation, rather than as a universal performance certificate.
