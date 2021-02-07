"""
Make the bot more responsive to words.

The command requires to be invoked in groups.
"""

import datetime
import random
from nonebot import on_command, on_endswith, on_notice
from nonebot.adapters.cqhttp import Bot, Event, PokeNotifyEvent
from littlefish._policy import check, empty
from littlefish._exclaim import exclaim_msg


admire = on_command(cmd='admire', aliases={'膜'}, rule=check('exclaim'))

praise = on_command(cmd='praise', aliases={'狂膜'}, rule=check('exclaim'))

cheer = on_command(cmd='cheer', aliases={'加油 '}, rule=check('exclaim'))

cheer_ending = on_endswith(msg='加油', priority=10, rule=check('exclaim'))

greet = on_command(cmd='greet', aliases={'小鱼'},
                   rule=check('exclaim') & empty())

poke_greet = on_notice(priority=10, block=True,
                       rule=check('exclaim', PokeNotifyEvent))


@admire.handle()
async def admire(bot: Bot, event: Event, state: dict):
    """Admire the person."""
    person = str(event.message).strip()
    await bot.send(event=event, message=exclaim_msg(person, '1', True))


@praise.handle()
async def praise(bot: Bot, event: Event, state: dict):
    """Praise the person."""
    person = str(event.message).strip()
    message = exclaim_msg(person, '1', False)
    await bot.send(event=event, message=message)
    await bot.send(event=event, message=message)


@cheer.handle()
async def cheer(bot: Bot, event: Event, state: dict):
    """Cheer the person."""
    person = str(event.message).strip()
    await bot.send(event=event, message=exclaim_msg(person, '2', True))


@cheer_ending.handle()
async def cheer_ending(bot: Bot, event: Event, state: dict):
    """Cheer the person with the ending."""
    person = str(event.message).strip()[:-2]
    await bot.send(event=event, message=exclaim_msg(person, '2', False))


@greet.handle()
async def greet(bot: Bot, event: Event, state: dict):
    """Greet the person."""
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    if current_hour not in [0, 23]:  # offset
        current_hour += random.choice([-1, 0, 0, 0, 1])   # add randomness
    time_tag = [10, 10, 11, 11, 12, 12, 13, 13,
                14, 14, 14, 15, 15, 15, 16, 16,
                16, 17, 17, 17, 18, 18, 19, 19]   # a tag for time
    await bot.send(event=event, message=exclaim_msg(
        '', str(time_tag[current_hour]), False, 1))


@poke_greet.handle()
async def poke_greet(bot: Bot, event: Event, state: dict):
    """Greet the person when the bot is poked."""
    await greet(bot, event, state)
