"""
A repeater in groups.

The bot will repeat the words in groups after the word has been
repeated for a certain time. Sometimes the bot will repeat the
word abnormal for fun.
"""

from nonebot import on_endswith
from nonebot.adapters.cqhttp import Bot, Event, Message
from littlefish._exclaim import slim_msg
from littlefish._policy import check
from littlefish._db import load, save


def check_block_wordlist(universal_id: str, message: str) -> bool:
    """Check whether the message contains blocked words."""
    block_wordlist = load(universal_id, 'block_wordlist')
    if not block_wordlist:
        block_wordlist = set()

    for w in block_wordlist:
        if w in message:
            return True  # the message contains blocked words

    return False  # the message does not contain blocked words


def update_combo(universal_id: str, message: str, combo: int) -> bool:
    """Update the current combo according to the message."""
    msg_base = load(universal_id, 'current_msg_base')
    left_increment = load(universal_id, 'current_left_increment')
    right_increment = load(universal_id, 'current_right_increment')

    if not msg_base:
        msg_base = message

    if combo <= 1:
        place = message.find(msg_base)
        left_increment = message[:place]
        right_increment = message[place + len(msg_base):]
        save(universal_id, 'current_msg_base', msg_base)
        save(universal_id, 'current_left_increment', left_increment)
        save(universal_id, 'current_right_increment', right_increment)

    left_append = combo * left_increment + msg_base
    right_append = msg_base + combo * right_increment
    if message == right_append or message == left_append:
        return combo + 1
    else:
        save(universal_id, 'current_msg_base', message)
        save(universal_id, 'current_left_increment', '')
        save(universal_id, 'current_right_increment', '')
        return 1


def get_repeated_message(universal_id: str, combo: int) -> str:
    """Get repeated message and add some variations on it."""
    msg_base = load(universal_id, 'current_msg_base')
    left_increment = load(universal_id, 'current_left_increment')
    right_increment = load(universal_id, 'current_right_increment')
    final = combo * left_increment + msg_base + combo * right_increment
    return Message(final)


repeater = on_endswith(msg='', priority=11, block=True, rule=check('repeat'))


@repeater.handle()
async def repeat(bot: Bot, event: Event, state: dict):
    """Handle the repeat command."""
    message = str(slim_msg(event.message)).strip()
    universal_id = str(event.self_id) + str(event.group_id)

    # get current combo for repetition
    combo = load(universal_id, 'current_combo')
    if not combo:
        combo = 0  # initialization for current combo

    if check_block_wordlist(universal_id, message):
        return

    combo = update_combo(universal_id, message, combo)

    if combo == 5:
        repeated_message = get_repeated_message(universal_id, combo)
        combo += 1  # add combo for self repetition
        await bot.send(event=event, message=repeated_message)

    save(universal_id, 'current_combo', combo)
