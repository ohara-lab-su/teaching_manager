"""ティーチングGUIのModel。

責務:
    DeviceProxyの共通APIで指定範囲のP変数をロボットから取得し、
    JSONから読み込んだP変数と現在位置を画面表示用に保持する。

責務外:
    Qt画面の構築、DeviceProxyの生成、ロボット固有APIの変換、
    Qt画面の構築とユーザーへの確認ダイアログ。

安全上の制約:
    実機への書き込みは指定番号の明示操作に限る。
    P変数の値から未使用かどうかを推測しない。
"""

import asyncio
import copy
import inspect
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from .robot_var_manager import RobotVarManager


class TeachingModel:
    """ロボットとJSONから読み取ったP変数の表示状態を管理する。"""

    def __init__(
        self,
        manager: RobotVarManager,
        filename: str,
        logger: Any = None,
        async_mode: bool = False,
    ) -> None:
        """既存の変数マネージャーとJSONファイルの場所を設定する。"""
        self._manager = manager
        self._filename = Path(filename)
        self._logger = logger
        self._async_mode = async_mode
        self._source = "未読込"
        self._positions: Dict[str, Any] = {}
        self._current_position: Any = None
        self._uses_robot_memory = True
        self._saved_positions: Dict[str, Any] = {}
        self._robot_positions: Dict[str, Any] = {}

    @property
    def has_unsaved_changes(self) -> bool:
        """表示内容が最後に保存したJSON相当の状態と異なるかを返す。"""
        return self._positions != self._saved_positions

    @property
    def has_robot_changes(self) -> bool:
        """Cobotta内部値と表示中のP変数に差があるかを返す。"""
        if not self._uses_robot_memory:
            return False
        for key, value in self._positions.items():
            if key not in self._robot_positions:
                return True
            if self._robot_positions[key] != value:
                return True
        return False

    def sync_robot(self) -> None:
        """表示中の変更されたP変数のみをCobottaに書き込み、読み戻す。

        一覧から削除した番号は対象外とし、実機の値を削除しない。
        """
        if not self._uses_robot_memory:
            return
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        for key, value in self._positions.items():
            if key in self._robot_positions:
                if self._robot_positions[key] == value:
                    continue
            number = int(key[1:])
            result = self.robot.set_var("P", number, value)
            if inspect.isawaitable(result):
                raise RuntimeError("書き込みには同期DeviceProxyが必要です")
            if result is False:
                raise RuntimeError(f"{key}への書き込みに失敗しました")
            readback = self.robot.get_var("P", number)
            if inspect.isawaitable(readback):
                raise RuntimeError("読み戻しには同期DeviceProxyが必要です")
            if readback is False or readback is None:
                raise RuntimeError(f"{key}の読み戻しに失敗しました")
            self._robot_positions[key] = copy.deepcopy(readback)
            self._positions[key] = readback
            self._manager.set_var(key, readback, save=False)

    def save_on_close(self) -> None:
        """終了時にCobottaへの同期後、デフォルトJSONへ保存する。"""
        self.sync_robot()
        self.save_file(allow_empty=True)

    def set_storage_mode(self, uses_robot_memory: bool) -> None:
        """P変数の保存先を設定する。Controllerがデバイス名から決定する。

        Args:
            uses_robot_memory: Trueなら実機P変数、FalseならJSONファイル。
        """
        self._uses_robot_memory = uses_robot_memory

    @property
    def robot(self) -> Any:
        """マネージャーに接続済みのロボットインスタンスを返す。"""
        return self._manager.robot_instance

    @property
    def source(self) -> str:
        """現在表示しているP変数の取得元を返す。"""
        return self._source

    @property
    def positions(self) -> Dict[str, Any]:
        """表示用のP変数一覧のコピーを返す。"""
        return self._positions.copy()

    @property
    def current_position(self) -> Any:
        """最後に読み取ったロボットの現在位置を返す。"""
        return self._current_position

    @staticmethod
    def _only_p(data: Dict[str, Any]) -> Dict[str, Any]:
        """Pに続いて数字がある変数名だけを抽出する。"""
        return {
            key: value
            for key, value in data.items()
            if isinstance(key, str) and key.startswith("P") and key[1:].isdigit()
        }

    @property
    def json_filename(self) -> str:
        """起動時に指定されたデフォルトJSONファイルのパスを返す。"""
        return str(self._filename)

    def load_file(self, filename: str | None = None) -> None:
        """JSONを読み取って表示状態を更新する。ロボットへは書き込まない。

        Args:
            filename: 読み込むJSONファイル。省略時はデフォルトファイル。
                任意ファイルを選んでも保存先のデフォルト設定は変更しない。
        """
        path = self._filename
        if filename is not None:
            path = Path(filename)
        if not path.exists():
            if filename is not None:
                raise FileNotFoundError(f"JSONファイルが見つかりません: {path}")
            self._positions = {}
            self._saved_positions = {}
            self._source = "JSON（ファイルなし）"
            return
        with path.open(encoding="utf-8") as stream:
            data = json.load(stream)
        if not isinstance(data, dict):
            raise ValueError("JSONのルートは辞書である必要があります")
        self._positions = self._only_p(data)
        self._saved_positions = copy.deepcopy(self._positions)
        self._source = "JSON"

    def read_robot(self, start: int, end: int) -> None:
        """指定したP番号範囲を実機から読み取る。

        DeviceProxyの共通API get_var("P", 番号) を利用する。
        get_all_var()は変数名一覧を返すため使用しない。
        読み取った値はRobotVarManagerのローカルキャッシュにも反映する。
        読み取った結果は表示に反映するが、JSONには保存しない。

        Args:
            start: 読み取り開始P番号（両端を含む）。
            end: 読み取り終了P番号（両端を含む）。

        Raises:
            RuntimeError: ロボット未接続の場合。
            ValueError: 番号範囲が不正な場合。
            Exception: 実機からの読み取りに失敗した場合、その例外を伝播する。
        """
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        if start < 0 or end < start:
            raise ValueError("P番号の範囲が不正です")

        # DeviceProxyではP0等の動的属性アクセスではなく、共通APIの
        # get_var("P", 番号) を使う。既存の通信ログでもこのAPIの成功を確認済み。
        # 全件の取得に成功するまでは表示状態・マネージャーを更新しない。
        result: Dict[str, Any] = {}
        for number in range(start, end + 1):
            value = self.robot.get_var("P", number)
            if inspect.isawaitable(value):
                raise RuntimeError(
                    "P変数の読み取りには同期DeviceProxyが必要です。"
                    "DeviceProxyをasync_mode=Falseで生成してください。"
                )
            result[f"P{number}"] = value

        for key, value in result.items():
            self._manager.set_var(key, value, save=False)
        self._positions = result
        self._robot_positions = copy.deepcopy(result)
        self._saved_positions = copy.deepcopy(result)
        self._source = f"ロボット（P{start}～P{end}）"

    @property
    def async_mode(self) -> bool:
        """現在位置取得APIを非同期で公開する設定を返す。"""
        return self._async_mode

    async def _read_current_position_async(self) -> Any:
        """現在位置を取得して保持する。同期・非同期のDeviceProxyを受け付ける。"""
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        result = self.robot.get_current_position()
        if inspect.isawaitable(result):
            result = await result
        if result is False or result is None:
            raise RuntimeError("現在位置の取得に失敗しました")
        self._current_position = result
        return result

    def read_current_position(self) -> Any:
        """現在位置を取得する。

        async_mode=False: 同期実行し、座標を返す。
        async_mode=True: コルーチンを返す。呼び出し側でawaitする。

        ロボット内部変数およびJSONへの書き込みは行わない。
        """
        operation = self._read_current_position_async()
        if self._async_mode:
            return operation
        return asyncio.run(operation)

    def first_unused(self, start: int, end: int) -> Optional[int]:
        """未使用判定の仕様が未確定のため、常にNoneを返す。

        取得できなかった番号や値だけを根拠に空き番号を判定しない。
        """
        return None

    def save_file(
        self,
        allow_empty: bool = False,
        data: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
    ) -> None:
        """現在画面に表示しているP変数をJSONへ保存する。

        ロボットには書き込まない。読み取り結果がない場合は既存ファイルを
        空のデータで上書きしない。保存成功後にだけ表示元を更新する。
        """
        values = self._positions if data is None else data
        if not values and not allow_empty:
            raise ValueError(
                "保存対象のP変数がありません。先にロボットから読み込んでください"
            )
        path = self._filename
        if filename is not None:
            path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        # JSONへ書く内容は表示中のP変数だけ。マネージャーの他種変数は含めない。

        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_name = stream.name
                json.dump(values, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, path)
            self._saved_positions = copy.deepcopy(values)
        finally:
            if temporary_name is not None and os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def teach_number(
        self,
        number: int,
    ) -> Any:
        """現在位置を指定P番号へ書き込み、実機から読み戻す。

        明示的な上書き操作専用。GUI側で番号と上書き確認を行う。
        読み戻し成功後、画面表示とローカルキャッシュを更新する。
        JSONへの保存は別ボタンで明示的に行う。
        """
        if number < 0:
            raise ValueError("P番号は0以上を指定してください")
        if self._current_position is None:
            raise RuntimeError("先に現在位置を取得してください")
        if not self._uses_robot_memory:
            key = f"P{number}"
            updated = self._positions.copy()
            updated[key] = self._current_position
            self.save_file(data=updated)
            self._positions = updated
            self._manager.set_var(key, self._current_position, save=False)
            self._source = "JSON（現在位置の登録後）"
            return self._current_position
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        result = self.robot.set_var("P", number, self._current_position)
        if inspect.isawaitable(result):
            raise RuntimeError("書き込みには同期DeviceProxyが必要です")
        if result is False:
            raise RuntimeError(f"P{number}への書き込みが失敗しました")
        readback = self.robot.get_var("P", number)
        if inspect.isawaitable(readback):
            raise RuntimeError("読み戻しには同期DeviceProxyが必要です")
        if readback is False or readback is None:
            raise RuntimeError(
                f"P{number}の読み戻しに失敗しました。実機の状態を確認してください"
            )
        self._manager.set_var(f"P{number}", readback, save=False)
        self._positions[f"P{number}"] = readback
        self._robot_positions[f"P{number}"] = copy.deepcopy(readback)
        self._source = "ロボット（書き込み後）"
        return readback

    def clear_number(
        self,
        number: int,
    ) -> Any:
        """指定P番号を未使用値に変更し、実機から読み戻して反映する。

        Cobottaでは実機のP変数を変更する。その他はJSONを更新する。
        """
        if number < 0:
            raise ValueError("P番号は0以上を指定してください")
        empty = [0, 0, 0, 0, 0, 0, -1]
        if not self._uses_robot_memory:
            key = f"P{number}"
            updated = self._positions.copy()
            updated[key] = empty.copy()
            self.save_file(data=updated)
            self._positions = updated
            self._manager.set_var(key, empty.copy(), save=False)
            self._source = "JSON（クリア後）"
            return empty
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        result = self.robot.set_var("P", number, empty)
        if inspect.isawaitable(result):
            raise RuntimeError("書き込みには同期DeviceProxyが必要です")
        if result is False:
            raise RuntimeError(f"P{number}のクリアに失敗しました")
        readback = self.robot.get_var("P", number)
        if inspect.isawaitable(readback):
            raise RuntimeError("読み戻しには同期DeviceProxyが必要です")
        if readback is False or readback is None:
            raise RuntimeError(f"P{number}の読み戻しに失敗しました")
        if list(readback) != empty:
            raise RuntimeError(f"P{number}のクリア値が一致しません: {readback!r}")
        self._manager.set_var(f"P{number}", readback, save=False)
        self._positions[f"P{number}"] = readback
        self._robot_positions[f"P{number}"] = copy.deepcopy(readback)
        self._source = "ロボット（クリア後）"
        return readback

    def delete_numbers(
        self,
        numbers: list[int],
    ) -> None:
        """選択P番号を表示一覧とローカルキャッシュから削除する。

        Cobottaでは実機とJSONを変更しない。その他はJSONからも削除する。
        """
        updated = self._positions.copy()
        for number in numbers:
            updated.pop(f"P{number}", None)
        if not self._uses_robot_memory:
            self.save_file(allow_empty=True, data=updated)
        self._positions = updated
        for number in numbers:
            self._manager.delete_var("P", number)
        if self._uses_robot_memory:
            self._source = "一覧（ローカル削除後）"
        else:
            self._source = "JSON（削除後）"

    def teach_first_unused(
        self,
        start: int,
        end: int,
    ) -> None:
        """空き番号への自動登録。未使用判定が未確定の間は書き込まない。"""
        raise RuntimeError(
            "未使用P番号の判定条件が未確認です。"
            "既存値を保護するため自動登録は実行できません"
        )
