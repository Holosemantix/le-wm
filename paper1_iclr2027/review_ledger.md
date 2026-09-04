# ICLR 2027 submission review ledger

Checked on 2026-09-04 against the current `main.tex` and the TeX Live 2025
build.

## Submission gates

- The local `iclr2027_conference.sty`, `iclr2027_conference.bst`, `fancyhdr.sty`,
  and `natbib.sty` are byte-identical to the files in the official ICLR 2027
  style archive.
- The abstract block is byte-identical to the frozen snapshot taken at the
  start of the source-restoration pass. It was not edited during that pass.
- The conclusion ends on page 9. The AI use statement, reproducibility
  statement, and references begin on page 10. Appendix A now begins directly
  with Proofs and Fixed-Pool Analysis on page 13. The full PDF has 24 pages.
- The PDF contains no author metadata, affiliation, email address, or public
  identity-bearing code link.
- No local margin, font-size, caption-spacing, list-spacing, or float-spacing
  override is used.
- The build has no LaTeX errors, undefined references or citations, overfull
  boxes, multiply-defined labels, or missing fonts.
- The 41 rendered references have been checked against primary
  publisher/proceedings, project, or arXiv records. Two NeurIPS 2025 proceedings URLs were
  replaced by their official DOIs, and the BS-MPC link was normalized to its
  OpenReview forum URL. The cited-key set and rendered bibliography match
  exactly. `references.bib` retains 17 unused inventory entries that do not
  render; see `reference_audit.md` for the exact selection and remaining
  pre-submission rechecks.

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
- Related Work now covers general latent world models, JEPA foundations,
  LeWM/PLDM, self-predictive collapse, action conditioning, predictable
  features, invariance/equivariance, visual augmentation, bisimulation, MWM,
  intended-use evaluation, and decision certificates. It also positions ACPC
  against ReOI, DreamerPro, Denoised MDPs, robust latent dynamics, ATM,
  WMAttack, and ARB4WM. There is no standalone Related Work appendix.
- Section 3.1 opens with the published clean/perturbed shared-action bridge
  before introducing notation. The Introduction ends with three explicit
  contributions covering the method, theory, and experiments. The compressed
  contribution paragraph retains the same-candidate-sequence scope of the cost
  bounds, the CEM extra-predicted-cost evidence, and the non-equivalence of IR
  and SR; it does not claim simulator return or universal certification.
- Final read-only review passed the complete Introduction chain
  (problem--gap--method--collapse guard--theory/evidence--contributions), the
  4.2-to-4.3 and 4.8-to-Discussion/Conclusion transitions, and the readability
  of Figures 2--5 after their small width reductions.
- A subsequent paragraph-by-paragraph review covered Sections 4.1--4.8,
  Discussion, and Conclusion. It restored the training-run replication unit in
  Section 4.1 and the probe severities/draw construction in Section 4.4; all
  subsection openers, figure transitions, and remaining claim boundaries
  passed final read-only review.
- An independent final read-only audit confirmed that all 41 cited keys are
  defined and rendered; that the t-SNE appendix citation remains present; and
  that the final three Related Work paragraphs contain no evident
  citation-to-claim mismatch, overclaim, or unreadable transition.

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
