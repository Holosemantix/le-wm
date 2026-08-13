#!/usr/bin/env bash
# Source from Paper 1 build scripts to select and verify the pinned TeX toolchain.

PAPER1_TEXLIVE_BIN="${PAPER1_TEXLIVE_BIN:-/opt/texlive/2025/bin/x86_64-linux}"

if [[ ! -x "$PAPER1_TEXLIVE_BIN/pdflatex" ]]; then
  echo "ERROR: TeX Live 2025 pdflatex not found at $PAPER1_TEXLIVE_BIN/pdflatex." >&2
  echo "Set PAPER1_TEXLIVE_BIN to the TeX Live 2025 platform bin directory." >&2
  return 1
fi

export PAPER1_TEXLIVE_BIN
export PATH="$PAPER1_TEXLIVE_BIN:$PATH"

for paper1_tex_tool in pdflatex bibtex latexmk; do
  paper1_tex_tool_path="$(command -v "$paper1_tex_tool" 2>/dev/null || true)"
  if [[ "$paper1_tex_tool_path" != "$PAPER1_TEXLIVE_BIN/"* ]]; then
    echo "ERROR: $paper1_tex_tool resolved outside the pinned TeX Live 2025 bin directory: $paper1_tex_tool_path" >&2
    return 1
  fi
done

if ! pdflatex --version | grep -Fq "TeX Live 2025"; then
  echo "ERROR: $PAPER1_TEXLIVE_BIN/pdflatex is not from TeX Live 2025." >&2
  return 1
fi

unset paper1_tex_tool paper1_tex_tool_path
