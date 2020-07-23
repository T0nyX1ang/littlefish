# Commands only for super users. Debug only.

from nonebot import on_startup, on_command, CommandSession
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from urllib.parse import quote, unquote
from .core import fetch, is_online, is_enabled
from .global_value import *
import json

def save_global_keys():
    ready_to_save = json.dumps(GLOBAL_KEYS, indent=4)
    with open(GLOBAL_KEYS_PATH, 'w') as f:
        f.write(ready_to_save)

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
