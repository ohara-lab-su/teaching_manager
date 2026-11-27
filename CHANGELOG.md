# Changelog

[![en](https://img.shields.io/badge/lang-en-red.svg)](CHANGELOG.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](CHANGELOG.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

## [0.1.4]

- Document how to retrieve all JSON entries and read sparse P point numbers through the existing variable-management API.
- Clarify COBOTTA device-side teaching, synchronization and default JSON saving on exit, the bundled UR GUI's client-side file, and use of the existing API by the UR control instance. The variable manager implementation is unchanged.
- Let launchers pass method names to `run_teaching_gui()`. The GUI reads all points managed by the device at startup and writes and reads back the selected point when teaching.

## [0.1.3]

- Split the Cobotta and UR launch examples and added `example/ur_server.yaml` for UR connections.
- Moved shared GUI startup to `run_teaching_gui()`, which initializes `QApplication` before creating the window.
- Updated the English and Japanese README and Pages launch instructions and added the shared launcher to the API reference.
- Fixed the Pages home navigation to both the English and Japanese documentation.

## [0.1.0] - 2026-10-23

### Added and changed

- Moved the GUI implementation to `src/teaching_manager/teaching_gui.py`; retained `example/teaching_gui.py` as a launcher.
- Refined the MVC responsibilities of GUI, Controller, Model, and RobotVarManager.
- Automatically selected robot P-variable storage for `CobottaCtrl`, and JSON storage for other devices.
- Added current-position retrieval, teaching to a specified/selected P number, and readback.
- Added context-menu teaching, clearing, row removal, and Ctrl/Command/Shift multi-selection.
- Added JSON open/save dialogs with a configurable default directory and filename.
- Added exit-time change confirmation, Cobotta synchronization, and JSON saving.
- Improved worker-based communications, simplified conditionals, and refined save-state handling.
- Added bilingual README/CHANGELOG, Sphinx tutorials, generated API references, and a GitHub Pages workflow.

### Known limitations

- Automatic teaching to the first unused P number is not implemented.
- DeviceProxy communication timeout behavior requires separate verification.
- GUI and hardware integration have not been tested here.

## [0.0.0] - 2026-10-23

Initial version with P-variable listing, current-position retrieval, teaching, JSON import/export, and basic MVC separation.
