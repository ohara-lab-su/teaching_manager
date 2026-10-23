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
    """P変数の一覧と現在位置を表示するQt画面（View）。"""

    def __init__(self, model: TeachingModel) -> None:
        super().__init__()
        self.model = model
        self.setWindowTitle("P座標ティーチング（読み取りテスト）")
        self.resize(920, 620)

        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)
        self.status = QLabel()

        layout.addWidget(self.status)
        row = QHBoxLayout()
        self.robot_button = QPushButton("ロボットから全P変数を読み込む")
        self.robot_button.clicked.connect(lambda: self.execute(self.model.read_robot))

        row.addWidget(self.robot_button)
        self.file_button = QPushButton("JSONファイルから読み込む")
        self.file_button.clicked.connect(lambda: self.execute(self.model.load_file))

        row.addWidget(self.file_button)
        layout.addLayout(row)
        self.position_label = QLabel("現在位置: 未取得")

        layout.addWidget(self.position_label)
        self.position_button = QPushButton("ロボットの現在P座標を取得")
        self.position_button.clicked.connect(
            lambda: self.execute(self.model.read_current_position)
        )
        layout.addWidget(self.position_button)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["P番号", "座標（読み取り専用）"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)
        row = QHBoxLayout()
        self.auto_button = QPushButton("空き番号にティーチング（テスト中：無効）")
        self.auto_button.setEnabled(False)

        row.addWidget(self.auto_button)
        row.addWidget(QLabel("指定P番号"))
        self.number = QSpinBox()
        self.number.setRange(FIRST_P, LAST_P)

        row.addWidget(self.number)
        self.spec_button = QPushButton("指定番号にティーチング（テスト中：無効）")
        self.spec_button.setEnabled(False)

        row.addWidget(self.spec_button)
        layout.addLayout(row)
        self.hint = QLabel(
            "書き込みは完全無効。ロボットからの読込ではJSONを変更しません。"
        )
        layout.addWidget(self.hint)
        self.model.load_file()
        self.refresh()

    def refresh(self) -> None:
        """Modelの保持状態を画面に反映する。"""
        connected = self.model.robot is not None
        self.status.setText(
            f"表示元: {self.model.source} / 接続: {'あり' if connected else 'なし'} / P変数: {len(self.model.positions)}件"
        )
        self.robot_button.setEnabled(connected)
        self.position_button.setEnabled(connected)
        keys = sorted(self.model.positions, key=lambda key: int(key[1:]))
        self.table.setRowCount(len(keys))
        for row, key in enumerate(keys):
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    json.dumps(self.model.positions[key], ensure_ascii=False)
                ),
            )
        if self.model.current_position is not None:
            self.position_label.setText("現在位置: " + str(self.model.current_position))
        available = self.model.first_unused(FIRST_P, LAST_P)
        if available is not None:
            self.hint.setText(
                f"取得結果のキーに存在しない最初の番号: P{available}（未使用確定ではありません） / 書込無効"
            )

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
