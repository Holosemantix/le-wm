#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAPER_TEX_BIN="${PAPER_TEX_BIN:-/opt/texlive/2025/bin/x86_64-linux}"
export PATH="$PAPER_TEX_BIN:$PATH"

cd "$SCRIPT_DIR"
mkdir -p build
build_document() {
  "$PAPER_TEX_BIN/latexmk" -pdf -interaction=nonstopmode -halt-on-error \
    -file-line-error -outdir=build "$1.tex"
}
# Two rounds resolve forward/back references between the independent PDFs.
build_document main
build_document supplementary
build_document main
build_document supplementary
build_document full
for document in main supplementary full; do
  cp "build/$document.pdf" "$document.pdf"
done
echo "Built and synchronized main.pdf, supplementary.pdf and full.pdf with $PAPER_TEX_BIN"
