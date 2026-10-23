# JSON storage, robot synchronization, and shutdown

[日本語](../jp/storage.md)

| Operation | CobottaCtrl | Other devices |
|---|---|---|
| Startup | Read robot P variables | Load JSON |
| Current position | DeviceProxy | DeviceProxy |
| Teaching | Write robot and read back | Update JSON |
| Clear | Write robot and read back | Update JSON |
| Remove from list | Keep robot value | Also remove from JSON |
| Explicit JSON save | Save to selected file | Save to selected file |

## JSON format

```json
{
  "P0": [0, 0, 0, 0, 0, 0, -1],
  "P1": [100, 200, 300, 0, 0, 0, -1]
}
```

This is a **format example**, not a guarantee about the coordinate format used by every robot. The Model loads keys consisting of `P` followed by digits. The JSON root must be an object.

Saving on exit synchronizes changed displayed values to Cobotta, then writes the default JSON file. Rows removed from the display are not deleted from the robot. A communication or file error may leave partial changes; back up important coordinates before overwriting them.
