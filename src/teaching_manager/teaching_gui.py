"""P座標ティーチングGUIのティーチング・JSON保存版。

Qtによる表示とボタン操作を担当する。データ取得と保持はControllerに委譲する。
実機への書き込みはユーザーが確認した指定番号に限定する。
"""

import asyncio
import inspect
import json
from typing import Any

from PySide6.QtCore import QThread, Signal, QTimer, Qt
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
    QFileDialog,
)

from .teaching_controller import TeachingController

FIRST_P = 0
LAST_P = 999


class _OperationWorker(QThread):
    """Controller操作をGUIスレッド外で順次実行する共通ワーカー。"""

    succeeded = Signal(object)
    failed = Signal(str, object)

    def __init__(self, action: Any) -> None:
        super().__init__()
        self._action = action

    def run(self) -> None:
        """操作を実行する。部分完了情報は例外に含めず、呼び出し側で保持する。"""
        try:
            result = self._action()
            if inspect.isawaitable(result):
                result = asyncio.run(result)
        except Exception as exc:
            self.failed.emit(str(exc), exc)
            return
        self.succeeded.emit(result)


class TeachingWindow(QMainWindow):
    """P変数の読み取り操作と表示を担当するQt画面（View）。

    データ取得と操作はControllerへ委譲する。実機への直接書き込みは行わない。
    """

    def __init__(self, controller: TeachingController, json_file: str) -> None:
        super().__init__()
        self._controller = controller
        self._json_file = json_file
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
        self._robot_button.setEnabled(controller.uses_robot_memory)

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
        self._file_button.clicked.connect(self._open_json_file)

        row.addWidget(self._file_button)
        layout.addLayout(row)
        self._position_label = QLabel("現在位置: 未取得")

        layout.addWidget(self._position_label)
        self._position_button = QPushButton("ロボットの現在P座標を取得")
        self._position_button.clicked.connect(self._read_current_position)
        self._worker: _OperationWorker | None = None
        self._closing = False
        self._close_approved = False
        self._busy = False
        layout.addWidget(self._position_button)
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["P番号", "座標"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_table_menu)
        self._table.itemSelectionChanged.connect(self._sync_selected_number)
        layout.addWidget(self._table)
        row = QHBoxLayout()
        self._auto_button = QPushButton("空き番号にティーチング")
        self._auto_button.clicked.connect(self._teach_unused)
        self._auto_button.setEnabled(False)
        self._auto_button.setToolTip("未使用P番号の判定仕様が未確定のため無効です")

        row.addWidget(self._auto_button)
        self._save_button = QPushButton("現在の一覧をJSONファイルに保存")
        self._save_button.clicked.connect(self._save_file)
        row.addWidget(self._save_button)
        row.addWidget(QLabel("指定P番号"))
        self._number = QSpinBox()
        self._number.setRange(FIRST_P, LAST_P)

        row.addWidget(self._number)
        self._spec_button = QPushButton("指定P番号に現在位置を書き込む")
        self._spec_button.clicked.connect(self._teach_specified)
        self._selected_button = QPushButton("選択したP番号に現在位置を書き込む")
        self._selected_button.clicked.connect(self._teach_selected)
        row.addWidget(self._selected_button)

        row.addWidget(self._spec_button)
        layout.addLayout(row)
        self._hint = QLabel(
            "Cobotta: 実機P変数を更新（JSON保存は手動）。その他: P変数はJSONに自動保存。"
        )
        layout.addWidget(self._hint)
        self.refresh()
        # Qtのイベントループ開始後に初期読込を行う。
        QTimer.singleShot(0, self._load_initial_data)

    def _open_json_file(self) -> None:
        """ファイル選択ダイアログでJSONを選び、Controllerへ読み込みを依頼する。

        ダイアログの初期パスにはModelで指定されたデフォルトJSONを使う。
        キャンセルした場合は表示中の一覧を変更しない。
        """
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "P変数のJSONファイルを開く",
            self._json_file,
            "JSONファイル (*.json);;すべてのファイル (*)",
        )
        if not filename:
            return
        self._run_operation(
            lambda: self._controller.load_file(filename),
            "JSON読込",
        )

    def _load_initial_data(self) -> None:
        """デバイス名に基づきCobottaは実機、それ以外はJSONを読み込む。"""
        start = self._start_number.value()
        end = self._end_number.value()
        self._run_operation(lambda: self._controller.load_initial(start, end), "初期読込")

    def closeEvent(self, event: Any) -> None:
        """未保存の変更がある場合に、同期・保存するか確認する。"""
        if self._worker is not None:
            self._closing = True
            self._status.setText("処理終了後に終了確認を行います...")
            event.ignore()
            return
        if self._close_approved:
            event.accept()
            return
        if not self._controller.has_unsaved_changes:
            if not self._controller.has_robot_changes:
                event.accept()
                return
        message = (
            "一覧の変更が保存されていません。\n"
            "保存しないで終了すると、未保存の内容は失われます。\n\n"
            "Yes: デフォルトJSONへ保存して終了\n"
            "No: 保存せず終了"
        )
        if self._controller.uses_robot_memory:
            message = (
                "一覧の内容をCobotta内部P変数とJSONに同期しますか？\n"
                "Yes: 変更されたP変数を実機へ書き込み、JSONへ保存して終了\n"
                "No: 同期・保存せず終了（未保存の内容は失われます）\n\n"
                "※一覧から削除した番号は実機から削除されません。"
            )
        reply = QMessageBox.question(
            self,
            "終了時の保存確認",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        if reply == QMessageBox.StandardButton.No:
            event.accept()
            return
        event.ignore()
        self._run_operation(
            self._controller.save_on_close,
            "終了時の同期・保存",
            on_success=self._close_after_save,
        )

    def _close_after_save(self, result: Any) -> None:
        """保存が成功した場合だけ終了する。"""
        self._close_approved = True
        self._closing = True

    def _run_operation(
        self,
        action: Any,
        title: str = "操作",
        on_success: Any = None,
        on_failure: Any = None,
    ) -> None:
        """一度に1件だけController操作をワーカーで実行する。"""
        if self._worker is not None:
            QMessageBox.warning(self, "処理中", "前の操作が終了するまでお待ちください")
            return
        self._busy = True
        self._set_busy(True)
        self._status.setText(f"{title}: 処理中...")
        worker = _OperationWorker(action)
        self._worker = worker

        def succeeded(result: Any) -> None:
            self.refresh()
            if not self._closing:
                if on_success is not None:
                    on_success(result)

        def failed(message: str, error: Any) -> None:
            self.refresh()
            if self._closing:
                return
            if on_failure is not None:
                on_failure(message, error)
            else:
                QMessageBox.critical(self, f"{title}失敗", message)

        worker.succeeded.connect(succeeded)
        worker.failed.connect(failed)
        worker.finished.connect(self._operation_finished)
        worker.start()

    def _operation_finished(self) -> None:
        """ワーカーを破棄し、閉じる要求があれば終了する。"""
        worker = self._worker
        self._worker = None
        self._busy = False
        if worker is not None:
            worker.deleteLater()
        self._set_busy(False)
        if self._closing:
            self._closing = False
            self.close()

    def _set_busy(self, busy: bool) -> None:
        """通信中の二重操作を防ぐ。"""
        for button in (
            self._robot_button, self._file_button, self._position_button,
            self._save_button, self._spec_button, self._selected_button,
        ):
            button.setEnabled(not busy)
        self._table.setEnabled(not busy)
        if not busy:
            self.refresh()

    def _read_current_position(self) -> None:
        """現在位置取得をワーカーで実行する。"""
        self._position_label.setText("現在位置: 取得中...")
        self._run_operation(
            self._controller.read_current_position,
            "現在位置取得",
            on_failure=lambda message, error: self._position_error(message),
        )

    def _position_error(self, message: str) -> None:
        """現在位置取得の失敗を表示する。"""
        self._position_label.setText("現在位置: 取得失敗")
        QMessageBox.critical(self, "現在位置取得失敗", message)

    def _execute_robot_read(self) -> None:
        """指定範囲のP変数をワーカーで取得する。"""
        start = self._start_number.value()
        end = self._end_number.value()
        self._run_operation(lambda: self._controller.read_robot(start, end), "P変数読込")

    def refresh(self) -> None:
        """Modelの保持状態を画面に反映する。"""
        model = self._controller.model
        positions = model.positions
        connected = model.robot is not None
        storage = "JSON"
        if self._controller.uses_robot_memory:
            storage = "実機P変数"
        connection = "なし"
        if connected:
            connection = "あり"
        self._status.setText(
            f"デバイス: {self._controller.device_name} / P変数管理: {storage} / "
            f"表示元: {model.source} / 接続: {connection} / "
            f"P変数: {len(positions)}件"
        )
        can_read_robot = connected
        if not self._controller.uses_robot_memory:
            can_read_robot = False
        if self._busy:
            can_read_robot = False
        self._robot_button.setEnabled(can_read_robot)
        can_read_position = connected
        if self._busy:
            can_read_position = False
        self._position_button.setEnabled(can_read_position)
        can_write_selected = len(self._table.selectionModel().selectedRows()) == 1
        if self._busy:
            can_write_selected = False
        self._selected_button.setEnabled(can_write_selected)
        keys = sorted(positions, key=lambda key: int(key[1:]))
        self._table.setRowCount(len(keys))
        for row, key in enumerate(keys):
            self._table.setItem(row, 0, QTableWidgetItem(key))
            self._table.setItem(row, 1, QTableWidgetItem(json.dumps(positions[key], ensure_ascii=False)))
        if model.current_position is not None:
            self._position_label.setText("現在位置: " + str(model.current_position))
        self._hint.setText(
            "Cobottaは実機P変数へ書き込み（JSON保存は手動）。"
            "その他はJSONへ自動保存。現在位置の書き込みは単一選択のみ。"
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
            pass
        can_write_selected = len(self._table.selectionModel().selectedRows()) == 1
        if self._busy:
            can_write_selected = False
        self._selected_button.setEnabled(can_write_selected)

    def _show_table_menu(self, point: Any) -> None:
        """右クリック時に複数選択を保持して、書き込み・削除メニューを表示する。"""
        item = self._table.itemAt(point)
        if item is None:
            return
        # 既存の複数選択を維持する。選択外の行を右クリックした場合だけ、その行を選択する。
        if not self._table.selectionModel().isRowSelected(
            item.row(), self._table.rootIndex()
        ):
            self._table.clearSelection()
            self._table.selectRow(item.row())
        menu = QMenu(self)
        action = menu.addAction("選択したP番号に現在位置を書き込む")
        action.setEnabled(len(self._selected_numbers()) == 1)
        delete_action = menu.addAction("選択したP番号を0クリア（未使用値を書き込む）")
        remove_action = menu.addAction("選択したP番号を一覧から削除")
        chosen = menu.exec(self._table.viewport().mapToGlobal(point))
        if chosen == action:
            self._teach_selected()
        if chosen == delete_action:
            self._clear_selected()
        if chosen == remove_action:
            self._delete_selected()

    def _clear_selected(self) -> None:
        """選択した複数のP番号を確認後に未使用値へ変更する。

        Ctrl/Commandによる複数選択を受け付け、確認は一度だけ行う。
        各番号の書き込みと読み戻しは既存のModelに委譲する。
        途中で失敗した場合は処理を中止し、成功済みの結果を画面へ反映する。
        CobottaではJSONを変更せず、その他のロボットではJSONに自動保存する。
        """
        try:
            numbers = self._selected_numbers()
        except ValueError as exc:
            QMessageBox.warning(self, "番号未選択", str(exc))
            return
        targets = ", ".join(f"P{number}" for number in numbers)
        reply = QMessageBox.warning(
            self,
            "P変数の0クリア確認",
            f"次の{len(numbers)}件を [0, 0, 0, 0, 0, 0, -1] に変更します。\n"
            f"{targets}\n元の座標は失われます。続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        def clear_all() -> list[int]:
            """順次クリアし、失敗時は成功済み番号を例外に付加する。"""
            completed: list[int] = []
            for number in numbers:
                try:
                    self._controller.clear_number(number)
                except Exception as exc:
                    completed_text = ", ".join(f"P{item}" for item in completed)
                    if not completed_text:
                        completed_text = "なし"
                    raise RuntimeError(
                        f"P{number}で失敗: {exc}。処理済み: {completed_text}"
                    ) from exc
                completed.append(number)
            return completed

        self._run_operation(
            clear_all,
            "0クリア",
            on_success=lambda completed: QMessageBox.information(
                self, "クリア完了", f"{len(completed)}件を未使用値に変更しました"
            ),
        )

    def _selected_numbers(self) -> list[int]:
        """選択行のP番号を取得する。複数選択を維持する。"""
        rows = sorted(
            index.row() for index in self._table.selectionModel().selectedRows()
        )
        if not rows:
            raise ValueError("一覧からP番号を選択してください")
        numbers: list[int] = []
        for row in rows:
            item = self._table.item(row, 0)
            if item is None:
                raise ValueError("選択行のP番号が取得できません")
            numbers.append(int(item.text()[1:]))
        return numbers

    def _delete_selected(self) -> None:
        """選択行を削除する。Cobottaでは一覧のみ、その他はJSONも更新する。"""
        try:
            numbers = self._selected_numbers()
        except ValueError as exc:
            QMessageBox.warning(self, "番号未選択", str(exc))
            return
        targets = ", ".join(f"P{number}" for number in numbers)
        delete_message = "JSONファイルからも削除します。"
        if self._controller.uses_robot_memory:
            delete_message = "実機のP変数とJSONファイルは変更しません。"
        reply = QMessageBox.question(
            self,
            "一覧から削除",
            f"次の{len(numbers)}件を表示一覧から削除します。\n{targets}\n"
            + delete_message
            + "続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._run_operation(lambda: self._controller.delete_numbers(numbers), "一覧削除")

    def _teach_selected(self) -> None:
        """一覧で選択したP番号への書き込みを確認する。"""
        try:
            numbers = self._selected_numbers()
            if len(numbers) != 1:
                raise ValueError("現在位置の書き込みは1件だけ選択してください")
            number = numbers[0]
        except ValueError as exc:
            QMessageBox.warning(self, "番号未選択", str(exc))
            return
        self._write_number(number)

    def _teach_specified(self) -> None:
        """番号入力欄のP番号への書き込みを確認する。"""
        self._write_number(self._number.value())

    def _write_number(self, number: int) -> None:
        """上書きの危険を明示し、承認された場合だけModelへ書き込みを依頼する。"""
        if self._controller.model.current_position is None:
            QMessageBox.warning(
                self, "現在位置未取得", "先に現在位置を取得してください"
            )
            return
        reply = QMessageBox.warning(
            self,
            "P変数の上書き確認",
            f"P{number}を現在位置で上書きします。\n"
            "既存の座標は失われます。続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._run_operation(
            lambda: self._controller.teach_number(number),
            "P変数書込",
            on_success=lambda result: QMessageBox.information(
                self, "書き込み完了", f"P{number}に現在位置を書き込みました"
            ),
        )

    def _teach_unused(self) -> None:
        """空き番号の自動判定は未確認のため、実機へは書き込まない。"""
        try:
            self._controller.teach_first_unused(
                self._start_number.value(), self._end_number.value()
            )
        except Exception as exc:
            QMessageBox.warning(self, "空き番号の判定不可", str(exc))

    def _save_file(self) -> None:
        """保存先を選択し、表示中のP変数をJSONへ書き出す。"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "P変数のJSONファイルを保存",
            self._json_file,
            "JSONファイル (*.json);;すべてのファイル (*)",
        )
        if not filename:
            return
        self._run_operation(
            lambda: self._controller.save_file(filename),
            "JSON保存",
            on_success=lambda result: QMessageBox.information(
                self, "保存完了", f"JSONへ保存しました: {filename}"
            ),
        )

