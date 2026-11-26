# 導入・起動

`PySide6` と `x_logger`、使用する装置のパッケージ（`cobotta2` または `ur`）、対応する装置サーバーを用意します。
リポジトリ直下から使用する装置の起動例を実行します。

```bash
python example/teaching_cobotta_gui.py
python example/teaching_ur_gui.py
```

| 装置 | 既定の接続設定 | 教示先 |
|---|---|---|
| Cobotta | `example/config_cobotta3_server5.yaml` | 実機の P 変数。JSON への書き出しも可能 |
| UR | `example/ur_server.yaml` | JSON ファイル |

各 YAML の `SERVER_IP` と `SERVER_PORT` は接続先の装置サーバーに合わせます。UR の既定値は `127.0.0.1:8000` で、
UR の起動例を実行する環境にサーバーがある場合に使います。UR の起動例には、`UrCtrl` を DeviceProxy に登録する版の `ur` が必要です。

両起動例とも既定で `example/robot_positions.json` を使います。機種ごとに教示点を分ける場合は、各起動例の
`JSON_FILE` に別のファイル名を指定します。相対パスの基準は起動例のディレクトリです。
保存方式と終了時の動作は [JSON管理・実機同期](storage.md) を参照してください。

## Pages のビルド

Sphinx、MyST Parser、Read the Docs Theme をインストールした環境で `bash docs/build.sh` を実行します。
出力は `docs/_build/html/` です。GitHub Actions も同じスクリプトを使います。
