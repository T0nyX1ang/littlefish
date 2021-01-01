"""
Generate random integers.

Invoke this command by: [begin] [end] [count] [extras]
Available extra commands:
r: allow repetitions
a: ascending order (prior to d)
d: descending order
"""

from nonebot import on_command
from nonebot.permission import GROUP
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._policy import check
from littlefish._exclaim import exclaim_msg
import random

randi = on_command(cmd='randi', aliases={'随机数'},
                   permission=GROUP, rule=check('randi'))


@randi.handle()
async def randi(bot: Bot, event: Event, state: dict):
    """Generate random integers."""
    args = str(event.message).split()
    try:
        begin = int(args[0])
        end = int(args[1])
        count = int(args[2])
        extras = args[3:]
        message = get_randi(begin, end, count, extras)
        await bot.send(event=event, message=message)
    except Exception:
        await bot.send(event=event, message=exclaim_msg('\x00', '3', False))


def get_randi(begin: int, end: int, count: int, extras: list):
    """Get random integers from a fixed range."""
    begin, end = min(begin, end), max(begin, end)  # ensure a valid list
    number_range = range(begin, end + 1)
    count = 1 + (count - 1) * (0 < count <= 10)   # shrink range

    if 'r' in extras:  # repetition feature
        result = [random.sample(number_range, 1) for _ in range(0, count)]
    else:
        result = random.sample(number_range, min(count, len(number_range)))

    if 'a' in extras:  # ascending order
        result.sort()
    elif 'd' in extras:  # descending order
        result.sort(reverse=True)

    return '随机结果: ' + str(result).replace('[', '').replace(
        ']', '').replace(',', '')
