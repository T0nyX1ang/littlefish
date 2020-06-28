from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
import nonebot
import traceback

PONG_COUNTER = {}

@on_command('conflict', aliases=('打架', '嘭[CQ:face,id=146]'), permission=SUPERUSER | GROUP, only_to_me=False)
async def conflict(session: CommandSession):
    global PONG_COUNTER
    if session.event['message_type'] == 'group':
        group_id = session.event['group_id']
        if group_id not in PONG_COUNTER:
            PONG_COUNTER[group_id] = 0
        if PONG_COUNTER[group_id] < 5:
            PONG_COUNTER[group_id] += 1
            await session.send('小爆')

@nonebot.scheduler.scheduled_job('cron', hour='0,12', minute=0, second=0, misfire_grace_time=30)
async def _():
    global PONG_COUNTER
    for key in PONG_COUNTER.keys():
        PONG_COUNTER[key] = 0
    logger.info('The PONG counter is resumed now ...')
