import os
import requests
from logging import getLogger
import xml.etree.ElementTree as ET

from .utils import *

class RSS_Bot():
    """
    class for RSS fetcher
    """
    
    def __init__(self):
        """
        Initialise the logger and create directories
        """
        # Create directories
        set_directories()
        # path to log file
        log_path = os.path.join(PRJCT_LOGS,'new_aggregator.log')
        # Create logger
        set_logger('RSS_Bot', log_path)
        
        
    def fetch(self,rows_list: list[dict], dest_dir: str) -> list[dict]:
        """
        Fetch RSS flux from rows to fetch in database
        
        Returns:
            List of rows fetched
        """
        
        logger = self.get_logger()
        logger.info("Begin fetch...")
        fetched_list=[]
        for rss_flux in rows_list:
            url = rss_flux['url']
            file_name = rss_flux['file_name']
            try:
                r = requests.get(url)
            except (requests.HTTPError,
                    requests.Timeout,
                    requests.exceptions.TooManyRedirects) as e:
                logger.warning(e)
                logger.debug(rss_flux)
            except (requests.ConnectionError,
                    requests.exceptions.InvalidURL) as e:
                logger.error(e)
                logger.debug(rss_flux)
            
            else :
                if r.status_code != 200:
                    logger.warning("Unable to fetch data from "+url+' '+str(r.status_code))
                    logger.debug(rss_flux)
                else:
                    xml_path = os.path.join(dest_dir,file_name)
                    open(xml_path,'wb').write(r.content)
                    fetched_list.append(rss_flux)

        logger.info("Fetch completed.")
        return fetched_list


    def xml_strip(self, xml_path: str, stop_title: str = None):
        """
        Strip items in xml file from stop_title item
        """
        
        logger = self.get_logger()
        
        if not stop_title == None:
            # Parse the xml file into a tree
            ## documentation https://docs.python.org/3/library/xml.etree.elementtree.html
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
            except ET.ParseError as e: # catch if the file is not in xml format
                logger.warning(e)

            items = root.find('channel').findall('item')
            # error if file is empty
            if len(items)<1:
                logger.error('File: '+xml_path+' does not contain any item.')
            else:
                i=0
                # Reach the item with stop_title Title attribut
                while i<len(items)-1 and items[i].find('title').text != stop_title:
                    i+=1
                # Delete the rest of the items
                for j in range(i,len(items)):
                    root.find('channel').remove(items[j])

                # Replace file
                tree.write(xml_path)
    
    # TODO : no longer relevant
    def get_logger(self):
        # Change the logger if it's a test
        if __name__ != '__main__':
            return getLogger('Test_RSS_Bot')
        else:
            return getLogger('RSS_Bot')