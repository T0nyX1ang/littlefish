from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import fetch, is_enabled
from .info import get_user_info, format_user_info
from .global_value import CURRENT_ENABLED
import nonebot
import traceback

async def get_daily_star():
    daily_star = await fetch(page='/MineSweepingWar/minesweeper/record/get/star')
    daily_star_id = daily_star['data']['user']['id']
    name = ' ' * 20 + str(daily_star_id)
    user_info = await get_user_info(name)
    user_info_message = '联萌每日一星:\n' + format_user_info(user_info)
    return user_info_message

@on_command('dailystar', aliases=('今日之星', '联萌每日一星'), permission=SUPERUSER | GROUP, only_to_me=False)
async def dailystar(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    daily_star_message = await get_daily_star()
    await session.send(daily_star_message)

@nonebot.scheduler.scheduled_job('cron', hour=0, minute=4, second=30, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    message = await get_daily_star()
    try:
        for group_id in CURRENT_ENABLED.keys():
            if CURRENT_ENABLED[group_id]:
                await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        logger.error(traceback.format_exc())
