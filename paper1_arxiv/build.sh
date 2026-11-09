#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAPER_TEX_BIN="${PAPER_TEX_BIN:-/opt/texlive/2025/bin/x86_64-linux}"
export PATH="$PAPER_TEX_BIN:$PATH"
cd "$SCRIPT_DIR"
latexmk -pdf -recorder -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
cp build/main.pdf main.pdf
