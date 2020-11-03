from nonebot import on_natural_language, NLPSession, on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from nonebot.command.argfilter.extractors import extract_text, extract_image_urls, extract_numbers
from .global_value import CURRENT_GROUP_MESSAGE, CURRENT_GROUP_MESSAGE_INCREMENT, CURRENT_COMBO_COUNTER, CURRENT_GROUP_MEMBERS, CURRENT_WORD_BLACKLIST
from .core import check_policy
import random

def get_image_hashes(message):
    image_urls = extract_image_urls(message)
    image_hashes = [ val.split('/')[-2].split('-')[-1] for val in image_urls ]
    return image_hashes

def random_reverse(message, randomness=0):
    if not (0 <= randomness <= 1):
        randomness = 0
    message_text = extract_text(message)
    if not message_text or randomness == 0:
        return message
    text_length = len(message_text)
    reverse_length = int(randomness * text_length)
    reverse_start = random.randint(0, text_length - reverse_length)
    reverse_stop = reverse_start + reverse_length
    reverse_text = message_text[reverse_start: reverse_stop]
    result = message_text[: reverse_start] + reverse_text[::-1] + message_text[reverse_stop:]
    return result

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

    if 0 < len(CURRENT_GROUP_MESSAGE[group_id]) <= len(msg) and (
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
                    await session.send(random_reverse(CURRENT_GROUP_MESSAGE[group_id], randomness=(5 - random_number) / 5) + CURRENT_GROUP_MESSAGE_INCREMENT[group_id] * CURRENT_COMBO_COUNTER[group_id])
                else:
                    cut_through = MessageSegment.text('打断复读') + MessageSegment.face(178) + MessageSegment.face(146)
                    if CURRENT_GROUP_MESSAGE[group_id] != str(cut_through):
                        await session.send(cut_through)
                    else:
                        await session.send(MessageSegment.text('打断') + cut_through)
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
    duration = session.get('duration')
    try:     
        await session.bot.set_group_ban(group_id=group_id, user_id=user_id, duration=duration)
    except Exception as e:
        logger.warning('Privilege not enough for banning ...')
        message = MessageSegment.at(user_id) + MessageSegment.text('权限不足，无法使用小黑屋~')
        await session.send(message)

@enterroom.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        prepare = extract_numbers(stripped_arg)
        if prepare and 1 <= prepare[0] <= 1440:
            session.state['duration'] = int(prepare[0]) * 60
        else:
            session.state['duration'] = 1800
        return
