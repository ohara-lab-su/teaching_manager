# Changelog

[English](CHANGELOG.en.md) | [日本語](CHANGELOG.md)

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
