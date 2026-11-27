# Teaching Manager

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/teaching_manager/en/)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/teaching_manager/ja/)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fteaching_manager-181717?logo=github)](https://github.com/ohara-lab-su/teaching_manager/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/teaching_manager/ja/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

**Version 0.1.4**

デバイスごとの起動例が同期 DeviceProxy を渡し、共通 GUI が現在位置の取得と教示を行います。Python から JSON を扱う場合は `RobotVarManager` を単独で利用できます。

## 座標の保存方式

Teaching Manager は、起動例が作った DeviceProxy を受け取り、共通の GUI で現在位置の取得、P 番号への教示、JSON の読み込み・書き出しを行います。

- **COBOTTA** は装置側の P 変数と GUI 側の JSON の両方を扱います。教示・0クリアは指定した P 点を装置側に書き込み、読み戻します。終了時に「保存」を選ぶと、一覧中の変更点を装置側に同期してから、一覧を既定の JSON に保存します。手動で JSON を書き出すこともできます。
- **UR の同梱例**は、DeviceProxy で現在位置を取得し、教示点を GUI 側の `JSON_FILE` に保存します。UR 制御側の `ROBOT_VAR_FILE` は別の保存先です。GUI 側の教示で UR 制御側の P 点は更新されません。

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
