# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/ja/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

**Version 0.1.3** — ロボット位置のティーチングとP変数のJSON管理を行うPythonパッケージ／PySide6 GUI。

## 機能

Cobotta の教示先は実機の P 変数で、一覧は JSON にも保存できます。UR など他の装置の教示先は JSON ファイルです。
現在位置の取得、指定 P 番号への書き込み、複数行の0クリアと削除、JSON の読み込み・保存、終了時の保存確認に対応します。

機種別の起動例が接続を組み立て、パッケージの `run_teaching_gui()` が共通の GUI を起動します。

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
