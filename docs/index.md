# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/teaching_manager/en/)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/teaching_manager/ja/)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

**Version 0.1.4**

Device-specific launchers supply a synchronous DeviceProxy to the shared GUI for position retrieval and teaching. Python applications can use `RobotVarManager` independently to manage JSON data.

## Storage behavior

Teaching Manager uses the DeviceProxy supplied by a launcher. Its shared GUI reads the current position, teaches numbered P points, and imports or exports JSON.

- **COBOTTA** uses both device-side P variables and a JSON file on the GUI computer. Teaching and clearing write and read back the selected point. Choosing Save on exit synchronizes changed points that are still listed, then writes the displayed list to the default JSON file. You can also export the list manually.
- **The bundled UR example** reads the current position through DeviceProxy and stores taught points in `JSON_FILE` on the GUI computer. The UR control instance has its own `ROBOT_VAR_FILE`. Teaching in this GUI leaves the control instance’s P points unchanged.

## Main functions

- Acquire the current robot position and associate it with a specified P number.
- Display and manage numbered positions in a Qt-based GUI.
- Load and save position tables as JSON files.
- Clear or delete selected positions, with behavior determined by storage mode.
- Manage variables programmatically using `RobotVarManager`.

## Operational notes

Teaching to a specified number can overwrite its existing value. The automatic “first unused P number” feature is
disabled because the implementation does not yet define a reliable unused-number criterion. Reading the current position
does not itself write to robot memory or JSON.

```{toctree}
:maxdepth: 2
:caption: Contents

Overview and architecture <en/overview>
Installation and launch <en/quickstart>
GUI tutorial <en/gui>
Python API usage <en/python_api>
JSON management and robot synchronization <en/storage>
Python API reference <en/api>
```
