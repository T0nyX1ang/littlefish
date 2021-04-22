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
import time
import gzip
import shutil
import json
import traceback
import nonebot
from nonebot.log import logger
from .config import DatabaseConfig

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler
global_config = nonebot.get_driver().config
plugin_config = DatabaseConfig(**global_config.dict())
database_location = os.path.join(os.getcwd(), plugin_config.database_location)
database_compress_level = plugin_config.database_compress_level
database_backup_directory = os.path.join(os.path.dirname(database_location), 'backup')
database_backup_max_storage = plugin_config.database_backup_max_storage
database = {}

logger.info('Loading the database from disk ...')
try:
    with gzip.open(database_location, 'rb', compresslevel=database_compress_level) as f:
        database = json.loads(f.read().decode())
except Exception:
    logger.warning('Failed to load the database, feature limited.')
    logger.info('Creating a empty database on disk ...')
    with gzip.open(database_location, 'wb', compresslevel=database_compress_level) as f:
        f.write(json.dumps(database).encode())

logger.info('Detecting backup directory ...')
if not os.path.isdir(database_backup_directory):
    os.mkdir(database_backup_directory)


def load(universal_id: str, item_name: str) -> json:
    """Load database item."""
    logger.debug(f'Loading item [{item_name}] from database ...')
    database.setdefault(universal_id, {})
    database[universal_id].setdefault(item_name, None)
    return database[universal_id][item_name]


def save(universal_id: str, item_name: str, new_data: json):
    """Save database item."""
    logger.debug(f'Saving item [{item_name}] to database ...')
    database.setdefault(universal_id, {})
    database[universal_id].setdefault(item_name, None)
    database[universal_id][item_name] = new_data


@scheduler.scheduled_job('cron', hour='*/2', minute=30, second=0, misfire_grace_time=30)
async def commit():
    """Commit to the database, saving the file on disk from memory."""
    logger.info('Saving the database to disk ...')

    database_backup = os.path.join(database_backup_directory, '%d.bak' % int(time.time() * 1000000))
    shutil.copyfile(database_location, database_backup)

    backups = os.listdir(database_backup_directory)
    removes = (0 < database_backup_max_storage < len(backups)) * (len(backups) - database_backup_max_storage)
    for i in range(removes):
        os.remove(os.path.join(database_backup_directory, backups[i]))  # remove the redundant files

    try:
        with gzip.open(database_location, 'wb', compresslevel=database_compress_level) as tf:
            tf.write(json.dumps(database, sort_keys=True).encode())
        return True
    except Exception:
        logger.error('Failed to save the database ...')
        logger.error(traceback.format_exc())
        return False
