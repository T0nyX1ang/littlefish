from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from urllib.parse import quote, unquote
from .core import fetch, is_online

def get_rank_core(begin=1, end=10, _type=0, mode=-1, level=4):
    if end - begin >= 20:
        raise ValueError('最大查询间隔为 20, 目前查询间隔为 %d' % (end - begin + 1))
    result = ''
    current = begin
    while current <= end:
        query = 'type=%d&mode=%d&level=%d&page=%d&count=1' % (_type, mode, level, current - 1)
        current_player = fetch(page='/MineSweepingWar/rank/timing/list', query=query)
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

@on_command('ranking', aliases=('排名', 'rank'), permission=SUPERUSER | GROUP, only_to_me=False)
async def ranking(session: CommandSession):
    begin = session.get('begin')
    end = session.get('end')
    _type = session.get('type')
    mode = session.get('mode')
    level = session.get('level')
    rank_result = await get_rank(begin, end, _type, mode, level)
    await session.send(rank_result)

@ranking.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        session.state['begin'] = 1
        session.state['end'] = 10
        session.state['type'] = 'time'
        session.state['mode'] = 'all'
        session.state['level'] = 'all'
        if stripped_arg:
            stripped_arg_new = stripped_arg.replace('  ', ' ')
            while stripped_arg != stripped_arg_new:
                stripped_arg = stripped_arg_new
                stripped_arg_new = stripped_arg_new.replace('  ', ' ')    
            split_arg = stripped_arg.split(' ')
            argc = len(split_arg)
            if argc == 2:
                session.state['begin'] = split_arg[0]
                session.state['end'] = split_arg[1]
            elif argc == 5: 
                session.state['begin'] = split_arg[0]
                session.state['end'] = split_arg[1]
                session.state['type'] = split_arg[2]
                session.state['mode'] = split_arg[3]
                session.state['level'] = split_arg[4]
            else:
                session.finish('不正确的参数数目')
        return

async def get_rank(begin: str, end: str, _type: str, mode: str, level: str) -> str: 
    if not is_online():
        return '账号处于离线状态，无法使用该功能'
    try:
        type_ref = {'time': 0, 'bvs': 1, '时间': 0, '3bvs': 1, 't': 0, 'b': 1}
        mode_ref = {'all': -1, 'nf': 0, 'fl': 1, '全部': -1, '盲扫': 0, '标旗': 1, 'a': -1, 'n': 0, 'f': 1}
        level_ref = {'all': 4, 'beg': 1, 'int': 2, 'exp': 3, 'a': 4, 'b': 1, 'i': 2, 'e': 3, '全部': 4, '初级': 1, '中级': 2, '高级': 3}
        begin = int(begin)
        end = int(end)
        _type = type_ref[_type.lower()]
        mode = mode_ref[mode.lower()]
        level = level_ref[level.lower()]
        return get_rank_core(begin, end, _type, mode, level)
    except Exception as e:
        return '错误的语法指令(error: %s)' % repr(e)