from nonebot import on_natural_language, NLPSession, on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from .global_value import CURRENT_GROUP_MESSAGE, CURRENT_GROUP_MESSAGE_INCREMENT, CURRENT_COMBO_COUNTER, CURRENT_GROUP_MEMBERS
from .core import is_enabled
import random

@on_natural_language(permission=SUPERUSER | GROUP, only_short_message=False, only_to_me=False)
async def _ (session: NLPSession):
    if not is_enabled(session.event):
        return

    msg = session.msg.strip() # for mis-input whitespace
    group_id = session.event['group_id']
    user_id = session.event['sender']['user_id']
    if CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted']:
        message = MessageSegment.at(user_id) + MessageSegment.text(' 在小黑屋里就别水群了，快去干更多有趣的事情吧') + MessageSegment.face(146)
        await session.send(message)
        # clear the counters
        CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = ''
        CURRENT_GROUP_MESSAGE[group_id] = ''
        CURRENT_COMBO_COUNTER[group_id] = 0        
    elif group_id not in CURRENT_GROUP_MESSAGE:
        CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = ''
        CURRENT_GROUP_MESSAGE[group_id] = msg
        CURRENT_COMBO_COUNTER[group_id] = 1

    elif len(CURRENT_GROUP_MESSAGE[group_id]) <= len(msg) and CURRENT_GROUP_MESSAGE[group_id] == msg[0: len(CURRENT_GROUP_MESSAGE[group_id])]:
        if CURRENT_COMBO_COUNTER[group_id] < 6:
            if CURRENT_COMBO_COUNTER[group_id] <= 1:
                if not CURRENT_GROUP_MESSAGE[group_id]:
                    CURRENT_GROUP_MESSAGE[group_id] = msg
                CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = msg[len(CURRENT_GROUP_MESSAGE[group_id]):]
            elif CURRENT_GROUP_MESSAGE[group_id] + CURRENT_GROUP_MESSAGE_INCREMENT[group_id] * CURRENT_COMBO_COUNTER[group_id] != msg:
                CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = ''
                CURRENT_GROUP_MESSAGE[group_id] = msg
                CURRENT_COMBO_COUNTER[group_id] = 0

            CURRENT_COMBO_COUNTER[group_id] += 1
            
            if CURRENT_COMBO_COUNTER[group_id] == 5:
                random_number = random.randint(1, 20)
                if random_number > 1:
                    await session.send(CURRENT_GROUP_MESSAGE[group_id] + CURRENT_GROUP_MESSAGE_INCREMENT[group_id] * CURRENT_COMBO_COUNTER[group_id])
                else:
                    cut_through = MessageSegment.text('打断复读') + MessageSegment.face(178) + MessageSegment.face(146)
                    await session.send(cut_through)
                    # clear the counters
                    CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = ''
                    CURRENT_GROUP_MESSAGE[group_id] = ''
                    CURRENT_COMBO_COUNTER[group_id] = 0

    else:
        CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = ''
        CURRENT_GROUP_MESSAGE[group_id] = msg
        CURRENT_COMBO_COUNTER[group_id] = 1

@on_command('blacklist', aliases=('小黑屋'), permission=SUPERUSER | GROUP, only_to_me=False)
async def blacklist(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')
        
    group_id = session.event['group_id']
    user_id = session.event['sender']['user_id']
    restricted_stat = CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted']
    print(restricted_stat)
    CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted'] = not restricted_stat
    message = MessageSegment.at(user_id) + ' %s小黑屋' % ('退出了' if restricted_stat else '进入了') 
    await session.send(message)
