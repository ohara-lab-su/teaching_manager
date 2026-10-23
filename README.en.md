# Robot Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.md)

A Qt-based teaching GUI for capturing robot positions, assigning them to P variables, and managing position data in JSON
files.

**Version: 0.0.0 (initial release)**

## Features

- Retrieve and display the robot's current position.
- Display P numbers and their position values in a table. Read a specified range of P variables from Cobotta.
- Write the **previously retrieved current position** to a specified P number or a selected row, with confirmation
  before overwriting.
- Use the table's context menu to write the current position, **clear to the unused value**, or **remove from the
  displayed list**.
- Select multiple rows using Ctrl/Command or a range using Shift. Clear or remove multiple selected rows in one
  operation.
- Clearing sets the P value to `[0, 0, 0, 0, 0, 0, -1]`.
- Load P variables from JSON and save the currently displayed list to JSON.

**Limitation:** The “teach to first unused number” button is present, but automatic teaching is unavailable because the
unused-number detection rule has not been established.

## Device-dependent storage

Storage mode is selected automatically from the `device_name` passed to `DeviceProxy`. The comparison with **
`CobottaCtrl` is exact and case-sensitive**.

| Operation                  | `CobottaCtrl`                        | Other device names          |
|----------------------------|--------------------------------------|-----------------------------|
| Initial P-variable loading | Robot's internal P variables         | JSON file                   |
| Current position retrieval | Robot API                            | Robot API                   |
| Teaching a position        | Robot's internal P variables         | Automatically saved to JSON |
| Clearing a P variable      | Robot's internal P variables         | Automatically saved to JSON |
| Removing a row             | Displayed list only; robot unchanged | Displayed list and JSON     |
| Explicit JSON save         | Save displayed list to JSON          | Save displayed list to JSON |

Changes to Cobotta's internal P variables are **not automatically saved to JSON**. Other devices use JSON for P-variable
storage instead of internal robot P-variable memory. **Retrieving the current position still requires a connected robot
in either mode.**

## Project structure

| File                                          | Responsibility                                                       |
|-----------------------------------------------|----------------------------------------------------------------------|
| `example/teaching_gui.py`                     | PySide6 widgets, user interactions, confirmation dialogs             |
| `src/teaching_manager/teaching_controller.py` | Device-dependent routing and operation coordination                  |
| `src/teaching_manager/teaching_model.py`      | P-variable state, robot API calls, current position, JSON operations |
| `src/teaching_manager/robot_var_manager.py`   | Local variable management                                            |

The application separates the GUI, Controller, and Model using an MVC structure.

## Setup and launch

The current `example/teaching_gui.py` imports `PySide6`, `x_logger`, and `cobotta2`. Provide these packages and the
connection configuration file for your environment. No packaging/dependency manifest was included among the files
reviewed for this release, so compatible dependency versions are not specified here.

Configure `Config("config_cobotta3_server5.yaml")`, `device_name = "CobottaCtrl"`, and `DeviceProxy(...)` in `main()` of
`example/teaching_gui.py`. The `JSON_FILE` constant defaults to `robot_positions.json` in the project root. The GUI
accepts P numbers from 0 through 999; the initial read range defaults to P0–P20.

Run from the project root:

```sh
python example/teaching_gui.py
```

Operations requiring robot communication need an available DeviceProxy and robot server.

## Important behavior

- Teaching and clearing overwrite existing positions; check the confirmation dialog carefully.
- On Cobotta, “remove from list” does **not** erase the robot's internal P variable. It differs from clearing.
- In JSON mode, removing rows also updates the JSON file.
- Robot writes are followed by a readback check.
- Closing the window while current-position retrieval is in progress may wait for the communication thread to finish.

## Changelog

[CHANGELOG.md](CHANGELOG.md) / [CHANGELOG.en.md](CHANGELOG.en.md)
