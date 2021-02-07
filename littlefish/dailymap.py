"""
Fetch the information of the daily map.

The information includes:
Map: lines, columns, mines, bv, openings, islands.
User: best_time (math.inf) as default.

The command is automatically invoked at 00:03:00 +- 30s everyday.
The command requires to be invoked in groups.
"""

import nonebot
import traceback
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._mswar.api import get_daily_map
from littlefish._policy import check, boardcast, empty

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler


def format_daily_map(daily_map: dict) -> str:
    """Formatter for information."""
    line = [
        '每日一图:',
        '%d 行, %d 列, %d 雷' %
        (daily_map['row'], daily_map['column'], daily_map['mines']),
        '%d bv, %d op, %d is' %
        (daily_map['bv'], daily_map['op'], daily_map['is']),
        '最佳时间: %.3f' % (daily_map['best_time']), '大佬们冲鸭!'
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


dailymap = on_command(cmd='dailymap', aliases={'每日一图'},
                      rule=check('dailymap') & empty())


@dailymap.handle()
async def dailymap(bot: Bot, event: Event, state: dict):
    """Handle the dailymap command."""
    daily_map_info = await get_daily_map()
    await bot.send(event=event, message=format_daily_map(daily_map_info))


@scheduler.scheduled_job('cron', hour=0, minute=3, second=0,
                         misfire_grace_time=30)
@boardcast('dailymap')
async def _(allowed: list):
    """Scheduled dailymap boardcast at 00:03:00."""
    daily_map = await get_daily_map()
    message = format_daily_map(daily_map)
    for bot_id, group_id in allowed:
        try:
            bot = nonebot.get_bots()[bot_id]
            await bot.send_group_msg(group_id=int(group_id),
                                     message=message)
        except Exception:
            logger.error(traceback.format_exc())
