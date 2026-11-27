# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

**Version 0.1.4** — A Python package and PySide6 GUI for robot position teaching and P-variable management.

## Features

Teaching Manager uses the DeviceProxy supplied by a launcher. Its shared GUI reads the current position, teaches numbered P points, and imports or exports JSON.

- **COBOTTA** uses both device-side P variables and a JSON file on the GUI computer. Teaching and clearing write and read back the selected point. Choosing Save on exit synchronizes changed points that are still listed, then writes the displayed list to the default JSON file. You can also export the list manually.
- **The bundled UR example** reads the current position through DeviceProxy and stores taught points in `JSON_FILE` on the GUI computer. The UR control instance has its own `ROBOT_VAR_FILE`. Teaching in this GUI leaves the control instance’s P points unchanged.
- **For device-managed teaching**, the launcher passes operation method names to `run_teaching_gui(..., methods=...)`. [Python API](docs/en/python_api.md)

To use saved variables from Python, load the entire JSON file with `RobotVarManager.load()`, then read the values via `list_vars()` and key lookup. Gaps remain absent. [Python API](docs/en/python_api.md)

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
