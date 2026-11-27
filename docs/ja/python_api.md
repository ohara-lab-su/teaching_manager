# Python APIの使い方（GUI不要）

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

`set_vars("P", 10, 12, value=[...])` で範囲登録できます。`get_var` の未登録時の既定値は `False` です。
`RobotVarManager.save/load` はマネージャーの全変数を対象にします。TeachingModelのJSONはP変数だけを対象にします。

`list_vars()` が返すキーを使い、`{key: manager[key] for key in manager.list_vars()}` で現在のキャッシュの全件を取得できます。例えば `P100` と `P1000` が保存されていれば、その二件が対象です。欠番は一覧に入りません。

指定した一点を削除する場合は `delete_var("P", 100)` を使います。全件取得の対象は読み込んだマネージャーの実在キーです。COBOTTA の装置側 P 変数は GUI が DeviceProxy 経由で取得します。

### 機器制御クラスから使うときの契約

`RobotVarManager` は変数名と値、JSON の全件読み書きを扱います。キャッシュに登録されたキーを列挙する `list_vars()` と、値を読む `manager[key]` が全件取得の基本です。一点の取得・更新・削除には `get_var()`、`set_var()`、`delete_var()` を使います。

番号・単位・座標の形式を決めるのは機器の制御クラスです。指定した点だけ変更して保存する場合は、キャッシュを更新した後、マネージャーが現在の全変数を同じ JSON に書きます。`set_var(..., save=True)` での保存失敗は呼び出し元に伝わり、その時点でキャッシュの更新は済んでいます。`save()` は既存ファイルを直接開くので、書き出し中に失敗した場合のファイル復元は保証しません。

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

上記例では実機に接続していないため `read_current_position()` と `teach_number()`
は呼びません。ティーチングには現在位置の取得が先に必要です。Cobottaを接続する場合は `DeviceProxy(..., async_mode=False)` を
`RobotVarManager(robot_instance=robot)` に渡してください。`TeachingController(..., device_name="CobottaCtrl")`
は装置側の P 変数モードです。終了時の `save_on_close()` は、一覧中の変更点の同期後に、一覧を既定 JSON に保存します。

**同期モード**の `read_current_position()` は値を返し、`async_mode=True` ではコルーチンを返します。P変数の実機読み書きは同期DeviceProxyを要求します。

## GUI 起動関数にメソッド名を渡す

`get_current_position()` は、Teaching Manager と接続先が共有する教示用の現在位置取得 I/F です。メソッドを直接記述する呼び出しと、名前を実行時に解決する呼び出しで契約は共通です。既存 API に別名を使う場合も、引数なしで教示に使える座標を返すメソッドを指定します。

`run_teaching_gui(robot, device_name, json_file, logger=None, *, methods=None)` の `methods` に、起動例から接続オブジェクトのメソッド名を文字列で指定できます。`current` の既定は `get_current_position` です。接続先が教示点を管理する場合は、`read_all`、`read`、`write` の三つをまとめて指定します。

| キー | 呼び出しと戻り値 |
| --- | --- |
| `current` | 既定名は `get_current_position`。引数なしで呼び、教示先が受け付ける座標を返す。 `False` または `None` は取得失敗。座標の単位は接続先の I/F に従い、GUI で変換せずに教示に使う。 |
| `read_all` | 引数なしで呼び、変数名と値の辞書を返す。GUI は起動時に一度呼び、存在する P 点をすべて表示する。 |
| `read` | P 番号を渡し、指定点の座標を取得する。 |
| `write` | P 番号と座標を渡し、成功時に `True` を返す。成功後は `read` で同じ一点を読み戻す。 |

保存は接続先の制御クラスが担います。クライアントでは同期 DeviceProxy を渡します。`methods` を省略した場合は従来の動作になります。
