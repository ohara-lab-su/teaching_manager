# 導入・起動

[English](../en/quickstart.md)

PythonとGUI依存パッケージ（PySide6、cobotta2、x_logger）、実機側サーバーおよび接続設定を用意します。パッケージの依存バージョンは本資料だけでは確定できません。

起動例（リポジトリルートから）：

```bash
python example/teaching_gui.py
```

`example/teaching_gui.py` の `device_name`、`Config(...)`、`JSON_FILE` を使用環境に合わせて設定します。`JSON_FILE` に相対パスを与えた場合、起動用 `teaching_gui.py` があるフォルダを基準に解決します。

`CobottaCtrl` は実機P変数、それ以外のデバイス名はJSON管理になります。現在位置取得にはいずれも接続先が必要です。

## Pages のビルド

Sphinx、MyST Parser、Read the Docs Themeをインストールした環境で `bash docs/build.sh` を実行します。出力は `docs/_build/html/` です。GitHub Actionsからも同じスクリプトを使用します。
