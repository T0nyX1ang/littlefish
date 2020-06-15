from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from urllib.parse import quote, unquote
from .core import fetch, is_online
import traceback

def format_number(number):
    if type(number) is int and number > 0:
        return str(number)
    elif type(number) is float and number > 0:
        return str(round(number, 3))
    else:
        return '-'

def format_user_info(user_info):
    sex_ref = {0: '', 1: 'GG', 2: 'mm'}
    level_ref = {0: '-', 1: 'E', 2: 'D', 3: 'C', 4: 'B', 5: 'A', 6: 'S', 7: 'SS', 8: 'SSS', 9: '★', 10: '★★', -1: '雷帝'}
    line = [
        '%s (Id: %d) %s' % (user_info['nickname'], user_info['id'], sex_ref[user_info['sex']]),
        '初级记录: %s(%s) | %s(%s)' % (user_info['stat']['best_beg_time'], user_info['stat']['best_beg_time_rank'], 
                                      user_info['stat']['best_beg_bvs'], user_info['stat']['best_beg_bvs_rank']),
        '初级局数: %d / %d (%.1f%%)' % (user_info['stat']['beg_win_total'], user_info['stat']['beg_total'], user_info['stat']['beg_win_rate']),
        '中级记录: %s(%s) | %s(%s)' % (user_info['stat']['best_int_time'], user_info['stat']['best_int_time_rank'], 
                                      user_info['stat']['best_int_bvs'], user_info['stat']['best_int_bvs_rank']),
        '中级局数: %d / %d (%.1f%%)' % (user_info['stat']['int_win_total'], user_info['stat']['int_total'], user_info['stat']['int_win_rate']),
        '高级记录: %s(%s) | %s(%s)' % (user_info['stat']['best_exp_time'], user_info['stat']['best_exp_time_rank'], 
                                      user_info['stat']['best_exp_bvs'], user_info['stat']['best_exp_bvs_rank']),
        '高级局数: %d / %d (%.1f%%)' % (user_info['stat']['exp_win_total'], user_info['stat']['exp_total'], user_info['stat']['exp_win_rate']),
        '总计: %s(%s) | %s(%s)' % (user_info['stat']['total_time'], user_info['stat']['total_time_rank'], 
                                  user_info['stat']['total_bvs'], user_info['stat']['total_bvs_rank']),
    ]
    if user_info['level'] != 0:
        line.append('评价: %s 级, 排位第 %d 名' % (level_ref[user_info['level']] , user_info['rank']))
    else:
        line.append('未加入排名, 无评价')
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()

async def search_user(name, padding=True):
    if padding:
        # If you search user by id, then the user matched with corresponding id will come out
        query = 'name=' + quote(' ' * 20 + name) + '&page=0&count=1'
    else:
        # If you search user by nickname, then the user matched with highest rank will come out
        query = 'name=' + quote(name) + '&page=0&count=1'
    result = await fetch(page='/MineSweepingWar/user/search', query=query)
    return result

async def get_user_career(uid):
    query = 'uid=' + quote(uid)
    result = await fetch(page='/MineSweepingWar/game/timing/career', query=query)
    return result

async def get_user_info(search_result):
    uid = search_result['uid']

    # basic info
    user_info = {}
    user_info['nickname'] = search_result['nickName']
    user_info['sex'] = search_result['sex'] 
    user_info['level'] = search_result['timingLevel']
    user_info['rank'] = search_result['timingRank']
    user_info['id'] = search_result['id']

    # career info
    career_result = await get_user_career(uid)
    user_info['stat'] = {}
    user_info['stat']['best_beg_time'] = format_number(career_result['data']['begTimeRank']['time'] / 1000)
    user_info['stat']['best_beg_time_rank'] = format_number(career_result['data']['begTimeRank']['rank'])
    user_info['stat']['best_beg_bvs'] = format_number(career_result['data']['begBvsRank']['bvs'])
    user_info['stat']['best_beg_bvs_rank'] = format_number(career_result['data']['begBvsRank']['rank'])

    user_info['stat']['best_int_time'] = format_number(career_result['data']['intTimeRank']['time'] / 1000)
    user_info['stat']['best_int_time_rank'] = format_number(career_result['data']['intTimeRank']['rank'])
    user_info['stat']['best_int_bvs'] = format_number(career_result['data']['intBvsRank']['bvs'])
    user_info['stat']['best_int_bvs_rank'] = format_number(career_result['data']['intBvsRank']['rank'])

    user_info['stat']['best_exp_time'] = format_number(career_result['data']['expTimeRank']['time'] / 1000)
    user_info['stat']['best_exp_time_rank'] = format_number(career_result['data']['expTimeRank']['rank'])
    user_info['stat']['best_exp_bvs'] = format_number(career_result['data']['expBvsRank']['bvs'])
    user_info['stat']['best_exp_bvs_rank'] = format_number(career_result['data']['expBvsRank']['rank'])

    user_info['stat']['total_time'] = format_number(career_result['data']['totalTimeRank']['time'] / 1000)
    user_info['stat']['total_time_rank'] = format_number(career_result['data']['totalTimeRank']['rank'])
    user_info['stat']['total_bvs'] = format_number(career_result['data']['totalBvsRank']['bvs'])
    user_info['stat']['total_bvs_rank'] = format_number(career_result['data']['totalBvsRank']['rank'])

    if career_result['data']['statistics']:
        user_info['stat']['beg_win_total'] = career_result['data']['statistics']['begSum']
        user_info['stat']['beg_total'] = career_result['data']['statistics']['begSum'] + career_result['data']['statistics']['begFail']
        user_info['stat']['beg_win_rate'] = user_info['stat']['beg_win_total'] / user_info['stat']['beg_total'] * 100 if user_info['stat']['beg_total'] > 0 else 0.0

        user_info['stat']['int_win_total'] = career_result['data']['statistics']['intSum']
        user_info['stat']['int_total'] = career_result['data']['statistics']['intSum'] + career_result['data']['statistics']['intFail']
        user_info['stat']['int_win_rate'] = user_info['stat']['int_win_total'] / user_info['stat']['int_total'] * 100 if user_info['stat']['int_total'] > 0 else 0.0

        user_info['stat']['exp_win_total'] = career_result['data']['statistics']['expSum']
        user_info['stat']['exp_total'] = career_result['data']['statistics']['expSum'] + career_result['data']['statistics']['expFail']
        user_info['stat']['exp_win_rate'] = user_info['stat']['exp_win_total'] / user_info['stat']['exp_total'] * 100 if user_info['stat']['exp_total'] > 0 else 0.0
    else:
        user_info['stat']['beg_win_total'], user_info['stat']['int_win_total'], user_info['stat']['exp_win_total'] = 0, 0, 0
        user_info['stat']['beg_total'], user_info['stat']['int_total'], user_info['stat']['exp_total'] = 0, 0, 0
        user_info['stat']['beg_win_rate'], user_info['stat']['int_win_rate'], user_info['stat']['exp_win_rate'] = 0.0, 0.0, 0.0     
    
    user_info_message = format_user_info(user_info)
    return user_info_message

@on_command('idsearch', aliases=('查询', '查找', 'id'), permission=SUPERUSER | GROUP, only_to_me=False)
async def idsearch(session: CommandSession):
    _id = session.get('id')
    search_result = await get_user_info_by_id(_id)
    await session.send(search_result)

@idsearch.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['id'] = stripped_arg
        else:
            session.state['id'] = None
        return

async def get_user_info_by_id(_id: str) -> str: 
    if not is_online():
        return '账号处于离线状态，无法使用该功能'
    try:
        int(_id) # literal check for integer    
        search_result = await search_user(_id)
        user_info = await get_user_info(search_result['data'][0])
        return user_info
    except (TypeError, ValueError) as e:
        logger.error(traceback.format_exc())
        return '非法的ID输入'
    except Exception as e:
        logger.error(traceback.format_exc())
        return '无法查找到该用户'

@on_command('namesearch', aliases=('昵称', 'name', 'nickname'), permission=SUPERUSER | GROUP, only_to_me=False)
async def namesearch(session: CommandSession):
    nickname = session.get('nickname')
    search_result = await get_user_info_by_nickname(nickname)
    await session.send(search_result)

@namesearch.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['nickname'] = stripped_arg
        else:
            session.state['nickname'] = ''
        return

async def get_user_info_by_nickname(nickname: str) -> str:  
    if not is_online():
        return '账号处于离线状态，无法使用该功能'
    try:    
        search_result = await search_user(nickname, padding=False)
        user_info = await get_user_info(search_result['data'][0])
        return user_info
    except Exception as e:
        logger.error(traceback.format_exc())
        return '无法查找到该用户'
