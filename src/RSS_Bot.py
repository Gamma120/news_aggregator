import os
import requests
from logging import getLogger
from utils import *
import xml.etree.ElementTree as ET


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
        # path to RSS_Bot.log
        log_path = os.path.join(PRJCT_LOGS,'RSS_Bot.log')
        # Create logger
        set_logger('RSS_Bot', log_path)
        
        
    def fetch(self,src_path: str, dest_dir: str):
        """
        Fetch RSS flux from RSS_sources file
        """
        
        logger = self.get_logger()
        try:
            rss_sources = open(src_path,'r')
            # To keep track of the fetched files for future merge
            fetched_file = open(os.path.join(PRJCT_TMP,'fetched_files.txt'),'w')
            
            logger.info("Begin fetch...")
            
            cpt_line = 1 # To track line number for easier error message
            for line in rss_sources:
                # Ignore empty and comment lines
                if line[0] != "\n" and line[0] != "#":
                    line = line.split(';')
                    # Check formating in the file
                    if len(line)!=2:
                        logger.error("Wrong formating in "+src_path+', line '+str(cpt_line))
                    else:
                        xml_url = line[0]
                        xml_file_name = line[1].strip('\n')
                        if xml_url=='' or xml_file_name=='':
                            logger.error("Wrong formating in "+src_path+', line '+str(cpt_line))
                        # Request the file
                        else:
                            try:
                                r = requests.get(xml_url)
                            except (requests.HTTPError,
                                    requests.Timeout,
                                    requests.exceptions.TooManyRedirects) as e:
                                logger.warning(e)
                                logger.debug('File: '+src_path+', line '+str(cpt_line))
                            except (requests.ConnectionError,
                                    requests.exceptions.InvalidURL) as e:
                                logger.error(e)
                                logger.debug('File: '+src_path+', line '+str(cpt_line))
                            
                            else :
                                if r.status_code != 200:
                                    logger.warning("Unable to fetch data from "+xml_url+' '+str(r.status_code))
                                    logger.debug('File: '+src_path+', line '+str(cpt_line))
                                else:
                                    xml_path = os.path.join(dest_dir,xml_file_name)
                                    # if the file exist, create a up to date copy 
                                    # that will be merge later with the old one
                                    if os.path.exists(xml_path):
                                        xml_path+='.new'
                                    open(xml_path,'wb').write(r.content)
                                    fetched_file.write(xml_path+'\n')
                cpt_line+=1
            rss_sources.close()
            logger.info("Fetch completed.")
                    
        except FileNotFoundError as e:
            logger.error(e)


    def xml_diff(self, xml_old: str, xml_new: str):
        """
        Create a RSS flux containing only items appearing in xml_new
        """
        
        logger = self.get_logger()
        
        # Parse the xml file into a tree
        ## documentation https://docs.python.org/3/library/xml.etree.elementtree.html
        try:
            old_tree = ET.parse(xml_old)
            old_root = old_tree.getroot()
            new_tree = ET.parse(xml_new)
            new_root = new_tree.getroot()
        except ET.ParseError as e: # catch if the file is not in xml format
            logger.warning(e)
        
        old_items = old_root.find('channel').findall('item')
        new_items = new_root.find('channel').findall('item')
        
        # serie of condition if xlm don't have items
        if len(old_items)<1 and len(new_items)<1:
            logger.error('Files: '+xml_old+' and '+xml_new+' does not contain any item.')
        elif len(old_items)<1 or len(new_items)<1:
            if len(old_items)<1:
                # replace old file by the new one and add post attribut
                logger.warning('File: '+xml_old+' does not contain any item.')
                for item in new_items:
                    item.set('post','yes')
                new_tree.write(xml_old)
            else:
                # conserve old file and add attribut to not post
                logger.warning('File: '+xml_new+' does not contain any item.')
                for old_item in old_items:
                    old_item.set('post','no')
                    old_tree.write(xml_old)
        else:
            # compare titles in the new xml file with the first title in the old one
            old_title = old_items[0].find('title').text
            i=0
            while i<len(new_items)-1 and new_items[i].find('title').text != old_title:
                # add an attribut to inform the discord bot to publish it
                new_items[i].set('post','yes')
                i+=1
            
            # if their is new item(s)
            if i!=0: 
                for j in range(i,len(new_items)):
                    new_root.find('channel').remove(new_items[j]) # delete old item(s) in the new xlm
                
                # Replace old file   
                new_tree.write(xml_old) 
            else:
                # add an attribut to inform the discord bot to not publish it
                for old_item in old_items:
                    old_item.set('post','no')
                old_tree.write(xml_old)
        os.remove(xml_new)
    
    def merge(self, fetched_files_path: str):
        """
        Merge old and new xml files

        Args:
            fetched_files_path (str): path to the file populated during fetch
        """
        
        logger = self.get_logger()
        
        # Read path of the most recent fetched files
        try:
            fetched_files = open(fetched_files_path,'r')
        except FileNotFoundError as e:
            logger.error(e)
        else:
            logger.info("Begin merge...")
            cpt_line=0 # for logging debug
            for line in fetched_files:
                line = line.strip('\n')
                line = line.split('.')
                # if it's a .new file, call xml_diff
                if len(line)==3 and line[2]=='new':
                    xml_old = line[0]+'.'+line[1]
                    xml_new = xml_old+'.'+line[2]
                    self.xml_diff(xml_old,xml_new)
                # if it's a .xml file make items attribut post=yes
                elif len(line)==2 and line[1]=='xml':
                    xml_path = line[0]+'.'+line[1]
                    if not os.path.exists(xml_path):
                        logger.error("File not found: "+xml_path)
                        logger.debug("File: "+fetched_files_path+', line '+str(cpt_line))
                    tree = ET.parse(xml_path)
                    root = tree.getroot()
                    channel = root.find('channel')
                    for item in channel.findall('item'):
                        item.set('post','yes')
                    tree.write(xml_path)
                cpt_line+=1
            fetched_files.close()
            logger.info("Merge completed.")
            
    def get_logger(self):
        # Change the logger if it's a test
        if __name__ != '__main__':
            return getLogger('Test_RSS_Bot')
        else:
            return getLogger('RSS_Bot')
    
    
    
    def start_bot(self):
        logger = self.get_logger()
        logger.info("Bot starting...")
        
        # Fetch files in rss_sources
        self.fetch(os.path.join(PRJCT_DIR,'rss_sources.txt'), PRJCT_RSS)
        self.merge(os.path.join(PRJCT_TMP,'fetched_files.txt'))
        

        
if __name__ == "__main__":
    rss_bot = RSS_Bot()
    rss_bot.start_bot()