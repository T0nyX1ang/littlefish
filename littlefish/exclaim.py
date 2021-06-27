"""
Make the bot more responsive to words.

Greeting / cheering / admiring:
The bot will greet the user when certain actions / commands
are triggered.

Repeating:
The bot will repeat the words in groups after the word has been
repeated for a certain time. Sometimes the bot will repeat the
word abnormal for fun.

The command requires to be invoked in groups.
"""

import random
import datetime
from nonebot import on_command, on_endswith, on_notice
from nonebot.adapters.cqhttp import Bot, Event, PokeNotifyEvent
from littlefish._db import load, save
from littlefish._policy.rule import check
from littlefish._policy.plugin import on_simple_command
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


praise = on_command(cmd='praise', aliases={'膜'}, rule=check('exclaim'))

admire = on_command(cmd='admire', aliases={'狂膜'}, rule=check('exclaim'))

cheer = on_command(cmd='cheer', aliases={'加油 '}, rule=check('exclaim'))

cheer_ending = on_endswith(msg='加油', priority=10, rule=check('exclaim'))

greet = on_simple_command(cmd='greet', aliases={'小鱼'}, rule=check('exclaim'))

poke_greet = on_notice(priority=10, block=True, rule=check('exclaim', PokeNotifyEvent))

repeater = on_endswith(msg='', priority=11, block=True, rule=check('exclaim'))


@praise.handle()
async def show_praise(bot: Bot, event: Event, state: dict):
    """Praise the person."""
    person = str(event.message).strip()
    await bot.send(event=event, message=exclaim_msg(person, '1', True))


@admire.handle()
async def show_admire(bot: Bot, event: Event, state: dict):
    """Admire(Praise * 2) the person."""
    person = str(event.message).strip()
    message = exclaim_msg(person, '1', False)
    await bot.send(event=event, message=message)
    await bot.send(event=event, message=message)


@cheer.handle()
async def show_cheer(bot: Bot, event: Event, state: dict):
    """Cheer the person."""
    person = str(event.message).strip()
    await bot.send(event=event, message=exclaim_msg(person, '2', True))


@cheer_ending.handle()
async def show_cheer_ending(bot: Bot, event: Event, state: dict):
    """Cheer the person with the ending."""
    if str(event.message).strip()[-2:] != '加油':
        return  # recheck the message
    person = str(event.message).strip()[:-2]
    await bot.send(event=event, message=exclaim_msg(person, '2', True))


@greet.handle()
async def show_greet(bot: Bot, event: Event, state: dict):
    """Greet the person."""
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    if current_hour not in [0, 23]:  # offset
        current_hour += random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 1])  # add randomness
    time_tag = [10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 14, 15, 15, 15, 16, 16, 16, 17, 17, 17, 18, 18, 19,
                19]  # a tag for time
    await bot.send(event=event, message=exclaim_msg('', str(time_tag[current_hour]), False, 1))


@poke_greet.handle()
async def show_poke_greet(bot: Bot, event: Event, state: dict):
    """Greet the person when the bot is poked, and repeat the poke action."""
    if event.target_id == event.self_id and event.sender_id != event.self_id:  # ensure poking target
        await show_greet(bot, event, state)

    universal_id = str(event.self_id) + str(event.group_id)
    poke_combo = load(universal_id, 'current_poke_combo', 0)
    poke_target = load(universal_id, 'current_poke_target', -1)

    poke_combo = poke_combo + 1 - poke_combo * (poke_target != event.target_id)

    if poke_combo == 5:
        poke_combo += 1
        await bot.send(event=event, message=slim_msg('[CQ:poke,qq=%d]' % poke_target))

    save(universal_id, 'current_poke_combo', poke_combo)
    save(universal_id, 'current_poke_target', event.target_id)


@repeater.handle()
async def repeat(bot: Bot, event: Event, state: dict):
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
        await bot.send(event=event, message=repeated_message)
