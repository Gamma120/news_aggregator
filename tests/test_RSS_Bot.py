import pytest
import os
from src.database import Database
from src.rss_bot import *
from logging import getLogger
from src.utils import *

db_path = os.path.join(PRJCT_TMP,'test.db')

@pytest.fixture(autouse=True)
def setup_function():
    # Create directories
    set_directories()
    path_log = os.path.join(PRJCT_TMP,'Test.log')   
    # Create logger
    set_logger('Test', path_log, 'w')
    yield
    # remove database
    if os.path.exists(db_path):
        os.remove(db_path)
    logging.shutdown()

def test_logger():
    """
    Test the logger
    """
    logger = getLogger('Test')
    path_log = os.path.join(PRJCT_TMP,'Test.log')
    
    info_log = "Info message."
    logger.info(info_log)

    # Open Test.log    
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
    
    rss_bot = RSS_Bot()
    # path to source file (test_rss_sources.txt)
    test_rss_sources_path = os.path.join(PRJCT_TEST_SRC,'test_rss_sources.txt')
    
    #
    db = Database(db_path)
    db.import_list(test_rss_sources_path,"test_channel")
    fetch_list = db.to_fetch()
    # Run tested function, result in tmp directory
    fetched_list = rss_bot.fetch(fetch_list, PRJCT_TMP)
    ## Test return of the function
    assert len(fetched_list) == 1
    
    # Check the existence of the file
    try:
        ## Open source file
        test_rss_sources_file = open(test_rss_sources_path,'r')
    except FileNotFoundError as e:
        print(e)
    else:
        log_line = test_rss_sources_file.readline()
        # Get the line with valid url
        while log_line != "# OK\n":
            log_line = test_rss_sources_file.readline()
        log_line = test_rss_sources_file.readline()
        name = log_line.split(';')[0].strip('\n')
        file_name = name_to_file(name) + '.xml'
        # Test existence
        assert(os.path.exists(os.path.join(PRJCT_TMP,file_name)))
        # Test return of function
        assert fetch_list[0]['file_name'] == file_name  
    
def build_xml(file_path: str, nb_item: int):
    """
    Build xml for test_xml_diff()
    """
    root = ET.Element('rss')
    channel = ET.SubElement(root,'channel')
    for i in range(nb_item):
        item = ET.SubElement(channel,'item')
        title = ET.SubElement(item,'title')
        link = ET.SubElement(item,'link')
        description = ET.SubElement(item,'description')
        
        title.text = 'Title '+str(nb_item-i)
        link.text = 'https://example.com'
        description.text = 'Description of item '+str(nb_item-i)
        
    tree = ET.ElementTree(root)
    tree.write(file_path)
             
def test_xml_strip():
    """
    Test RSS_Bot.xml_strip()
    """
    
    # Path for the tmp xml files
    test_xml_path = os.path.join(PRJCT_TMP,'test_xml.xml')
    
    # Build xml files
    nb_item = 4
    build_xml(test_xml_path, nb_item)
    
    # Run tested function
    rss_bot = RSS_Bot()
    rss_bot.xml_strip(test_xml_path, "Title 2")
    
    # Check the result
    tree = ET.parse(test_xml_path)
    channel = tree.getroot().find('channel')
    items = channel.findall('item')
    ## Check if the number of items is correct
    assert len(items) == 2
    ## Check each title
    for i in range(len(items)):
        title = items[i].find('title')
        assert title.text == "Title "+str(nb_item-i)

    # Test with same items
    nb_item = 2
    build_xml(test_xml_path, nb_item)
    rss_bot.xml_strip(test_xml_path, "Title 2")
    
    tree = ET.parse(test_xml_path)
    items = tree.getroot().find('channel').findall('item')
    assert len(items) == 0
    
    # Test with no item
    build_xml(test_xml_path,0)
    rss_bot.xml_strip(test_xml_path,"Title 2")
    
    tree = ET.parse(test_xml_path)
    channel = tree.getroot().find('channel')
    items = channel.findall('item')
    
    # Test with stop_title=None
    build_xml(test_xml_path,1)
    rss_bot.xml_strip(test_xml_path)

    tree = ET.parse(test_xml_path)
    channel = tree.getroot().find('channel')
    items = channel.findall('item')
    assert len(items) == 1
