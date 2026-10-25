# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/ja/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

**Version 0.1.0** — ロボット位置のティーチングとP変数のJSON管理を行うPythonパッケージ／PySide6 GUI。

## 機能

Cobotta (`device_name == "CobottaCtrl"`)
は実機P変数、それ以外のロボットはJSONファイルを保存先に使用します。現在位置の取得、指定P番号への書き込み、一覧の右クリック操作、複数行の0クリアと削除、任意JSONの読み込み・保存、終了時の保存確認に対応します。

GUI本体は `src/teaching_manager/teaching_gui.py`、起動例は `example/teaching_gui.py`
にあります。Controller、Model、RobotVarManagerを分離したMVC構成です。

## 起動

実機用の `cobotta2`、`x_logger`、GUI用の `PySide6` と接続設定を用意し、起動用スクリプトの `device_name`、`Config(...)`、
`JSON_FILE` を設定してください。

```bash
python example/teaching_gui.py
```

## ドキュメント

- [日本語チュートリアル・API](docs/jp/index.md)
- [English tutorial and API](docs/en/index.md)
- [言語選択トップ](docs/index.md)

PagesはSphinxで生成し、`RobotVarManager`、`TeachingModel`、`TeachingController`、GUIのAPIをdocstringから自動抽出します。
`bash docs/build.sh` でビルドできます。

**注意:** 0クリアは `[0, 0, 0, 0, 0, 0, -1]`
を書き込みます。Cobottaの「一覧削除」は実機値を削除しません。空き番号への自動ティーチングは未実装です。実機書き込みは終了時の「保存しない」では元に戻りません。

[変更履歴](CHANGELOG.md)
