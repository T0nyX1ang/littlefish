from nonebot import on_natural_language, NLPSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .global_value import CURRENT_GROUP_MESSAGE, CURRENT_COMBO_COUNTER
import traceback

@on_natural_language(permission=SUPERUSER | GROUP, only_short_message=False, only_to_me=False)
async def _ (session: NLPSession):
	if session.event['message_type'] == 'group':
		msg = session.msg
		group_id = session.event['group_id']
		if group_id not in CURRENT_GROUP_MESSAGE:
			CURRENT_GROUP_MESSAGE[group_id] = msg
			CURRENT_COMBO_COUNTER[group_id] = 1
		elif CURRENT_GROUP_MESSAGE[group_id] == msg:
			if CURRENT_COMBO_COUNTER[group_id] < 6:
				CURRENT_COMBO_COUNTER[group_id] += 1
				if CURRENT_COMBO_COUNTER[group_id] == 5:
					await session.send(CURRENT_GROUP_MESSAGE[group_id])
		else:
			CURRENT_GROUP_MESSAGE[group_id] = msg
			CURRENT_COMBO_COUNTER[group_id] = 1
