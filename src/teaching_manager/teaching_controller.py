"""ティーチング画面の操作を調整するController。

責務: 起動時の読込元の選択、現在位置取得、P変数の読書き、
      クリア、ローカル削除、JSON保存のModelへの委譲。
責務外: Qtウィジェット、確認ダイアログ、ロボット固有APIの実装。
"""

import asyncio
import inspect
from typing import Any

from .teaching_model import TeachingModel


class TeachingController:
    """GUIからの操作をModelへ振り分ける。"""

    def __init__(
        self,
        model: TeachingModel,
        device_name: str,
        logger=None,
    ) -> None:
        """DeviceProxyのデバイス名からP変数の保存先を決定する。

        Args:
            model: P変数と現在位置を管理するModel。
            device_name: DeviceProxy生成時に指定したデバイス名。
                CobottaCtrlのみロボット内部P変数を利用し、その他はJSONを利用する。
        """
        self._model = model
        self._device_name = device_name
        self._uses_robot_memory = device_name == "CobottaCtrl"
        self._model.set_storage_mode(self._uses_robot_memory)
        self._logger = logger

    @property
    def uses_robot_memory(self) -> bool:
        """P変数の保存先がロボット内部メモリかどうかを返す。"""
        return self._uses_robot_memory

    @property
    def model(self) -> TeachingModel:
        """表示状態を保持するModelを返す。"""
        return self._model

    def load_initial(
        self,
        start: int,
        end: int,
    ) -> None:
        """明示設定に従って初期データを読み込む。"""
        if self._uses_robot_memory:
            self._model.read_robot(start, end)
        else:
            self._model.load_file()

    def read_robot(
        self,
        start: int,
        end: int,
    ) -> None:
        """指定範囲のP変数を実機から読み込む。"""
        if not self._uses_robot_memory:
            raise RuntimeError(
                "このデバイスのP変数はJSON管理です。JSONから読み込んでください"
            )
        self._model.read_robot(start, end)

    def load_file(self) -> None:
        """JSONを読み込む。"""
        self._model.load_file()

    def save_file(self) -> None:
        """表示中の一覧をJSONへ保存する。"""
        self._model.save_file()

    def read_current_position(self) -> Any:
        """現在位置を取得する。同期/非同期モードはModel設定に従う。"""
        return self._model.read_current_position()

    def teach_number(
        self,
        number: int,
    ) -> Any:
        """現在位置を指定P番号へ書き込む。"""
        return self._model.teach_number(number)

    def teach_first_unused(
        self,
        start: int,
        end: int,
    ) -> None:
        """空き番号への登録をModelへ委譲する。"""
        self._model.teach_first_unused(start, end)

    def clear_numbers(
        self,
        numbers: list[int],
    ) -> list[int]:
        """選択したP変数を保存先に応じて順次クリアする。"""
        completed: list[int] = []
        for number in numbers:
            self._model.clear_number(number)
            completed.append(number)
        return completed

    def clear_number(
        self,
        number: int,
    ) -> Any:
        """指定P変数を未使用値に変更する。"""
        return self._model.clear_number(number)

    def delete_numbers(
        self,
        numbers: list[int],
    ) -> None:
        """一覧から削除する。JSON管理ではファイルにも反映する。"""
        self._model.delete_numbers(numbers)
