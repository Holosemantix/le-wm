# ICLR 2027 writing contract

## Submission target

- Venue: ICLR 2027 main conference, anonymous submission.
- Format: official ICLR 2027 style, with no local spacing or margin overrides.
- Main-text limit: at most 9 pages, excluding references and the required statements.
- Draft target: end the conclusion by page 9 with roughly 0.3 page of safety margin.

## Claim frame

This is a diagnostic paper about how visual perturbations propagate through
action-conditioned latent rollouts; it is not a new training objective or an
adaptive planning algorithm.

Central thesis: pairwise ACPC measures perturbation propagation in the latent
dynamics, while IR and SR summarize, respectively, whether perturbed views stay
close and whether tested state distinctions remain separated.

Positive evidence to expose in the main paper:

1. Pairwise ACPC tracks perturbation-induced prediction-error change and the
   cost of fixed-pool CEM plan changes beyond short-horizon or action-destroyed
   controls.
2. Across four tasks, the IR condition locates checkpoint recovery in the
   original Gaussian sweep; at larger evaluation severities, the fixed SR
   condition becomes an active guard on IR-passing checkpoints.
3. The diagnostic trend is checked under blur and resize and on PLDM, with the
   scope of each comparison stated precisely.

Boundary claim: the checkpoint screen is an offline, paired-data diagnostic
under a frozen protocol. It is not a reference-free robustness certificate or
a guarantee for adaptive closed-loop planning.

## Abstract decision

- Preserve the accepted V1 abstract byte-for-byte.
- Supporting high-severity and fixed-pool analyses do not change the central
  contribution and therefore do not earn abstract space.

## Main-paper evidence budget

- Figure 1: conceptual ACPC/IR/SR overview.
- Figure 2: original four-task Gaussian sweep and recovery behavior.
- Figure 3: high-severity activation of the SR condition.
- Figure 4: prediction-error evidence with recorded-action and
  action-destroyed controls.
- Figure 5: planner-horizon evidence for CEM selection regret.
- Table 1: a four-row PLDM summary over recovery ranges, with no single-level
  selection. The full PLDM sweep remains in the appendix.
- Main prose: concise quantitative summaries for cross-task transfer and
  blur/resize. Full inventories and secondary figures belong in appendix.
- Fixed-pool certificate: one positive, scoped sentence in the main text; full
  definition, coverage and calibration remain in appendix.

## Section page budget

| Block | Target pages |
|---|---:|
| Title and abstract | 0.45 |
| Introduction and overview | 1.25 |
| Related work | 0.55 |
| Diagnostic and theory | 1.85 |
| Experimental protocol | 0.55 |
| Main results | 3.55 |
| Discussion and conclusion | 0.50 |
| Safety margin | 0.30 |

## Writing rules

- Compress before demoting evidence to the appendix.
- One paragraph, one job; topic sentence first.
- Use question -> protocol -> result -> boundary for experiment paragraphs.
- State the scientific result directly; remove reviewer-response, audit, and
  project-management language.
- Prefer concrete verbs and short clauses; do not stack caveats.
- Do not call a range or plateau an optimal training value.
- Keep IR and SR separate when their roles differ; do not revive a continuous
  scalar joint score.
- Any number in the main text must trace to a current machine-readable result.
- A display stays in the main paper only if a first-time reader needs it to
  recover the evidence chain.

## Verification gates

- Accepted abstract matches the V1 source exactly.
- Conclusion ends no later than page 9 in the official template.
- No author names, affiliations, acknowledgments, public identity-bearing code
  links, or identifying PDF metadata in the anonymous source/PDF.
- No geometry, font, caption-size, list-spacing, or float-spacing override.
- Figures remain readable at normal zoom and in grayscale.
- Fresh reader review can state the problem, contribution, strongest evidence,
  and boundary without consulting the appendix.
