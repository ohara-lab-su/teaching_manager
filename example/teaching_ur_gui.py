"""P座標ティーチングGUIの起動例。

機種ごとの DeviceProxy を生成し、共通の教示画面を起動する。
"""

import logging
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
ROOT = EXAMPLE_DIR.parent
sys.path.insert(0, str(ROOT / "src"))

from teaching_manager.teaching_gui import run_teaching_gui
from x_logger import XLogger

#######################################################
# UR の接続設定は、この起動スクリプトと同じディレクトリから読む。
CONFIG_FILE = EXAMPLE_DIR / "ur_server.yaml"

# JSONの既定値。フォルダとファイル名の両方を変更できる。
# 相対パスを指定した場合も、起動スクリプトの場所を基準に解決する。
JSON_FILE = "robot_positions.json"
#######################################################

JSON_PATH = Path(JSON_FILE)
if not JSON_PATH.is_absolute():
    JSON_PATH = EXAMPLE_DIR / JSON_PATH
JSON_FILE = str(JSON_PATH.resolve())

# httpx のログを WARNING レベル以上にする（INFO を抑制）
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> int:
    """機種に対応する接続オブジェクトを作り、教示画面を起動する。"""

    from ur import Config
    from ur.server_fastapi import DeviceProxy

    device_name = "UrCtrl"
    config = Config(str(CONFIG_FILE))
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
