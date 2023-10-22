"""
Fetch the information of the daily star.

The information includes:
The user information of the daily star.
The dailystar information is automatically fetched on every trigger.
"""

import time
import traceback

import nonebot
from nonebot.log import logger
from nonebot_plugin_alconna import on_alconna, Alconna, Args, Arparma

from littlefish._db import load, save
from littlefish._mswar.api import get_daily_star
from littlefish._mswar.references import sex_ref
from littlefish._policy.rule import broadcast, check


def format_daily_star(daily_star_info: dict) -> str:
    """Format the message of daily star."""
    # use f-string
    line = [
        "联萌每日一星:", f"{daily_star_info['nickname']} (Id: {daily_star_info['uid']}) {sex_ref[daily_star_info['sex']]}",
        f"局面信息: {daily_star_info['time']:.3f}s / {daily_star_info['bvs']:.3f}"
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


def _load_daily_star(uid: str) -> list:
    """Load the daily star from database."""
    star_db = load('0', 'dailystar', {})
    try:
        return star_db[uid]
    except Exception:
        return []


def _save_daily_star(uid: str):
    """Save the daily star into database."""
    today = time.strftime('%Y-%m-%d', time.localtime())

    star_db = load('0', 'dailystar', {})

    star_db.setdefault(uid, [])

    if today not in star_db[uid]:
        star_db[uid].append(today)

    save('0', 'dailystar', star_db)


dailystar = on_alconna(Alconna(['dailystar', '联萌每日一星']), rule=check('dailystar'))

dailystar_counter = on_alconna(Alconna(['dailystarcount', '联萌每日一星次数'], Args["uid", int]), rule=check('dailystar'))


@dailystar.handle()
async def _():
    """Handle the dailystar command."""
    daily_star_info = await get_daily_star()
    _save_daily_star(str(daily_star_info['uid']))
    await dailystar.send(message=format_daily_star(daily_star_info))


@dailystar_counter.handle()
async def _(result: Arparma):
    """Handle the dailystar_count command."""
    uid = str(result.uid)
    dailystar_count = _load_daily_star(uid)
    if len(dailystar_count) > 0:
        counts = len(dailystar_count)
        message = f"用户[{uid}]在联萌的每日一星次数: {counts}, 最近{min(counts, 5)}次获得时间为: {', '.join(dailystar_count[-1:-6:-1])}"
        await dailystar_counter.send(message=message)
    else:
        await dailystar_counter.send(message='该用户尚未获得每日一星, 请继续努力~')


@broadcast('dailystar')
async def _(bot_id: str, group_id: str):
    """Scheduled dailystar broadcast."""
    daily_star = await get_daily_star()
    _save_daily_star(str(daily_star['uid']))
    message = format_daily_star(daily_star)

    try:
        bot = nonebot.get_bots()[bot_id]
        await bot.send_group_msg(group_id=int(group_id), message=message)
    except Exception:
        logger.error(traceback.format_exc())
