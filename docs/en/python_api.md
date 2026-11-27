# Python API without the GUI

## RobotVarManager: local variable cache

The following example requires no robot connection. `get_var()` reads the **local cache**, not the robot.

```python
from teaching_manager.robot_var_manager import RobotVarManager

manager = RobotVarManager(autosave=False, autoload=False)
manager.set_var("P", 10, [1, 2, 3, 4, 5, 6, -1], save=False)
print(manager.get_var("P", 10))
print(manager.get_var("P10"))
print(manager.list_vars())
manager.save("positions.json")
manager.load("positions.json")
manager.delete_var("P", 10)
```

`set_vars("P", 10, 12, value=[...])` sets a range. Missing variables default to `False`. `RobotVarManager.save/load`
handles **all** cached variable kinds; `TeachingModel` filters to P variables.

Use `{key: manager[key] for key in manager.list_vars()}` to retrieve all keys and values in the current cache. If it contains `P100` and `P1000`, the gap does not create entries.

Use `delete_var("P", 100)` to delete one point. Full retrieval enumerates the entries held by the manager. For COBOTTA, the GUI retrieves device-side P variables through DeviceProxy.

### Contract for device control classes

`RobotVarManager` stores named values and reads and writes whole JSON files. To retrieve all cached entries, enumerate the keys with `list_vars()` and read each value through `manager[key]`. Use `get_var()`, `set_var()`, and `delete_var()` for individual entries.

The device control class defines valid numbers, units, and coordinate formats. To persist a one-point change, update that entry in the cache. The manager then writes all current variables to the same JSON file. If `set_var(..., save=True)` fails while saving, the exception reaches the caller after the cache has been updated. `save()` opens the existing file directly and does not guarantee recovery after a failed write.

## TeachingModel and Controller

```python
from teaching_manager.robot_var_manager import RobotVarManager
from teaching_manager.teaching_model import TeachingModel
from teaching_manager.teaching_controller import TeachingController

manager = RobotVarManager(autosave=False, autoload=False)
model = TeachingModel(manager, "robot_positions.json", async_mode=False)
controller = TeachingController(model, device_name="OtherRobot")
controller.load_initial(0, 20)  # Load JSON in non-Cobotta mode
print(controller.model.positions)
controller.save_file("backup.json")
```

This example has no robot connection, so it does not call `read_current_position()` or `teach_number()`. Teaching
requires a previously retrieved current position. For Cobotta, pass a synchronous `DeviceProxy(..., async_mode=False)`
as `RobotVarManager(robot_instance=robot)` and use `device_name="CobottaCtrl"`. Calling `save_on_close()` synchronizes changed points still in the list, then saves the displayed list to the default JSON.

With `async_mode=False`, `read_current_position()` returns the position. With `async_mode=True`, it returns a coroutine
that must be awaited. Reading/writing robot P variables requires a synchronous DeviceProxy.

## Supplying method names to the GUI launcher

`get_current_position()` is the shared interface between Teaching Manager and the device for reading the pose used in teaching. Direct calls and runtime name lookup share the same contract. If the device uses a different method name, supply a method that takes no arguments and returns a pose the teaching operation accepts.

The launcher can supply method names as strings in `run_teaching_gui(robot, device_name, json_file, logger=None, *, methods=None)`. The `current` entry defaults to `get_current_position`. When the device manages its own taught points, supply `read_all`, `read`, and `write` together.

| Key | Call and result |
| --- | --- |
| `current` | Defaults to `get_current_position`. Takes no arguments and returns a pose that the teaching operation accepts. `False` or `None` indicates failure. The GUI uses the device's pose and units as returned. |
| `read_all` | Takes no arguments and returns a dictionary of variable names and values. The GUI calls it once at startup and displays all existing P points. |
| `read` | Takes a P number and returns that point’s pose. |
| `write` | Takes a P number and a pose and returns `True` on success. The GUI then calls `read` for the same point. |

The device control class handles saving. Pass a synchronous DeviceProxy when running the GUI as a client. Omitting `methods` preserves the existing behavior.
