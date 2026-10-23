# Robot Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.md)

ロボットの現在位置を P 変数として登録・確認し、JSON ファイルで管理する Qt ベースのティーチング GUI です。

**バージョン: 0.0.0（初期版）**

## 主な機能

- ロボットの現在位置を取得して表示します。
- P 番号と座標の一覧を表示します。P 番号範囲を指定して読み込めます（Cobotta）。
- 指定した P 番号、または一覧で選択した P 番号に **取得済みの現在位置**を書き込みます。書き込み前に確認します。
- 一覧の右クリックメニューから、現在位置の書き込み、 **0 クリア**、 **一覧から削除**を実行できます。
- Ctrl／Command による複数行選択と Shift による範囲選択に対応します。0 クリアと一覧から削除は複数行をまとめて操作できます。
- 0 クリアは対象 P 番号を `[0, 0, 0, 0, 0, 0, -1]` に設定します。
- JSON ファイルからの読み込み、表示中の一覧の JSON 保存に対応します。

**注意:** 「空き番号にティーチング」ボタンはありますが、未使用番号の判定仕様が未確定のため、自動登録は実行できません。

## デバイスごとの保存先

`DeviceProxy` に渡す `device_name` で自動的に切り替わります。名前の比較は **`CobottaCtrl` と完全一致**です。

| 操作                 | `CobottaCtrl`                    | その他のデバイス名     |
|----------------------|----------------------------------|------------------------|
| 起動時の P 変数読込  | ロボット内部 P 変数              | JSON ファイル          |
| 現在位置の取得       | ロボット API                     | ロボット API           |
| 現在位置の登録       | ロボット内部 P 変数              | JSON に自動保存        |
| 0 クリア             | ロボット内部 P 変数              | JSON に自動保存        |
| 一覧から削除         | 表示一覧のみ（実機は変更しない） | 表示一覧と JSON        |
| 「JSONに保存」ボタン | 表示一覧を JSON に保存           | 表示一覧を JSON に保存 |

Cobotta の実機 P 変数の変更は JSON に自動保存されません。その他のデバイスでは、P 変数をロボット内部メモリに保存せず、JSON
を利用します。 **現在位置の取得には、どちらの場合も接続済みのロボットが必要です。**

## 構成

| ファイル                                      | 役割                                        |
|-----------------------------------------------|---------------------------------------------|
| `example/teaching_gui.py`                     | PySide6 の画面・操作・確認ダイアログ        |
| `src/teaching_manager/teaching_controller.py` | デバイス名による保存先選択と操作の振り分け  |
| `src/teaching_manager/teaching_model.py`      | P 変数・現在位置・ロボット API・JSON の処理 |
| `src/teaching_manager/robot_var_manager.py`   | ローカル変数管理                            |

GUI、Controller、Model を分離した MVC 構成です。

## 起動と設定

現行の `example/teaching_gui.py` は `PySide6`、`x_logger`、`cobotta2` を import
します。これらのパッケージと接続先の設定ファイルを、使用環境に合わせて用意してください。依存関係を宣言するパッケージ設定ファイルは今回の確認対象に含まれていないため、対応バージョンはここでは規定しません。

`example/teaching_gui.py` の `main()` で、`Config("config_cobotta3_server5.yaml")`、`device_name = "CobottaCtrl"`、
`DeviceProxy(...)` を設定します。JSON の保存先は同ファイル内の `JSON_FILE` で、初期値はプロジェクトルートの
`robot_positions.json` です。P 番号の GUI 入力範囲は 0〜999、起動時の読込範囲の初期値は P0〜P20 です。

プロジェクトルートからの実行例:

```sh
python example/teaching_gui.py
```

ロボット通信が必要な操作は、対応する DeviceProxy とサーバーが利用可能な状態で実行してください。

## 操作上の注意

- 書き込み・0 クリアは既存の座標を上書きします。確認ダイアログで対象を確認してください。
- Cobotta の「一覧から削除」はロボット内部 P 変数を消去しません。0 クリアとは別操作です。
- JSON 管理モードの「一覧から削除」は JSON にも反映されます。
- ロボットへの書き込み後は P 変数を読み戻して検証します。
- 現在位置の取得中に画面を閉じると、通信スレッドの終了待ちが発生する場合があります。

## 更新履歴

[CHANGELOG.md](CHANGELOG.md) / [CHANGELOG.en.md](CHANGELOG.en.md)
