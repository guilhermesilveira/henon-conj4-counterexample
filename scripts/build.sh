#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
export SOURCE_DATE_EPOCH=1793145600
export FORCE_SOURCE_DATE=1
for doc in article/paper supplement/supplement; do
  dir=${doc%/*}
  name=${doc##*/}
  (cd "$dir"; pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" > build-pass1.txt; pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" > build-pass2.txt)
done
