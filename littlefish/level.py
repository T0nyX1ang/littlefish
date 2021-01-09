"""
Fetch the infomation of the level status.

The information includes:
The number of people in each rank.

The command is automatically invoked at 00:00:00 +- 30s weekly.
The command requires to be invoked in groups.
"""

import nonebot
import traceback
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._netcore import fetch
from littlefish._policy import check, boardcast
from littlefish._mswar.references import level_ref
from littlefish._db import load, save

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler
min_level, max_level = 1, max(level_ref)
level = on_command(cmd='level', aliases={'用户等级'}, rule=check('level'))


def _initialize_history():
    """Initialize the user level data."""
    return {level_ref[lv]: 0 for lv in range(min_level, max_level + 1)}


async def get_user_level():
    """Get the level information from the remote server."""
    user_level_result = await fetch(
        page='/MineSweepingWar/rank/timing/level/count')
    data = user_level_result['data']

    # reconstruct the data from list to dict
    user_level_data = _initialize_history()
    for val in data:
        user_level_data[level_ref[val['level']]] = val['count']

    return user_level_data


def format_user_level(data):
    """Format the user level info data."""
    line = ['等级: 当前 | 合计']
    total, history_total = 0, 0
    user_level_history = load('0', 'level_history')
    if not user_level_history:
        # create default value for history
        user_level_history = _initialize_history()

    for lv in range(max_level, min_level - 1, -1):
        ref = level_ref[lv]  # global reference
        total += data[ref]
        history_total += user_level_history[ref]
        line.append('%s: %d(%+d) | %d(%+d)' % (
            ref,
            data[ref], data[ref] - user_level_history[ref],
            total, total - history_total)
        )
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


@level.handle()
async def level(bot: Bot, event: Event, state: dict):
    """Handle the level command."""
    user_level_data = await get_user_level()
    await bot.send(event=event, message=format_user_level(user_level_data))


@scheduler.scheduled_job('cron', day_of_week=0, hour=0, minute=0, second=0,
                         misfire_grace_time=30)
@boardcast('level')
async def _(allowed: list):
    """Scheduled level boardcast at 00:00:00(weekly)."""
    user_level_data = await get_user_level()
    message = format_user_level(user_level_data)
    save('0', 'level_history', user_level_data)

    for bot_id, group_id in allowed:
        bot = nonebot.get_bots()[bot_id]
        try:
            await bot.send_group_msg(group_id=int(group_id), message=message)
        except Exception:
            logger.error(traceback.format_exc())
