#!/usr/bin/env bash
set -euo pipefail
DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DOCS_DIR/.." && pwd)"
PKG_DIR="$ROOT_DIR/src/teaching_manager"
HTML_DIR="$DOCS_DIR/_build/html"
export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

if [ ! -d "$PKG_DIR" ]; then
    echo "Package source not found: $PKG_DIR" >&2
    exit 1
fi

for lang in en ja; do
    TEACHING_DOC_LANGUAGE="$lang" sphinx-build -b html -c "$DOCS_DIR" \
        "$DOCS_DIR/$lang" "$HTML_DIR/$lang"
done

cp -a "$HTML_DIR/en/." "$HTML_DIR/"
touch "$HTML_DIR/.nojekyll"
