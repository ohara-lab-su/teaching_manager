# Python APIの使い方（GUI不要）

[English](../en/python_api.md)

## RobotVarManager：ローカル変数

以下の例はロボット接続を必要としません。`get_var()` は実機から読み込まず、ローカルキャッシュを参照します。

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

`set_vars("P", 10, 12, value=[...])` で範囲登録できます。`get_var` の未登録時の既定値は `False` です。`RobotVarManager.save/load` はマネージャーの全変数を対象にします。TeachingModelのJSONはP変数だけを対象にします。

## TeachingModel / Controller：保存先切り替え

```python
from teaching_manager.robot_var_manager import RobotVarManager
from teaching_manager.teaching_model import TeachingModel
from teaching_manager.teaching_controller import TeachingController

manager = RobotVarManager(autosave=False, autoload=False)
model = TeachingModel(manager, "robot_positions.json", async_mode=False)
controller = TeachingController(model, device_name="OtherRobot")
controller.load_initial(0, 20)  # OtherRobot: JSONから読み込み
print(controller.model.positions)
controller.save_file("backup.json")  # 表示データを任意JSONへ保存
```

上記例では実機に接続していないため `read_current_position()` と `teach_number()` は呼びません。ティーチングには現在位置の取得が先に必要です。Cobottaを接続する場合は `DeviceProxy(..., async_mode=False)` を `RobotVarManager(robot_instance=robot)` に渡してください。`TeachingController(..., device_name="CobottaCtrl")` は内部P変数モードです。

**同期モード**の `read_current_position()` は値を返し、`async_mode=True` ではコルーチンを返します。P変数の実機読み書きは同期DeviceProxyを要求します。
