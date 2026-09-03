# ICLR 2027 manuscript draft

This directory is an isolated, anonymous ICLR 2027 version of Paper 1. It uses
the official conference style and bibliography files copied into this
directory. The accepted arXiv-v1 abstract is preserved verbatim in `main.tex`.

Build with TeX Live 2025:

```bash
./build.sh
```

The default TeX binary directory is
`/opt/texlive/2025/bin/x86_64-linux`; set `PAPER_TEX_BIN` to override it. The
output is `build/main.pdf`. In the current build, the conclusion and required
statements fit within the nine-page submission allowance, and references begin
on page 9.

The main text reports recovery ranges rather than a single selected training
noise level. Continuous joint IR--SR scores are not part of the manuscript.
