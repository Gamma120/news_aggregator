from logging import getLogger
from time import sleep
from datetime import datetime,timedelta,timezone

from src.utils import *

os.environ["TEST"] = "0"

def test_name_to_file():
    string_1 = "String0 String-String_String\n"
    assert name_to_file(string_1) == "string0_string-string_string"
    
def test_date_to_file():
    # Test conversion datetime to float
    ## epoch : 1970-1-1 0:0:0
    date = datetime(1970,1,3,tzinfo=timezone.utc)
    date = date_to_int(date)
    ## function return = date - epoch = 2 days
    assert date == 3600*24*2

def test_delate_to_int():
    # Basic test for 1 hour
    delta_1 = timedelta(hours=1)
    delta_1 = timedelta_to_int(delta_1)
    assert delta_1 == 3600
    
    # Test for 1 millisecond
    delta_2 = timedelta(milliseconds=1)
    delta_2 = timedelta_to_int(delta_2)
    assert delta_2 == 0.001
    
def test_time_delta():
    # Test for last_time_fetched + update_rate >= now
    date = datetime.utcnow()
    date = date_to_int(date)
    ## hypotetical update_rate
    delta = timedelta(days=1)
    delta = timedelta_to_int(delta)
    
    ## now + 23h
    date_2 = datetime.utcnow() + timedelta(hours=23)
    date_2 = date_to_int(date_2)
    
    assert date + delta >= date_2
    
    sleep(0.2) # just to be sure
    date_3 = datetime.utcnow() + timedelta(days=1)
    date_3 = date_to_int(date_3)
    assert date + delta <= date_3

def test_log():
    log_path = os.path.join(PRJCT_TMP,'Test.log')
    set_logger('Test',log_path)
    logger = getLogger('Test')
    logger.info("Test info")