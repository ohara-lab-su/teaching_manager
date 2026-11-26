# Teaching Manager 引継書

Teaching Manager は、ロボットの現在位置を読み取り、指定した P 番号と結び付けて管理する末端ツールです。座標を GUI 側の JSON で管理する方式を基本とし、`CobottaCtrl` にはロボット内部の P 変数を読み書きする既存機能があります。装置ごとの接続処理は起動例にあり、画面の生成、教示操作、保存処理はパッケージにあります。

## 1. 引継ぎ時点の状態

| 対象 | ソースで確認した状態 | 実行で確認できた範囲 |
|---|---|---|
| Teaching Manager | ローカル `60882ba`、パッケージ定義は `0.1.2`。Cobotta・UR の起動例ともに共通の `run_teaching_gui()` を呼ぶ | 以前のローカル確認では模擬オブジェクトで起動経路と Qt の生成順を確認 |
| Cobotta | `DeviceProxy("CobottaCtrl", ..., async_mode=False)` が同期クライアントを選ぶ | 提示ログでクライアント生成と `get_var("P", 0)`〜`get_var("P", 20)` の要求を確認。個々の応答値、現在位置取得、教示書き込み、JSON 保存の結果はログに含まれていない |
| UR | 起動例は現時点で `DeviceProxy("UrCtrl", ...)` を呼ぶ。後述の互換名への変更は案の段階 | 提示ログで YAML の解決と読み込みを通過し、Factory の登録検索で `KeyError`。HTTP 接続や現在位置取得には未到達 |

今回の作業ではソースと資料の照合を行いました。インストール済みパッケージの版、実機、公開 Pages、Sphinx ビルドは今回の確認対象外です。

## 2. 起動から教示までの責務

| 場所 | 担当 |
|---|---|
| [Cobotta 起動例](example/teaching_cobotta_gui.py) | `cobotta2.Config` で YAML を読み、`cobotta2.server_fastapi.DeviceProxy` で `CobottaCtrl` の同期クライアントを生成する |
| [UR 起動例](example/teaching_ur_gui.py) | `ur.Config` で YAML を読み、現行コードでは `ur.server_fastapi.DeviceProxy` に `UrCtrl` を指定する |
| [共通起動と View](src/teaching_manager/teaching_gui.py) | `run_teaching_gui(robot, device_name, json_file, logger=None)` が `QApplication`、Manager、Model、Controller、Window の順に生成し、Qt の終了コードを返す。Window がボタン、確認、一覧、ワーカーを担当する |
| [Controller](src/teaching_manager/teaching_controller.py) | `device_name` が厳密に `CobottaCtrl` のとき実機 P 変数モードにし、それ以外は JSON モードにする。操作を Model に委譲する |
| [Model](src/teaching_manager/teaching_model.py) | 最新の現在位置、表示中の教示点、保存・同期の比較状態を保持し、必要に応じてロボット API または JSON を使う |
| [Manager](src/teaching_manager/robot_var_manager.py) | 接続オブジェクトとローカル変数キャッシュを保持する。Manager の `get_var()` / `set_var()` はキャッシュ用。独立した JSON 入出力と、動的属性経由の明示的な転送 API も持つ |

画面の「現在位置を取得」は `TeachingWindow → TeachingController → TeachingModel → robot.get_current_position()` と進みます。Model は Manager の `robot_instance` を参照し、返り値が awaitable なら待機します。`False` と `None` は取得失敗として扱い、成功時に取得値を保持します。教示ボタンが保存するのは**最後に取得した位置**です。ボタンを押した時点で現在位置を取り直す動作はありません。

Window は通信やファイル操作を `QThread` に渡し、一度に一件ずつ処理します。起動時の初期読込は Qt イベントループ開始後です。Cobotta の初期範囲は P0〜P20 を両端込みで読み、入力欄は 0〜999 を受け付けます。ステータスの「接続あり」は `robot` が存在することを示します。サーバー到達性は、実際の読み取り結果で判断します。

別の装置を JSON モードで利用する場合は、その装置の接続オブジェクトを起動側で生成し、`get_current_position()` から JSON 化できる座標を返せるようにします。装置側の API 名が異なる場合は、起動側のアダプターで吸収できます。現在位置取得と JSON 教示に、装置側の `get_var()` / `set_var()` は不要です。

## 3. YAML と機種固有の実装

- **接続 YAML** は各装置パッケージの `Config` が読み、Teaching Manager は設定オブジェクトをクライアントに渡します。提示された Cobotta と UR の同期 ClientClass は `SERVER_IP` と `SERVER_PORT` を読み、HTTP の接続先を組み立てます。`COBOTTA_IP` / `ROBOT_IP` はサーバー側の装置設定です。少なくとも確認した同期クライアントでは、YAML の `TIMEOUT` を基底クライアントに渡す処理はありません。Cobotta の提示ログには実際のタイムアウトとして `60.0` が出ています。
- **Cobotta** の起動例が参照するのは [config_cobotta3_server5.yaml](example/config_cobotta3_server5.yaml) です。[config_cobotta1_server1.yaml](example/config_cobotta1_server1.yaml) は別の接続先の設定です。Cobotta パッケージは `CobottaCtrl` と別名 `cobotta` を Factory に登録し、同期経路では `SyncCobottaClient` を選びます。HTTP 側の公開名は `cobotta` です。サーバー側の `CobottaCtrl` は現在位置と変数操作を b-CAP または ORiN2 のバックエンドに委譲します。
- **UR** の起動例は [ur_server.yaml](example/ur_server.yaml) の絶対パスを渡します。提供された `Config` は、相対パスでも呼び出し元のスクリプトを基準に解決します。以前の「作業ディレクトリ基準」という説明は誤りです。現行 YAML の接続先は `127.0.0.1:8000` です。UR サーバーが別のホストで動く構成なら、GUI 側の YAML にはそのサーバーの到達可能なアドレスを指定します。
- **UR の現在位置取得**は `SyncURClient → ese774 の API ディスパッチ → UrRouterCtrl / ur_ctrl_api_spec → UrCtrl → UrRtde → RTDEReceiveInterface.getActualTCPPose()` の経路です。HTTP 側の公開名は `ur` で、戻り値は `[x, y, z, rx, ry, rz]` の 6 成分です。位置は mm、姿勢は degree 表記の回転ベクトルです。Cobotta の通常の P 形式は末尾に `fig` を含む 7 成分です。GUI は座標系・姿勢・成分数を変換せず、受け取った値を保持します。

SUSANOO の DeviceClass はサーバー側で装置処理を実装し、DeviceServer がその API を公開します。利用側の ClientClass はその操作を代理します。`DeviceProxy()` はクライアントプロセス内で登録名から ClientClass を選ぶ Factory です。Factory の登録名、HTTP の公開名、Teaching Manager の画面表示・保存モード用の名前は、それぞれ別の役割を持ちます。

## 4. UR の起動エラーと差し替え案

提示ログの `DeviceProxy is not registered: UrCtrl` は、YAML の読み込み後、Factory が `UrCtrl` の登録を探す時点で発生しています。UR ソースの `831e102` と作業ツリーの `src/ur/server_fastapi/__init__.py` を比較しました。

| UR ソース | 登録名 | 別名 | 同期 ClientClass |
|---|---|---|---|
| `831e102` | `UrRtde` | `ur` | `SyncURClient` |
| 作業ツリー | `UrCtrl` | `ur`、`UrRtde` | `SyncURClient` |

`UrCtrl` が見つからないことは前者の登録内容と整合します。`site-packages` から import された UR の実ファイルを確認するまでは、実行環境の版を確定できません。UR の現行利用例は公開入口の `ur.server` を import します。この入口は内部の `ur.server_fastapi` を読み込むため、import の変更だけで登録名の差は解決しません。

両方の UR ソースに対応させる変更案は、[UR 起動例](example/teaching_ur_gui.py) の次の2点です。

```diff
-    from ur.server_fastapi import DeviceProxy
+    from ur.server import DeviceProxy

     robot = DeviceProxy(
-        device_name,
+        "ur",
         config=config,
         logger=logger,
         async_mode=False,
     )
```

`device_name = "UrCtrl"` は共通 GUI に渡し、表示名と JSON モードを保ちます。修正後の確認は、クライアント生成、実際の HTTP 接続先、`get_current_position()` の応答、JSON 保存の順に行うと失敗箇所を切り分けられます。UR リポジトリの `client_sample.py` には状態変更や移動操作も含まれるため、現在位置の確認には Teaching Manager の読取ボタンを使います。

## 5. モード別の保存と状態管理

| 操作 | Cobotta の実機 P 変数モード | UR などの JSON モード |
|---|---|---|
| 初期一覧 | 実機に `get_var("P", number)` を範囲分呼ぶ | 既定 JSON を読む。未作成なら空一覧 |
| 現在位置取得 | `get_current_position()` の結果を保持 | 同じ |
| 指定番号へ教示 | `set_var()` 後に `get_var()` で読み戻し、一覧を更新 | 値を既定 JSON に保存後、一覧を更新 |
| 0クリア | `[0, 0, 0, 0, 0, 0, -1]` を実機に書き、読み戻し値を照合 | 現状は同じ固定値を既定 JSON に保存 |
| 一覧から削除 | 表示とキャッシュから削除。操作時に実機と JSON には書き込まない | 既定 JSON からも削除 |
| 手動の JSON 保存 | 選んだファイルに表示一覧を書き出す | 同じ |
| 終了確認で Yes | 表示中の差分を実機へ同期し、既定 JSON も保存 | 既定 JSON を保存 |

- **Cobotta の内部 P 変数モードでも JSON は保存できます。** 教示と0クリアの直後は実機側を更新し、JSON への書き出しは手動保存または終了時の Yes で実行します。終了時の No は、すでに行った実機への書き込みを取り消しません。内部 P 変数モードを一時停止する専用の設定項目は現行コードにありません。
- **GUI の JSON と UR サーバー側の仮想変数は別です。** UR の `ROBOT_VAR_FILE` は UR 制御側の仮想変数設定です。Teaching Manager の JSON モードは GUI 側の `JSON_FILE` へ保存します。両起動例の既定値は同じ `example/robot_positions.json` です。機種ごとの教示点を別々に管理するには、各起動例に別々の `JSON_FILE` を指定します。
- **一覧の状態は Model が所有します。** `_positions` は表示、`_saved_positions` は保存判定の比較基準、`_robot_positions` は実機同期の比較基準です。実機から一覧を読み直した時点でも保存判定の基準は更新されるため、読み取っただけでは終了時の JSON 保存確認は出ません。任意ファイルの読込・保存では既定パスは変わりません。次の JSON モードの教示や削除は既定 JSON に反映されます。Manager のキャッシュは表示一覧とは別管理で、JSON の読込だけではキャッシュへ再投入されません。
- **書き込みの途中状態を区別します。** JSON 保存には同じディレクトリの一時ファイルと `os.replace()` を使います。実機書き込み後の読み戻しや終了時の JSON 保存が失敗しても、行われた実機書き込みは残る可能性があります。複数行の0クリアは各番号を順次処理し、途中失敗時は完了済み番号を表示します。

## 6. 続きの作業

1. **UR の起動を復旧する。** 第4節の差分を UR の起動例に適用し、該当 Python 環境で Factory の登録検索を通過することを確認します。その後、正しいサーバーに対する現在位置の読取と、運用データから分けた JSON への保存を確認します。
2. **機種ごとの JSON と0クリアの扱いを決める。** 既定 JSON の共有には、UR の6成分と Cobotta の7成分や姿勢表現が混在する余地があります。UR の JSON モードにも7成分の固定クリア値が入ります。空き番号への自動教示は、`first_unused()` が常に `None`、実行側は例外、GUI ボタンは無効という現状です。空き判定やクリアの意味を変更する場合は、装置ごとの要件を確認します。
3. **README と Pages の現行化。** 日英 README と `docs/{ja,en}/quickstart.md`・`overview.md` に旧起動例 `example/teaching_gui.py` が残っています。日本語 README の `docs/jp/index.md` は現行配置では `docs/ja/index.md` です。API ページの GUI 節は `TeachingWindow` のみを明示しているため、共通起動 API も文書化する場合はそこへ追加します。パッケージ版の `0.1.2` と Sphinx・README の `0.1.0` 表示、`docs/index.md` 直下の toctree 参照も照合が必要です。変更履歴にある古い起動名は、当時の記録として扱います。
4. **ドキュメントと対応 Python を検証する。** [docs/build.sh](docs/build.sh) は `src` を `PYTHONPATH` に加え、Sphinx で `docs/_build/html/` を生成して `.nojekyll` を置きます。[docs/conf.py](docs/conf.py) では MyST、autodoc、外部依存のモックを設定し、Pages Workflow は同じビルドスクリプトを呼びます。ビルド結果と公開反映は別々に確認します。`pyproject.toml` の `requires-python = ">=3.7"` は、現コードの `str | None` などの型注釈と整合していません。提示された実行ログの環境は Python 3.12.11 です。

## 7. 参照したソース

プロジェクトの追跡ファイル、Cobotta の指定されたソース・資料、UR の指定ファイルと日本語資料、Ohara Lab のトップと日本語 SUSANOO 資料のテキストを全文読み込み、登録、起動、座標取得、保存に関わる実装を追跡しました。資料の図はファイルの所在を確認しました。

- Teaching Manager `60882ba` の起動例、パッケージ4ファイル、日本語 README と変更履歴、Sphinx と日英資料。 [パッケージ](src/teaching_manager/) · [日本語資料](docs/ja/)
- cobotta2 `195e67a` のパッケージと資料。主な根拠は `config.py`、`server_fastapi/__init__.py`、`clients/sync_cobotta_client.py`、`spec_ctrl.py`、`cobotta_ctrl.py`、b-CAP と ORiN2 バックエンド。 [ソース](../cobotta2/src/cobotta2/) · [資料](../cobotta2/docs/)
- UR `831e102` と作業ツリーの差分。主な根拠は `run_server.py`、`client_sample.py`、`server.py`、`config.py`、`server_fastapi/`、`ur_ctrl.py`、`ur_rtde.py` と座標・変数の資料。 [起動例](../ur/examples/) · [FastAPI 実装](../ur/src/ur/server_fastapi/) · [日本語資料](../ur/docs/ja/)
- Ohara Lab `1b2762e` と作業ツリーの日本語 SUSANOO 資料。装置 API、公開経路、クライアント選択の役割を照合しました。 [索引](../ohara-lab-su/index.md) · [DeviceProxy Factory](../ohara-lab-su/ja/susanoo/susanoo_device_proxy_factory.md) · [UR の ese774 実装例](../ohara-lab-su/ja/susanoo/susanoo_ese774_examples.md)
