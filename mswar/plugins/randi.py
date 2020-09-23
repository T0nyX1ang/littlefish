from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import check_policy
import traceback
import random

@on_command('randi', aliases=('随机数'), permission=SUPERUSER | GROUP, only_to_me=False)
async def randi(session: CommandSession):
    if not check_policy(session.event, 'randi'):
        session.finish('小鱼睡着了zzz~')

    begin = session.get('begin')
    end = session.get('end')
    count = session.get('count')
    allow_repeat = session.get('allow_repeat')
    randi_result = get_randi(begin, end, count, allow_repeat)
    await session.send(randi_result)

@randi.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        session.state['begin'] = 0
        session.state['end'] = 1
        session.state['count'] = 1
        session.state['allow_repeat'] = 1
        if stripped_arg:
            stripped_arg_new = stripped_arg.replace('  ', ' ')
            while stripped_arg != stripped_arg_new:
                stripped_arg = stripped_arg_new
                stripped_arg_new = stripped_arg_new.replace('  ', ' ')    
            split_arg = stripped_arg.split(' ')
            argc = len(split_arg)
            if argc == 1:
                session.state['end'] = split_arg[0]
            elif argc == 2:
                session.state['begin'] = split_arg[0]
                session.state['end'] = split_arg[1]
            elif argc == 3:
                session.state['begin'] = split_arg[0]
                session.state['end'] = split_arg[1]
                session.state['count'] = split_arg[2]
            elif argc == 4: 
                session.state['begin'] = split_arg[0]
                session.state['end'] = split_arg[1]
                session.state['count'] = split_arg[2]
                session.state['allow_repeat'] = split_arg[3]
            else:
                session.finish('不正确的参数数目')
        return

def get_randi(begin, end, count, allow_repeat):
    try:
        begin = int(begin)
        end = int(end)
        count = int(count) if 0 < int(count) <= 20 else 1
        allow_repeat = int(allow_repeat)
        number_range = range(begin, end + 1)
        if allow_repeat:
            result = [ random.sample(number_range, 1) for _ in range(0, count) ]
        else:
            result = random.sample(number_range, count)
        return '随机结果: ' + str(result).replace('[', '').replace(']', '').replace(',', '')
    except Exception as e:
        logger.error(traceback.format_exc())
        return '错误的语法指令'
