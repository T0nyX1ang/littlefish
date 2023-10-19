"""
Get personal information from the remote server.

The information includes:
record of time and bvs in beg, int and exp).
the number of wins and losses.

The command requires to be invoked in groups.
"""

import time
import traceback

from nonebot import on_command, on_fullmatch
from nonebot.adapters import Event
from nonebot.log import logger

from littlefish._db import load, save
from littlefish._exclaim import exclaim_msg
from littlefish._mswar.api import get_user_info
from littlefish._mswar.references import level_ref, sex_ref
from littlefish._policy.rule import check, is_in_group


def format_rank_change(change: int) -> str:
    """Format rank change."""
    if change > 0:
        return f'↓{change}'
    elif change < 0:
        return f'↑{abs(change)}'
    return '-'


def format_user_info(user_info: dict) -> str:
    """Format detailed user info."""
    line = [f"{user_info['nickname']} [{user_info['uid']}] {sex_ref[user_info['sex']]}"]

    if user_info['level'] != 0:
        # convert to f-string
        line += [
            f"初级: {user_info['record_beg'][0]:.3f} | {user_info['record_beg'][1]:.3f}",
            f"局数: {user_info['stat_beg'][0] / 10000:.1f}w ({user_info['stat_beg'][1]:.1f}%)",
            f"中级: {user_info['record_int'][0]:.3f} | {user_info['record_int'][1]:.3f}",
            f"局数: {user_info['stat_int'][0] / 10000:.1f}w ({user_info['stat_int'][1]:.1f}%)",
            f"高级: {user_info['record_exp'][0]:.3f} | {user_info['record_exp'][1]:.3f}",
            f"局数: {user_info['stat_exp'][0] / 10000:.1f}w ({user_info['stat_exp'][1]:.1f}%)",
            f"总计: {user_info['record_total'][0]:.3f} | {user_info['record_total'][1]:.3f}",
            f"评价: {level_ref[user_info['level']]}, {user_info['rank']} ({format_rank_change(user_info['rank_change'])})"
        ]
    else:
        line.append('未加入排名, 无评价')

    line.append(f"雷网: {user_info['saoleiID']}")
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


def _validate_id(universal_id: str, uid: str, gap: int) -> int:
    """Add id into colding list."""
    current = load(universal_id, 'id_colding_list', {})
    current_time = int(time.time())
    if uid not in current or current_time - current[uid] >= gap:
        current[uid] = current_time
        save(universal_id, 'id_colding_list', current)
        return 0

    return gap - current_time + current[uid]


id_info = on_command(cmd='id', aliases={'联萌'}, force_whitespace=True, rule=check('info') & is_in_group)

id_battle = on_command(cmd='battle', aliases={'对战'}, force_whitespace=True, rule=check('info') & is_in_group)

id_me = on_fullmatch(msg=('me', '个人信息'), rule=check('info') & is_in_group)


@id_info.handle()
async def _(event: Event):
    """Handle the id_info command."""
    try:
        uid = int(str(event.message).split()[1])
    except Exception:
        await id_info.finish(message=exclaim_msg('', '3', False, 1))

    universal_id = str(event.self_id) + str(event.group_id)
    colding_time = _validate_id(universal_id, str(uid), gap=3600)
    if colding_time > 0:
        wait_message = f'用户[{uid}]尚在查询冷却期，剩余时间{colding_time}秒~'
        await id_info.finish(message=wait_message)

    try:
        user_info = await get_user_info(uid)
    except Exception:
        await id_info.send(message='用户信息获取失败~')
        logger.error(traceback.format_exc())
        return

    user_info_message = format_user_info(user_info)
    await id_info.send(message=user_info_message)


@id_battle.handle()
async def _(event: Event):
    """Handle the id_battle command."""
    try:
        args = str(event.message).split()
        uid1, uid2 = int(args[1]), int(args[2])
    except Exception:
        await id_battle.finish(message=exclaim_msg('', '3', False, 1))

    try:
        uid1_info = await get_user_info(uid1)
        uid2_info = await get_user_info(uid2)
    except Exception:
        logger.error(traceback.format_exc())
        await id_battle.finish(message='用户信息获取失败~')

    battle_message = f'[{uid1}] vs [{uid2}]\n'

    for v in ['beg', 'int', 'exp', 'total']:
        tdiff = uid1_info[f'record_{v}'][0] - uid2_info[f'record_{v}'][0]
        bdiff = uid1_info[f'record_{v}'][1] - uid2_info[f'record_{v}'][1]
        result = f'{v}: {tdiff:+0.3f} | {bdiff:+0.3f}'
        battle_message += (result + '\n')

    await id_battle.send(message=battle_message.strip())


@id_me.handle()
async def _(event: Event):
    """Handle the id_me command."""
    universal_id = str(event.self_id) + str(event.group_id)
    user_id = f'{event.get_user_id()}'
    try:
        members = load(universal_id, 'members', {})
        uid = int(members[user_id]['id'])
    except Exception:
        await id_me.finish(message='个人信息获取失败，请检查头衔~')

    colding_time = _validate_id(universal_id, str(uid), gap=3600)
    if colding_time > 0:
        wait_message = f'用户ID[{uid}]尚在查询冷却期，剩余冷却时间{colding_time}秒~'
        await id_me.finish(message=wait_message)

    try:
        user_info = await get_user_info(uid)
    except Exception:
        logger.error(traceback.format_exc())
        await id_me.finish(message='用户信息获取失败~')

    user_info_message = format_user_info(user_info)
    await id_me.send(message=user_info_message)
