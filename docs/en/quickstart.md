# Installation and launch

[日本語](../jp/quickstart.md)

Prepare Python, the GUI dependencies (PySide6, cobotta2, x_logger), the robot server, and its configuration. Exact dependency versions cannot be established from the provided sources.

From the repository root:

```bash
python example/teaching_gui.py
```

Configure `device_name`, `Config(...)`, and `JSON_FILE` in `example/teaching_gui.py`. Relative JSON paths are resolved against the directory containing that launcher script.

`CobottaCtrl` uses internal robot P variables; all other device names use JSON. Retrieving current position still requires a robot connection.

## Building Pages

With Sphinx, MyST Parser, and sphinx-rtd-theme installed, run `bash docs/build.sh`. The output is `docs/_build/html/`. GitHub Actions uses the same script.
