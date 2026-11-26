"""Teaching Manager Sphinx documentation configuration."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
project = "Teaching Manager"
release = "0.1.3"
version = release
master_doc = "index"
language = os.environ.get("TEACHING_DOC_LANGUAGE", "en")
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
autosummary_generate = True
autodoc_default_options = {"members": True, "show-inheritance": True}
autodoc_typehints = "description"
# GUI/実機用の依存はAPI生成時に実行しない。モック対象は外部ライブラリのみ。
autodoc_mock_imports = ["PySide6", "cobotta2", "x_logger", "ese774_frame", "grpc", "httpx"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {"navigation_depth": 4, "titles_only": False}
html_title = f"{project} {release}"
exclude_patterns = ["_build", "_generated", "**/.DS_Store"]
