import logging
import os
import requests

PRJCT_DIR = os.path.abspath('.') # TODO : maybe broken if not executed in the right folder

class RSS_Bot():
    """
    class for RSS fetcher
    """
    
    def __init__(self):
        # Create logger
        self.init_logger()
        
    def init_logger(self):
        # Log file name
        PRJCT_LOG = PRJCT_DIR+r"\logs"       
        filename = PRJCT_LOG+r"\RSS_Bot.log"
        
        # Create logger
        format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=filename,
                            level=logging.DEBUG,
                            format=format)
        
        # Add handler
        # handler = logging.FileHandler(filename=filename)
        # handler.setFormatter(logging.Formatter(format))
        # handler.setLevel(logging.DEBUG)
        # logging.getLogger().addHandler(handler)

    def get_logger(self):
        return logging.getLogger('RSS_Bot_Logger')
    
      
    def start_bot(self):
        logger = self.get_logger()
        logger.info("Bot starting...")
        

        
if __name__ == "__main__":
    rss_bot = RSS_Bot()
    rss_bot.start_bot()