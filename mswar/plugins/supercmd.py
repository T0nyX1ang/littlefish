# Commands only for super users. Debug only.

from nonebot import on_startup, on_command, CommandSession
from nonebot.permission import SUPERUSER
from .core import fetch, is_online, is_enabled
from .global_value import *

@on_command('login', aliases=('登录'), permission=SUPERUSER, only_to_me=False)
async def login(session: CommandSession):
    login_result = await login_account()
    await session.send(login_result)

async def login_account() -> str:
    try:
        # reset uid and token when login
        keyring.set_password('mswar-account', 'uid', '')
        keyring.set_password('mswar-account', 'token', '')

        # do the login process
        uid = 'qaqaqaqaq@protonmail.com'
        password_hash = 'e490e35aadd4caf18b92c13907fa5eb9'
        query = 'id=' + quote(uid) + '&password=' + password_hash + '&platform=0'
        credentials = await fetch(page='/MineSweepingWar/user/login', query=query)
        
        # set the credentials
        keyring.set_password('mswar-account', 'uid', uid)
        keyring.set_password('mswar-account', 'token', credentials['data']['token'])
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
        keyring.set_password('mswar-account', 'uid', '')
        keyring.set_password('mswar-account', 'token', '')
        return '登出成功'
    except Exception as e:
        logger.error(traceback.format_exc())
        return '登出失败，请重试'

@on_command('status', aliases=('状态', '账号状态'), permission=SUPERUSER, only_to_me=False)
async def status(session: CommandSession):
    status_result = await get_status()
    await session.send(status_result)

async def get_status() -> str:
    if is_online():
        return '关联账号状态: 已登录'
    else:
        return '关联账号状态: 未登录'

@on_command('debug', aliases=('调试'), permission=SUPERUSER, only_to_me=False)
async def debug(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')
    group_id = session.event['group_id']
    debug_message = await get_debug_message(group_id)
    await session.send(debug_message)

async def get_debug_message(group_id):
    line = []
    line.append('-- 调试信息 --')
    line.append('上条群内消息: %s' % (CURRENT_GROUP_MESSAGE[group_id] if len(CURRENT_GROUP_MESSAGE[group_id]) > 0 else '无'))
    line.append('复读计数器: %d' % (CURRENT_COMBO_COUNTER[group_id]))
    line.append('42点游戏: %s' % ('游玩中' if CURRENT_42_APP[group_id].is_playing() else '未开始'))
    line.append('冷却ID: %s' % (str(CURRENT_ID_COLDING_LIST[group_id]).replace('[', '').replace(']', '') if CURRENT_ID_COLDING_LIST[group_id] else '无'))
    line.append('打架计数器: %d' % (CURRENT_CONFLICT_COUNTER[group_id]))
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()
