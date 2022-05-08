import os
import requests
from inspect import currentframe, getframeinfo
from logging import exception, getLogger
from Logger import set_logger

# TODO : make path Linux compatible

PRJCT_DIR = os.path.abspath('.') # FIXME : maybe broken if not executed in the right folder
PRJCT_LOGS = PRJCT_DIR+r'\logs'

class RSS_Bot():
    """
    class for RSS fetcher
    """
    
    def __init__(self):
        """
        Initialise the logger and create log folder
        """
        
        # Create log folder
        if not os.path.exists(PRJCT_LOGS):
            os.mkdir(PRJCT_LOGS)
        # path to RSS_Bot.log
        path_log = PRJCT_LOGS+r"\RSS_Bot.log"
        # Create logger
        set_logger('RSS_Bot', path_log)
        
        
    def fetch(self,path_src_file: str):
        """
        Fetch RSS flux from RSS_sources file
        """
        
        logger = self.get_logger()
        try:
            rss_sources = open(path_src_file,'r')
            logger.info("Begin fetching...")
            
            cpt_line = 1 # To track line number for easier error message
            for line in rss_sources:
                # Ignore empty and comment lines
                if line[0] != "\n" and line[0] != "#":
                    line = line.split(';')
                    # Check formating in the file
                    xml_url = line[0]
                    xml_file = line[1].strip('\n')
                    try:
                        r = requests.get(xml_url)
                        if r.status_code != 200:
                            logger.warning("Unable to fetch data from "+xml_url+' '+str(r.status_code))
                            logger.debug('File: '+path_src_file+', line '+str(cpt_line))
                        else:
                            open(PRJCT_DIR+r'\rss_src\\'+xml_file,'wb').write(r.content)

                    except requests.HTTPError as e:
                        logger.warning(e)
                        logger.debug('File: '+path_src_file+', line '+str(cpt_line))
                    except requests.Timeout as e:
                        logger.warning(e)
                        logger.debug('File: '+path_src_file+', line '+str(cpt_line))
                    except requests.ConnectionError as e:
                        logger.warning(e)
                        logger.debug('File: '+path_src_file+', line '+str(cpt_line))
                    except FileNotFoundError as e:
                        logger.error("Wrong formating in "+path_src_file+', line '+str(cpt_line))
                        logger.error(e)
                    except requests.exceptions.MissingSchema as e:
                        logger.error("Wrong formating in "+path_src_file+', line '+str(cpt_line))
                        logger.error(e)
                cpt_line+=1
                    
        except FileNotFoundError as e:
            logger.error(e)
                    
        finally:
            rss_sources.close()
            logger.info("Fetch completed.")
        
    
    def get_logger(self):
        # Change the logger if it's a test
        if __name__ != '__main__':
            return getLogger('Test_RSS_Bot')
        else:
            return getLogger('RSS_Bot')
    
    
    
    def start_bot(self):
        logger = self.get_logger()
        logger.info("Bot starting...")
        
        # fetch files in rss_sources
        self.fetch(PRJCT_DIR+r"\rss_sources.txt")
        

        
if __name__ == "__main__":
    rss_bot = RSS_Bot()
    rss_bot.start_bot()