# Installation and launch

Prepare `PySide6`, `x_logger`, the device package (`cobotta2` or `ur`), and the corresponding device server.
Run the launcher for your device from the repository root.

```bash
python example/teaching_cobotta_gui.py
python example/teaching_ur_gui.py
```

| Device | Default connection configuration | Teaching storage |
|---|---|---|
| Cobotta | `example/config_cobotta3_server5.yaml` | Robot P variables, with JSON export available |
| UR | `example/ur_server.yaml` | JSON file |

Set `SERVER_IP` and `SERVER_PORT` in the YAML file to match the device server. The UR default is `127.0.0.1:8000`,
for a server running in the same environment as the launcher. The UR example requires a version of `ur` that
registers `UrCtrl` with DeviceProxy.

Both examples default to `example/robot_positions.json`. Set a different `JSON_FILE` in each launcher to keep the
devices' taught positions separate. Relative paths are resolved against the launcher's directory.
See [JSON management and robot synchronization](storage.md) for storage and exit behavior.

## Building Pages

With Sphinx, MyST Parser, and the Read the Docs theme installed, run `bash docs/build.sh`.
The output is `docs/_build/html/`. GitHub Actions uses the same script.
