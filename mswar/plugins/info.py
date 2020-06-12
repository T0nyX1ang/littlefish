from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from urllib.parse import quote, unquote
from .core import fetch, is_online
import traceback

def format_user_info(user_info):
    sex_ref = {0: '', 1: 'GG', 2: 'mm'}
    level_ref = {0: '-', 1: 'E', 2: 'D', 3: 'C', 4: 'B', 5: 'A', 6: 'S', 7: 'SS', 8: 'SSS', 9: '★', 10: '★★', -1: '雷帝'}
    line_1 = user_info['nickname'] + ' (Id: %s)' % (str(user_info['id'])) + ' ' + sex_ref[user_info['sex']]
    if user_info['level'] != 0:
        line_2 = '初级记录: %.3f(%d) | %.3f(%d)' % (user_info['stat']['best_beg_time'] / 1000, user_info['stat']['best_beg_time_rank'], 
                                                     user_info['stat']['best_beg_bvs'], user_info['stat']['best_beg_bvs_rank'])
        line_3 = '初级局数: %d / %d (%.1f%%)' % (user_info['stat']['beg_win_total'], user_info['stat']['beg_total'], user_info['stat']['beg_win_total'] / user_info['stat']['beg_total'] * 100)
        line_4 = '中级记录: %.3f(%d) | %.3f(%d)' % (user_info['stat']['best_int_time'] / 1000, user_info['stat']['best_int_time_rank'], 
                                                     user_info['stat']['best_int_bvs'], user_info['stat']['best_int_bvs_rank'])
        line_5 = '中级局数: %d / %d (%.1f%%)' % (user_info['stat']['int_win_total'], user_info['stat']['int_total'], user_info['stat']['int_win_total'] / user_info['stat']['int_total'] * 100)
        line_6 = '高级记录: %.3f(%d) | %.3f(%d)' % (user_info['stat']['best_exp_time'] / 1000, user_info['stat']['best_exp_time_rank'], 
                                                     user_info['stat']['best_exp_bvs'], user_info['stat']['best_exp_bvs_rank'])
        line_7 = '高级局数: %d / %d (%.1f%%)' % (user_info['stat']['exp_win_total'], user_info['stat']['exp_total'], user_info['stat']['exp_win_total'] / user_info['stat']['exp_total'] * 100)
        line_8 = '评价: %s 级, 排位第 %d 名' % (level_ref[user_info['level']] , user_info['rank'])
        message = line_1 + '\n' + line_2 + '\n' + line_3 + '\n' + line_4 + '\n' + line_5 + '\n' + line_6 + '\n' + line_7 + '\n' + line_8
    else:
        line_2 = '未加入排名, 无评价'
        message = line_1 + '\n' + line_2
    return message

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
    user_info['stat']['best_beg_time'] = career_result['data']['begTimeRank']['time']
    user_info['stat']['best_beg_time_rank'] = career_result['data']['begTimeRank']['rank']
    user_info['stat']['best_beg_bvs'] = career_result['data']['begBvsRank']['bvs']
    user_info['stat']['best_beg_bvs_rank'] = career_result['data']['begBvsRank']['rank']

    user_info['stat']['best_int_time'] = career_result['data']['intTimeRank']['time']
    user_info['stat']['best_int_time_rank'] = career_result['data']['intTimeRank']['rank']
    user_info['stat']['best_int_bvs'] = career_result['data']['intBvsRank']['bvs']
    user_info['stat']['best_int_bvs_rank'] = career_result['data']['intBvsRank']['rank']

    user_info['stat']['best_exp_time'] = career_result['data']['expTimeRank']['time']
    user_info['stat']['best_exp_time_rank'] = career_result['data']['expTimeRank']['rank']
    user_info['stat']['best_exp_bvs'] = career_result['data']['expBvsRank']['bvs']
    user_info['stat']['best_exp_bvs_rank'] = career_result['data']['expBvsRank']['rank']

    if career_result['data']['statistics']:
        user_info['stat']['beg_win_total'] = career_result['data']['statistics']['begSum']
        user_info['stat']['beg_total'] = career_result['data']['statistics']['begSum'] + career_result['data']['statistics']['begFail']

        user_info['stat']['int_win_total'] = career_result['data']['statistics']['intSum']
        user_info['stat']['int_total'] = career_result['data']['statistics']['intSum'] + career_result['data']['statistics']['intFail']

        user_info['stat']['exp_win_total'] = career_result['data']['statistics']['expSum']
        user_info['stat']['exp_total'] = career_result['data']['statistics']['expSum'] + career_result['data']['statistics']['expFail']

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