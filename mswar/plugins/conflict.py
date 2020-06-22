from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
import nonebot

PONG_COUNTER = 0

@on_command('conflict', aliases=('打架', '嘭[CQ:face,id=146]'), permission=SUPERUSER | GROUP, only_to_me=False)
async def conflict(session: CommandSession):
	global PONG_COUNTER
	if PONG_COUNTER < 5:
		PONG_COUNTER += 1
		await session.send('小爆')

@nonebot.scheduler.scheduled_job('cron', hour='0,12', minute=0, second=0, misfire_grace_time=30)
async def _():
	# resuming the counter
	global PONG_COUNTER
	PONG_COUNTER = 0
	logger.info('The PONG counter is resumed now ...')
