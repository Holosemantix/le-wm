# ICLR 2027 submission review ledger

Checked on 2026-09-02 against the current `main.tex` and the TeX Live 2025
build.

## Submission gates

- Official `iclr2027_conference.sty` and bibliography style are copied without
  modification.
- The abstract block is byte-identical to `paper1/main.tex`.
- The conclusion ends on page 8; required statements and references begin
  before the page-9 boundary is exceeded.
- The PDF contains no author metadata, affiliation, email address, or public
  identity-bearing code link.
- No local margin, font-size, caption-spacing, list-spacing, or float-spacing
  override is used.
- The build has no undefined references, overfull boxes, or missing fonts.

## Claim gates

- Pairwise ACPC is the target-free quantity; checkpoint summaries are described
  as offline diagnostics with their future-frame and state-label dependencies.
- Recovery is reported as a range. No single training-noise level is selected
  or described as optimal.
- IR and SR are reported separately; no continuous joint score or paired score
  change is used.
- High-severity results establish activation and non-equivalence of the frozen
  IR/SR conditions, not prospective checkpoint-selection utility.
- Fixed-pool statements do not claim an adaptive-CEM or simulator-return
  certificate.

## Quantitative cross-check

- High-severity SR rejections: 3/96, 3/96, 10/82, and 11/46.
- PLDM recovery-range levels and metric ranges match the three-run level table.
- Blur/resize component agreement, correlations, LOTO signs, and SR veto count
  match the frozen component artifact.
- Fixed first-round CEM coverage ranges match the certificate summary.
- Training runs are aggregated within the stated hierarchy rather than treated
  as independent checkpoint evidence.

## Remaining submission operation

Before upload, create a clean supplementary/source bundle from the compiled
dependency graph and scan that bundle for identifying metadata. Do not upload
the working directory wholesale because it also contains unused development
sidecars.
