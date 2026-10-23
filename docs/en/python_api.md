# Python API without the GUI

[日本語](../jp/python_api.md)

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

`set_vars("P", 10, 12, value=[...])` sets a range. Missing variables default to `False`. `RobotVarManager.save/load` handles **all** cached variable kinds; `TeachingModel` filters to P variables.

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

This example has no robot connection, so it does not call `read_current_position()` or `teach_number()`. Teaching requires a previously retrieved current position. For Cobotta, pass a synchronous `DeviceProxy(..., async_mode=False)` as `RobotVarManager(robot_instance=robot)` and use `device_name="CobottaCtrl"`.

With `async_mode=False`, `read_current_position()` returns the position. With `async_mode=True`, it returns a coroutine that must be awaited. Reading/writing robot P variables requires a synchronous DeviceProxy.
