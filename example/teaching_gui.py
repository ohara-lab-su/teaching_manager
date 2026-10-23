"""P座標ティーチングGUIのティーチング・JSON保存版。

Qtによる表示とボタン操作を担当する。データ取得と保持はTeachingModelに委譲する。
実機への書き込みはユーザーが確認した指定番号に限定する。
"""

import asyncio
import inspect
import json
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QThread, Signal
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
    QMenu,
    QAbstractItemView,
    QHeaderView,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from teaching_manager.robot_var_manager import RobotVarManager
from teaching_manager.teaching_model import TeachingModel

from x_logger import XLogger

JSON_FILE = str(ROOT / "robot_positions.json")
FIRST_P = 0
LAST_P = 999


class _PositionWorker(QThread):
    """現在位置取得をGUIスレッド外で実行する読み取り専用ワーカー。"""

    succeeded = Signal()
    failed = Signal(str)

    def __init__(self, model: TeachingModel) -> None:
        super().__init__()
        self._model = model

    def run(self) -> None:
        """同期・非同期いずれのDeviceProxy呼び出しも画面を止めずに処理する。"""
        try:
            result = self._model.read_current_position()
            if inspect.isawaitable(result):
                asyncio.run(result)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.succeeded.emit()


class TeachingWindow(QMainWindow):
    """P変数の読み取り操作と表示を担当するQt画面（View）。

    データ取得はTeachingModelへ委譲する。実機への書き込みは行わない。
    """

    def __init__(self, model: TeachingModel) -> None:
        super().__init__()
        self._model = model
        self.setWindowTitle("P座標ティーチング")
        self.resize(920, 620)

        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)
        self._status = QLabel()

        layout.addWidget(self._status)
        row = QHBoxLayout()
        self._robot_button = QPushButton("ロボットから指定範囲のP変数を読み込む")
        self._robot_button.clicked.connect(lambda: self._execute_robot_read())

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
        self._position_button.clicked.connect(self._read_current_position)
        self._position_worker: _PositionWorker | None = None
        layout.addWidget(self._position_button)
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["P番号", "座標"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setContextMenuPolicy(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_table_menu)
        self._table.itemSelectionChanged.connect(self._sync_selected_number)
        layout.addWidget(self._table)
        row = QHBoxLayout()
        self._auto_button = QPushButton("空き番号にティーチング")
        self._auto_button.clicked.connect(self._teach_unused)

        row.addWidget(self._auto_button)
        self._save_button = QPushButton("現在の一覧をJSONファイルに保存")
        self._save_button.clicked.connect(self._save_file)
        row.addWidget(self._save_button)
        row.addWidget(QLabel("指定P番号"))
        self._number = QSpinBox()
        self._number.setRange(FIRST_P, LAST_P)

        row.addWidget(self._number)
        self._spec_button = QPushButton("指定番号にティーチング")
        self._spec_button.clicked.connect(self._teach_specified)
        self._selected_button = QPushButton("選択したP番号に書き込む")
        self._selected_button.clicked.connect(self._teach_selected)
        row.addWidget(self._selected_button)

        row.addWidget(self._spec_button)
        layout.addLayout(row)
        self._hint = QLabel(
            "実機への書き込みには確認が必要です。JSON保存は別操作です。"
        )
        layout.addWidget(self._hint)
        self._model.load_file()
        self.refresh()

    def _read_current_position(self) -> None:
        """現在位置取得を別スレッドで開始し、完了後に画面へ反映する。"""
        if self._position_worker is not None:
            return
        self._position_button.setEnabled(False)
        self._position_label.setText("現在位置: 取得中...")
        worker = _PositionWorker(self._model)
        self._position_worker = worker
        worker.succeeded.connect(self._position_read_succeeded)
        worker.failed.connect(self._position_read_failed)
        worker.finished.connect(self._position_read_finished)
        worker.start()

    def _position_read_succeeded(self) -> None:
        """取得した現在位置を表示する。"""
        self.refresh()

    def _position_read_failed(self, message: str) -> None:
        """取得エラーを表示する。"""
        self._position_label.setText("現在位置: 取得失敗")
        QMessageBox.critical(self, "現在位置取得失敗", message)

    def _position_read_finished(self) -> None:
        """取得終了後にボタンとワーカー参照を復旧する。"""
        self._position_button.setEnabled(self._model.robot is not None)
        if self._position_worker is not None:
            self._position_worker.deleteLater()
        self._position_worker = None

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
            self._position_label.setText(
                "現在位置: " + str(self._model.current_position)
            )
        self._hint.setText(
            "選択行への書き込みは確認後に実行。JSON保存は別操作です。"
        )

    def _selected_number(self) -> int:
        """選択行からP番号を取得する。"""
        row = self._table.currentRow()
        if row < 0:
            raise ValueError("一覧からP番号を選択してください")
        item = self._table.item(row, 0)
        if item is None:
            raise ValueError("P番号が取得できません")
        return int(item.text()[1:])

    def _sync_selected_number(self) -> None:
        """一覧で選んだP番号を指定番号欄にも反映する。"""
        try:
            self._number.setValue(self._selected_number())
        except ValueError:
            return

    def _show_table_menu(self, point: Any) -> None:
        """一覧の右クリックから、選択P番号への書き込みを選べるようにする。"""
        item = self._table.itemAt(point)
        if item is None:
            return
        self._table.selectRow(item.row())
        menu = QMenu(self)
        action = menu.addAction("選択したP番号に現在位置を書き込む")
        chosen = menu.exec(self._table.viewport().mapToGlobal(point))
        if chosen == action:
            self._teach_selected()

    def _teach_selected(self) -> None:
        """一覧で選択したP番号への書き込みを確認する。"""
        try:
            number = self._selected_number()
        except Exception as exc:
            QMessageBox.warning(self, "番号未選択", str(exc))
            return
        self._write_number(number)

    def _teach_specified(self) -> None:
        """番号入力欄のP番号への書き込みを確認する。"""
        self._write_number(self._number.value())

    def _write_number(self, number: int) -> None:
        """上書きの危険を明示し、承認された場合だけModelへ書き込みを依頼する。"""
        if self._model.current_position is None:
            QMessageBox.warning(self, "現在位置未取得", "先に現在位置を取得してください")
            return
        reply = QMessageBox.warning(
            self,
            "実機P変数の上書き確認",
            f"実機のP{number}を現在位置で上書きします。\n"
            "既存の座標は失われます。続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self._model.teach_number(number)
            self.refresh()
            QMessageBox.information(self, "書き込み完了", f"P{number}を書き込み、読み戻しました")
        except Exception as exc:
            QMessageBox.critical(self, "書き込み失敗", str(exc))

    def _teach_unused(self) -> None:
        """空き番号の自動判定は未確認のため、実機へは書き込まない。"""
        try:
            self._model.teach_first_unused(self._start_number.value(), self._end_number.value())
        except Exception as exc:
            QMessageBox.warning(self, "空き番号の判定不可", str(exc))

    def _save_file(self) -> None:
        """表示中のP変数をJSONへ保存する。ロボットには書き込まない。"""
        try:
            self._model.save_file()
            QMessageBox.information(
                self, "保存完了", f"JSONへ保存しました: {JSON_FILE}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "JSON保存失敗", str(exc))

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

    # httpx のログを WARNING レベル以上にする（INFO を抑制）
    import logging

    logging.getLogger("httpx").setLevel(logging.WARNING)

    ##################################################
    # 接続先の変更は、以下のimportとDeviceProxyの生成箇所のみで行う。
    from cobotta2 import Config
    from cobotta2.server_fastapi import DeviceProxy

    # 実機接続時は次の2行を有効化し、import元と制御クラス名を指定する。
    logger = XLogger(log_level="info")
    config = Config("config_cobotta3_server5.yaml")

    robot = DeviceProxy(
        "CobottaCtrl",
        config=config,
        logger=logger,
        async_mode=False,
    )
    # robot = None  # 未接続でGUIの読み取り表示を確認する場合
    ##################################################

    manager = RobotVarManager(
        robot_instance=robot,
        autosave=False,
        autoload=False,
        logger=logger,
    )
    model = TeachingModel(
        manager,
        JSON_FILE,
        logger=logger,
        async_mode=False,
    )

    window = TeachingWindow(model)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
