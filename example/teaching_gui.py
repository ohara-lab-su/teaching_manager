"""P座標ティーチングGUIの読み取りテスト版。

Qtによる表示とボタン操作を担当する。データ取得と保持はTeachingModelに委譲する。
ロボットおよびJSONへの書き込み操作は行わない。
"""

import json
import sys
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from teaching_manager.robot_var_manager import RobotVarManager
from teaching_manager.teaching_model import TeachingModel

from x_logger import XLogger

JSON_FILE = str(ROOT / "robot_positions.json")
FIRST_P = 0
LAST_P = 999


class TeachingWindow(QMainWindow):
    """P変数の読み取り操作と表示を担当するQt画面（View）。

    データ取得はTeachingModelへ委譲する。実機への書き込みは行わない。
    """

    def __init__(self, model: TeachingModel) -> None:
        super().__init__()
        self._model = model
        self.setWindowTitle("P座標ティーチング（読み取りテスト）")
        self.resize(920, 620)

        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)
        self._status = QLabel()

        layout.addWidget(self._status)
        row = QHBoxLayout()
        self._robot_button = QPushButton("ロボットから指定範囲のP変数を読み込む")
        self._robot_button.clicked.connect(
            lambda: self._execute_robot_read()
        )

        row.addWidget(self._robot_button)
        row.addWidget(QLabel("開始P番号"))
        self._start_number = QSpinBox()
        self._start_number.setRange(FIRST_P, LAST_P)
        self._start_number.setValue(0)
        row.addWidget(self._start_number)
        row.addWidget(QLabel("終了P番号"))
        self._end_number = QSpinBox()
        self._end_number.setRange(FIRST_P, LAST_P)
        self._end_number.setValue(20)
        row.addWidget(self._end_number)
        self._file_button = QPushButton("JSONファイルから読み込む")
        self._file_button.clicked.connect(lambda: self.execute(self._model.load_file))

        row.addWidget(self._file_button)
        layout.addLayout(row)
        self._position_label = QLabel("現在位置: 未取得")

        layout.addWidget(self._position_label)
        self._position_button = QPushButton("ロボットの現在P座標を取得")
        self._position_button.clicked.connect(
            lambda: self.execute(self._model.read_current_position)
        )
        layout.addWidget(self._position_button)
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["P番号", "座標（読み取り専用）"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self._table)
        row = QHBoxLayout()
        self._auto_button = QPushButton("空き番号にティーチング（テスト中：無効）")
        self._auto_button.setEnabled(False)

        row.addWidget(self._auto_button)
        row.addWidget(QLabel("指定P番号"))
        self._number = QSpinBox()
        self._number.setRange(FIRST_P, LAST_P)

        row.addWidget(self._number)
        self._spec_button = QPushButton("指定番号にティーチング（テスト中：無効）")
        self._spec_button.setEnabled(False)

        row.addWidget(self._spec_button)
        layout.addLayout(row)
        self._hint = QLabel(
            "書き込みは完全無効。ロボットからの読込ではJSONを変更しません。"
        )
        layout.addWidget(self._hint)
        self._model.load_file()
        self.refresh()

    def _execute_robot_read(self) -> None:
        """画面で指定した範囲のP変数をロボットから取得する。"""
        start = self._start_number.value()
        end = self._end_number.value()
        self.execute(lambda: self._model.read_robot(start, end))

    def refresh(self) -> None:
        """Modelの保持状態を画面に反映する。"""
        connected = self._model.robot is not None
        self._status.setText(
            f"表示元: {self._model.source} / 接続: {'あり' if connected else 'なし'} / P変数: {len(self._model.positions)}件"
        )
        self._robot_button.setEnabled(connected)
        self._position_button.setEnabled(connected)
        keys = sorted(self._model.positions, key=lambda key: int(key[1:]))
        self._table.setRowCount(len(keys))
        for row, key in enumerate(keys):
            self._table.setItem(row, 0, QTableWidgetItem(key))
            self._table.setItem(
                row,
                1,
                QTableWidgetItem(
                    json.dumps(self._model.positions[key], ensure_ascii=False)
                ),
            )
        if self._model.current_position is not None:
            self._position_label.setText("現在位置: " + str(self._model.current_position))
        self._hint.setText("読み取りテスト版：書き込み無効。空き番号は判定しません。")

    def execute(self, action: Any) -> None:
        """読み取り操作を実行し、成功時に画面を更新する。"""
        try:
            action()
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "読み取り失敗", str(exc))


def main() -> None:
    """QtアプリケーションとModelを生成し、GUIを起動する。"""
    app = QApplication(sys.argv)

    ##################################################
    # 接続先の変更は、以下のimportとDeviceProxyの生成箇所のみで行う。
    from cobotta2 import Config
    from cobotta2.server_fastapi import DeviceProxy

    # 実機接続時は次の2行を有効化し、import元と制御クラス名を指定する。
    logger = XLogger(log_level="info")
    config = Config("config_cobotta3_server5.yaml")
    robot = DeviceProxy("CobottaCtrl", config=config, logger=logger)
    # robot = None  # 未接続でGUIの読み取り表示を確認する場合
    ##################################################

    manager = RobotVarManager(
        robot_instance=robot,
        autosave=False,
        autoload=False,
        logger=logger,
    )
    model = TeachingModel(manager, JSON_FILE)

    window = TeachingWindow(model)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
