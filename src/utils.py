import os
import logging
from datetime import timedelta, datetime

PRJCT_DIR = os.getcwd() # FIXME : maybe broken if not executed in the right folder
PRJCT_LOGS = os.path.join(PRJCT_DIR,'logs')
PRJCT_RSS = os.path.join(PRJCT_DIR,'rss_src')
PRJCT_TMP = os.path.join(PRJCT_DIR,'tmp')
PRJCT_SRC = os.path.join(PRJCT_DIR,'src')
PRJCT_TEST = os.path.join(PRJCT_DIR,'tests')
PRJCT_TEST_SRC = os.path.join(PRJCT_TEST,'tests_src')
PRJCT_DB = os.path.join(PRJCT_DIR,'database')

def set_directories():
        # Create rss_src folder
        if not os.path.exists(PRJCT_RSS):
            os.mkdir(PRJCT_RSS)
        # Create log folder
        if not os.path.exists(PRJCT_LOGS):
            os.mkdir(PRJCT_LOGS)
        # Create tmp folder
        if not os.path.exists(PRJCT_TMP):
            os.mkdir(PRJCT_TMP)
        # Create database folder
        if not os.path.exists(PRJCT_DB):
            os.mkdir(PRJCT_DB)

  
def set_logger(logger_name: str, log_file_path: str, mode='a', level=logging.DEBUG):
    l = logging.getLogger(logger_name)
    format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    fileHandler = logging.FileHandler(log_file_path, mode=mode)
    
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(level)
    l.setLevel(level)
    l.addHandler(fileHandler)

def get_logger():
    test = os.environ["TEST"]
    if(test != "0"):
        return logging.getLogger("News_aggregator")
    else:
        return logging.getLogger("Test")

def name_to_file(name: str) -> str:
    return "".join(x for x in name if x.isalnum() or x in " _-").lower().replace(' ','_')

def date_to_int(date: datetime) -> int:
    return date.timestamp()

def timedelta_to_int(delta: timedelta) -> int:
    return delta.total_seconds()