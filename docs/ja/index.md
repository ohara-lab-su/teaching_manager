# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/teaching_manager/)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/teaching_manager/ja/)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/ja/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

Teaching Manager は、ロボットの座標をティーチングし、番号付きの位置変数（P変数）として管理するためのGUIソフトウェアです。主な目的は、
**ロボットコントローラ内部の変数メモリに依存せず、ロボットの座標を外部で管理すること**
です。座標データをローカルで保持し、JSONファイルに保存することで、ロボット内部のP変数領域とは独立して運用できます。

接続したロボットから現在位置を取得し、指定したP番号に対応付けて座標一覧を管理します。`RobotVarManager`
により、Pythonからの変数キャッシュ操作、JSONの読み書き、ロボットとの明示的な変数転送にも対応しています。

## 座標の保存方式

実装では、デバイス名に応じて次の2方式を切り替えます。

- **`CobottaCtrl` 以外のデバイス：** ロボット内部のP変数メモリを使わず、JSONで座標を管理します。ティーチング、クリア、削除はJSONに反映されます。
- **`CobottaCtrl`：** ロボット内部のP変数を使用します。指定番号へのティーチングやクリアでは実機へ書き込み、読み戻して結果を確認します。JSONへの保存は別操作です。

したがって、外部での座標管理が中心的な用途ですが、既存実装には `CobottaCtrl` 用の実機P変数管理機能も残されています。

## 主な機能

- ロボットの現在位置を取得し、指定したP番号へ登録
- Qt GUIによる座標一覧の表示と編集操作
- JSONファイルによる座標データの読み込み・保存
- 保存方式に応じたP変数のクリアと削除
- `RobotVarManager` を使ったPythonからの変数管理

## 使用上の注意

指定番号へのティーチングは既存の座標を上書きする場合があります。未使用P番号の自動判定条件は確定していないため、「空き番号にティーチング」は無効化されています。現在位置を取得するだけでは、ロボット内部メモリにもJSONにも書き込みません。

```{toctree}
:maxdepth: 2
:caption: 目次

overview
quickstart
gui
python_api
storage
api
```
