"""ティーチングGUIのModel。

責務:
    DeviceProxyを保持するRobotVarManagerを通じたロボット参照、
    P変数と現在位置の読み取り、JSONの読み取り、画面表示用状態の保持、
    および取得済みP番号の照会を担当する。

責務外:
    Qtウィジェット・イベント処理、ロボット接続インスタンスの生成、
    ロボット固有APIの変換、ロボットおよびJSONへの書き込み。

安全性:
    このテスト版では書き込みメソッドを実装しない。
    first_unused()は取得結果に存在しないキーを探すだけで、
    ロボット側の未使用状態を保証しない。
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from .robot_var_manager import RobotVarManager


class TeachingModel:
    """GUI非依存の読み取り状態と操作を管理する。

    _manager: ロボット参照を保持する既存RobotVarManager（内部属性）。
    _filename: 読み取り対象JSONファイル（内部属性）。
    positions: 最後に読み込んだP変数の表示用スナップショット（公開プロパティ）。
    source: スナップショットの取得元。
    current_position: 最後に取得した現在位置。
    """

    def __init__(
        self,
        manager: RobotVarManager,
        filename: str,
        logger=None,
    ) -> None:
        """既存マネージャーとJSONのパスを保持し、読み取り状態を初期化する。"""
        self._manager = manager
        self._filename = Path(filename)
        self._source = "未読込"
        self._positions: Dict[str, Any] = {}
        self._current_position: Any = None
        self._logger = logger

    @property
    def robot(self) -> Any:
        """RobotVarManager._robot_instanceの参照を返す。"""
        return self._manager._robot_instance

    @property
    def source(self) -> str:
        """最後に読み込んだP変数一覧の取得元を返す。"""
        return self._source

    @property
    def positions(self) -> Dict[str, Any]:
        """表示用P変数一覧のコピーを返す。"""
        return self._positions.copy()

    @property
    def current_position(self) -> Any:
        """最後に取得した現在位置を返す。"""
        return self._current_position

    def load_file(self) -> None:
        """JSONからP変数を読み込む。実機には書き込まない。"""
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

    @staticmethod
    def _only_p(data: Dict[str, Any]) -> Dict[str, Any]:
        """Pと数字からなるキーだけを抽出する内部処理。"""
        return {
            key: value
            for key, value in data.items()
            if isinstance(key, str) and key.startswith("P") and key[1:].isdigit()
        }

    def read_robot(self) -> None:
        """共通APIで実機変数を取得する。JSONは変更しない。"""
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        result = self.robot.get_all_var()
        if not isinstance(result, dict):
            raise TypeError(
                f"get_all_var() の戻り値がdictではありません: {type(result).__name__}"
            )
        self._positions = self._only_p(result)
        self._source = "ロボット（読み取り専用）"

    def read_current_position(self) -> None:
        """共通APIで現在位置を取得する。書き込みは行わない。"""
        if self.robot is None:
            raise RuntimeError("ロボットが接続されていません")
        result = self.robot.get_current_position()
        if result is False or result is None:
            raise RuntimeError("現在位置の取得に失敗しました")
        self._current_position = result

    def first_unused(self, start: int, end: int) -> Optional[int]:
        """取得結果にキーがない最初の番号を返す。実機の未使用保証ではない。"""
        if self._source != "ロボット（読み取り専用）":
            return None
        for number in range(start, end + 1):
            if f"P{number}" not in self._positions:
                return number
        return None
