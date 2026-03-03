from colorlog import ColoredFormatter
import colorlog
import logging
import sys

def setup_logger(name_file):
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

    logger_file = logging.FileHandler(filename=f"{name_file}.log", mode='w')
    logger_file.setFormatter(logger_format)

    logger.addHandler(logger_file)

    console_logger = colorlog.StreamHandler(sys.stdout)
    console_logger.setFormatter(color_formater)
    logger.addHandler(console_logger)