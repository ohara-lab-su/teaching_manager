#!/usr/bin/env python
import json
from typing import Any, Optional, Set, Dict, List, Union, Tuple, Type, TypeVar


class RobotVarManager:
    """
    Cobotta だけではなく一般的な　Robot 向けの座標マネージャ
    """

    def __init__(
        self,
        robot_instance=None,
        logger=None,
        filename: Optional[str] = None,
        autosave: bool = False,
        autoload: bool = False,
    ):
        self._robot_instance = robot_instance
        self._vars = {}  # ローカルキャッシュ: {"P10": [...], "F1": ...}
        self._logger = logger
        self._filename = filename
        self._autosave = bool(autosave)

        if autoload:
            if filename is not None:
                try:
                    self.load(filename)
                except FileNotFoundError:
                    pass

    @property
    def robot_instance(self) -> Any:
        """接続済みロボットを返す。接続がない場合はNone。"""
        return self._robot_instance

    def delete_var(self, kind: str, num: int) -> None:
        """ローカルキャッシュの指定変数のみ削除する。実機には影響しない。"""
        self._vars.pop(self._make_key(kind, num), None)
        self._autosave_if_enabled()

    def _autosave_if_enabled(self):
        """autosave=True のときだけ現在のローカル変数を保存する。"""
        if self._autosave:
            if self._filename is not None:
                self.save(self._filename)

    @staticmethod
    def _make_key(kind_or_combined: str, num: Optional[Union[str, int]] = None) -> str:
        """("P", 10) と "P10" を同じキー表現へ正規化する。"""
        if num is None:
            return str(kind_or_combined).upper()
        return f"{str(kind_or_combined).upper()}{int(num)}"

    # --- プロパティアクセス（var.P10 = ...） ---
    def __getattr__(self, name):
        """内部値を読む (cobotta値は読んでいない)"""
        if name in self._vars:
            return self._vars[name]
        raise AttributeError(f"No such variable: {name}")

    def __setattr__(
        self,
        name,
        value,
    ):
        """内部値を書き換える (cobotta値は直接いじらない)"""
        # 先頭が '_' の内部属性はそのまま属性として保持
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._vars[str(name).upper()] = value
            self._autosave_if_enabled()

    # dict風アクセス（var["P10"]） ---
    def __getitem__(self, key):
        return self._vars[key]

    def __setitem__(self, key, value):
        self._vars[str(key).upper()] = value
        self._autosave_if_enabled()

    # ローカル変数一括/範囲セット ---
    def set_vars(
        self,
        kind,
        start,
        end=None,
        value=None,
    ):
        """
        ローカル変数の一括/範囲セット（cobotta本体には影響しない）

        例::
            set_vars("P", 10, value=[1,2,3,4,5,6])
            set_vars("P", 10, 12, value=[ [1,2,3,4,5,6], ... ])

        Args:
            kind:
            start:
            end:
            value:

        Returns:

        """
        if end is None:
            keys = [f"{kind}{start}"]
            values = [value]
        else:
            keys = [f"{kind}{i}" for i in range(start, end + 1)]
            if not isinstance(value, (list, tuple)):
                raise ValueError("値リスト長と変数数が一致しません")
            if len(value) != len(keys):
                raise ValueError("値リスト長と変数数が一致しません")
            values = value

        for k, v in zip(keys, values):
            self._vars[str(k).upper()] = v
        self._autosave_if_enabled()

    def get_var(
        self,
        kind_or_combined: str,
        num: Optional[Union[str, int]] = None,
        default: Any = False,
    ):
        """単一ローカル変数を取得する。

        `get_var("P", 10)` と `get_var("P10")` は同じ意味である。
        変数が存在しない場合は CobottaCtrl 側の慣例に合わせて False を返す。
        """
        key = self._make_key(kind_or_combined, num)
        return self._vars.get(key, default)

    def set_var(
        self,
        kind: str,
        num: Union[str, int, Any],
        value=None,
        save: Optional[bool] = None,
    ):
        """単一ローカル変数のセット。

        `set_var("P", 10, value)` と `set_var("P10", value)` の両方を受け付ける。

        Args:
            kind: 変数種別または結合済み変数名。例: `"P"`, `"P10"`。
            num: 変数番号、または `kind` が結合済み変数名の場合の値。
            value: 保存する値。
            save: JSON保存制御。`None` の場合は `autosave` 設定に従う。
                `True` の場合は即保存し、`False` の場合は保存しない。
        """
        if value is None:
            key = self._make_key(kind)
            resolved = num
        else:
            key = self._make_key(kind, num)
            resolved = value
        self._vars[key] = resolved
        if save is True:
            self.save(self._filename)
        elif save is None:
            self._autosave_if_enabled()

    #
    # robot_instance
    #

    # --- cobottaインスタンス管理 ---
    def attach_robot(self, cobotta):
        self._robot_instance = cobotta

    def add_robot(self, cobotta):
        self._robot_instance = cobotta

    # simple 版
    def get_robot(self, varname: str):
        """Cobotta本体から値を取得し、managerにも反映"""
        value = getattr(self._robot_instance, varname)
        self._vars[varname] = value
        return value

    # ローカル変数一括/範囲取得（cobotta本体→ローカル） ---
    def read_vars_from_robot(
        self,
        kind: str,
        start: Union[str, int],
        end=None,
    ):
        """
        cobotta本体 --> managerに反映
        """
        if self._robot_instance is None:
            raise RuntimeError("No robot_instance attached")

        if end is None:
            keys = [f"{kind}{start}"]
        else:
            keys = [f"{kind}{i}" for i in range(start, end + 1)]

        for key in keys:
            self._vars[key] = getattr(self._robot_instance, key)

    def read_var_from_robot(
        self,
        kind: str,
        num: Union[str, int, None] = None,
    ):
        """
        cobotta本体 --> managerに反映
        """
        if self._robot_instance is None:
            raise RuntimeError("No robot_instance attached")

        if num is None:
            # ex) kine = P10
            key = f"{kind}"
        else:
            # ex) kine = P, num = 10
            key = f"{kind}{num}"

        self._vars[key] = getattr(self._robot_instance, key)

    # ローカル変数一括/範囲書き込み（ローカル→cobotta本体、危険！） ---
    def write_vars_to_cobotta(
        self,
        kind,
        start,
        end=None,
    ):
        """
        end 省略で var のみ登録(一つだけ)
        manager --> cobotta本体へ反映（危険！）
        """
        if self._robot_instance is None:
            raise RuntimeError("No robot_instance attached")
        if end is None:
            keys = [f"{kind}{start}"]
        else:
            keys = [f"{kind}{i}" for i in range(start, end + 1)]

        for key in keys:
            if key in self._vars:
                setattr(self._robot_instance, key, self._vars[key])
            else:
                self._logger.warning(f"Warning: {key} not found in local vars. Skip.")

    def write_var_to_robot(
        self,
        kind: str,
        num: Union[str, int, None] = None,
    ):
        """
        end 省略と同じ意味
        manager --> cobotta本体へ反映（危険！）
        """
        if self._robot_instance is None:
            raise RuntimeError("No robot_instance attached")

        if num is None:
            key = f"{kind}"
        else:
            key = f"{kind}{num}"

        if key in self._vars:
            setattr(self._robot_instance, key, self._vars[key])
        else:
            self._logger.warning(f"Warning: {key} not found in local vars. Skip.")

    # 全部一括で書き込み（ローカル→robot_instance、全壊注意） ---
    def write_all_to_robot(self):
        """
        Manager に存在する全変数を robot_instance 本体に一斉反映（超危険）
        """
        if self._robot_instance is None:
            raise RuntimeError("No robot_instance attached")

        for key, value in self._vars.items():
            setattr(self._robot_instance, key, value)

    # JSON保存・ロード
    def save(self, filename=None):
        if filename is None:
            filename = self._filename
        if filename is None:
            raise ValueError("filename is not specified")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self._vars, f, indent=2, ensure_ascii=False)
        self._filename = filename

    def load(self, filename=None):
        if filename is None:
            filename = self._filename
        if filename is None:
            raise ValueError("filename is not specified")
        with open(filename, "r", encoding="utf-8") as f:
            self._vars = json.load(f)
        self._filename = filename

    # --- 現在のローカル変数リスト取得 ---
    def list_vars(self):
        return list(self._vars.keys())

    def __repr__(self):
        cls = self.__class__.__name__
        robot_state = "none"
        if self._robot_instance is not None:
            robot_state = "attached"
        n = len(self._vars)
        # 先頭3件だけプレビュー
        preview_keys = list(self._vars.keys())[:3]
        preview = ", ".join(f"{k}={self._vars[k]!r}" for k in preview_keys)
        if n > 3:
            preview += ", ..."
        return f"{cls}(robot={robot_state}, vars={n}, preview=[{preview}])"

    # 人間向けの詳細表示が欲しい場合
    def __str__(self):
        try:
            return json.dumps(self._vars, ensure_ascii=False, indent=2)
        except Exception:
            return repr(self)
