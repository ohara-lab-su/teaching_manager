# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/ja/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

**Version 0.1.4** — ロボット位置のティーチングとP変数のJSON管理を行うPythonパッケージ／PySide6 GUI。

## 機能

Teaching Manager は、起動例が作った DeviceProxy を受け取り、共通の GUI で現在位置の取得、P 番号への教示、JSON の読み込み・書き出しを行います。

- **COBOTTA** は装置側の P 変数と GUI 側の JSON の両方を扱います。教示・0クリアは指定した P 点を装置側に書き込み、読み戻します。終了時に「保存」を選ぶと、一覧中の変更点を装置側に同期してから、一覧を既定の JSON に保存します。手動で JSON を書き出すこともできます。
- **UR の同梱例**は、DeviceProxy で現在位置を取得し、教示点を GUI 側の `JSON_FILE` に保存します。UR 制御側の `ROBOT_VAR_FILE` は別の保存先です。GUI 側の教示で UR 制御側の P 点は更新されません。
- **機器が教示点を管理する構成**では、起動例から `run_teaching_gui(..., methods=...)` に操作のメソッド名を渡します。[Python API](docs/ja/python_api.md)

Python から保存済み変数を使う場合は、`RobotVarManager.load()` で JSON を全件読み、`list_vars()` とキー参照で値を取得します。欠番を埋める必要はありません。 [Python API](docs/ja/python_api.md)

## 起動

`PySide6` と `x_logger`、使用する装置のパッケージ（`cobotta2` または `ur`）、対応する装置サーバーを用意してください。
リポジトリ直下から使用する装置の起動例を実行します。

```bash
python example/teaching_cobotta_gui.py
python example/teaching_ur_gui.py
```

Cobotta の起動例は既定で `config_cobotta3_server5.yaml` を読みます。UR は `ur_server.yaml` を読み、
`UrCtrl` を DeviceProxy に登録する版の `ur` が必要です。接続先と `JSON_FILE` の詳細は [導入・起動](docs/ja/quickstart.md) を参照してください。

## ドキュメント

- [日本語チュートリアル・API](docs/ja/index.md)
- [English tutorial and API](docs/en/index.md)
- [ドキュメントトップ](docs/index.md)

PagesはSphinxで生成し、`RobotVarManager`、`TeachingModel`、`TeachingController`、GUIのAPIをdocstringから自動抽出します。
`bash docs/build.sh` でビルドできます。

**注意:** 0クリアは `[0, 0, 0, 0, 0, 0, -1]`
を書き込みます。Cobottaの「一覧削除」は実機値を削除しません。空き番号への自動ティーチングは未実装です。実機書き込みは終了時の「保存しない」では元に戻りません。

[変更履歴](CHANGELOG.ja.md)
