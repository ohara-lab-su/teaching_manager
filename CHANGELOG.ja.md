# 変更履歴

[![en](https://img.shields.io/badge/lang-en-red.svg)](CHANGELOG.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](CHANGELOG.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/ja/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

## [0.1.3]

- Cobotta と UR の起動例を分け、UR 用の接続設定 `example/ur_server.yaml` を追加。
- `run_teaching_gui()` に共通の GUI 起動処理をまとめ、画面の生成前に `QApplication` を初期化。
- 日英の README と Pages を現在の起動方法に更新し、共通起動関数を API リファレンスに追加。
- Pages のトップから英語版と日本語版の目次へ移動できるように修正。

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
