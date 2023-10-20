"""
Fetch the infomation of the autopvp bot.

The information includes:
Bot: rank, level (including progress), wins / loses, latest winner.
"""

import traceback

import nonebot
from nonebot import on_fullmatch
from nonebot.log import logger

from littlefish._exclaim import exclaim_msg
from littlefish._mswar.api import get_autopvp_info
from littlefish._policy.rule import broadcast, check


def format_pvp_info(autopvp_info: dict) -> str:
    """Formatter for information."""
    level_rate = autopvp_info['current_exp'] / autopvp_info['next_stage_exp'] * 100
    win_rate = autopvp_info['win'] / (autopvp_info['win'] + autopvp_info['lose']) * 100
    line = [
        "对战机器人状态:", f"排名: {autopvp_info['rank']}", f"等级: {autopvp_info['level']} (完成 {level_rate:.1f}%)",
        f"战绩: 胜利 {autopvp_info['win']} 场, 失败 {autopvp_info['lose']} 场, 胜率 {win_rate:.1f}%",
        f"最近挑战胜者: {autopvp_info['latest_battle_winner']}"
    ]

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


autopvp = on_fullmatch(msg=('autopvp', '对战机器人'), rule=check('autopvp'))


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
