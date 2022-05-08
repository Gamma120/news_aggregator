import os
import requests
from logging import getLogger
from Logger import set_logger

# TODO : make path Linux compatible

PRJCT_DIR = os.path.abspath('.') # FIXME : maybe broken if not executed in the right folder
PRJCT_LOGS = PRJCT_DIR+r'\logs'

class RSS_Bot():
    """
    class for RSS fetcher
    """
    
    def __init__(self):
        # Create log folder
        if not os.path.exists(PRJCT_LOGS):
            os.mkdir(PRJCT_LOGS)
        # path to RSS_Bot.log
        path_log = PRJCT_LOGS+r"\RSS_Bot.log"
        # Create logger
        set_logger('RSS_Bot', path_log)
        
    def fetch(self,src_file: str):
        """
        Fetch RSS flux from RSS_sources file
        """
        
        logger = self.get_logger()
        path_rss_sources = src_file
        try:
            rss_sources = open(path_rss_sources,'r')
            logger.info("Begin fetching...")
            
            for line in rss_sources:
                # Ignore empty and comment lines
                if line != "\n" and line[0] != "#":
                    line = line.split(';')
                    xml_url = line[0]
                    xml_file = line[1].strip('\n')
                    try:
                        r = requests.get(xml_url)
                        if r.status_code != 200:
                            logger.warning("Unable to fetch data from "+xml_url+' '+str(r.status_code))
                        else:
                            open(PRJCT_DIR+r'\rss_src\\'+xml_file,'wb').write(r.content)
                            
                    except requests.HTTPError:
                        logger.warning("Unable to fetch data from "+xml_url+' '+str(r.status_code))
                    except requests.Timeout:
                        logger.warning("Connexion timeout from "+xml_url)
                    except requests.ConnectionError:
                        logger.warning("A Connection error occurred.")
                    
        except FileNotFoundError:
            logger.error("File not found : "+path_rss_sources)
        
        logger.info("Fetch completed.")
        
    
    def get_logger(self):
        return getLogger('RSS_Bot')
    
    
    
    def start_bot(self):
        logger = self.get_logger()
        logger.info("Bot starting...")
        
        # fetch files in rss_sources
        self.fetch(PRJCT_DIR+r"\rss_sources.txt")
        

        
if __name__ == "__main__":
    rss_bot = RSS_Bot()
    rss_bot.start_bot()