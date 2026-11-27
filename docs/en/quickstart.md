# Installation and launch

Prepare `PySide6`, `x_logger`, the device package (`cobotta2` or `ur`), and the corresponding device server.
Run the launcher for your device from the repository root.

```bash
python example/teaching_cobotta_gui.py
python example/teaching_ur_gui.py
```

| Device | Default connection configuration | Teaching storage |
|---|---|---|
| Cobotta | `example/config_cobotta3_server5.yaml` | Device-side P variables and GUI-side JSON saved after synchronization on exit |
| UR | `example/ur_server.yaml` | JSON file |

Set `SERVER_IP` and `SERVER_PORT` to match the running device server. The UR example requires a version of `ur` that registers `UrCtrl` with DeviceProxy.

Both examples handle `JSON_FILE` on the computer running the GUI. Relative paths are resolved from the launcher's directory. Both default to `robot_positions.json`. Set a distinct `JSON_FILE` in each example to separate COBOTTA's saved list from the UR GUI's teaching data. [Storage and exit behavior](storage.md)

The bundled UR GUI needs a UR server whose control instance is already connected to read the current position. It stores taught points in its local `JSON_FILE`. The launchers in the UR repository pass `methods` to Teaching Manager 0.1.4 and use the UR control instance’s `ROBOT_VAR_FILE` for teaching. When running the GUI as a client, the UR server handles this file. [Launcher configuration](python_api.md)

## Building Pages

With Sphinx, MyST Parser, and the Read the Docs theme installed, run `bash docs/build.sh`.
The output is `docs/_build/html/`. GitHub Actions uses the same script.
