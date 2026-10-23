# GUI tutorial

[日本語](../jp/gui.md)

1. At startup, Cobotta loads the requested P range from the robot; other devices load the default JSON file.
2. Retrieve the robot's current position.
3. Teach the **retrieved current position** to a specified P number or a single selected table row; confirm overwrites.
4. Right-click a row to teach, clear, or remove. Ctrl/Command and Shift support multi-row selection for clearing/removal.
5. **Clear** assigns `[0, 0, 0, 0, 0, 0, -1]`. **Remove from list** only removes rows; it does not delete internal Cobotta P variables.
6. Use file dialogs to load/save arbitrary JSON files. Their initial path and filename come from `JSON_FILE`.
7. When closing with pending changes, choose to save, discard, or cancel. In Cobotta mode, the save operation also considers synchronization to the robot.

**Warning:** Cobotta writes are executed when the teaching action is performed. Discarding changes on exit does **not** roll back completed robot writes. Shutdown may wait for an active communication operation.
