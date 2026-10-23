# robot-teaching-manager: 読み取りテスト版

- `example/teaching_gui.py` を直接起動するとQt GUIが開きます（PySide6が必要）。
- `make_robot()` の import と `DeviceProxy(...)` の生成部分だけを実環境に合わせて変更します。
- ロボット読込: `DeviceProxy` 経由の `get_all_var()` を1回呼び、戻り値が辞書の場合に `P数字` キーを一覧表示します。
- 現在位置: `get_current_position()` を呼び、GUIに表示します。`get_current_pose()` は呼びません。
- 起動時は `robot_positions.json` を読み込みます。ファイルが存在しない場合は空表示です。
- JSONからの読込とロボットからの読込は独立しています。**ロボット読込時にJSONは上書きしません。**
- ティーチングボタンは配置していますが無効です。**`set_P()`、`set_var()`、`setattr()`、`save()` はGUIから呼びません。**
- `get_all_var()` が辞書以外を返す場合は、推測して解釈せずエラー表示します。実際の戻り値構造を確認してから対応します。
- 表示される「キーに存在しない番号」は、未使用が確定した番号ではありません。実機に書き込む根拠には使用しません。

配置: `src/teaching_manager/robot_var_manager.py` は提供された元ファイルを無変更で同梱しています。
