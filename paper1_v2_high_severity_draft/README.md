# Paper v2 high-severity draft

This directory is an isolated candidate revision. It does not modify
`paper1/main.tex` and is not part of the arXiv v1 source bundle.

The draft tests one narrow revision: connect the original moderate-severity
Gaussian result to a separate broad-severity experiment without presenting the
two training grids as one homogeneous sweep.

## Build

Generate the quantitative assets from the frozen three-seed summary:

```bash
python paper1_v2_high_severity_draft/scripts/build_draft_assets.py
```

Build the reader-facing preview with TeX Live 2025:

```bash
/opt/texlive/2025/bin/x86_64-linux/pdflatex \
  -interaction=nonstopmode -halt-on-error \
  -output-directory=paper1_v2_high_severity_draft/build \
  paper1_v2_high_severity_draft/preview.tex
```

Run `pdflatex` twice so cross-references settle. The preview is intentionally
standalone; approved prose can later be integrated into the real paper-v2
source.

## Files

- `writing_contract.md`: allowed claims, blocked claims, and quality gates.
- `integration_plan.md`: exact manuscript locations and main/appendix split.
- `main_text_extension.tex`: proposed main-text subsection.
- `appendix_extension.tex`: proposed supplementary analysis.
- `replacement_blocks.md`: candidate abstract/introduction/discussion/conclusion text.
- `full_main.tex`: full isolated v2 manuscript with the candidate extension
  integrated and the forced-collapse experiment removed.
- `tables/multiseverity_numbers.tex`: generated macros used by every numerical
  statement in the candidate prose.
- `source_map.json`: mechanically generated mapping from source results to the
  draft figure, table, and number macros, with pinned source hashes.
- `review_ledger.md`: independent reader and writing-quality review.

The full manuscript PDF is built from the `paper1/` directory so its existing
relative figure, table, metadata, and bibliography paths remain unchanged:

```bash
cd paper1
/opt/texlive/2025/bin/x86_64-linux/pdflatex \
  -interaction=nonstopmode -halt-on-error \
  -output-directory=../paper1_v2_high_severity_draft/full_build \
  ../paper1_v2_high_severity_draft/full_main.tex
cd ../paper1_v2_high_severity_draft/full_build
BIBINPUTS=../../paper1: BSTINPUTS=../../paper1: \
  /opt/texlive/2025/bin/x86_64-linux/bibtex full_main
cd ../../paper1
/opt/texlive/2025/bin/x86_64-linux/pdflatex \
  -interaction=nonstopmode -halt-on-error \
  -output-directory=../paper1_v2_high_severity_draft/full_build \
  ../paper1_v2_high_severity_draft/full_main.tex
/opt/texlive/2025/bin/x86_64-linux/pdflatex \
  -interaction=nonstopmode -halt-on-error \
  -output-directory=../paper1_v2_high_severity_draft/full_build \
  ../paper1_v2_high_severity_draft/full_main.tex
```

The old factorial heatmap/rank-association composite is deliberately not used
in this draft. The main display answers one question only: when is each fixed
diagnostic condition active?
