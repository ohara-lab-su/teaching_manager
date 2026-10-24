# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/teaching_manager/)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/teaching_manager/ja/)

Teaching Manager provides a graphical interface for teaching robot positions and managing numbered position variables (P variables). Its primary purpose is to manage robot coordinates **outside the robot's internal variable memory**, using local data and JSON files. This allows position data to be maintained independently of the robot controller's built-in P-variable storage.

The software reads the robot's current position through a connected device interface, assigns that position to a selected P number, and stores the resulting position table. A `RobotVarManager` class also provides a Python interface for managing cached variables, loading and saving JSON, and explicitly transferring variables to or from a connected robot.

## Storage behavior

The implementation supports two storage modes selected by the device name:

- **Devices other than `CobottaCtrl`:** P variables are managed in JSON rather than in the robot's internal variable memory. Teaching, clearing, and deleting entries update the JSON data.
- **`CobottaCtrl`:** the application uses the robot's internal P variables. Explicit teaching or clearing writes to the robot and reads the result back. JSON export is available separately.

This distinction matters: external coordinate management is the primary use case, but the existing code retains a robot-memory mode for `CobottaCtrl`.

## Main functions

- Acquire the current robot position and associate it with a specified P number.
- Display and manage numbered positions in a Qt-based GUI.
- Load and save position tables as JSON files.
- Clear or delete selected positions, with behavior determined by storage mode.
- Manage variables programmatically using `RobotVarManager`.

## Operational notes

Teaching to a specified number can overwrite its existing value. The automatic “first unused P number” feature is disabled because the implementation does not yet define a reliable unused-number criterion. Reading the current position does not itself write to robot memory or JSON.

```{toctree}
:maxdepth: 2
:caption: Contents

overview
quickstart
gui
python_api
storage
api
```
