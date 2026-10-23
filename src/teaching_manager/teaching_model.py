"""ティーチングGUIのModel。

責務:
    RobotVarManagerを介して指定範囲のP変数をロボットから取得し、
    JSONから読み込んだP変数と現在位置を画面表示用に保持する。

責務外:
    Qt画面の構築、DeviceProxyの生成、ロボット固有APIの変換、
    ロボット内部変数およびJSONへの書き込み。

安全上の制約:
    読み取りテスト版。ロボットへの書き込みAPIは呼び出さない。
    P変数の値から未使用かどうかを推測しない。
"""

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
    ) -> None:
        """既存の変数マネージャーとJSONファイルの場所を設定する。"""
        self._manager = manager
        self._filename = Path(filename)
        self._logger = logger
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

        RobotVarManager.read_vars_from_robot()を利用する。
        get_all_var()は変数名一覧を返すため使用しない。
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

        # 既存マネージャーのキャッシュには他の変数も存在し得る。
        # 今回要求した番号だけを、全件取得成功後に画面へ反映する。
        self._manager.read_vars_from_robot("P", start, end)
        result: Dict[str, Any] = {}
        for number in range(start, end + 1):
            key = f"P{number}"
            result[key] = self._manager.get_var(key)
        self._positions = result
        self._source = f"ロボット（P{start}～P{end}）"

    def read_current_position(self) -> None:
        """共通APIから現在位置を取得する。ロボットへの書き込みは行わない。"""
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        result = self.robot.get_current_position()
        if result is False or result is None:
            raise RuntimeError("現在位置の取得に失敗しました")
        self._current_position = result

    def first_unused(self, start: int, end: int) -> Optional[int]:
        """未使用判定の仕様が未確定のため、常にNoneを返す。

        取得できなかった番号や値だけを根拠に空き番号を判定しない。
        """
        return None
