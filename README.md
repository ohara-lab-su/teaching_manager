# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](README.ja.md)

**Version 0.1.0** — A Python package and PySide6 GUI for robot position teaching and P-variable management.

## Features

Cobotta (`device_name == "CobottaCtrl"`) stores P variables on the robot; other devices use JSON files. The application
supports current-position retrieval, teaching to a specified P number, context-menu operations, multi-row clear/removal,
JSON open/save dialogs, and save confirmation on exit.

The GUI implementation resides in `src/teaching_manager/teaching_gui.py`; `example/teaching_gui.py` is the launcher.
Controller, Model, and RobotVarManager follow a simple MVC design.

## Launch

Provide `PySide6`, `cobotta2`, `x_logger`, and the appropriate connection configuration. Configure `device_name`,
`Config(...)`, and `JSON_FILE` in the launcher.

```bash
python example/teaching_gui.py
```

## Documentation

- [English tutorials and API](docs/en/index.md)
- [日本語チュートリアル・API](docs/jp/index.md)
- [Language selection](docs/index.md)

Sphinx generates the API reference from docstrings for `RobotVarManager`, `TeachingModel`, `TeachingController`, and the
GUI. Build with `bash docs/build.sh`.

**Important:** Clear writes `[0, 0, 0, 0, 0, 0, -1]`. Removing a Cobotta row does not delete the robot's internal
variable. Automatic teaching to an unused P number is not implemented. Discarding on exit does not undo robot writes
already performed.

[Changelog](CHANGELOG.en.md)
