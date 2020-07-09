from nonebot import on_command, CommandSession, scheduler
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from urllib.parse import quote, unquote
from apscheduler.triggers.date import DateTrigger
from .core import fetch, is_online
from .global_value import * #CURRENT_ID_COLDING_LIST
import traceback
import datetime

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
    line.append('雷网主页: %s' % user_info['lw_url'])
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()

async def search_user(name):
    query = 'name=' + quote(name) + '&page=0&count=1'
    result = await fetch(page='/MineSweepingWar/user/search', query=query)
    return result

async def get_user_career(uid):
    query = 'uid=' + quote(uid)
    result = await fetch(page='/MineSweepingWar/game/timing/career', query=query)
    return result

async def get_user_home_info(uid):
    query = 'targetUid=' + quote(uid)
    result = await fetch(page='/MineSweepingWar/user/home', query=query)
    return result

async def get_user_info(name):
    search_result = await search_user(name)
    if len(search_result['data']) == 0:
        return {}
    else:
        uid = search_result['data'][0]['uid']

    # basic info
    user_info = {}
    user_info['nickname'] = search_result['data'][0]['nickName']
    user_info['sex'] = search_result['data'][0]['sex'] 
    user_info['level'] = search_result['data'][0]['timingLevel']
    user_info['rank'] = search_result['data'][0]['timingRank']
    user_info['id'] = search_result['data'][0]['id']

    # home info
    home_info_result = await get_user_home_info(uid)
    if home_info_result['data']['saoleiOauth']:
        user_info['lw_url'] = '(%s) http://saolei.wang/Player/Index.asp?Id=%s' % (home_info_result['data']['saoleiOauth']['name'].strip(), home_info_result['data']['saoleiOauth']['openId'].strip())
    else:
        user_info['lw_url'] = '暂未关联'

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
    
    return user_info

def remove_id_from_colding_list(group_id, user_id):
    if user_id in CURRENT_ID_COLDING_LIST[group_id]:
        CURRENT_ID_COLDING_LIST[group_id].remove(user_id)

@on_command('info', aliases=('查询', '查找', 'search', 'id', 'name'), permission=SUPERUSER | GROUP, only_to_me=False)
async def info(session: CommandSession):
    if session.event['message_type'] == 'group':
        group_id = session.event['group_id']
        if group_id not in CURRENT_ID_COLDING_LIST:
            CURRENT_ID_COLDING_LIST[group_id] = []
        name = session.get('name')
        user_info = await get_user_info(name)
        if user_info:
            searched_user_id = user_info['id']
            if searched_user_id not in CURRENT_ID_COLDING_LIST[group_id]:
                user_info_message = format_user_info(user_info)
                await session.send(user_info_message)
                CURRENT_ID_COLDING_LIST[group_id].append(searched_user_id)
                
                delta = datetime.timedelta(hours=1)
                trigger = DateTrigger(run_date=datetime.datetime.now() + delta)
                scheduler.add_job(
                    func=remove_id_from_colding_list,
                    trigger=trigger,
                    args=(group_id, searched_user_id),
                    misfire_grace_time=30,
                )
        else:
            await session.send('无法查找到该用户')

@info.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg and stripped_arg[0] == '%':
            stripped_arg = ' ' * 20 + stripped_arg[1:]
        session.state['name'] = stripped_arg
