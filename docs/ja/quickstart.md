# 導入・起動

`PySide6` と `x_logger`、使用する装置のパッケージ（`cobotta2` または `ur`）、対応する装置サーバーを用意します。
リポジトリ直下から使用する装置の起動例を実行します。

```bash
python example/teaching_cobotta_gui.py
python example/teaching_ur_gui.py
```

| 装置 | 既定の接続設定 | 教示先 |
|---|---|---|
| Cobotta | `example/config_cobotta3_server5.yaml` | 装置側の P 変数と、終了時の同期後に保存する GUI 側 JSON |
| UR | `example/ur_server.yaml` | JSON ファイル |

各 YAML の `SERVER_IP` と `SERVER_PORT` を実際の装置サーバーに合わせます。UR の起動例には、`UrCtrl` を DeviceProxy に登録する版の `ur` が必要です。

両起動例の `JSON_FILE` は GUI を実行する PC が扱い、相対パスは起動例のディレクトリが基準です。コード上の既定ファイル名は両方とも `robot_positions.json` です。COBOTTA の同期後の保存先と、UR の教示点の保存先を分けて運用するには、起動例ごとに `JSON_FILE` を設定します。[保存のタイミングと終了時の動作](storage.md)

同梱の UR GUI は現在位置を取得するために、接続済みの制御実体を持つ UR サーバーを使います。教示点は GUI 側の `JSON_FILE` に保存します。UR リポジトリの起動例は Teaching Manager 0.1.4 の `methods` を指定し、UR 制御側の `ROBOT_VAR_FILE` を教示点の保存先にします。クライアントで起動すると、ファイルを扱うのは UR サーバーです。[起動関数の設定](python_api.md)

## Pages のビルド

Sphinx、MyST Parser、Read the Docs Theme をインストールした環境で `bash docs/build.sh` を実行します。
出力は `docs/_build/html/` です。GitHub Actions も同じスクリプトを使います。
