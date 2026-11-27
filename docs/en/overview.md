# Overview and architecture

Version 0.1.4 provides position retrieval, teaching to P variables, JSON import/export, clearing and removing rows, and
save confirmation on exit.

- `src/teaching_manager/teaching_gui.py`: Qt View, dialogs, table, and workers.
- `teaching_controller.py`: device-dependent storage selection and operation coordination.
- `teaching_model.py`: positions, DeviceProxy operations, JSON and synchronization.
- `robot_var_manager.py`: local variable cache and generic access methods.
- `example/teaching_cobotta_gui.py`, `example/teaching_ur_gui.py`: device-specific connection settings and proxy creation.
- `run_teaching_gui()`: accepts the device connection object and starts the shared Qt GUI.

**Important:** `RobotVarManager.get_var` and `set_var` operate on a **local cache**; they do not invoke the robot's
`DeviceProxy.get_var` / `set_var`. Robot writes overwrite stored coordinates. Automatic teaching to the first unused
number is not implemented.
