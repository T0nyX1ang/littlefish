"""
Fetch the information of the daily star.

The information includes:
The user information of the daily star.
The dailystar information is automatically fetched on every trigger.

The command requires to be invoked in groups.
"""

import time
import traceback
import nonebot
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._exclaim import exclaim_msg
from littlefish._mswar.api import get_daily_star
from littlefish._mswar.references import sex_ref
from littlefish._policy.rule import check, broadcast
from littlefish._policy.plugin import on_simple_command
from littlefish._db import load, save


def format_daily_star(daily_star_info: dict) -> str:
    """Format the message of daily star."""
    line = [
        '联萌每日一星:',
        '%s (Id: %d) %s' % (daily_star_info['nickname'], daily_star_info['uid'], sex_ref[daily_star_info['sex']]),
        '局面信息: %.3fs / %.3f' % (daily_star_info['time'], daily_star_info['bvs']),
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


def _load_daily_star(uid: str) -> list:
    """Load the daily star from database."""
    star_db = load('0', 'dailystar')
    try:
        return star_db[uid]
    except Exception:
        return []


def _save_daily_star(uid: str):
    """Save the daily star into database."""
    today = time.strftime('%Y-%m-%d', time.localtime())

    star_db = load('0', 'dailystar')
    if not star_db:
        star_db = {}

    star_db.setdefault(uid, [])

    if today not in star_db[uid]:
        star_db[uid].append(today)

    save('0', 'dailystar', star_db)


dailystar = on_simple_command(cmd='dailystar', aliases={'今日之星', '联萌每日一星'}, rule=check('dailystar'))

dailystar_counter = on_command(cmd='dailystarcount ', aliases={'联萌每日一星次数 '}, rule=check('dailystar'))


@dailystar.handle()
async def show_dailystar(bot: Bot, event: Event, state: dict):
    """Handle the dailystar command."""
    daily_star_info = await get_daily_star()
    _save_daily_star(str(daily_star_info['uid']))
    await bot.send(event=event, message=format_daily_star(daily_star_info))


@dailystar_counter.handle()
async def show_dailystar_count(bot: Bot, event: Event, state: dict):
    """Handle the dailystar_count command."""
    try:
        uid = str(int(str(event.message).strip()))
    except Exception:
        await bot.send(event=event, message=exclaim_msg('', '3', False, 1))
        return

    dailystar_count = _load_daily_star(uid)
    if len(dailystar_count) > 0:
        message = '用户[%s]在联萌的每日一星次数: %d, 最近%d次获得时间为: %s' % (uid, len(dailystar_count), min(len(dailystar_count), 5), ', '.join(
            dailystar_count[-1:-6:-1]))
        await bot.send(event=event, message=message)
    else:
        await bot.send(event=event, message='该用户尚未获得每日一星, 请继续努力~')


@broadcast('dailystar')
async def dailystar_broadcast(bot_id: str, group_id: str):
    """Scheduled dailystar broadcast."""
    daily_star = await get_daily_star()
    _save_daily_star(str(daily_star['uid']))
    message = format_daily_star(daily_star)

    try:
        bot = nonebot.get_bots()[bot_id]
        await bot.send_group_msg(group_id=int(group_id), message=message)
    except Exception:
        logger.error(traceback.format_exc())
