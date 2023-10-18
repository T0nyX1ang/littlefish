"""
Make the bot more responsive to words.

Greeting / cheering / admiring:
The bot will greet the user when certain actions / commands
are triggered.

Repeating:
The bot will repeat the words in groups after the word has been
repeated for a certain time. Sometimes the bot will repeat the
word abnormal for fun.

Some commands require to be invoked in groups.
"""

import random
import datetime
from nonebot import on_fullmatch, on_startswith, on_endswith
from nonebot.adapters import Event
from littlefish._db import load, save
from littlefish._policy.rule import check, is_in_group
from littlefish._exclaim import exclaim_msg, slim_msg, mutate_msg


def check_block_wordlist(universal_id: str, message: str) -> bool:
    """Check whether the message contains blocked words."""
    block_wordlist = set(load(universal_id, 'block_wordlist', []))

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

    msg_append = combo * left_increment + msg_base + combo * right_increment
    if message == msg_append:
        save(universal_id, 'current_msg_base', msg_base)
        save(universal_id, 'current_left_increment', left_increment)
        save(universal_id, 'current_right_increment', right_increment)
        return combo + 1
    else:
        save(universal_id, 'current_msg_base', message)
        save(universal_id, 'current_left_increment', '')
        save(universal_id, 'current_right_increment', '')
        return 1


def get_repeated_message(universal_id: str) -> str:
    """Get repeated message and add some variations on it."""
    msg_base = load(universal_id, 'current_msg_base')
    left_increment = load(universal_id, 'current_left_increment')
    right_increment = load(universal_id, 'current_right_increment')
    combo = load(universal_id, 'current_combo')

    mutate_prob = load(universal_id, 'mutate_probability', 5)
    cut_in_prob = load(universal_id, 'cut_in_probability', 5)

    if random.randint(1, 100) <= cut_in_prob:
        # reset the combo counter here
        save(universal_id, 'current_combo', 0)
        return exclaim_msg('打断' * (msg_base[0:2] == '打断'), '4', True, 1)

    final = combo * left_increment + msg_base + combo * right_increment
    can_mutate = random.randint(1, 100) <= mutate_prob

    # add combo for self repetition if the message is not mutated
    save(universal_id, 'current_combo', (combo + 1) * (not can_mutate))
    return mutate_msg(final, mutate=can_mutate)


def get_time_tag() -> int:
    """Get time tag according to current hour and some randomness."""
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    if current_hour not in [0, 23]:  # offset
        current_hour += random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 1])  # add randomness
    time_tag = [10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 14, 15, 15, 15, 16, 16, 16, 17, 17, 17, 18, 18, 19,
                19]  # a tag for time
    return time_tag[current_hour]


praise = on_startswith(msg='膜', rule=check('exclaim'))

admire = on_startswith(msg='狂膜', rule=check('exclaim'))

cheer = on_endswith(msg='加油', rule=check('exclaim'))

greet = on_fullmatch(msg=('greet', '小鱼'), rule=check('exclaim'))

repeater = on_endswith(msg='', priority=11, block=True, rule=check('exclaim') & is_in_group)


@praise.handle()
async def _(event: Event):
    """Handle the praise command."""
    if str(event.message).strip()[:1] != '膜':
        return  # recheck the message
    person = str(event.message).strip()[1:]
    await praise.send(message=exclaim_msg(person, '1', True))


@admire.handle()
async def _(event: Event):
    """Handle the admire (praise * 2) command."""
    if str(event.message).strip()[:2] != '狂膜':
        return  # recheck the message
    person = str(event.message).strip()[2:]
    message = exclaim_msg(person, '1', False)
    await admire.send(message=message)
    await admire.send(message=message)


@cheer.handle()
async def _(event: Event):
    """Handle the cheer (ending version) command."""
    if str(event.message).strip()[-2:] != '加油':
        return  # recheck the message
    person = str(event.message).strip()[:-2]
    await cheer.send(message=exclaim_msg(person, '2', True))


@greet.handle()
async def _():
    """Handle the greet command."""
    await greet.send(message=exclaim_msg('', str(get_time_tag()), False, 1))


@repeater.handle()
async def _(event: Event):
    """Handle the repeat command."""
    message = str(slim_msg(event.message)).strip()
    universal_id = str(event.self_id) + str(event.group_id)

    # get current combo for repetition
    combo = load(universal_id, 'current_combo', 0)

    if check_block_wordlist(universal_id, message):
        return

    combo = update_combo(universal_id, message, combo)
    save(universal_id, 'current_combo', combo)

    if combo == 5:
        repeated_message = get_repeated_message(universal_id)
        await repeater.send(message=repeated_message)
