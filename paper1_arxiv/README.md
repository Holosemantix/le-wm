# Paper 1 arXiv update

This public manuscript uses the complete current `../paper1_iclr2027/main.tex`, its appendix, bibliography, tables, and figures, retaining the ICLR typography without conference or review headers.

Author order, contribution notes, and contact information come from `../paper1/arxiv_metadata.tex`. Shanzhao Ruan's affiliation is updated to **The Chinese University of Hong Kong Shenzhen**.

The only body wording changes remove “anonymous” from the supplementary-material description and change “submission” to “paper” in the AI use statement. The public code link is restored. The original ICLR and previous arXiv directories are preserved.

Build with `bash build.sh` (TeX Live 2025). Preview: `main.pdf`. Upload source: `paper1_arxiv_source.zip`; entrypoint: `main.tex`; compiler: pdfLaTeX. The ZIP includes only recorded source dependencies, bibliography/style files, and the generated `main.bbl`.

Use Replace on the existing arXiv record, update title/abstract metadata to this manuscript, and inspect arXiv's generated PDF before final submission. This directory has not been submitted to arXiv.
