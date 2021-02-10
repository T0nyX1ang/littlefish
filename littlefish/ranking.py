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
    return result_message


ranking = on_command(cmd='rank', aliases={'排名'}, rule=check('ranking'))


@ranking.handle()
async def ranking(bot: Bot, event: Event, state: dict):
    """Handle the ranking command."""
    args = str(event.message).split()

    try:
        item = type_ref[args[0]]
        page = max(0, int(args[1]) - 1)
        extra = ''
        if len(args[2:]) >= 2:
            extra = 'type=%d&mode=%d&level=%d' % (item, style_ref[args[2]],
                                                  mode_ref[args[3]])
        result = await get_ranking_info(item, page, extra)
        await bot.send(event=event, message=format_ranking_info(result))
    except Exception:
        await bot.send(event=event, message=exclaim_msg('', '3', False, 1))
