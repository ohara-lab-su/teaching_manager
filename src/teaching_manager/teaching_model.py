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
import inspect
import json
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

    def set_storage_mode(self, uses_robot_memory: bool) -> None:
        """P変数の保存先を設定する。Controllerがデバイス名から決定する。

        Args:
            uses_robot_memory: Trueなら実機P変数、FalseならJSONファイル。
        """
        self._uses_robot_memory = uses_robot_memory

    @property
    def robot(self) -> Any:
        """マネージャーに接続済みのロボットインスタンスを返す。"""
        return self._manager._robot_instance

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

    def load_file(self) -> None:
        """JSONを読み取って表示状態を更新する。ロボットへは書き込まない。"""
        if not self._filename.exists():
            self._positions = {}
            self._source = "JSON（ファイルなし）"
            return
        with self._filename.open(encoding="utf-8") as stream:
            data = json.load(stream)
        if not isinstance(data, dict):
            raise ValueError("JSONのルートは辞書である必要があります")
        self._positions = self._only_p(data)
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
    ) -> None:
        """現在画面に表示しているP変数をJSONへ保存する。

        ロボットには書き込まない。読み取り結果がない場合は既存ファイルを
        空のデータで上書きしない。保存成功後にだけ表示元を更新する。
        """
        if not self._positions and not allow_empty:
            raise ValueError(
                "保存対象のP変数がありません。先にロボットから読み込んでください"
            )
        self._filename.parent.mkdir(parents=True, exist_ok=True)
        # JSONへ書く内容は表示中のP変数だけ。マネージャーの他種変数は含めない。
        import os
        import tempfile

        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._filename.parent,
                prefix=f".{self._filename.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_name = stream.name
                json.dump(self._positions, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, self._filename)
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
            self._positions[key] = self._current_position
            self._manager.set_var(key, self._current_position, save=False)
            self.save_file()
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
        self._source = "ロボット（書き込み後）"
        return readback

    def clear_number(
        self,
        number: int,
    ) -> Any:
        """指定P番号を未使用値に変更し、実機から読み戻して反映する。

        実機のP変数を変更する操作であり、JSONファイルは変更しない。
        """
        if number < 0:
            raise ValueError("P番号は0以上を指定してください")
        empty = [0, 0, 0, 0, 0, 0, -1]
        if not self._uses_robot_memory:
            key = f"P{number}"
            self._positions[key] = empty.copy()
            self._manager.set_var(key, empty.copy(), save=False)
            self.save_file()
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
        self._source = "ロボット（クリア後）"
        return readback

    def delete_numbers(
        self,
        numbers: list[int],
    ) -> None:
        """選択P番号を表示一覧とローカルキャッシュから削除する。

        ロボット内部のP変数とJSONファイルには一切書き込まない。
        JSONへの削除反映は別途「JSONに保存」を実行した場合のみ行う。
        """
        for number in numbers:
            key = f"P{number}"
            self._positions.pop(key, None)
            self._manager._vars.pop(key, None)
        if not self._uses_robot_memory:
            self.save_file(allow_empty=True)
            self._source = "JSON（削除後）"
        else:
            self._source = "一覧（ローカル削除後）"

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
