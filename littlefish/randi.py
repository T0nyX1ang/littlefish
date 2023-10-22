"""
Generate random integers.

Invoke this command by: [begin] [end] [count] [extras]
Available extra commands:
r: allow repetitions
a: ascending order (prior to d)
d: descending order
"""

import random

from nonebot_plugin_alconna import Alconna, Args, Arparma, on_alconna

from littlefish._policy.rule import check


def get_randi(begin: int, end: int, count: int, extras: list) -> list:
    """Get random integers from a fixed range."""
    begin, end = min(begin, end), max(begin, end)  # ensure a valid list
    number_range = range(begin, end + 1)
    count = 1 + (count - 1) * (0 < count <= 10)  # shrink range

    if 'r' in extras:  # repetition feature
        result = [random.sample(number_range, 1)[0] for _ in range(0, count)]
    else:
        result = random.sample(number_range, min(count, len(number_range)))

    if 'a' in extras:  # ascending order
        result.sort()
    elif 'd' in extras:  # descending order
        result.sort(reverse=True)

    return result


alc_randi = Alconna(['randi', '随机数'], Args['begin', int]['end', int]['count', int]['rep;?', 'r']['order;?', ['a', 'd']])
randi = on_alconna(alc_randi, rule=check('randi'))


@randi.handle()
async def _(result: Arparma):
    """Handle the randi command."""
    begin, end = result.begin, result.end
    count = min([result.count, 10, abs(end - begin) + 1])
    extras = [result.rep, result.order]
    randi_result = get_randi(begin, end, count, extras)
    message = f"随机结果: {' '.join(map(str, randi_result))}"
    await randi.send(message=message)
