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
`/opt/texlive/2025/bin/x86_64-linux`; set `PAPER_TEX_BIN` to override it. The
outputs are `build/main.pdf` and the synchronized `main.pdf`. In the current build, the conclusion ends on page
9; the required statements and references begin on page 10, and Appendix A
begins on page 13.

On 2026-09-16, the approved `preview_20260914/writing_preview.tex` was
promoted unchanged to `main.tex`. The preview and its adjustment ledger are
retained as the reviewed source snapshot. The current PDF has 24 pages and
44 bibliography entries. See `reference_audit.md` for current build checks
and the separately identified historical reference audit.

The main text reports recovery ranges rather than a single selected training
noise level. Continuous joint IR--SR scores are not part of the manuscript.

See `writing_adjustments_ledger.md` for the source-preservation and compression
record used to review the nine-page main text.
