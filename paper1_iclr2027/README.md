# ICLR 2027 manuscript draft

This directory is an isolated, anonymous ICLR 2027 version of Paper 1. It uses
the official conference style and bibliography files copied into this
directory. The abstract was frozen at the start of the source-restoration pass
and was not edited during that pass.

Build with TeX Live 2025:

```bash
./build.sh
```

The default TeX binary directory is
`/opt/texlive/2025/bin/x86_64-linux`; set `PAPER_TEX_BIN` to override it.
The script builds all three versions and synchronizes the PDFs from `build/`
to this directory:

| File | Contents |
|---|---|
| `main.pdf` / `build/main.pdf` | Main paper, existing AI/reproducibility statements, and its 41 references (13 pages) |
| `supplementary.pdf` / `build/supplementary.pdf` | Standalone Supplementary Material, Appendices A–I and its 3 references (14 pages) |
| `full.pdf` / `build/full.pdf` | Complete reading version with all 44 references and appendices (25 pages) |

The conclusion still ends on page 9. `main.tex` contains the main text and
existing statements, `appendix.tex` contains the appendix content, and
`preamble.tex` shares the unchanged ICLR 2027 template and manuscript macros.
`supplementary.tex` and `full.tex` are separate build entries. The existing
`appendix_extension.tex` remains a dependency of the appendix.

Main and supplementary PDFs retain the original section, figure, table,
equation and proposition numbers. Their bibliographies are independent;
`full.pdf` retains the original combined bibliography. Cross-document links
work when `main.pdf` and `supplementary.pdf` are kept together; printed
reference numbers remain meaningful when the files are viewed separately.
Run `./build.sh` to resolve both directions of references automatically.
In Overleaf, use pdfLaTeX and compile `main.tex`, `supplementary.tex`, then
`main.tex` again, or select `full.tex` for the combined reading version.

This split preserves the main text, abstract, existing declarations, figures,
results and bibliography metadata. The combined PDF text was checked against
a clean build of the original source, and every existing label number was
preserved. See `reference_audit.md` for the build verification and the
separately identified historical reference audit.

On 2026-09-16, the approved `preview_20260914/writing_preview.tex` was
promoted to `main.tex`. The preview and its adjustment ledger remain as the
reviewed historical snapshot; edits should now use the shared sources above.

The main text reports recovery ranges rather than a single selected training
noise level. Continuous joint IR--SR scores are not part of the manuscript.

See `writing_adjustments_ledger.md` for the source-preservation and compression
record used to review the nine-page main text.
