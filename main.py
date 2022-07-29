import sys
import os
from dotenv import load_dotenv

if __name__ == '__main__' :
    load_dotenv()
    # set the environ as not TEST
    os.environ["TEST"] = "false"
    
    from src.utils import set_logger
    from src.utils import set_directories
    from src.utils import PRJCT_LOGS
    from src import discord_bot

    set_directories()
    log_path = os.path.join(PRJCT_LOGS,'news_aggregator.log')
    set_logger('News_aggregator', log_path)
    sys.exit(discord_bot.run())