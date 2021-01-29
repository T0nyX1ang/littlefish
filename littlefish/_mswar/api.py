"""
A module which provides necessary APIs.

Available APIs:
get_autopvp_info.
get_daily_map.
get_level_list.
get_user_info(with uid).
_get_latest_battle_winner.
"""

import nonebot
import math
from .analyzer import get_board, get_board_result
from .config import PVPConfig
from .netcore import fetch

global_config = nonebot.get_driver().config
plugin_config = PVPConfig(**global_config.dict())
autopvp_uid = plugin_config.autopvp_uid


async def _get_latest_battle_winner() -> str:
    """Get latest battle winner of autopvp."""
    battle_query = "uid=%s&page=0&count=1" % autopvp_uid
    autopvp_last_battle = await fetch(
        page='/MineSweepingWar/game/pvp/list/record', query=battle_query)
    battle_id = autopvp_last_battle['data'][0]['record']['id']

    battle_detail_query = 'id=%d' % (battle_id)
    latest_battle_detail = await fetch(
        page='/MineSweepingWar/game/pvp/record/detail',
        query=battle_detail_query)
    winner = latest_battle_detail['data']['records'][0]['user']['nickName']
    return winner


async def get_autopvp_info() -> dict:
    """Get full information of autopvp bot."""
    query = "uid=%s" % autopvp_uid
    autopvp_result = await fetch(page='/MineSweepingWar/game/pvp/career',
                                 query=query)

    autopvp_info = {}
    autopvp_info['win'] = autopvp_result['data']['minesweeperWin']
    autopvp_info['lose'] = autopvp_result['data']['minesweeperLose']
    autopvp_info['rank'] = autopvp_result['data']['rank']
    autopvp_info['level'] = autopvp_result['data']['level']
    autopvp_info['current_exp'] = autopvp_result['data']['exp']
    autopvp_info['next_stage_exp'] = autopvp_result['data']['levelExp']
    autopvp_info['latest_battle_winner'] = await _get_latest_battle_winner()

    return autopvp_info


async def get_daily_map() -> dict:
    """Get daily map information from the remote server."""
    daily_map_result = await fetch(
        page='/MineSweepingWar/minesweeper/daily/map/today')
    daily_map_board = get_board(
        daily_map_result['data']['map']['map'].split('-')[0:-1])
    daily_map = get_board_result(daily_map_board)
    daily_map['id'] = daily_map_result['data']['mapId']

    query = 'mapId=%d&page=0&count=1' % (daily_map['id'])
    daily_map_highest_result = await fetch(
        page='/MineSweepingWar/rank/daily/list', query=query)
    if daily_map_highest_result['data']:
        daily_map[
            'best_time'] = daily_map_highest_result['data'][0]['time'] / 1000
    else:
        daily_map['best_time'] = math.inf
    return daily_map


async def get_level_list() -> list:
    """Get the level information from the remote server."""
    user_level_result = await fetch(
        page='/MineSweepingWar/rank/timing/level/count')
    user_level_data = user_level_result['data']

    return user_level_data


async def get_user_info(uid: int) -> dict:
    """
    Gather user information.

    The information is made up of two parts: home_info and career_info.
    """
    user_info = {}
    user_info['uid'] = uid

    # home info
    home_info_result = await fetch(page='/MineSweepingWar/user/home',
                                   query='targetUid=%s' % uid)
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
    career_result = await fetch(
        page='/MineSweepingWar/minesweeper/timing/career',
        query='uid=%s' % uid)

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