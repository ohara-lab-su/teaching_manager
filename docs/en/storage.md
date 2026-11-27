# JSON storage, robot synchronization, and shutdown

The table describes the bundled examples, which omit `methods`.

| Operation          | CobottaCtrl               | Other devices         |
|--------------------|---------------------------|-----------------------|
| Startup            | Read robot P variables    | Load JSON             |
| Current position   | DeviceProxy               | DeviceProxy           |
| Teaching           | Write robot and read back | Update JSON           |
| Clear              | Write robot and read back | Update JSON           |
| Remove from list   | Keep robot value          | Also remove from JSON |
| Explicit JSON save | Save to selected file     | Save to selected file |
| Save on exit | Synchronize changed displayed points, then save the displayed list to the default JSON | Save the list to the default JSON |

The COBOTTA GUI initially reads P0 through P20. This is the GUI's initial selection. Users allocate the device-side P slots through a separate controller register, and allocated slots can be empty. Reading the entire JSON file returns the keys present in that file.

## JSON format

```json
{
  "P0": [
    0,
    0,
    0,
    0,
    0,
    0,
    -1
  ],
  "P1": [
    100,
    200,
    300,
    0,
    0,
    0,
    -1
  ]
}
```

This is a **format example**, not a guarantee about the coordinate format used by every robot. The Model loads keys
consisting of `P` followed by digits. The JSON root must be an object.

Saving on exit synchronizes changed displayed values to Cobotta, then writes the default JSON file. Rows removed from
the display are not deleted from the robot. A communication or file error may leave partial changes; back up important
coordinates before overwriting them.

When the launcher supplies `methods` to use device-managed points, the GUI loads all points at startup and the device saves teaching and clear operations. The GUI can export a separate copy.
