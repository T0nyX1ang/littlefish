"""
Fetch the information of a user's ranking.

The information includes:
The ranking and basic information of the user.
"""

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._exclaim import exclaim_msg
from littlefish._mswar.api import get_ranking_info
from littlefish._mswar.references import type_ref, style_ref, mode_ref
from littlefish._policy import check


def format_ranking_info(ranking_info: list) -> str:
    """Formatter for information."""
    result_message = ''
    for v in ranking_info:
        result_message += '%d: %s[%d] - %s\n' % v
    if not result_message:
        # deal with empty query
        result_message = '未查询到符合条件的排名~'
    return result_message


ranking = on_command(cmd='rank ', aliases={'排名 '}, rule=check('ranking'))


@ranking.handle()
async def ranking(bot: Bot, event: Event, state: dict):
    """Handle the ranking command."""
    args = str(event.message).split()

    try:
        item = type_ref[args[0]]
        page = max(0, int(args[1]) - 1)
        extra = {'type': item, 'mode': -1, 'level': 4}
        if len(args[2:]) >= 2:
            extra['mode'] = style_ref[args[2]]
            extra['level'] = mode_ref[args[3]]
        if item not in [0, 1]:
            extra = {}
        result = await get_ranking_info(item, page, extra)
        await bot.send(event=event, message=format_ranking_info(result))
    except Exception:
        await bot.send(event=event, message=exclaim_msg('', '3', False, 1))
