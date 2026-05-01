from colorlog import ColoredFormatter
from logging import handlers
from pathlib import Path
import colorlog
import logging
import sys

def setup_logger(name_file):
    logger_folder_path = Path(__file__).parent.resolve() / "logger"
    logger_folder_path.mkdir(parents=True, exist_ok=True)
    color_formater = ColoredFormatter(
        "%(light_black)s[%(asctime)s] %(log_color)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG" : "white",
            "INFO" : "cyan",
            "WARNING": "yellow",
            "ERROR" : "red",
        },
    )
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger_format = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    logger_file = logging.handlers.TimedRotatingFileHandler(filename=f"{logger_folder_path / name_file}.log", when='midnight', backupCount=7)
    logger_file.setFormatter(logger_format)

    logger.addHandler(logger_file)

    console_logger = colorlog.StreamHandler(sys.stdout)
    console_logger.setFormatter(color_formater)
    logger.addHandler(console_logger)