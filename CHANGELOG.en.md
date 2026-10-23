# Changelog

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/CHANGELOG.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/CHANGELOG.md)

## [0.0.0] - 2026-10-23

Initial release.

### Added

- PySide6-based P-variable teaching GUI.
- MVC architecture separating the GUI, Controller, and Model.
- Robot current-position retrieval and display through `DeviceProxy`.
- Reading and listing a selected range of Cobotta P variables.
- Writing the retrieved current position to a specified P number or selected row, with overwrite confirmation.
- Table context-menu actions for writing, clearing, and removing rows.
- Multi-row selection with Ctrl/Command or Shift, including batch clear and removal.
- Clear value `[0, 0, 0, 0, 0, 0, -1]`.
- JSON import and export of the displayed P-variable list.
- Automatic storage selection: internal robot P variables for `device_name == "CobottaCtrl"`; JSON for other device
  names.
- Automatic JSON updates for teaching, clearing, and removal in JSON storage mode.
- Robot write readback verification.
- Background worker for current-position retrieval and thread waiting during shutdown.

### Known limitations

- Automatic unused-P-number detection and teaching are not implemented; attempting the action reports an error.
- Closing the window may take time while a robot communication thread is still running.
