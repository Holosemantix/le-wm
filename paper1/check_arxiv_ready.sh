#!/usr/bin/env bash
# Lightweight arXiv submission readiness checks for Paper 1.
# Run from repository root: bash paper1/check_arxiv_ready.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER="$ROOT/paper1"
ALLOW_AUTHOR_PLACEHOLDER="${ALLOW_AUTHOR_PLACEHOLDER:-0}"
BUNDLE_TAR="/tmp/paper1_arxiv_v1_src.tar.gz"
BUNDLE_TAR_TMP=""
BUNDLE_SRC=""
BUNDLE_VERIFY=""
cd "$PAPER"

cleanup() {
  for bundle_dir in "$BUNDLE_SRC" "$BUNDLE_VERIFY"; do
    if [[ -n "$bundle_dir" && -d "$bundle_dir" ]]; then
      rm -rf -- "$bundle_dir"
    fi
  done
  if [[ -n "$BUNDLE_TAR_TMP" && -f "$BUNDLE_TAR_TMP" ]]; then
    rm -f -- "$BUNDLE_TAR_TMP"
  fi
}
trap cleanup EXIT

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

PREVIOUS_LONG_NAME='Distinction'' Rate'
RETIRED_LONG_NAME='Distinguishability'' Rate'
CURRENT_LONG_NAME='Separation Rate'
RETIRED_ABBREVIATION='D''R'

contains_retired_abbreviation() {
  grep -Eq "(^|[^[:alnum:]_])${RETIRED_ABBREVIATION}([^[:alnum:]_]|$)" "$1"
}

check_current_metric_source() {
  local metric_source="$1"
  [[ -f "$metric_source" ]] || fail "missing current metric source: $metric_source"
  for retired_name in "$PREVIOUS_LONG_NAME" "$RETIRED_LONG_NAME"; do
    if grep -Fq "$retired_name" "$metric_source"; then
      fail "$metric_source contains retired metric name: $retired_name"
    fi
  done
  if contains_retired_abbreviation "$metric_source"; then
    fail "$metric_source contains the standalone retired metric abbreviation"
  fi
}

# Hard blockers that should not reach arXiv.
if grep -q "Author names to be supplied" arxiv_metadata.tex && [[ "$ALLOW_AUTHOR_PLACEHOLDER" != "1" ]]; then
  fail "arxiv_metadata.tex still contains the arXiv author placeholder. Replace \\arxivauthors with the real author list."
fi

if grep -q "Author names to be supplied" arxiv_metadata.tex; then
  echo "WARN: author placeholder in arxiv_metadata.tex allowed because ALLOW_AUTHOR_PLACEHOLDER=1; replace it before final arXiv upload." >&2
fi

if grep -q "\\\\author{}" main.tex; then
  fail "main.tex contains an empty \\author{} field. arXiv v1 must be non-anonymous."
fi

if grep -q "Scope of this arXiv version" main.tex; then
  fail "main.tex still contains internal release-note wording: 'Scope of this arXiv version'. Use 'Scope' / 'This paper' instead."
fi

if grep -q "paper-facing\|method-facing" main.tex; then
  fail "main.tex still contains paper-facing/method-facing internal wording. Move such wording to tooling notes or rewrite for readers."
fi

if grep -q "tree/ag/dev\|tree/main" main.tex arxiv_metadata.tex; then
  fail "main.tex points to a branch-specific GitHub tree. Use the public repository root URL for arXiv."
fi

if grep -q "complete code and data" main.tex arxiv_metadata.tex arxiv_release_notes.tex; then
  fail "main.tex over-claims the release package as 'complete code and data'. Use code/artifacts/scripts/pointers wording."
fi

for metric_source in \
  main.tex \
  scripts/plot_acpc_ir_sr_overview.py \
  scripts/plot_full_sweep_diagnostics.py \
  scripts/plot_pldm_sweep_diagnostics.py \
  scripts/cross_task_selective_rule.py \
  scripts/build_acpc_submission_assets.py \
  scripts/build_cross_stressor_ir_sr_comparison.py \
  scripts/build_linearization_horizon_artifact.py; do
  check_current_metric_source "$metric_source"
done

for metric_source in main.tex scripts/plot_acpc_ir_sr_overview.py; do
  if ! grep -Fq "$CURRENT_LONG_NAME" "$metric_source"; then
    fail "$metric_source is missing current metric name: $CURRENT_LONG_NAME"
  fi
done

if ! grep -q "https://github.com/Anguo-star/acpc-diagnostics" arxiv_metadata.tex; then
  fail "main.tex does not contain the intended public repository URL https://github.com/Anguo-star/acpc-diagnostics."
fi

if grep -q "tab:theory-metric-map\|tab:sweep-summary\|fig:atr-smpr-plane\|fig_atr_smpr_plane\|fig_feature_neighborhood_atr_smpr" main.tex; then
  fail "main.tex still references a removed table or figure from the pre-convergence draft."
fi

# Build first; build.sh also greps undefined refs/cites/fatal diagnostics.
bash build.sh --clean

[[ -f main.bbl ]] || fail "main.bbl was not generated; arXiv source package should include main.bbl matching main.tex."

# Prepare a minimal arXiv source bundle in isolated temporary directories.
# arxiv_release_notes.tex is intentionally excluded: main.tex does not input it,
# and internal revision notes do not belong in the submission source archive.
BUNDLE_SRC="$(mktemp -d /tmp/paper1_arxiv_src.XXXXXX)"
BUNDLE_VERIFY="$(mktemp -d /tmp/paper1_arxiv_verify.XXXXXX)"
BUNDLE_TAR_TMP="$(mktemp /tmp/paper1_arxiv_v1_src.XXXXXX.tar.gz)"
rm -f -- "$BUNDLE_TAR"
mkdir -p "$BUNDLE_SRC/figures" "$BUNDLE_SRC/tables"
cp main.tex arxiv_metadata.tex references.bib main.bbl "$BUNDLE_SRC/"

# Copy exactly the figures referenced by main.tex. The helper expands simple
# \input{...} files and resolves the configured \graphicspath entries.
python scripts/collect_tex_figures.py \
  --tex main.tex \
  --base-dir . \
  --out-dir "$BUNDLE_SRC/figures" \
  --table-out-dir "$BUNDLE_SRC/tables"
compgen -G "$BUNDLE_SRC/tables/*.tex" >/dev/null || fail "main.tex has no collected table inputs"

while IFS= read -r -d '' metric_source; do
  check_current_metric_source "$metric_source"
done < <(find "$BUNDLE_SRC" -type f -name '*.tex' -print0)

tar -czf "$BUNDLE_TAR_TMP" -C "$BUNDLE_SRC" .

if tar -tzf "$BUNDLE_TAR_TMP" | grep -E '(^|/)(PLAN|CODEX|ARXIV_V1|FINAL_SUBMISSION_AUDIT|arxiv_release_notes\.tex|\.git|.*\.log|.*\.aux|.*\.out|.*\.toc|.*\.fls|.*\.fdb_latexmk|.*\.synctex\.gz|main\.pdf)$'; then
  fail "arXiv source tarball contains internal planning/build/output files."
fi

# Verify the artifact that will actually be uploaded, not only the repository
# checkout from which it was assembled.
tar -xzf "$BUNDLE_TAR_TMP" -C "$BUNDLE_VERIFY"
if ! (
  cd "$BUNDLE_VERIFY"
  if command -v latexmk >/dev/null 2>&1; then
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
  else
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
  fi
) >/tmp/paper1_arxiv_bundle_build.log 2>&1; then
  tail -n 80 /tmp/paper1_arxiv_bundle_build.log >&2
  fail "isolated arXiv source bundle did not compile"
fi

if grep -En "Citation .* undefined|Reference .* undefined|There were undefined references|Undefined control sequence|Fatal error|No file main.bbl|Overfull|Underfull" "$BUNDLE_VERIFY/main.log" >/tmp/paper1_arxiv_bundle_grep.log 2>/dev/null; then
  cat /tmp/paper1_arxiv_bundle_grep.log
  fail "isolated arXiv source bundle has unresolved references or layout diagnostics"
fi

if command -v pdftotext >/dev/null 2>&1; then
  ARXIV_PDF_TEXT=/tmp/paper1_arxiv_pdf_text.txt
  pdftotext "$BUNDLE_VERIFY/main.pdf" "$ARXIV_PDF_TEXT"
  check_current_metric_source "$ARXIV_PDF_TEXT"
  if ! grep -Fq "$CURRENT_LONG_NAME" "$ARXIV_PDF_TEXT"; then
    fail "isolated arXiv PDF is missing current metric name: $CURRENT_LONG_NAME"
  fi
fi

mv -f -- "$BUNDLE_TAR_TMP" "$BUNDLE_TAR"
BUNDLE_TAR_TMP=""

echo "OK: Paper 1 arXiv readiness checks passed."
echo "Source bundle: $BUNDLE_TAR"
