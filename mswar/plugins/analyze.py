from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from urllib.parse import quote, unquote
from .core import fetch, is_online
from .mswar import get_board, get_action, get_result
from .admire import get_admire_message
from base64 import b64decode
import gzip
import traceback
import time

def format_analyze_result(result: dict) -> str:
    line = [
        'mode: %s (%s)' % (result['difficulty'], result['fmode']),
        'time/est: %.3f/%.3f' % (result['rtime'], result['est']),
        'bv/bvs: %d/%d, %.3f' % (result['solved_bv'], result['bv'], result['bvs']),
        'ce/ces: %d, %.3f' % (result['ce'], result['ces']),
        'cl/cls: %d, %.3f' % (result['cl'], result['cls']),
        'l/fl/r/d: %d, %d, %d, %d' % (result['left'], result['flags'], result['right'], result['double']),
        'op/is: %d/%d, %d' % (result['solved_op'], result['op'], result['is']),
        'path: %.3f' % (result['path']),
        'ioe/iome: %.3f, %.3f' % (result['ioe'], result['iome']),
        'corr/thrp: %.3f, %.3f' % (result['corr'], result['thrp']),
        'rqp/qg: %.3f, %.3f' % (result['rqp'], result['qg']),
    ]
    if result['difficulty'] in ['beg', 'int', 'exp-h', 'exp-v']:
        line.append('stnb: %.3f' % result['stnb'])
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()

def format_user_result(result: dict) -> str:
    level_ref = {0: '-', 1: 'E', 2: 'D', 3: 'C', 4: 'B', 5: 'A', 6: 'S', 7: 'SS', 8: 'SSS', 9: '★', 10: '★★', -1: '雷帝'}
    result_message = ''
    if result['level'] != 0:
        result_message = '当前评价: %s 级, 排位第 %d 名' % (level_ref[result['level']], result['rank'])
    else:
        result_message = '未加入排名, 无评价'
    return result_message

async def from_record_id(record_id: int) -> str:   
    record_file = await fetch(page='/MineSweepingWar/game/record/get', query='recordId=%d' % (record_id))
    board = get_board(record_file['data']['map'].split('-')[0: -1])
    action = get_action(gzip.decompress(b64decode(record_file['data']['handle'])).decode().split('-'))

    user = {}
    user['level'] = record_file['data']['user']['timingLevel']
    user['rank'] = record_file['data']['user']['timingRank']

    return (get_result(board, action), user)

async def from_post_id(post_id: int) -> str:
    # First get the record ID, then use the former function to analyze.
    retries, fetched, result = 10, False, {}
    while not fetched and retries > 0:
        record_result = await fetch(page='/MineSweepingWar/post/get', query='postId=%d' % (post_id))
        if 'data' in record_result and record_result['data'] and 'recordId' in record_result['data']: 
            result = await from_record_id(record_result['data']['recordId'])
            fetched = True
        else:
            retries -= 1
            time.sleep(0.5)
    if retries == 0:
        raise ConnectionError('Unable to get record ID from post ID.')
    return result

@on_command('analyze', aliases=('分析'), permission=SUPERUSER | GROUP, only_to_me=False)
async def analyze(session: CommandSession):
    if not is_online():
        await session.send('账号处于离线状态，无法使用该功能')
        return 
    mode = session.get('mode')
    target_id = session.get('id')
    admire_person = session.get('admire_person')
    analyze_result = await get_analyze_result(mode, target_id)
    await session.send(analyze_result[0])

    if admire_person:
        await session.send(analyze_result[1])
        admire_message = get_admire_message(admire_person)
        await session.send(admire_message)

@analyze.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            stripped_arg_new = stripped_arg.replace('  ', ' ')
            while stripped_arg != stripped_arg_new:
                stripped_arg = stripped_arg_new
                stripped_arg_new = stripped_arg_new.replace('  ', ' ')    
            split_arg = stripped_arg.split(' ')
            argc = len(split_arg)
            if argc == 2:
                session.state['mode'] = split_arg[0]
                session.state['id'] = split_arg[1]
                session.state['admire_person'] = None
            elif argc >= 3:
                session.state['mode'] = split_arg[0]
                session.state['id'] = split_arg[1]
                admire_person = ''
                for i in range(2, argc):
                    admire_person += (split_arg[i] + ' ')
                session.state['admire_person'] = admire_person.strip()
            else:
                session.finish('不正确的参数数目')
        else:
            session.finish()

async def get_analyze_result(mode: str, target_id: str) -> str:
    try:
        mode_ref = {'record': True, 'r': True, '录像': True, 'post': False, 'p': False, '帖子': False}
        target_id = int(target_id)
        if mode_ref[mode]:
            result = await from_record_id(target_id)
        else:
            result = await from_post_id(target_id)
        return format_analyze_result(result[0]), format_user_result(result[1])
    except ConnectionError as e:
        logger.error(traceback.format_exc())
        return '无法查询到录像信息'    	
    except Exception as e:
        logger.error(traceback.format_exc())
        return '错误的语法指令'

@on_natural_language(permission=SUPERUSER | GROUP, only_short_message=False, only_to_me=False)
async def _(session: NLPSession):
    stripped_msg = session.msg.strip()
    keywords = stripped_msg.find('http://tapsss.com')
    start_seq = stripped_msg.find('post=')
    if keywords == -1 or start_seq == -1 or not is_online():
        return
    current = start_seq + 5
    post_id = ''
    while current < len(stripped_msg) and stripped_msg[current] in '0123456789':
        post_id += stripped_msg[current]
        current += 1
    post_id = int(post_id) # forcibly convert to int

    start_name = stripped_msg.find('恭喜')
    end_name = stripped_msg.find('刷新')
    if start_name != -1 and end_name != -1:
        admire_person = stripped_msg[start_name + 2:end_name]
        return IntentCommand(100.0, 'analyze', current_arg='post %d %s' % (post_id, admire_person))
    else:
        return IntentCommand(100.0, 'analyze', current_arg='post %d' % (post_id))
