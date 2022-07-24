from datetime import datetime
from time import sleep
import pytest
import os
from logging import getLogger

from src.database import *
from src.utils import *

db_path = os.path.join(PRJCT_TMP,'test.db')
os.environ["TEST"] = "0"

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

@pytest.fixture()
def rss_dicts() -> list[dict]:
    dict_1 = {'name': 'test_name_1', 'url': 'test_url_1', 'channel': 'test_channel', 'update_rate': timedelta_to_int(timedelta(seconds=1))}
    dict_2 = {'name': 'test_name_2', 'url': 'test_url_2', 'update_rate': timedelta_to_int(timedelta(seconds=5))}
    dict_3 = {'name': 'test_name_3', 'url': 'test_url_1', 'channel': 'test_channel_2', 'update_rate': timedelta_to_int(timedelta(hours=1))}
    return dict_1, dict_2, dict_3
    
def test_init():
    """
    Test the initialisation of the database
    """
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    assert os.path.exists(db_path)
    
    table_list = db.get_table_list()
    assert len(table_list)==2
    assert table_list == ['rss_flux', 'channels_filters']
    
    rss_flux = db.get_table('rss_flux')
    assert  rss_flux != None
    columns = db.get_column_list('rss_flux')
    assert len(columns) == 8
    assert columns == ['id', 'name', 'file_name', 'url', 'channel', 'last_item', 'last_time_fetched', 'update_rate']
    
    channels_filters = db.get_table('channels_filters')
    assert channels_filters != None
    columns = db.get_column_list('channels_filters')
    assert len(columns) == 3
    assert columns == ['id', 'filter', 'channel']

# TODO : test_uniqueConstraint
   
def test_add_rss_flux(rss_dicts):
    """
    Test to insert a row in rss_flux table
    """
    
    db = Database(db_path)
    # Test: add a first entry
    db.add_rss_flux(rss_dicts[0], 'arg_channel')
    rss_flux = db.get_rss_row({'name': 'test_name_1', 'channel': 'test_channel'})
    assert len(rss_flux) == 8
    assert rss_flux['channel'] == 'test_channel'
    
    # Test: add a second entry with channel=None
    db.add_rss_flux(rss_dicts[1], 'arg_channel')
    rss_list = db.get_rss_flux_list()
    assert len(rss_list) == 2
    assert rss_list == ['test_name_1', 'test_name_2']
    ## check the name of the channel
    rss_flux = db.get_rss_row({'name': 'test_name_2', 'channel': 'arg_channel'})
    assert rss_flux['channel'] == 'arg_channel'

def test_remove_rss_flux(rss_dicts):
    """
    Test to delete a row in rss_flux table
    """
    
    db = Database(db_path)
    
    # Test the supression of a row in a table of one
    rss_dict = {'name': 'test_name', 'url': 'test_url', 'channel': 'test_channel', 'update_rate': timedelta_to_int(timedelta(hours=1))}
    db.add_rss_flux(rss_dict)
    db.remove_rss_flux('test_name', 'test_channel')
    rss_list = db.get_rss_flux_list()
    assert len(rss_list) == 0
    
    # Test the supression of a row in a table with multiple rows
    db.add_rss_flux(rss_dicts[0])
    db.add_rss_flux(rss_dicts[1], 'test_channel')
    db.add_rss_flux(rss_dicts[2])
    db.remove_rss_flux('test_name_2', 'test_channel')
    rss_list = db.get_rss_flux_list()
    assert len(rss_list) == 2
    assert rss_list == ['test_name_1', 'test_name_3']

def test_get_rss_list(rss_dicts):
    db = Database(db_path)
    
    # Populate database
    db.add_rss_flux(rss_dicts[0])
    db.add_rss_flux(rss_dicts[1], 'test_channel')
    db.add_rss_flux(rss_dicts[2])
    
    # Get all entries with channel=test_channel
    rss_list = db.get_rss_flux_list('test_channel')
    assert len(rss_list) == 2
    assert rss_list == ['test_name_1', 'test_name_2']
    
    # Get all entries in the table rss_flux 
    rss_list_all = db.get_rss_flux_list()
    assert len(rss_list_all) == 3
    
def test_get_row(rss_dicts):
    """
    Test to get a row from name and channel columns
    """
    
    db = Database(db_path)
    # Populate the table
    rss_dict_1 = rss_dicts[0]
    rss_dict_2 = rss_dicts[1]
    db.add_rss_flux(rss_dict_1)
    db.add_rss_flux(rss_dict_2, 'arg_channel')
    # Test: get the rows
    rss_dict_1.update({'id': 1, 'last_time_fetched': None, 'file_name': 'test_name_1.xml', 'last_item': None})
    rss_dict_2.update({'id': 2, 'channel': 'arg_channel', 'last_time_fetched': None, 'file_name': 'test_name_2.xml', 'last_item': None})
    rss_dict_1_res = db.get_rss_row(rss_dict_1)
    rss_dict_2_res = db.get_rss_row(rss_dict_2)
    for key in rss_dict_1.keys(): # assumption: same keys between dictionnaries
        assert rss_dict_1_res[key] == rss_dict_1[key]
        assert rss_dict_2_res[key] == rss_dict_2[key]

def test_edit_rss_flux(rss_dicts):
    """
    Test editing a row in rss_flux table
    """

    db = Database(db_path)
    # Populate the table
    rss_dict = rss_dicts[0]
    db.add_rss_flux(rss_dict)
    # Test : edit row in rss_flux
    db.edit_rss_flux('test_name_1', 'test_channel', {'channel': 'test_channel_edit', 'url': 'test_url_edit', 'update_rate': timedelta_to_int(timedelta(days=2))})
    ## update the channel in the old copy for accurate result from get_rss_row
    rss_dict.update({'channel': 'test_channel_edit'})
    rss_dict_res = db.get_rss_row(rss_dict)
    ## the answer
    rss_dict_ans = {'id': 1, 'name': 'test_name_1', 'file_name': 'test_name_1.xml', 'url': 'test_url_edit', 'channel': 'test_channel_edit', 'last_item': None, 'last_time_fetched': None, 'update_rate': timedelta_to_int(timedelta(days=2))}
    for key in rss_dict_ans.keys(): # assumption: same keys between dictionnaries
        assert rss_dict_res[key] == rss_dict_ans[key]

def test_to_fetch(rss_dicts):
    """
    Test fetch()
    """
    
    db = Database(db_path)
    rss_dict_1 = rss_dicts[0]
    rss_dict_2 = rss_dicts[1]
    # Test where both should be in the list, because last_time_fetched is None
    db.add_rss_flux(rss_dict_1)
    db.add_rss_flux(rss_dict_2, "test_channel")
    ## update old entries to become answers 
    rss_dict_1.update({'id': 1, 'file_name': 'test_name_1.xml', 'last_item':None, 'last_time_fetched':None})
    rss_dict_2.update({'id': 2, 'channel': 'test_channel', 'file_name': 'test_name_2.xml', 'last_item':None, 'last_time_fetched':None})
    ## sleep 2 seconds > to timedelta of first row,
    ## but < to timedelta of seconde row
    sleep(2)
    fetch_list = db.to_fetch()
    assert len(fetch_list) == 2
    for key in rss_dict_1.keys(): # assumption: same keys between dictionnaries
        assert fetch_list[0][key] == rss_dict_1[key]
        assert fetch_list[1][key] == rss_dict_2[key]
    
    # Test where only the first should be in the list
    ## Edit entries last_time_fetch to change behaviour
    now = date_to_int(datetime.utcnow())
    ## Update old entry to become answer
    rss_dict_1.update({'last_time_fetched': now})
    db.edit_rss_flux('test_name_1','test_channel',{'last_time_fetched': now})
    db.edit_rss_flux('test_name_2','test_channel',{'last_time_fetched': now})
    sleep(2)
    fetch_list = db.to_fetch()
    assert len(fetch_list) == 1
    for key in rss_dict_1.keys(): # assumption: same keys between dictionnaries
        assert fetch_list[0][key] == rss_dict_1[key]
        
def test_valid_line():
    db = Database(db_path)
    
    line_1 = "test_name;https://test.com"
    assert db.valid_line(line_1,"test_path",0) == True
    
    line_2 = "# comment"
    assert db.valid_line(line_2,"test_path",0) == False
    
    line_3 = ";"
    assert db.valid_line(line_3,"test_path",0) == False
    
    line_4 = "test_name"
    assert db.valid_line(line_4,"test_path",0) == False

def test_import_list():
    db = Database(db_path)
    
    src_path = os.path.join(PRJCT_TEST_SRC,"test_rss_sources.txt")
    db.import_list_rss(src_path, "test_channel")
    rss_list = db.get_rss_flux_list()
    assert len(rss_list) == 3
    assert rss_list == ["Google index","Google idex","zafeazhkf"]

def test_export_list(rss_dicts):
    db = Database(db_path)
    
    # Populate the database
    db.add_rss_flux(rss_dicts[0])
    db.add_rss_flux(rss_dicts[1], 'test_channel')
    db.add_rss_flux(rss_dicts[2])
    
    # Test
    file_name = "RSS-"+datetime.strftime(datetime.utcnow(),'%Y-%m-%d')+'.csv'
    db.export_list_rss(file_name)
    
    # Assert creation
    file_path = os.path.join(PRJCT_TMP,file_name)
    assert os.path.exists(file_path)
    