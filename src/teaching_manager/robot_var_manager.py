#!/usr/bin/env python
"""機器変数を名前付きのメモリ上の値として保持し、一つの JSON に保存する。"""

import json
from typing import Any, Optional, Set, Dict, List, Union, Tuple, Type, TypeVar


class RobotVarManager:
    """名前付きの変数とその永続化を扱う機器非依存のクラス。

    キーには `P10` や `I1` を使う。番号の範囲、座標の長さや単位、
    値の意味は呼び出し元の制御クラスが決める。欠番は辞書に置かない。
    全件参照は `list_vars()` と `manager[key]`、個別参照は `get_var()`。
    `load()` は JSON 全件でメモリを置き換え、`save()` はメモリ全件を
    一つの JSON に書く。機器と明示的に同期する操作は、接続先の同名属性を使う。
    """

    def __init__(
        self,
        robot_instance=None,
        logger=None,
        filename: Optional[str] = None,
        autosave: bool = False,
        autoload: bool = False,
    ):
        """変数キャッシュを作り、必要なら初期 JSON を読み込む。

        Args:
            robot_instance: 属性経由で機器と同期する場合の接続オブジェクト。
                キャッシュと JSON だけを使う場合は None。
            logger: 機器への書き戻し対象がキャッシュにない場合に警告を出すロガー。
            filename: 引数なしの `load()` と `save()` が使う JSON のパス。
            autosave: 対応する変更操作で既定 JSON を自動保存するか。
            autoload: `filename` を指定したとき、初期化中に JSON 全件を読むか。
                ファイルがまだなければ空のキャッシュで開始する。

        Raises:
            OSError: ファイル不存在以外の理由で初期 JSON を読めない場合。
            ValueError: 初期 JSON をデコードできない場合。
        """
        self._robot_instance = robot_instance
        self._vars = {}
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
        """明示的な機器同期に使うオブジェクトを返す。未設定なら None。"""
        return self._robot_instance

    def delete_var(self, kind: str, num: int) -> None:
        """指定したキーをキャッシュから削除する。

        Args:
            kind: 変数種別。例として `P10` を削除するなら `"P"`。
            num: 変数番号。上の例では 10。

        存在しないキーの削除は許容する。自動保存が有効で既定パスがあれば
        削除後の全変数を JSON に保存する。接続先の機器側変数には触れない。
        """
        self._vars.pop(self._make_key(kind, num), None)
        self._autosave_if_enabled()

    def _autosave_if_enabled(self):
        """自動保存が有効で既定パスが設定済みの場合に全変数を保存する。"""
        if self._autosave:
            if self._filename is not None:
                self.save(self._filename)

    @staticmethod
    def _make_key(kind_or_combined: str, num: Optional[Union[str, int]] = None) -> str:
        """種別と番号、または結合済みの名前を大文字のキャッシュキーにする。"""
        if num is None:
            return str(kind_or_combined).upper()
        return f"{str(kind_or_combined).upper()}{int(num)}"

    def __getattr__(self, name):
        """キャッシュを属性名そのままで参照し、未登録なら AttributeError を送出する。"""
        if name in self._vars:
            return self._vars[name]
        raise AttributeError(f"No such variable: {name}")

    def __setattr__(
        self,
        name,
        value,
    ):
        """内部属性以外を大文字のキャッシュキーに変換して登録し、自動保存を判定する。"""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._vars[str(name).upper()] = value
            self._autosave_if_enabled()

    def __getitem__(self, key):
        """キャッシュの指定キーをそのまま引いて値を返す。

        `list_vars()` が返したキーを渡せば、対応する値を得られる。
        キーが存在しない場合は KeyError。未登録時に既定値を返す操作は `get_var()`。
        """
        return self._vars[key]

    def __setitem__(self, key, value):
        """キーを大文字にしてキャッシュを更新し、自動保存を判定する。"""
        self._vars[str(key).upper()] = value
        self._autosave_if_enabled()

    def set_vars(
        self,
        kind,
        start,
        end=None,
        value=None,
    ):
        """ローカルキャッシュの一点、または連続した番号をまとめて更新する。

        Args:
            kind: 変数種別。例えば `"P"`。
            start: 開始番号。
            end: 終了番号を含む。省略時は `start` の一点だけを扱う。
            value: 一点指定ではその点の値。範囲指定では各番号の値を並べた
                リストまたはタプル。

        Raises:
            ValueError: 範囲指定の値がリスト・タプル以外、または件数に合わない場合。

        自動保存が有効なら、一連の更新後に全変数を一度保存する。
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
        """指定した変数をローカルキャッシュから一件取得する。

        Args:
            kind_or_combined: 種別 `"P"` または結合済みの名前 `"P10"`。
            num: 種別と分けて指定するときの番号。
            default: 未登録時に返す値。既定は False。登録済みの False と
                未登録を区別するときは、呼び出し元が専用の値を指定する。

        Returns:
            登録値または `default`。
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
        """指定した変数をキャッシュに登録または更新する。

        Args:
            kind: 種別 `"P"` または結合済みの名前 `"P10"`。
            num: 種別指定時の番号。結合済み指定なら保存する値。
            value: 種別と番号を分けて指定した場合の値。None は二引数形式の判定に使う。
            save: True なら全変数を既定 JSON に保存する。False ならメモリだけを
                更新する。None ならインスタンスの自動保存設定に従う。

        Returns:
            None。

        保存が失敗すると例外を呼び出し元に伝える。キャッシュの更新は保存より先に
        行うため、その時点で値は更新済み。
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


    def attach_robot(self, cobotta):
        """機器同期の相手を設定する。キャッシュや機器の値は操作しない。"""
        self._robot_instance = cobotta

    def add_robot(self, cobotta):
        """機器同期の接続先を一つ設定する。既に接続先があれば置き換える。"""
        self._robot_instance = cobotta

    def get_robot(self, varname: str):
        """接続先の `varname` 属性を読み、同じ名前でキャッシュして値を返す。"""
        value = getattr(self._robot_instance, varname)
        self._vars[varname] = value
        return value

    def read_vars_from_robot(
        self,
        kind: str,
        start: Union[str, int],
        end=None,
    ):
        """機器の属性を一点または指定範囲だけ順に読み、キャッシュする。

        Args:
            kind: 連結する属性の種別。
            start: 開始番号。終了番号を省略した場合は一点の番号。
            end: 終了番号を含む。機器属性の取得結果を一件ずつ反映するため、
                途中で取得に失敗した場合は先に読めた値が残る。
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
        """接続先の属性から一件読み、キャッシュに入れる。

        `kind` に `"P10"` を渡すか、`kind="P", num=10` で指定する。
        この読み取りでは JSON を保存しない。
        """
        if self._robot_instance is None:
            raise RuntimeError("No robot_instance attached")

        if num is None:
            key = f"{kind}"
        else:
            key = f"{kind}{num}"

        self._vars[key] = getattr(self._robot_instance, key)

    def write_vars_to_cobotta(
        self,
        kind,
        start,
        end=None,
    ):
        """キャッシュ内の指定点を COBOTTA の変数属性に順に代入する。

        Args:
            kind: 機器属性名の種別。
            start: 開始番号。
            end: 終了番号を含む。省略した場合は `start` の一点。

        キャッシュにない番号は警告を出して飛ばす。途中の例外より前に
        完了した属性代入の結果は機器側に残る。
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
        """指定した一件をキャッシュから機器の同名属性へ代入する。

        `kind` に結合済みの名前を渡すか、`kind` と `num` を分けて渡す。
        キャッシュにキーがなければ警告を出し、その属性には代入しない。
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

    def write_all_to_robot(self):
        """キャッシュに存在する全変数を機器の同名属性へ順に代入する。

        登録済みの全キーを対象とするため、呼び出し元は対象一覧を確認して使う。
        途中で例外が発生した場合も、それ以前の機器側への代入は残る。
        """
        if self._robot_instance is None:
            raise RuntimeError("No robot_instance attached")

        for key, value in self._vars.items():
            setattr(self._robot_instance, key, value)

    def save(self, filename=None):
        """現在保持する全変数を UTF-8 の JSON 一つに書き出す。

        Args:
            filename: 書き出し先。省略時は既定パス。成功時は今回のパスを
                次回以降の既定パスとして保持する。

        Raises:
            ValueError: 保存先が未設定の場合。
            OSError: ファイルを開く、または書き出す処理に失敗した場合。
            TypeError: JSON に変換できない値を含む場合。

        既存ファイルは開く時点で切り詰める。部分更新や原子的置換は行わない。
        """
        if filename is None:
            filename = self._filename
        if filename is None:
            raise ValueError("filename is not specified")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self._vars, f, indent=2, ensure_ascii=False)
        self._filename = filename

    def load(self, filename=None):
        """UTF-8 の JSON を全件読み込み、現在のキャッシュを置き換える。

        Args:
            filename: 読込元。省略時は既定パス。成功時は今回のパスを
                次回以降の既定パスとして保持する。

        Raises:
            ValueError: パスの未設定、または JSON のデコード失敗時。
            OSError: ファイル不存在などで読み込めない場合。

        変数名と値の対応を持つ JSON オブジェクトを渡す。既存のキャッシュとの
        マージや座標の形式・単位の変換は行わない。
        """
        if filename is None:
            filename = self._filename
        if filename is None:
            raise ValueError("filename is not specified")
        with open(filename, "r", encoding="utf-8") as f:
            self._vars = json.load(f)
        self._filename = filename

    def list_vars(self):
        """登録済みキーを一度に列挙する。値は `manager[key]` で得られる。

        例えば P100 と P1000 が登録済みなら、その間の欠番は列挙されない。
        P 以外の変数も登録されていれば含める。
        """
        return list(self._vars.keys())

    def __repr__(self):
        """機器の有無、変数件数、先頭三件のキーと値を短い文字列で返す。"""
        cls = self.__class__.__name__
        robot_state = "none"
        if self._robot_instance is not None:
            robot_state = "attached"
        n = len(self._vars)
        preview_keys = list(self._vars.keys())[:3]
        preview = ", ".join(f"{k}={self._vars[k]!r}" for k in preview_keys)
        if n > 3:
            preview += ", ..."
        return f"{cls}(robot={robot_state}, vars={n}, preview=[{preview}])"

    def __str__(self):
        """全変数の整形済み JSON を返す。シリアライズできなければ概要に切り替える。"""
        try:
            return json.dumps(self._vars, ensure_ascii=False, indent=2)
        except Exception:
            return repr(self)
