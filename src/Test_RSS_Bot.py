from RSS_Bot import *
from logging import getLogger
from Logger import set_logger

# FIXME : curently not working with pytest

def test_logger():
    """
    Test if the logger add a line in the log file
    """
    
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

    # path to test_rss_sources.txt
    path_test_rss_sources = PRJCT_DIR+r'\src\tests_src\test_rss_sources.txt'
    # Test
    rss_bot.fetch(path_test_rss_sources)
    
    ## Verify the entries in the log file
    # Compare log level between Test_RSS_Bot.log and test_fetch_res.txt
    try:
        log_file = open(path_log,'r')
        res_file = open(PRJCT_DIR+r'\src\tests_src\test_fetch_res.txt','r')
        for line in log_file:
            res_line = res_file.readline().strip('\n') # get rid of \n
            line = line.split(' - ')
            assert line[1] == res_line  
    
    except FileNotFoundError as e:
        print(e)
    finally:
        log_file.close()


if __name__ == '__main__':
    # Create tmp folder
    PRJCT_TMP = PRJCT_DIR+r'\tmp'
    if not os.path.exists(PRJCT_TMP):
        os.mkdir(PRJCT_TMP)
    
    rss_bot = RSS_Bot()
    # Create logger
    path_log = PRJCT_TMP+r'\Test_RSS_Bot.log'
    set_logger('Test_RSS_Bot', path_log, 'w')
    logger = getLogger('Test_RSS_Bot')
    
    #Tests
    logger.info('Begin Tests...')
    test_logger()
    test_fetch()
    logger.info('End Tests...')