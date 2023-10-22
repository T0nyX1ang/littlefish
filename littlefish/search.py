"""
Search user using a nickname filter.

The result will contain the exact nickname and ID of top-10 found users.
"""

from nonebot_plugin_alconna import on_alconna, Alconna, Args, Arparma

from littlefish._mswar.api import get_search_info
from littlefish._policy.rule import check


def format_search(search_result: list) -> str:
    """Formatter for information."""
    result_message = ''
    for single in search_result:
        line = f"{single['nickname']} [{single['uid']}]"
        result_message = result_message + line + '\n'
    if not result_message:
        # deal with empty query
        result_message = '未查询到符合条件的玩家~'
    return result_message.strip()


searcher = on_alconna(Alconna(['search', '查询昵称'], Args['nickname', str]), rule=check('search'))


@searcher.handle()
async def _(result: Arparma):
    """Handle the search command."""
    search_nickname = result.nickname
    search_result = await get_search_info(search_nickname)
    if len(search_result) == 0:
        await searcher.send(message='未查询到符合条件的玩家~')
    else:
        await searcher.send(message=format_search(search_result))
