"""
Get personal information from the remote server.

The information includes:
record of time and bvs in beg, int and exp).
the number of wins and losses.

The command requires to be invoked in groups.
"""

import time
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._exclaim import exclaim_msg
from littlefish._policy import check
from littlefish._mswar.api import get_user_info
from littlefish._mswar.references import sex_ref, level_ref
from littlefish._db import load, save


def format_user_info(user_info: dict):
    """Format detailed user info."""
    line = [
        '%s (Id: %d) %s' % (
            user_info['nickname'],
            user_info['uid'], sex_ref[user_info['sex']]
        )
    ]

    if user_info['level'] != 0:
        line += [
            '初级: %.3f(%s) | %.3f(%s)' % user_info['record_beg'],
            '局数: %.1fw (%.1f%%)' % user_info['stat_beg'],
            '中级: %.3f(%s) | %.3f(%s)' % user_info['record_int'],
            '局数: %.1fw (%.1f%%)' % user_info['stat_int'],
            '高级: %.3f(%s) | %.3f(%s)' % user_info['record_exp'],
            '局数: %.1fw (%.1f%%)' % user_info['stat_exp'],
            '总计: %.3f(%s) | %.3f(%s)' % user_info['record_total'],
            '评价: %s 级, 排位第 %d 名' % (
                level_ref[user_info['level']],
                user_info['rank']
            )
        ]
    else:
        line.append('未加入排名, 无评价')

    line.append('雷网: %s' % user_info['saoleiID'])
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


def _validate_id(universal_id: str, uid: str, gap: int):
    """Add id into colding list."""
    current = load(universal_id, 'id_colding_list')
    if not current:
        current = {}

    current_time = int(time.time())
    if uid not in current or current_time - current[uid] >= gap:
        current[uid] = current_time
        save(universal_id, 'id_colding_list', current)
        return True
    else:
        return False


id_info = on_command(cmd='id', aliases={'联萌'}, rule=check('info'))


@id_info.handle()
async def id_info(bot: Bot, event: Event, state: dict):
    """Handle the id command."""
    try:
        uid = int(str(event.message).strip())
    except Exception:
        await bot.send(event=event, message=exclaim_msg('', '3', False, 1))
        return

    universal_id = str(event.self_id) + str(event.group_id)
    if _validate_id(universal_id, str(uid), gap=3600):
        user_info = await get_user_info(uid)
        user_info_message = format_user_info(user_info)
        await bot.send(event=event, message=user_info_message)
    else:
        await bot.send(event=event, message=exclaim_msg('', '12', False, 1))
