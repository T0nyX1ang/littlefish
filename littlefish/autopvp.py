"""
Fetch the infomation of the autopvp bot.

The information includes:
Bot: rank, level (including progress), wins / loses, latest winner.

The command is automatically invoked at 00:00:00 +- 30s everyday.
The command requires to be invoked in groups.
"""

import nonebot
import traceback
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._mswar.api import get_autopvp_info
from littlefish._policy import check, boardcast, empty
from littlefish._exclaim import exclaim_msg

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler


def format_pvp_info(autopvp_info: dict) -> str:
    """Formatter for information."""
    line = [
        '对战机器人状态:',
        '排名: %d' % (autopvp_info['rank']),
        '等级: %d (完成 %.1f%%)' %
        (autopvp_info['level'],
         autopvp_info['current_exp'] / autopvp_info['next_stage_exp'] * 100),
        '战绩: 胜利 %d 场, 失败 %d 场, 胜率 %.1f%%' %
        (autopvp_info['win'], autopvp_info['lose'], autopvp_info['win'] /
         (autopvp_info['win'] + autopvp_info['lose']) * 100),
        '最近挑战胜者: %s' % (autopvp_info['latest_battle_winner'])
    ]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


autopvp = on_command(cmd='autopvp', aliases={'对战机器人'},
                     rule=check('autopvp') & empty())


@autopvp.handle()
async def autopvp(bot: Bot, event: Event, state: dict):
    """Handle the autopvp command."""
    autopvp_result = await get_autopvp_info()
    await bot.send(event=event, message=format_pvp_info(autopvp_result))
    if autopvp_result['latest_battle_winner'] != 'autopvp':
        await bot.send(event=event,
                       message=exclaim_msg(
                           autopvp_result['latest_battle_winner'], '1', False))


@scheduler.scheduled_job('cron', hour=0, minute=0, second=0,
                         misfire_grace_time=30)
@boardcast('autopvp')
async def _(allowed: list):
    """Scheduled dailymap boardcast at 00:00:00."""
    autopvp_result = await get_autopvp_info()
    message = [format_pvp_info(autopvp_result)]
    if autopvp_result['latest_battle_winner'] != 'autopvp':
        message.append(
            exclaim_msg(autopvp_result['latest_battle_winner'], '1', False))

    for bot_id, group_id in allowed:
        bot = nonebot.get_bots()[bot_id]
        try:
            for msg in message:
                await bot.send_group_msg(group_id=int(group_id), message=msg)
        except Exception:
            logger.error(traceback.format_exc())
