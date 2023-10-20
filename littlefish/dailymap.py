"""
Fetch the information of the daily map.

The information includes:
Map: lines, columns, mines, bv, openings, islands.
User: best_time (math.inf) as default.
"""

import traceback

import nonebot
from nonebot import on_fullmatch
from nonebot.log import logger

from littlefish._mswar.api import get_daily_map
from littlefish._policy.rule import broadcast, check


def format_daily_map(daily_map: dict) -> str:
    """Formatter for information."""
    line = [
        "每日一图:", f"{daily_map['row']} 行, {daily_map['column']} 列, {daily_map['mines']} 雷",
        f"{daily_map['bv']} bv, {daily_map['op']} op, {daily_map['is']} is", f"最佳时间: {daily_map['best_time']:.3f}", "大佬们冲鸭!"
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


dailymap = on_fullmatch(msg=('dailymap', '每日一图'), rule=check('dailymap'))


@dailymap.handle()
async def _():
    """Handle the dailymap command."""
    daily_map_info = await get_daily_map()
    await dailymap.send(message=format_daily_map(daily_map_info))


@broadcast('dailymap')
async def _(bot_id: str, group_id: str):
    """Scheduled dailymap broadcast."""
    daily_map = await get_daily_map()
    message = format_daily_map(daily_map)
    try:
        bot = nonebot.get_bots()[bot_id]
        await bot.send_group_msg(group_id=int(group_id), message=message)
    except Exception:
        logger.error(traceback.format_exc())
