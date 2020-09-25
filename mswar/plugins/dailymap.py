from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import fetch, check_policy, check_boardcast_policy
from .mswar import get_board, get_board_result
from .global_value import CURRENT_ENABLED
import nonebot
import math
import traceback

def format_daily_map(daily_map: dict) -> str:
    line = [
        '每日一图:',
        '%d 行, %d 列, %d 雷' % (daily_map['row'], daily_map['column'], daily_map['mines']),
        '%d bv, %d op, %d is' % (daily_map['bv'], daily_map['op'], daily_map['is']),
        '最佳时间: %.3f' % (daily_map['best_time']),
        '大佬们冲鸭!'
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()

async def get_daily_map() -> str:
    daily_map_result = await fetch(page='/MineSweepingWar/minesweeper/daily/map/today')
    daily_map_board = get_board(daily_map_result['data']['map']['map'].split('-')[0: -1])
    daily_map = get_board_result(daily_map_board)
    daily_map['id'] = daily_map_result['data']['mapId']

    query = 'mapId=%d&page=0&count=1' % (daily_map['id'])
    daily_map_highest_result = await fetch(page='/MineSweepingWar/rank/daily/list', query=query)
    if daily_map_highest_result['data']:
        daily_map['best_time'] = daily_map_highest_result['data'][0]['time'] / 1000
    else:
        daily_map['best_time'] = math.inf
    return daily_map

@on_command('dailymap', aliases=('每日一图'), permission=SUPERUSER | GROUP, only_to_me=False)
async def dailymap(session: CommandSession):
    if not check_policy(session.event, 'dailymap'):
        session.finish('小鱼睡着了zzz~')

    daily_map_info = await get_daily_map()
    daily_map_message = format_daily_map(daily_map_info)
    await session.send(format_daily_map(daily_map_info))

@nonebot.scheduler.scheduled_job('cron', hour=0, minute=3, second=0, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    daily_map = await get_daily_map()
    message = format_daily_map(daily_map)
    try:
        for group_id in CURRENT_ENABLED.keys():
            if CURRENT_ENABLED[group_id] and check_boardcast_policy(group_id, 'dailymap'):
                await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        logger.error(traceback.format_exc())
