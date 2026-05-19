import PyInstaller.__main__ as pyinstall
from logger import setup_logger
from pathlib import Path
import logging

setup_logger(__name__)
logger = logging.getLogger(__name__)

def getPath():
    logger.debug("Getting path...")
    base_path = Path(__file__).parent.resolve()
    logger.info(f"Successfully got path({base_path})")

    logger.info("Getting path to main file...")
    main_path = str(base_path / "main.py")
    logger.info(f"Successfully got path({main_path})")

    logger.info("Getting path to icon...")
    icon_path = str(base_path / "assets" / "icons" / "icon.ico")
    logger.info(f"Successfully got path({icon_path})")
    input("Press any key to start creating application...")
    getApp(base_path, icon_path, main_path)

def getApp(base_path, icon_path, main_path):
    logger.info("Creating application...")
    pyinstall.run([
        "--noconfirm",
        "--onefile",
        "--console",
        "--icon",
        icon_path,
        "--name", 
        "DiscordAutoSender",
        main_path
    ])
    
if __name__ == "__main__":
    getPath()
    input("Press any key to close app...")
    exit()