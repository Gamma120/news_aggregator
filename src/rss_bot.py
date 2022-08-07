import os
import requests
import xml.etree.ElementTree as ET

from src.utils import *

class RSS_Bot():
    """
    class for RSS fetcher
    """
    
    def fetch(self,rows_list: list[dict], dest_dir: str) -> list[dict]:
        """
        Fetch RSS flux from rows to fetch in database
        
        Returns:
            List of rows fetched
        """
        
        logger = get_logger()
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
                    logger.info("Fetched "+file_name+" from "+url)

        logger.info("Fetch completed.")
        return fetched_list


    def xml_strip(self, xml_path: str, stop_title: str = None):
        """
        Strip items in xml file from stop_title item
        """
        
        logger = get_logger()
        
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
    
    def get_items(self, xml_path: str) -> list[dict]:
        """
        Format items in xml file to a list of dictionnaries

        Args:
            xml_path (str): path to the xml file

        Returns:
            list[dict]: list of items in dictionnary\n
            example : [{title:'title',url:'url'}]
        """
        
        logger = get_logger()
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e: # catch if the file is not in xml format
            logger.error(f"On file {xml_path}: {e}")
        else:
            channel = root.find('channel')
            items_list = []
            items = channel.findall('item')
            for item in items:
                item_dict = {}
                for child in item:
                    if child.tag in "title|description|link":
                        if child.text != None:
                            item_dict[child.tag] = child.text
                items_list.append(item_dict)
            return items_list