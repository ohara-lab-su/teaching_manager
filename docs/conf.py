import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
project = "Teaching Manager"
release = "0.1.0"
version = "0.1.0"
language = "ja"
master_doc = "index"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.napoleon", "sphinx.ext.viewcode", "myst_parser"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
autosummary_generate = True
autodoc_default_options = {"members": True, "show-inheritance": True}
autodoc_typehints = "description"
# GUI/実機用の依存はAPI生成時に実行しない。モック対象は外部ライブラリのみ。
autodoc_mock_imports = ["PySide6", "cobotta2", "x_logger", "ese774_frame", "grpc", "httpx"]
html_theme = "sphinx_rtd_theme"
html_title = "Teaching Manager 0.1.0"
exclude_patterns = ["_build"]
