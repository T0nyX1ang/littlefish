from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from urllib.parse import quote, unquote
from .core import fetch, is_online
import traceback

async def get_classic_rank(_type=0, begin=1, end=10, mode=-1, level=4):
    if end - begin >= 20:
        raise ValueError('最大查询间隔为 20, 目前查询间隔为 %d' % (end - begin + 1))
    result = ''
    current = begin
    while current <= end:
        query = 'type=%d&mode=%d&level=%d&page=%d&count=1' % (_type, mode, level, current - 1)
        current_player = await fetch(page='/MineSweepingWar/rank/timing/list', query=query)
        if current_player['data']:
            if _type == 1:
                current_message = '%d: %s(Id: %d) - %.3f' % (current, current_player['data'][0]['user']['nickName'], current_player['data'][0]['user']['id'], current_player['data'][0]['bvs'])
            else:
                current_message = '%d: %s(Id: %d) - %.3f' % (current, current_player['data'][0]['user']['nickName'], current_player['data'][0]['user']['id'], current_player['data'][0]['time'] / 1000)
        else:
            current_message = '%d: -' % (current)
        result = result + current_message + '\n'
        current += 1
    return result.strip()

async def get_endless_rank():
    query = 'page=0&count=10'
    endless_rank = await fetch(page='/MineSweepingWar/rank/endless/list', query=query)
    current_message = ''
    for each_player in endless_rank['data']:
        current_message += '%d: %s (Id: %d) - 通过 %d 关' % (each_player['rank'], each_player['user']['nickName'], each_player['user']['id'], each_player['stage']) + '\n'
    return current_message.strip()

async def get_nonguessing_rank():
    query = 'page=0&count=10'
    nonguessing_rank = await fetch(page='/MineSweepingWar/rank/nonguessing/list', query=query)
    current_message = ''
    for each_player in nonguessing_rank['data']:
        current_message += '%d: %s (Id: %d) - 通过 %d 关' % (each_player['rank'], each_player['user']['nickName'], each_player['user']['id'], each_player['stage']) + '\n'
    return current_message.strip()

async def get_coin_rank():
    query = 'page=0&count=10'
    coin_rank = await fetch(page='/MineSweepingWar/rank/coin/list', query=query)
    current_message = ''
    for each_player in coin_rank['data']:
        current_message += '%d: %s (Id: %d) - 获得 %d 币' % (each_player['rank'], each_player['user']['nickName'], each_player['user']['id'], each_player['stage']) + '\n'
    return current_message.strip()

async def get_chaos_rank():
    query = 'page=0&count=10'
    chaos_rank = await fetch(page='/MineSweepingWar/rank/chaos/list', query=query)
    current_message = ''
    for each_player in chaos_rank['data']:
        current_message += '%d: %s (Id: %d) - 获胜 %d 场' % (each_player['rank'], each_player['user']['nickName'], each_player['user']['id'], each_player['win']) + '\n'
    return current_message.strip()

async def get_advance_rank():
    query = 'page=0&count=10'
    advance_rank = await fetch(page='/MineSweepingWar/rank/timing/advance/list', query=query)
    current_message = ''
    for each_player in advance_rank['data']:
        current_message += '%d: %s (Id: %d) - 进步 %d 名' % (each_player['rank'], each_player['user']['nickName'], each_player['user']['id'], each_player['stage']) + '\n'
    return current_message.strip()

@on_command('ranking', aliases=('排名', 'rank'), permission=SUPERUSER | GROUP, only_to_me=False)
async def ranking(session: CommandSession):
    _type = session.get('type')
    begin = session.get('begin')
    end = session.get('end')
    mode = session.get('mode')
    level = session.get('level')
    rank_result = await get_rank(_type, begin, end, mode, level)
    await session.send(rank_result)

@ranking.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        session.state['type'] = 'time'
        session.state['begin'] = 1
        session.state['end'] = 10
        session.state['mode'] = 'all'
        session.state['level'] = 'all'
        if stripped_arg:
            stripped_arg_new = stripped_arg.replace('  ', ' ')
            while stripped_arg != stripped_arg_new:
                stripped_arg = stripped_arg_new
                stripped_arg_new = stripped_arg_new.replace('  ', ' ')    
            split_arg = stripped_arg.split(' ')
            argc = len(split_arg)
            if argc == 1:
                session.state['type'] = split_arg[0]
            elif argc == 3:
                session.state['type'] = split_arg[0]
                session.state['begin'] = split_arg[1]
                session.state['end'] = split_arg[2]
            elif argc == 5: 
                session.state['type'] = split_arg[0]
                session.state['begin'] = split_arg[1]
                session.state['end'] = split_arg[2]
                session.state['mode'] = split_arg[3]
                session.state['level'] = split_arg[4]
            else:
                session.finish('不正确的参数数目')
        return

async def get_rank(_type: str, begin: str, end: str, mode: str, level: str) -> str: 
    if not is_online():
        return '账号处于离线状态，无法使用该功能'
    try:
        type_ref = {'time': 0, '时间': 0, 't': 0, 
                    'bvs': 1, '3bvs': 1, 'b': 1, 
                    'endless': 2, '无尽': 2, 'e': 2,
                    'nonguessing': 3, '无猜': 3, 'n': 3,  
                    'coin': 4, '财富': 4, 'o': 4, 
                    'chaos': 5, '乱斗': 5, 'c': 5,
                    'advance': 6, '进步': 6, 'a': 6}
        mode_ref = {'all': -1, 'nf': 0, 'fl': 1, '全部': -1, '盲扫': 0, '标旗': 1, 'a': -1, 'n': 0, 'f': 1}
        level_ref = {'all': 4, 'beg': 1, 'int': 2, 'exp': 3, 'a': 4, 'b': 1, 'i': 2, 'e': 3, '全部': 4, '初级': 1, '中级': 2, '高级': 3}
        _type = type_ref[_type.lower()]
        if _type in [0, 1]:
            begin = int(begin)
            end = int(end)
            mode = mode_ref[mode.lower()]
            level = level_ref[level.lower()]
            rank = await get_classic_rank(_type, begin, end, mode, level)
        elif _type == 2:
            rank = await get_endless_rank()
        elif _type == 3:
            rank = await get_nonguessing_rank()
        elif _type == 4:
            rank = await get_coin_rank()
        elif _type == 5:
            rank = await get_chaos_rank()
        elif _type == 6:
            rank = await get_advance_rank()
        return rank
    except Exception as e:
        logger.error(traceback.format_exc())
        return '错误的语法指令'
