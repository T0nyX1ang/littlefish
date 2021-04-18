"""
A repeater in groups.

The bot will repeat the words in groups after the word has been
repeated for a certain time. Sometimes the bot will repeat the
word abnormal for fun.

The command requires to be invoked in groups.
"""

import random
from nonebot import on_endswith
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._exclaim import exclaim_msg, slim_msg, mutate_msg
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

    left_append = combo * left_increment + msg_base
    right_append = msg_base + combo * right_increment
    if message == right_append or message == left_append:
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

    mutate_prob = load(universal_id, 'mutate_probability')
    if not mutate_prob:
        mutate_prob = 5
        save(universal_id, 'mutate_probability', mutate_prob)

    cut_in_prob = load(universal_id, 'cut_in_probability')
    if not cut_in_prob:
        cut_in_prob = 5
        save(universal_id, 'cut_in_probability', cut_in_prob)

    if random.randint(1, 100) <= cut_in_prob:
        # reset the combo counter here
        save(universal_id, 'current_combo', 0)
        return exclaim_msg('打断' * ('打断' == msg_base[0:2]), '4', True, 1)

    final = combo * left_increment + msg_base + combo * right_increment
    can_mutate = random.randint(1, 100) <= mutate_prob

    # add combo for self repetition if the message is not mutated
    save(universal_id, 'current_combo', (combo + 1) * (not can_mutate))
    return mutate_msg(final, mutate=can_mutate)


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
    save(universal_id, 'current_combo', combo)

    if combo == 5:
        repeated_message = get_repeated_message(universal_id)
        await bot.send(event=event, message=repeated_message)
