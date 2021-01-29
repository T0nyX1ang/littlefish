"""
A database module which handles internal data flows.

The database is created on disk, using JSON format. The database contains
two types: global and local. The global database can be used by all bots,
but the local database can be only used by a certain bot in a certain group.
A universal ID is used for the database, the ID is generated by bot_id,
group_id (in local databases) or '0' (in global databases).

This module contains three public methods to be used:
load: load the data from the database. (The data should be json compatible)
save: save the data to the database. (The data should be json compatible)
commit: save the database on disk. This module is invoked every two hours.
"""

import os
import shutil
import json
import nonebot
import traceback
from nonebot.log import logger
from .config import Config

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler
global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())
database_location = os.path.join(os.getcwd(), plugin_config.database_location)
database_backup = f'{database_location}.bak'
database = {}

logger.info('Loading the database from disk ...')
try:
    with open(database_location, 'r') as f:
        database = json.loads(f.read())
except Exception:
    logger.warning('Failed to load the database, feature limited.')


def _initialize(universal_id: str, item_name: str):
    """Initialize the database."""
    logger.info(f'Initialize item [{item_name}] from database ...')
    if universal_id not in database:
        database[universal_id] = {}

    if item_name not in database[universal_id]:
        database[universal_id][item_name] = None


def load(universal_id: str, item_name: str) -> json:
    """Load database item."""
    logger.info(f'Loading item [{item_name}] from database ...')
    try:
        return database[universal_id][item_name]
    except Exception:
        _initialize(universal_id, item_name)
        return None


def save(universal_id: str, item_name: str, new_data: json):
    """Save database item."""
    logger.info(f'Saving item [{item_name}] to database ...')
    try:
        database[universal_id][item_name] = new_data
    except Exception:
        _initialize(universal_id, item_name)
        logger.error(traceback.format_exc())


@scheduler.scheduled_job('cron', hour='*/2', minute=30, second=0,
                         misfire_grace_time=30)
def commit():
    """Commit to the database, saving the file on disk from memory."""
    logger.info('Saving the database to disk ...')
    shutil.copyfile(database_location, database_backup)

    try:
        with open(database_location, 'w') as f:
            f.write(json.dumps(database))
    except Exception:
        logger.error('Failed to save the database ...')
        logger.error(traceback.format_exc())