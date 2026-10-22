#!/usr/bin/env python
"""P座標専用ティーチングGUI。実機の現在位置取得は呼び出し側で注入する。"""

import json
from pathlib import Path
from typing import Any, Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from teaching_manager.robot_var_manager import RobotVarManager

JSON_FILENAME = "robot_positions.json"
MIN_P_NUMBER = 0
MAX_P_NUMBER = 999


class TeachingService:
    """空き番号のみ登録。robot は P番号属性の読み書きができる場合に接続する。"""

    def __init__(
        self,
        manager: RobotVarManager,
        get_current_pose: Callable[[], Any],
        robot: Optional[Any] = None,
    ) -> None:
        self.manager = manager
        self.get_current_pose = get_current_pose
        self.robot = robot
        self._validate_loaded()

    def _validate_loaded(self) -> None:
        for key in self.manager.list_vars():
            if key.startswith("P"):
                number = key[1:]
                if not number.isdecimal():
                    raise ValueError(f"不正なP変数名: {key}")

    def used_numbers(self) -> set[int]:
        return {
            int(k[1:])
            for k in self.manager.list_vars()
            if k.startswith("P") and k[1:].isdecimal()
        }

    def first_free(self) -> int:
        used = self.used_numbers()
        for number in range(MIN_P_NUMBER, MAX_P_NUMBER + 1):
            if number not in used:
                return number
        raise RuntimeError("空きP番号がありません")

    def teach(self, number: int) -> str:
        if not MIN_P_NUMBER <= number <= MAX_P_NUMBER:
            raise ValueError("番号が許容範囲外です")
        key = f"P{number}"
        if number in self.used_numbers():
            raise ValueError(f"{key} は登録済みです。上書きしません")
        pose = self.get_current_pose()
        json.dumps(pose)  # JSONシリアライズ可能であることを先に確認
        if not isinstance(pose, (list, tuple)):
            raise ValueError("現在位置はP座標の配列で返してください")
        pose = list(pose)
        if not pose:
            raise ValueError("空のP座標は登録できません")
        # 実機側の既存変数は消去済みとみなせない。既存値との一致は保証できないため拒否。
        if self.robot is not None:
            old = getattr(self.robot, key)
            if old is not None and old is not False:
                raise RuntimeError(f"実機の {key} に値があります。上書き防止のため中止")
            setattr(self.robot, key, pose)
            confirmed = getattr(self.robot, key)
            if confirmed != pose:
                raise RuntimeError(
                    f"実機の {key} の書込検証に失敗しました。JSONには保存していません"
                )
        self.manager.set_var("P", number, pose, save=True)
        return key


class TeachingWindow(QMainWindow):
    def __init__(self, service: TeachingService) -> None:
        super().__init__()
        self.service = service
        self.setWindowTitle("P座標ティーチング")
        self.resize(700, 500)
        root = QWidget()
        layout = QVBoxLayout(root)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["番号", "P座標 (JSON)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        controls = QHBoxLayout()
        self.auto_button = QPushButton("空き番号へティーチング")
        self.auto_button.clicked.connect(self.teach_auto)
        controls.addWidget(self.auto_button)
        controls.addWidget(QLabel("指定番号:"))
        self.number = QSpinBox()
        self.number.setRange(MIN_P_NUMBER, MAX_P_NUMBER)
        controls.addWidget(self.number)
        self.specific_button = QPushButton("指定番号へティーチング")
        self.specific_button.clicked.connect(self.teach_specific)
        controls.addWidget(self.specific_button)
        layout.addLayout(controls)
        self.status = QLabel()
        layout.addWidget(self.status)
        self.setCentralWidget(root)
        self.refresh()

    def refresh(self) -> None:
        entries = [
            (k, self.service.manager.get_var(k))
            for k in self.service.manager.list_vars()
            if k.startswith("P")
        ]
        entries.sort(key=lambda entry: int(entry[0][1:]))
        self.table.setRowCount(len(entries))
        for row, (key, value) in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(
                row, 1, QTableWidgetItem(json.dumps(value, ensure_ascii=False))
            )
        try:
            self.status.setText(f"次の空き番号: P{self.service.first_free()}")
        except RuntimeError:
            self.status.setText("空き番号なし")

    def teach_auto(self) -> None:
        try:
            self._teach(self.service.first_free())
        except Exception as exc:
            QMessageBox.critical(self, "ティーチング失敗", str(exc))

    def teach_specific(self) -> None:
        self._teach(self.number.value())

    def _teach(self, number: int) -> None:
        try:
            key = self.service.teach(number)
            self.refresh()
            self.status.setText(f"保存しました: {key}")
            QMessageBox.information(self, "登録完了", f"{key} に現在位置を登録しました")
        except Exception as exc:
            QMessageBox.critical(self, "ティーチング失敗", str(exc))


def run_gui(
    get_current_pose: Callable[[], Any],
    robot: Optional[Any] = None,
    filename: str = JSON_FILENAME,
) -> int:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    manager = RobotVarManager(filename=filename, autoload=True, autosave=False)
    service = TeachingService(manager, get_current_pose, robot)
    window = TeachingWindow(service)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(
        "実機の現在P座標取得関数を指定して run_gui(get_current_pose, robot) を呼び出してください"
    )
