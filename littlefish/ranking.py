"""
Fetch the information of a user's ranking.

The information includes:
The ranking and basic information of the user.

Invoke this command by: [item] [page] [extra: mode] [extra: level]
Available items: time, bvs, endless, nonguessing, coins, chaos, advance and popularity.
The page should be an integer, 10 users will be shown on each page.
The [mode] and [level] command is only available in [time] and [bvs] item.
"""

from nonebot_plugin_alconna import Alconna, Args, Arparma, on_alconna

from littlefish._mswar.api import get_ranking_info
from littlefish._mswar.references import mode_ref, style_ref, type_ref
from littlefish._policy.rule import check


def format_ranking_info(ranking_info: list) -> str:
    """Formatter for information."""
    result_message = ''
    for v in ranking_info:
        result_message += f'{v[0]}: {v[1]}[{v[2]}] - {v[3]}\n'
    if not result_message:
        # deal with empty query
        result_message = '未查询到符合条件的排名~'
    return result_message.strip()


# ranking = on_command(cmd='rank', aliases={'排名'}, force_whitespace=True, rule=check('ranking'))
alc_ranking = Alconna(['rank', '排名'], Args['item', type_ref]['page;?', int]['mode;?', style_ref]['level;?', mode_ref])
ranking = on_alconna(alc_ranking, rule=check('ranking'))


@ranking.handle()
async def _(result: Arparma):
    """Handle the ranking command."""
    item = result.item
    page = 0 if not result.page else max(0, result.page - 1)
    mode = -1 if not result.mode else result.mode
    level = 4 if not result.level else result.level
    extra = {'type': item, 'mode': mode, 'level': level} if item in [0, 1] else None
    rank_result = await get_ranking_info(item, page, 10, extra)
    await ranking.send(message=format_ranking_info(rank_result))
