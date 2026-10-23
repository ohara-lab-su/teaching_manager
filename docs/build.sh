#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"
sphinx-build -b html "$SCRIPT_DIR" "$SCRIPT_DIR/_build/html"
touch "$SCRIPT_DIR/_build/html/.nojekyll"
