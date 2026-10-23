# 変更履歴

[English](CHANGELOG.en.md) | [日本語](CHANGELOG.md)

## [0.1.0] - 2026-10-23

### 変更・追加

- GUI実装を `src/teaching_manager/teaching_gui.py` に移し、`example/teaching_gui.py` を起動専用に整理。
- GUI／Controller／Model／RobotVarManagerのMVC責務を整理。
- `CobottaCtrl` とその他のデバイス名で実機P変数／JSON保存先を自動選択。
- 現在位置の取得、指定番号と選択行へのティーチング、読み戻し。
- 右クリックからの書き込み、0クリア、一覧削除。Ctrl/Command・Shiftによる複数選択。
- JSON読込・保存ダイアログに既定のフォルダとファイル名を設定。任意ファイルの選択に対応。
- 終了時の未保存変更確認、Cobotta内部値の同期、JSON保存。
- 通信処理のワーカー化、条件分岐の簡素化、保存時の状態管理を改善。
- 日本語／英語のREADME、CHANGELOG、Sphinxチュートリアル、API自動生成、GitHub Pagesワークフローを整備。

### 既知の制限

- 空き番号への自動ティーチングは未実装。
- 通信タイムアウトはDeviceProxy側の仕様確認が必要。
- GUIと実機での動作確認は未実施。

## [0.0.0] - 2026-10-23

初期版。P変数一覧、現在位置の取得、ティーチング、JSON入出力、基本的なMVC構成を導入。
