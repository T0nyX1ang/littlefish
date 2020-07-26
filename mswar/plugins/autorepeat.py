from nonebot import on_natural_language, NLPSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from .global_value import CURRENT_GROUP_MESSAGE, CURRENT_COMBO_COUNTER
from .core import is_enabled
import random

@on_natural_language(permission=SUPERUSER | GROUP, only_short_message=False, only_to_me=False)
async def _ (session: NLPSession):
    if not is_enabled(session.event):
        return

    msg = session.msg
    group_id = session.event['group_id']
    if group_id not in CURRENT_GROUP_MESSAGE:
        CURRENT_GROUP_MESSAGE[group_id] = msg
        CURRENT_COMBO_COUNTER[group_id] = 1
    elif CURRENT_GROUP_MESSAGE[group_id] == msg:
        if CURRENT_COMBO_COUNTER[group_id] < 6:
            CURRENT_COMBO_COUNTER[group_id] += 1
            if CURRENT_COMBO_COUNTER[group_id] == 5:
                random_number = random.randint(1, 4)
                if random_number > 1:
                    await session.send(CURRENT_GROUP_MESSAGE[group_id])
                else:
                    cut_through = MessageSegment.text('打断复读') + MessageSegment.face(178) + MessageSegment.face(146)
                    await session.send(cut_through)
                    # clear the counters
                    CURRENT_GROUP_MESSAGE[group_id] = ''
                    CURRENT_COMBO_COUNTER[group_id] = 0
    else:
        CURRENT_GROUP_MESSAGE[group_id] = msg
        CURRENT_COMBO_COUNTER[group_id] = 1
