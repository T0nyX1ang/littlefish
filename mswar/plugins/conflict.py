from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import check_policy
from .global_value import CURRENT_CONFLICT_COUNTER, CURRENT_ENABLED
import nonebot

@on_command('conflict', aliases=('打架', '嘭[CQ:face,id=146]'), permission=SUPERUSER | GROUP, only_to_me=False)
async def conflict(session: CommandSession):
    if not check_policy(session.event, 'conflict'):
        session.finish()

    group_id = session.event['group_id']
    if CURRENT_CONFLICT_COUNTER[group_id] < 5:
        CURRENT_CONFLICT_COUNTER[group_id] += 1
        await session.send('小爆')

@on_command('response', aliases=('小鱼哥哥你来啦[CQ:face,id=111]', '我来玩啦！！！'), permission=SUPERUSER | GROUP, only_to_me=False)
async def conflict(session: CommandSession):
    if not check_policy(session.event, 'conflict'):
        session.finish()
    await session.send('小爆妹妹好鸭[CQ:face,id=111]')

@on_command('weirdhappy', aliases=('你在哈哈啥呢'), permission=SUPERUSER | GROUP, only_to_me=False)
async def weirdhappy(session: CommandSession):
    if not check_policy(session.event, 'conflict'):
        session.finish()
    await session.send('那咋回事呢')

@nonebot.scheduler.scheduled_job('cron', hour='0,12', minute=0, second=0, misfire_grace_time=30)
async def _():
    for group_id in CURRENT_ENABLED.keys():
        if CURRENT_ENABLED[group_id]:
            CURRENT_CONFLICT_COUNTER[group_id] = 0
    logger.info('The PONG counter is resumed now ...')
