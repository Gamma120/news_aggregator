import pytest
import os
from rss_bot import *
from logging import getLogger
from utils import *

@pytest.fixture(autouse=True)
def setup_function():
    # Create directories
    set_directories()
    path_log = os.path.join(PRJCT_TMP,'Test_RSS_Bot.log')   
    # Create logger
    set_logger('Test_RSS_Bot', path_log, 'w')
    yield
    logging.shutdown()

def test_logger():
    """
    Test the logger
    """
    logger = getLogger('Test_RSS_Bot')
    path_log = os.path.join(PRJCT_TMP,'Test_RSS_Bot.log')
    
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

    path_log = os.path.join(PRJCT_TMP,'Test_RSS_Bot.log')
    rss_bot = RSS_Bot()
    # path to source file (test_rss_sources.txt)
    test_rss_sources_path = os.path.join(PRJCT_TEST_SRC,'test_rss_sources.txt')
    
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
        assert(os.path.exists(os.path.join(PRJCT_TMP,file_name)))
    except FileNotFoundError as e:
        print(e)
        
    # Verify the entries in the log file
    ## Compare log level between Test_RSS_Bot.log and test_fetch_res.txt
    log_file=None
    res_file=None
    try:
        log_file = open(path_log,'r')
        res_file = open(os.path.join(PRJCT_TEST_SRC,'test_fetch_res.txt'),'r')
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
    assert(os.path.exists(os.path.join(PRJCT_TMP,file_name+'.new')))
    
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
             
def test_xml_diff():
    """
    Test RSS_Bot.xml_diff()
    """
    
    # Path for the tmp xml files
    test_xml_path = os.path.join(PRJCT_TMP,'test_xml.xml')
    test_xml_new_path = os.path.join(PRJCT_TMP,'test_xml_new.xml')
    
    # Build xml files
    nb_item = 2
    nb_item_new = 4
    build_xml(test_xml_path, nb_item)
    build_xml(test_xml_new_path, nb_item_new)

    
    # Run tested function
    rss_bot = RSS_Bot()
    rss_bot.xml_diff(test_xml_path, test_xml_new_path)
    
    # Check existence of new file
    assert(not os.path.exists(test_xml_new_path))
    
    # Check the result
    tree = ET.parse(test_xml_path)
    channel = tree.getroot().find('channel')
    items = channel.findall('item')
    
    ## Check if the number of item is correct
    assert len(items) == nb_item_new-nb_item
    ## Check each title
    for i in range(len(items)):
        title = items[i].find('title')
        assert title.text == "Title "+str(nb_item_new-i)
        ## Check the attribut on the first item
        assert items[i].get('post') == 'yes'
        
           
    # Test with same items
    nb_item = 2
    build_xml(test_xml_path, nb_item)
    build_xml(test_xml_new_path, nb_item)
    rss_bot.xml_diff(test_xml_path, test_xml_new_path)
    
    tree = ET.parse(test_xml_path)
    items = tree.getroot().find('channel').findall('item')
    ## The file should be the same with attribut to not post
    assert len(items) == 2
    for item in items:
        assert item.get('post') == 'no'
    
    # Tests with no item
    build_xml(test_xml_path,0)
    build_xml(test_xml_new_path,1)
    
    rss_bot.xml_diff(test_xml_path,test_xml_new_path)
    tree = ET.parse(test_xml_path)
    channel = tree.getroot().find('channel')
    items = channel.findall('item')
    assert len(items) == 1
    assert items[0].get('post') == 'yes'
    
    build_xml(test_xml_path,1)
    build_xml(test_xml_new_path,0)
    
    rss_bot.xml_diff(test_xml_path,test_xml_new_path)
    tree = ET.parse(test_xml_path)
    channel = tree.getroot().find('channel')
    items = channel.findall('item')
    assert len(items) == 1
    assert items[0].get('post') == 'no'

def test_merge():
    """ 
    Test RSS_Bot.merge()
    """
    
    test_xml_path = os.path.join(PRJCT_TMP,'test_xml.xml')
    test_xml_new_path = os.path.join(PRJCT_TMP,'test_xml_new.xml')
    
    # Test with only one file
    ## Create the xml to test
    build_xml(test_xml_path,2)
    ## Simulate the inscription of it fetch in the fetched file
    fetched_path = os.path.join(PRJCT_TMP,'test_fetched_file.txt')
    try:
        fetched_file = open(fetched_path,'w')
        fetched_file.write(test_xml_path)
        fetched_file.close()
    except FileNotFoundError as e:
        print(e)
    else:
        ## Run tested function
        rss_bot = RSS_Bot()
        rss_bot.merge(fetched_path)
        
        ## Verify attributs of items
        tree = ET.parse(test_xml_path)
        channel = tree.getroot().find('channel')
        for item in channel.findall('item'):
            assert item.get('post') == 'yes'
    
