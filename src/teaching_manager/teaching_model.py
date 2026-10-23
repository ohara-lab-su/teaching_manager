"""ティーチングGUIのModel。

責務:
    DeviceProxyの共通APIで指定範囲のP変数をロボットから取得し、
    JSONから読み込んだP変数と現在位置を画面表示用に保持する。

責務外:
    Qt画面の構築、DeviceProxyの生成、ロボット固有APIの変換、
    ロボット内部変数への書き込み（テスト中は無効）。

安全上の制約:
    読み取りテスト版。ロボットへの書き込みAPIは呼び出さない。
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

    def save_file(self) -> None:
        """現在画面に表示しているP変数をJSONへ保存する。

        ロボットには書き込まない。読み取り結果がない場合は既存ファイルを
        空のデータで上書きしない。保存成功後にだけ表示元を更新する。
        """
        if not self._positions:
            raise ValueError("保存対象のP変数がありません。先にロボットから読み込んでください")
        self._filename.parent.mkdir(parents=True, exist_ok=True)
        # JSONへ書く内容は表示中のP変数だけ。マネージャーの他種変数は含めない。
        import os
        import tempfile
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self._filename.parent,
                prefix=f".{self._filename.name}.", suffix=".tmp", delete=False,
            ) as stream:
                temporary_name = stream.name
                json.dump(self._positions, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, self._filename)
        finally:
            if temporary_name is not None and os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def teach_first_unused(self, start: int, end: int) -> None:
        """空き番号へのティーチング操作（実機書き込みテスト前は実行禁止）。

        現時点では未使用P変数の判定条件が確認されていない。
        ロボットの既存値を破壊しないため、書き込みAPIは呼び出さない。
        """
        raise RuntimeError("実機書き込みテスト前のため、ティーチングは無効です")
