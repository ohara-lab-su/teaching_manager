# 概要・構成

[English](../en/overview.md)

v0.1.0 は、現在位置の取得、P番号へのティーチング、JSONの読み書き、一覧の0クリアと削除、終了時の保存確認を備えます。

MVCの役割は以下のとおりです。

- `teaching_gui.py`（`src/teaching_manager/`）：Qt View、ダイアログ、画面更新、ワーカー。
- `teaching_controller.py`：デバイス名に基づくP変数保存先の選択、操作の調整。
- `teaching_model.py`：位置データ、DeviceProxy API、JSON、同期処理。
- `robot_var_manager.py`：ローカル変数の保持と汎用的な入出力API。
- `example/teaching_gui.py`：実機接続設定とGUI起動。

## 注意

実機のP変数への書き込み・0クリアは既存座標を上書きします。`RobotVarManager` の `get_var` / `set_var` は**ローカルキャッシュ**の操作であり、実機の `DeviceProxy.get_var` / `set_var` とは異なります。

空き番号への自動ティーチングは未実装です。
