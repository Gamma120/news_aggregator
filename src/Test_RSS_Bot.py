from random import randint
from RSS_Bot import *

# TODO : curently not working with pytest

def test_logger():
    rss_bot = RSS_Bot()
    logger = rss_bot.get_logger()
    # Add some randomness to check if it's the right log
    salt = randint(0,1000)
    info_log = "Info message "+str(salt)
    logger.info(info_log)
    
    # Open log file
    PRJCT_LOG = PRJCT_DIR + r"\logs"
    filename = PRJCT_LOG+r"\RSS_Bot.log"
    try:
        log_file = open(filename,'r')
        # Read the last line
        log_msg = log_file.readlines()[-1]
        log_msg = log_msg.split(' - ')
        
        assert len(log_msg) == 3
        assert log_msg[1] == "INFO"
        assert log_msg[2] == info_log+'\n'
        
        log_file.close()
        
    except FileNotFoundError:
        print("[ERROR] File not found :", filename)            

if __name__ == '__main__':      
    test_logger()  