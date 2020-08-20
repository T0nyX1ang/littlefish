# Commands only for super users.

from nonebot import on_startup, on_command, CommandSession, scheduler
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from urllib.parse import quote, unquote
from .core import fetch, is_online, is_enabled
from .global_value import *
import shutil
import nonebot
import json
import traceback

def save_global_keys():
    with open(GLOBAL_KEYS_PATH, 'wb') as f:
        f.write(PRIMARY_ENCRYPT(json.dumps(GLOBAL_KEYS)))

def save_local_data(group_id):
    group_hash = hashlib.sha3_256(PRIMARY_PASSWORD + str(group_id).encode()).hexdigest()
    database_path = os.path.join(LOCAL_DATABASE_PATH, '%s.dat') % (group_hash)
    database_backup = os.path.join(LOCAL_DATABASE_PATH, '%s.bak') % (group_hash)
    
    # First backup the former database
    shutil.copyfile(database_path, database_backup)
    
    # Then write the latter database
    database = {
        'group_message': CURRENT_GROUP_MESSAGE[group_id], 
        'group_message_increment': CURRENT_GROUP_MESSAGE_INCREMENT[group_id],
        'combo_counter': CURRENT_COMBO_COUNTER[group_id], 
        'group_members': CURRENT_GROUP_MEMBERS[group_id], 
        'conflict_counter': CURRENT_CONFLICT_COUNTER[group_id],
        '42_probability_list': CURRENT_42_PROB_LIST[group_id]
    }
    with open(database_path, 'wb') as f:
        f.write(PRIMARY_ENCRYPT(json.dumps(database, sort_keys=True)))

@on_command('login', aliases=('登录'), permission=SUPERUSER, only_to_me=False)
async def login(session: CommandSession):
    login_result = await login_account()
    await session.send(login_result)

async def login_account() -> str:
    try:
        # do the login process
        uid = GLOBAL_KEYS['connected_uid']
        password_hash = GLOBAL_KEYS['connected_hash']
        query = 'id=' + quote(uid) + '&password=' + password_hash + '&platform=0'
        credentials = await fetch(page='/MineSweepingWar/user/login', query=query)
        
        # set the credentials
        GLOBAL_KEYS['connected_token'] = credentials['data']['token']
        save_global_keys()
        return '登录成功'
    except Exception as e:
        logger.error(traceback.format_exc())
        return '登录失败，请重试'

@on_command('logout', aliases=('登出', '退出登录'), permission=SUPERUSER, only_to_me=False)
async def logout(session: CommandSession):
    logout_result = await logout_account()
    await session.send(logout_result)

async def logout_account() -> str:
    try:
        # reset uid and token when logout
        GLOBAL_KEYS['connected_token'] = ""
        save_global_keys()
        return '登出成功'
    except Exception as e:
        logger.error(traceback.format_exc())
        return '登出失败，请重试'

@on_command('debug', aliases=('调试'), permission=SUPERUSER, only_to_me=False)
async def debug(session: CommandSession):
    if session.event['message_type'] == 'group':
        group_id = session.event['group_id']
        debug_message = await get_debug_message(group_id)
        await session.send(debug_message)

async def get_debug_message(group_id):
    line = []
    line.append('-- 调试信息 --')
    line.append('关联账号: %s' % ('已登录' if is_online() else '未登录'))
    if group_id in CURRENT_ENABLED:
        line.append('小鱼状态: %s' % ('已启动' if CURRENT_ENABLED[group_id] else '未启动'))
        line.append('上条群内消息: %s' % (CURRENT_GROUP_MESSAGE[group_id] if len(CURRENT_GROUP_MESSAGE[group_id]) > 0 else '无'))
        line.append('增量复读消息: %s' % (CURRENT_GROUP_MESSAGE_INCREMENT[group_id] if len(CURRENT_GROUP_MESSAGE_INCREMENT[group_id]) > 0 else '空'))
        line.append('复读计数器: %d' % (CURRENT_COMBO_COUNTER[group_id]))
        line.append('42点游戏: %s' % ('游玩中' if CURRENT_42_APP[group_id].is_playing() else '未开始'))
        line.append('冷却ID: %s' % (str(CURRENT_ID_COLDING_LIST[group_id]).replace('[', '').replace(']', '') if CURRENT_ID_COLDING_LIST[group_id] else '无'))
        line.append('打架计数器: %d' % (CURRENT_CONFLICT_COUNTER[group_id]))
    else:
        line.append('小鱼状态: %s' % ('未初始化'))
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()

@on_command('save', aliases=('存档'), permission=SUPERUSER, only_to_me=False)
async def save(session: CommandSession):
    if session.event['message_type'] == 'group':
        group_id = session.event['group_id']
        save_message = await get_save_message(group_id) 
        await session.send(save_message)

async def get_save_message(group_id):
    try:
        save_local_data(group_id)
        return '存档成功'
    except Exception as e:
        logger.error(traceback.format_exc())
        return '存档失败，请重试'

@nonebot.scheduler.scheduled_job('cron', hour='*/2', minute=0, second=0, misfire_grace_time=30)
async def _():
    try:
        logger.info('Saving data to disk ...')
        for group_id in CURRENT_ENABLED.keys():
            save_local_data(group_id)
    except Exception as e:
        logger.error(traceback.format_exc())
