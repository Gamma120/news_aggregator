import logging
import os

# TODO : make path Linux compatible

PRJCT_DIR = os.getcwd() # FIXME : maybe broken if not executed in the right folder
PRJCT_LOGS = os.path.join(PRJCT_DIR,'logs')
PRJCT_RSS = os.path.join(PRJCT_DIR,'rss_src')
PRJCT_TMP = os.path.join(PRJCT_DIR,'tmp')
PRJCT_SRC = os.path.join(PRJCT_DIR,'src')
PRJCT_TEST_SRC = os.path.join(PRJCT_SRC,'tests_src')

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

  
def set_logger(logger_name, log_file, mode='a', level=logging.DEBUG):
    l = logging.getLogger(logger_name)
    format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    fileHandler = logging.FileHandler(log_file, mode=mode)
    
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(level)
    l.setLevel(level)
    l.addHandler(fileHandler)
    
# TODO : create xml item