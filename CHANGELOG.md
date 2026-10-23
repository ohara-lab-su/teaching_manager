# 変更履歴

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/CHANGELOG.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/teaching_manager/blob/main/CHANGELOG.md)

## [0.0.0] - 2026-10-23

初期バージョン。

### 追加

- PySide6 による P 変数ティーチング GUI。
- GUI / Controller / Model を分離した MVC 構成。
- `DeviceProxy` を使用したロボット現在位置の取得と表示。
- Cobotta の指定範囲 P 変数の読み込みと一覧表示。
- 指定 P 番号・選択行への現在位置の書き込みと確認ダイアログ。
- 一覧の右クリックメニューによる書き込み、0 クリア、一覧からの削除。
- Ctrl／Command・Shift による複数行選択と一括 0 クリア・一覧削除。
- 0 クリア値 `[0, 0, 0, 0, 0, 0, -1]`。
- JSON の読み込みと表示一覧の保存。
- `device_name == "CobottaCtrl"` の場合は実機 P 変数、それ以外は JSON を保存先とする自動切り替え。
- JSON 管理モードでの登録・クリア・削除時のファイル自動更新。
- 実機への書き込み後の読み戻し確認。
- 現在位置取得用ワーカースレッドと終了時のスレッド待機。

### 既知の制限

- 空き P 番号の自動判定・自動ティーチングは未実装（操作時にエラーを表示）。
- 実機通信中の終了待機により、ウィンドウを閉じるまで時間がかかる場合がある。
