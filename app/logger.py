import logging
import os
from datetime import datetime
from pytz import timezone

tz = timezone('Asia/Taipei')
dir_path = './app/log/'  # 設定 logs 目錄
filename = datetime.strftime(datetime.now().astimezone(tz), '%Y%m%d_%H%M%S') + '.log'  # 設定檔名


def create_logger():
    # config
    logging.captureWarnings(True)  # 捕捉 py waring message
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(message)s]')
    logging.Formatter.converter = lambda *args: datetime.now(tz=tz).timetuple()
    my_logger = logging.getLogger('my_logger')  # set logger name to use across modules.
    my_logger.setLevel(logging.INFO)

    # 若不存在目錄則新建
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # file handler
    fileHandler = logging.FileHandler(dir_path + filename, 'w', 'utf-8')
    fileHandler.setFormatter(formatter)
    my_logger.addHandler(fileHandler)

    # console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)
    my_logger.addHandler(consoleHandler)

    return my_logger

