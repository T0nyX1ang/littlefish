"""
Search user using a nickname filter.

The result will contain the exact nickname and ID of top-10 found users.
"""

from nonebot import on_command
from nonebot.adapters import Event
from littlefish._mswar.api import get_search_info
from littlefish._policy.rule import check
from littlefish._exclaim import exclaim_msg


def format_search(search_result: list) -> str:
    """Formatter for information."""
    result_message = ''
    for single in search_result:
        line = '%s [%s]' % (single['nickname'], single['uid'])
        result_message = result_message + line + '\n'
    if not result_message:
        # deal with empty query
        result_message = '未查询到符合条件的玩家~'
    return result_message.strip()


searcher = on_command(cmd='search', aliases={'查询昵称'}, force_whitespace=True, rule=check('search'))


@searcher.handle()
async def _(event: Event):
    """Handle the search command."""
    search_nickname = str(event.message).split()[1]

    try:
        search_result = await get_search_info(search_nickname)
        if len(search_result) == 0:
            await searcher.send(message='未查询到符合条件的玩家~')
        else:
            await searcher.send(message=format_search(search_result))
    except Exception:
        await searcher.send(message=exclaim_msg('', '3', False, 1))
