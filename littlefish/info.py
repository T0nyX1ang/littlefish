"""
Get personal information from the remote server.

The information includes:
record of time and bvs in beg, int and exp).
the number of wins and losses.
"""

import time
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._exclaim import exclaim_msg
from littlefish._netcore import fetch
from littlefish._policy import check
from littlefish._mswar.references import sex_ref, level_ref
from littlefish._db import load, save


def format_user_info(user_info):
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


async def get_user_career(uid: int):
    """Get user career information from the remote server."""
    query = 'uid=%d' % uid
    result = await fetch(page='/MineSweepingWar/minesweeper/timing/career',
                         query=query)
    return result


async def get_user_home_info(uid: int):
    """Get user home information from the remote server."""
    query = 'targetUid=%d' % uid
    result = await fetch(page='/MineSweepingWar/user/home', query=query)
    return result


async def get_user_info(uid: int):
    """
    Gather user information.

    The information is made up of two parts: home_info and career_info.
    """
    user_info = {}
    user_info['uid'] = uid

    # home info
    home_info_result = await get_user_home_info(uid)    
    user_info['saoleiID'] = '暂未关联'
    if home_info_result['data']['saoleiOauth']:
        user_info['saoleiID'] = '%s [%s]' % (
            home_info_result['data']['saoleiOauth']['name'].strip(),
            home_info_result['data']['saoleiOauth']['openId'].strip(),
        )
    user_info['nickname'] = home_info_result['data']['user']['nickName']
    user_info['sex'] = home_info_result['data']['user']['sex']
    user_info['level'] = home_info_result['data']['user']['timingLevel']
    user_info['rank'] = home_info_result['data']['user']['timingRank']

    if user_info['level'] == 0:  # shorten query process if necessary
        return user_info

    # career info
    career_result = await get_user_career(uid)
    
    for v in ['beg', 'int', 'exp', 'total']:  # fetch rank information
        user_info[f'record_{v}'] = (
            career_result['data'][f'{v}TimeRank']['time'] / 1000,
            career_result['data'][f'{v}TimeRank']['rank'],
            career_result['data'][f'{v}BvsRank']['bvs'],
            career_result['data'][f'{v}BvsRank']['rank'],
        )

    for v in ['beg', 'int', 'exp']:  # fetch statistics information
        success = career_result['data']['statistics'][f'{v}Sum']
        fail = career_result['data']['statistics'][f'{v}Fail']
        total = success + fail + (success == 0)  # make the result divisible
        user_info[f'stat_{v}'] = (
            total / 10000,  # set the unit to 10000
            success / total * 100,
        )

    return user_info


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


id_info = on_command(cmd='id', rule=check('联萌'))


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
