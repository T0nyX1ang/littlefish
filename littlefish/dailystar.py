"""
Fetch the information of the daily star.

The information includes:
The user information of the daily star.

The command is automatically invoked at 00:01:30 +- 30s everyday.
The command requires to be invoked in groups.
"""

import nonebot
import traceback
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._mswar.api import get_daily_star
from littlefish._mswar.references import sex_ref
from littlefish._policy import check, boardcast

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler


def format_daily_star(daily_star_info: dict):
    """Format the message of daily star."""
    line = [
        '联萌每日一星:',
        '%s (Id: %d) %s' % (
            daily_star_info['nickname'],
            daily_star_info['uid'], sex_ref[daily_star_info['sex']]
        ),
        '局面信息: %.3fs / %.3f' % (
            daily_star_info['time'], daily_star_info['bvs']
        ),
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


dailystar = on_command(cmd='dailystar', aliases={'今日之星', '联萌每日一星'},
                       rule=check('dailystar'))


@dailystar.handle()
async def dailystar(bot: Bot, event: Event, state: dict):
    """Handle the dailystar command."""
    daily_star_info = await get_daily_star()
    await bot.send(event=event, message=format_daily_star(daily_star_info))


@scheduler.scheduled_job('cron', hour=0, minute=1, second=15,
                         misfire_grace_time=30)
@boardcast('dailystar')
async def _(allowed: list):
    """Scheduled dailystar boardcast at 00:03:00."""
    daily_star = await get_daily_star()
    message = format_daily_star(daily_star)
    for bot_id, group_id in allowed:
        try:
            bot = nonebot.get_bots()[bot_id]
            await bot.send_group_msg(group_id=int(group_id),
                                     message=message)
        except Exception:
            logger.error(traceback.format_exc())
