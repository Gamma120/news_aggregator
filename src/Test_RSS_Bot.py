import shutil
import pytest
from RSS_Bot import *
from logging import getLogger
from Logger import set_logger

PRJCT_TEST_SRC = PRJCT_DIR+r'\src\tests_src'

@pytest.fixture(autouse=True)
def setup_function():
    path_log = PRJCT_TMP+r'\Test_RSS_Bot.log'   
    # Create logger
    set_logger('Test_RSS_Bot', path_log, 'w')


def test_logger():
    """
    Test the logger
    """
    logger = getLogger('Test_RSS_Bot')
    path_log = PRJCT_TMP+r'\Test_RSS_Bot.log'
    
    info_log = "Info message."
    logger.info(info_log)

    # Open Test_RSS_Bot.log    
    try:
        log_file = open(path_log,'r')
        # Read the last line
        log_msg = log_file.readlines()[-1]
        log_msg = log_msg.split(' - ')
            
        assert len(log_msg) == 3
        assert log_msg[1] == "INFO"
        assert log_msg[2] == info_log+'\n'
        
        log_file.close()
        
    except FileNotFoundError:
        print("[ERROR] File not found :", path_log)            

def test_fetch():
    """
    Test RSS_Bot.fetch()
    """

    path_log = PRJCT_TMP+r'\Test_RSS_Bot.log'
    rss_bot = RSS_Bot()
    # path to source file (test_rss_sources.txt)
    test_rss_sources_path = PRJCT_TEST_SRC+r'\test_rss_sources.txt'
    
    # Run tested function, result in tmp directory
    rss_bot.fetch(test_rss_sources_path, PRJCT_TMP)
    
    # Check the existence of the file
    try:
        ## Get the file name
        test_rss_sources_file = open(test_rss_sources_path,'r')
        log_line = test_rss_sources_file.readline()
        while log_line != "# OK\n":
            log_line = test_rss_sources_file.readline()
        log_line = test_rss_sources_file.readline()
        file_name = log_line.split(';')[1].strip('\n')
        # Test existence
        assert(os.path.exists(PRJCT_TMP+file_name))
    except FileNotFoundError as e:
        print(e)
        
    # Verify the entries in the log file
    ## Compare log level between Test_RSS_Bot.log and test_fetch_res.txt
    try:
        log_file = open(path_log,'r')
        res_file = open(PRJCT_TEST_SRC+r'\test_fetch_res.txt','r')
    except FileNotFoundError as e:
        print(e)
    else :
        for log_line in log_file:
            res_line = res_file.readline().strip('\n')
            log_line = log_line.split(' - ')
            assert log_line[1] == res_line
    finally:
        if log_file != None:
            log_file.close()
        if res_file != None:
            res_file.close()
    
    # Rerun fetch to assert the creation of .new
    rss_bot.fetch(test_rss_sources_path, PRJCT_TMP)
    # Test existence
    assert(os.path.exists(PRJCT_TMP+file_name+'.new'))
    
         
#def test_xml_diff():