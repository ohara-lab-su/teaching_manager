# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

**Version 0.1.3** — A Python package and PySide6 GUI for robot position teaching and P-variable management.

## Features

Cobotta teaching updates the robot's P variables and can also save the table as JSON. UR and other devices store
taught positions in JSON. The application supports current-position retrieval, teaching to a specified P number,
clearing and removing multiple rows, JSON loading and saving, and save confirmation on exit.

Each device-specific example creates its connection. The package's `run_teaching_gui()` starts the shared GUI.

## Launch

Prepare `PySide6`, `x_logger`, the device package (`cobotta2` or `ur`), and the corresponding device server.
Run the launcher for your device from the repository root.

```bash
python example/teaching_cobotta_gui.py
python example/teaching_ur_gui.py
```

The Cobotta example reads `config_cobotta3_server5.yaml` by default. The UR example reads `ur_server.yaml` and requires
a version of `ur` that registers `UrCtrl` with DeviceProxy. See [Installation and launch](docs/en/quickstart.md) for
connection settings and `JSON_FILE`.

## Documentation

- [English tutorials and API](docs/en/index.md)
- [日本語チュートリアル・API](docs/ja/index.md)
- [Documentation home](docs/index.md)

Sphinx generates the API reference from docstrings for `RobotVarManager`, `TeachingModel`, `TeachingController`, and the
GUI. Build with `bash docs/build.sh`.

**Important:** Clear writes `[0, 0, 0, 0, 0, 0, -1]`. Removing a Cobotta row does not delete the robot's internal
variable. Automatic teaching to an unused P number is not implemented. Discarding on exit does not undo robot writes
already performed.

[Changelog](CHANGELOG.md)
