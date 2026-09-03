#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAPER_TEX_BIN="${PAPER_TEX_BIN:-/opt/texlive/2025/bin/x86_64-linux}"

cd "$SCRIPT_DIR"
mkdir -p build
"$PAPER_TEX_BIN/pdflatex" -interaction=nonstopmode -halt-on-error \
  -file-line-error -output-directory=build main.tex
"$PAPER_TEX_BIN/bibtex" build/main
"$PAPER_TEX_BIN/pdflatex" -interaction=nonstopmode -halt-on-error \
  -file-line-error -output-directory=build main.tex
"$PAPER_TEX_BIN/pdflatex" -interaction=nonstopmode -halt-on-error \
  -file-line-error -output-directory=build main.tex

echo "Built $SCRIPT_DIR/build/main.pdf with $PAPER_TEX_BIN"
