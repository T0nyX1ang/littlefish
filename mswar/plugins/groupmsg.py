from nonebot import on_natural_language, NLPSession, on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from nonebot.command.argfilter.extractors import extract_image_urls
from .global_value import CURRENT_GROUP_MESSAGE, CURRENT_GROUP_MESSAGE_INCREMENT, CURRENT_COMBO_COUNTER, CURRENT_GROUP_MEMBERS, CURRENT_WORD_BLACKLIST
from .core import check_policy
import random

def get_image_hashes(message):
    image_urls = extract_image_urls(message)
    image_hashes = [ val.split('/')[-2].split('-')[-1] for val in image_urls ]
    return image_hashes

@on_natural_language(permission=SUPERUSER | GROUP, only_short_message=False, only_to_me=False)
async def _ (session: NLPSession):
    if not check_policy(session.event, 'groupmsg'):
        return

    msg = session.msg.strip() # for mis-input whitespace
    group_id = session.event['group_id']
    user_id = session.event['sender']['user_id']
    message_id = session.event['message_id']
    cmsg_image_hashes = get_image_hashes(CURRENT_GROUP_MESSAGE[group_id])
    msg_image_hashes = get_image_hashes(msg)

    for word in CURRENT_WORD_BLACKLIST[group_id]:
        if word in msg:
            logger.info('%s triggered the word blacklist ...' % (word))
            CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = ''
            CURRENT_GROUP_MESSAGE[group_id] = ''
            CURRENT_COMBO_COUNTER[group_id] = 0
            return

    if CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted']:
        try:
            decision = random.randint(1, 100)
            if decision <= 1:
                ban_time = random.randint(1, 3) * 86400              
            if decision <= 10:
                ban_time = random.randint(1, 24) * 3600
            else:
                ban_time = random.randint(1, 60) * 60            
            await session.bot.set_group_ban(group_id=group_id, user_id=user_id, duration=ban_time)
        except Exception as e:
            logger.warning('Privilege not enough for banning ...')
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

    elif 0 < len(CURRENT_GROUP_MESSAGE[group_id]) <= len(msg) and (
            CURRENT_GROUP_MESSAGE[group_id] == msg[0: len(CURRENT_GROUP_MESSAGE[group_id])] or (
                msg_image_hashes and cmsg_image_hashes == msg_image_hashes)):

        if CURRENT_COMBO_COUNTER[group_id] < 6:

            if CURRENT_COMBO_COUNTER[group_id] <= 1:
                if not CURRENT_GROUP_MESSAGE[group_id]:
                    CURRENT_GROUP_MESSAGE[group_id] = msg
                CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = msg[len(CURRENT_GROUP_MESSAGE[group_id]):]

            elif msg_image_hashes and cmsg_image_hashes == msg_image_hashes:
                CURRENT_GROUP_MESSAGE_INCREMENT[group_id] = ''
                new_msg = ''
                for url in extract_image_urls(CURRENT_GROUP_MESSAGE[group_id]):
                    new_msg += '[CQ:image,url=%s]' % (url)
                CURRENT_GROUP_MESSAGE[group_id] = new_msg

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

@on_command('enterroom', aliases=('进入小黑屋'), permission=SUPERUSER | GROUP, only_to_me=False)
async def enterroom(session: CommandSession):
    if not check_policy(session.event, 'groupmsg'):
        session.finish('小鱼睡着了zzz~')
        
    group_id = session.event['group_id']
    user_id = session.event['sender']['user_id']
    role = session.event['sender']['role']
    restricted = CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted']
    if role != 'member':
        message = '管理员无法使用小黑屋功能~'
    elif not restricted:
        CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted'] = True
        message = MessageSegment.at(user_id) + ' 进入了小黑屋' 
    else:
        message = MessageSegment.at(user_id) + ' 已经在小黑屋中' 
    await session.send(message)

@on_command('exitroom', aliases=('退出小黑屋'), permission=SUPERUSER | GROUP, only_to_me=False)
async def exitroom(session: CommandSession):
    if not check_policy(session.event, 'groupmsg'):
        session.finish('小鱼睡着了zzz~')
        
    group_id = session.event['group_id']
    user_id = session.event['sender']['user_id']
    role = session.event['sender']['role']
    restricted = CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted']
    if role != 'member':
        message = '管理员无法使用小黑屋功能~'
    elif restricted:
        CURRENT_GROUP_MEMBERS[group_id][str(user_id)]['restricted'] = False
        message = MessageSegment.at(user_id) + ' 退出了小黑屋' 
    else:
        message = MessageSegment.at(user_id) + ' 已经不在小黑屋中' 
    await session.send(message)
