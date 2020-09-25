from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import fetch, check_policy, check_boardcast_policy
from .global_value import CURRENT_ENABLED
import nonebot

async def get_user_level():
    user_level_result = await fetch(page='/MineSweepingWar/rank/timing/level/count')
    level_ref = {0: '-', 1: 'E', 2: 'D', 3: 'C', 4: 'B', 5: 'A', 6: 'S', 7: 'SS', 8: 'SSS', 9: '★', 10: '★★'}
    line = ['等级: 当前 | 合计']
    total = 0
    data = user_level_result['data']
    data.reverse()
    for val in user_level_result['data']:
        total += val['count']
        line.append('%s: %d | %d' % (level_ref[val['level']], val['count'], total))
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()

@on_command('level', aliases=('用户等级'), permission=SUPERUSER | GROUP, only_to_me=False)
async def level(session: CommandSession):
    if not check_policy(session.event, 'level'):
        session.finish('小鱼睡着了zzz~')

    user_level_info = await get_user_level()
    await session.send(user_level_info)

@nonebot.scheduler.scheduled_job('cron', day_of_week=0, hour=0, minute=0, second=0, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    message = await get_user_level()
    try:
        for group_id in CURRENT_ENABLED.keys():
            if CURRENT_ENABLED[group_id] and check_boardcast_policy(group_id, 'level'):
                await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        logger.error(traceback.format_exc())
