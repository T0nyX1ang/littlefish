"""
Fetch the infomation of the autopvp bot.

The information includes:
Bot: rank, level (including progress), wins / loses, latest winner.

The command requires to be invoked in groups.
"""

import traceback
import nonebot
from nonebot import on_command
from nonebot.log import logger
from littlefish._mswar.api import get_autopvp_info
from littlefish._policy.rule import check, broadcast
from littlefish._exclaim import exclaim_msg


def format_pvp_info(autopvp_info: dict) -> str:
    """Formatter for information."""
    line = [
        '对战机器人状态:',
        '排名: %d' % (autopvp_info['rank']),
        '等级: %d (完成 %.1f%%)' % (autopvp_info['level'], autopvp_info['current_exp'] / autopvp_info['next_stage_exp'] * 100),
        '战绩: 胜利 %d 场, 失败 %d 场, 胜率 %.1f%%' % (autopvp_info['win'], autopvp_info['lose'], autopvp_info['win'] /
                                             (autopvp_info['win'] + autopvp_info['lose']) * 100),
        '最近挑战胜者: %s' % (autopvp_info['latest_battle_winner'])
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


autopvp = on_command(cmd='autopvp', aliases={'对战机器人'}, rule=check('autopvp'))


@autopvp.handle()
async def _():
    """Handle the autopvp command."""
    autopvp_result = await get_autopvp_info()
    await autopvp.send(message=format_pvp_info(autopvp_result))
    if autopvp_result['latest_battle_winner'] != 'autopvp':
        await autopvp.send(message=exclaim_msg(autopvp_result['latest_battle_winner'], '1', False))


@broadcast('autopvp')
async def _(bot_id: str, group_id: str):
    """Scheduled autopvp broadcast."""
    autopvp_result = await get_autopvp_info()
    message = [format_pvp_info(autopvp_result)]
    if autopvp_result['latest_battle_winner'] != 'autopvp':
        message.append(exclaim_msg(autopvp_result['latest_battle_winner'], '1', False))

    bot = nonebot.get_bots()[bot_id]
    try:
        for msg in message:
            await bot.send_group_msg(group_id=int(group_id), message=msg)
    except Exception:
        logger.error(traceback.format_exc())
