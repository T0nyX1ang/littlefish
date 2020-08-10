from nonebot import on_startup, on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP_ADMIN
from apscheduler.triggers.date import DateTrigger
from ftptsgame import FTPtsGame
from .core import fetch, is_online, is_enabled
from .global_value import *
import os
import sys
import json
import hashlib
import nonebot
import traceback

async def update_group_members(bot, group_id):
    group_members_list = await bot.get_group_member_list(group_id=group_id)
    for member in group_members_list:
        group_member_info = await bot.get_group_member_info(group_id=group_id, user_id=member['user_id'])
        user_id = str(group_member_info['user_id'])
        if user_id not in CURRENT_GROUP_MEMBERS[group_id]:
            CURRENT_GROUP_MEMBERS[group_id][user_id] = {}
        CURRENT_GROUP_MEMBERS[group_id][user_id]['id'] = group_member_info['title']
        CURRENT_GROUP_MEMBERS[group_id][user_id]['nickname'] = group_member_info['nickname']
        CURRENT_GROUP_MEMBERS[group_id][user_id]['card'] = group_member_info['card']
        if '42score' not in CURRENT_GROUP_MEMBERS[group_id][user_id]:
            CURRENT_GROUP_MEMBERS[group_id][user_id]['42score'] = 0
        if 'restricted' not in CURRENT_GROUP_MEMBERS[group_id][user_id]:
            CURRENT_GROUP_MEMBERS[group_id][user_id]['restricted'] = False

@on_command('enable', aliases=('启动', '启动机器人'), permission=SUPERUSER | GROUP_ADMIN, only_to_me=False)
async def enable(session: CommandSession):
    if not is_online():
        session.finish('请登录关联账号')

    if is_enabled(session.event):
        session.finish()

    group_id = session.event['group_id']
    group_hash = hashlib.sha3_256(PRIMARY_PASSWORD + str(group_id).encode()).hexdigest()
    database_path = os.path.join(LOCAL_DATABASE_PATH, '%s.dat') % (group_hash)

    if os.path.isfile(database_path): # preserving state when the bot is shut
        with open(database_path, 'rb') as f:
            database = json.loads(PRIMARY_DECRYPT(f.read()))
    else: # default database
        database = {
            'group_message': '', 
            'combo_counter': 0, 
            'group_members': {}, 
            'conflict_counter': 0
        }
        with open(database_path, 'wb') as f:
            f.write(PRIMARY_ENCRYPT(json.dumps(database)))

    if group_id not in CURRENT_ENABLED: 
        CURRENT_GROUP_MESSAGE[group_id] = database['group_message']
        CURRENT_COMBO_COUNTER[group_id] = database['combo_counter']
        CURRENT_42_APP[group_id] = FTPtsGame()
        CURRENT_GROUP_MEMBERS[group_id] = database['group_members']
        CURRENT_ID_COLDING_LIST[group_id] = []
        CURRENT_CONFLICT_COUNTER[group_id] = database['conflict_counter']

    CURRENT_ENABLED[group_id] = True

    await update_group_members(session.bot, group_id)
    await session.send('小鱼已启动，内核版本 v0.8.0 ~')

@on_command('disable', aliases=('关闭', '关闭机器人'), permission=SUPERUSER | GROUP_ADMIN, only_to_me=False)
async def disable(session: CommandSession):
    if not is_enabled(session.event):
        session.finish()

    group_id = session.event['group_id']
    CURRENT_ENABLED[group_id] = False
    await session.send('小鱼已关闭')

@nonebot.scheduler.scheduled_job('cron', hour='11,23', minute=0, second=0, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    try:
        for group_id in CURRENT_ENABLED.keys():
            if CURRENT_ENABLED[group_id]:
                logger.info('Updating group members database ...')
                await update_group_members(session.bot, group_id)
    except Exception as e:
        logger.error(traceback.format_exc())
