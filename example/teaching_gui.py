"""P座標ティーチングGUIの起動例。

DeviceProxyとMVC各要素を組み立て、パッケージ内のQt画面を起動する。
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from teaching_manager.robot_var_manager import RobotVarManager
from teaching_manager.teaching_model import TeachingModel
from teaching_manager.teaching_controller import TeachingController
from teaching_manager.teaching_gui import TeachingWindow
from x_logger import XLogger

JSON_FILE = str(ROOT / "robot_positions.json")


def main() -> None:
    """QtアプリケーションとModelを生成し、GUIを起動する。"""
    app = QApplication(sys.argv)

    # httpx のログを WARNING レベル以上にする（INFO を抑制）
    import logging

    logging.getLogger("httpx").setLevel(logging.WARNING)

    ##################################################
    # 接続先の変更は、以下のimportとDeviceProxyの生成箇所のみで行う。
    from cobotta2 import Config
    from cobotta2.server_fastapi import DeviceProxy

    # 実機接続時は次の2行を有効化し、import元と制御クラス名を指定する。
    logger = XLogger(log_level="info")
    config = Config("config_cobotta3_server5.yaml")

    device_name = "CobottaCtrl"

    robot = DeviceProxy(
        device_name,
        config=config,
        logger=logger,
        async_mode=False,
    )
    # robot = None  # 未接続でGUIの読み取り表示を確認する場合
    ##################################################

    manager = RobotVarManager(
        robot_instance=robot,
        autosave=False,
        autoload=False,
        logger=logger,
    )
    model = TeachingModel(
        manager,
        JSON_FILE,
        logger=logger,
        async_mode=False,
    )

    # DeviceProxyに渡したデバイス名で保存先を決定する。
    controller = TeachingController(
        model,
        device_name=device_name,
        logger=logger,
    )
    window = TeachingWindow(controller, JSON_FILE)
    window.show()
    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
