import logging
import os
from loguru import logger

class CustomFormatter(logging.Formatter):
    """ Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override', if it exists.
    2. Overrides 'filename' with the value of 'file_name_override', if it exists.
    """

    def format(self, record):
        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        return super(CustomFormatter, self).format(record)


def get_logger_old(log_file_name, log_sub_dir=""):
    """ Creates a Log File and returns Logger object """
    log_file_name = log_file_name.split('.')[0]
    windows_log_dir = 'c:\\logs_dir\\'
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    linux_log_dir = os.path.join(base_path,"logs")

    # Build Log file directory, based on the OS and supplied input
    log_dir = windows_log_dir if os.name == 'nt' else linux_log_dir
    log_dir = os.path.join(log_dir, log_sub_dir)

    # Create Log file directory if not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Build Log File Full Path
    logPath = log_file_name if os.path.exists(log_file_name) else os.path.join(log_dir, (str(log_file_name) + '.log'))

    # Create logger object and set the format for logging and other attributes
    logger = logging.Logger(log_file_name)
    # logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(logPath, 'a+')
    handler.setLevel(logging.ERROR)
    """ Set the formatter of 'CustomFormatter' type as we need to log base function name and base file name """
    handler.setFormatter(CustomFormatter('%(asctime)s  %(levelname)-10s  %(filename)s  %(funcName)s  %(message)s'))
    logger.addHandler(handler)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatter('%(levelname)s:     %(asctime)s    %(filename)s  %(funcName)s  %(message)s'))
    logger.addHandler(ch)
    # Return logger object
    return logger

def get_logger(log_file_name):
    logger.add(f'/tmp/{log_file_name}.log',rotation="10 MB", level="ERROR")
    return logger

