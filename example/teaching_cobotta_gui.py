"""P座標ティーチングGUIの起動例。

機種ごとの DeviceProxy を生成し、共通の教示画面を起動する。
"""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from teaching_manager.teaching_gui import run_teaching_gui
from x_logger import XLogger

# httpx のログを WARNING レベル以上にする（INFO を抑制）
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> int:
    """機種に対応する接続オブジェクトを作り、教示画面を起動する。"""

    # 接続先の変更は、以下のimportとDeviceProxyの生成箇所のみで行う。
    from cobotta2 import Config
    from cobotta2.server_fastapi import DeviceProxy

    #######################################################
    # JSONの既定値。フォルダとファイル名の両方を変更できる。
    # 相対パスを指定した場合も、起動スクリプトの場所を基準に解決する。
    JSON_FILE = "robot_positions.json"

    JSON_PATH = Path(JSON_FILE)
    if not JSON_PATH.is_absolute():
        JSON_PATH = Path(__file__).resolve().parent / JSON_PATH
    JSON_FILE = str(JSON_PATH.resolve())
    #######################################################

    config = Config("config_cobotta3_server5.yaml")
    device_name = "CobottaCtrl"
    logger = XLogger(log_level="info")

    robot = DeviceProxy(
        device_name,
        config=config,
        logger=logger,
        async_mode=False,
    )
    # robot = None  # 未接続でGUIの読み取り表示を確認する場合
    return run_teaching_gui(robot, device_name, JSON_FILE, logger=logger)


if __name__ == "__main__":
    sys.exit(main())
