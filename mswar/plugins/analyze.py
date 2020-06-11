from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from urllib.parse import quote, unquote
from .core import fetch, is_online
from .mswar import get_board, get_action, get_result
from base64 import b64decode
import gzip
import traceback

def format_analyze_result(result: dict) -> str:
    line = ['mode: %dx%d + %d (%s)' % (result['row'], result['column'], result['mines'], result['fmode']),
            'time/est: %.3f/%.3f' % (result['rtime'], result['est']),
            'bv/bvs: %d/%d, %.3f' % (result['solved_bv'], result['bv'], result['bvs']),
            'ce/ces: %d, %.3f' % (result['ce'], result['ces']),
            'cl/cls: %d, %.3f' % (result['cl'], result['cls']),
            'l/fl/r/d: %d, %d, %d, %d' % (result['left'], result['flags'], result['right'], result['double']),
            'op/is: %d/%d, %d' % (result['solved_op'], result['op'], result['is']),
            'path: %.3f' % (result['path']),
            'ioe/iome: %.3f, %.3f' % (result['ioe'], result['iome']),
            'corr/thrp: %.3f, %.3f' % (result['corr'], result['thrp']),
            'rqp/qg: %.3f, %.3f' % (result['rqp'], result['qg'])]
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()

async def from_record_id(record_id: int) -> str:      
    record_file = await fetch(page='/MineSweepingWar/game/record/get', query='recordId=%d' % (record_id))
    board = get_board(record_file['data']['map'].split('-')[0: -1])
    action = get_action(gzip.decompress(b64decode(record_file['data']['handle'])).decode().split('-'))
    return get_result(board, action)

async def from_post_id(post_id: int) -> str:
    # First get the record ID, then use the former function to analyze.
    record_result = await fetch(page='/MineSweepingWar/post/get', query='postId=%d' % (post_id))
    result = await from_record_id(record_result['data']['recordId'])
    return result

@on_command('analyze', aliases=('分析'), permission=SUPERUSER | GROUP, only_to_me=False)
async def analyze(session: CommandSession):
    mode = session.get('mode')
    target_id = session.get('id')
    analyze_result = await get_analyze_result(mode, target_id)
    await session.send(analyze_result)

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
            else:
                session.finish('不正确的参数数目')
        return

async def get_analyze_result(mode: str, target_id: str) -> dict:
    try:
        mode_ref = {'record': True, 'r': True, '录像': True, 'post': False, 'p': False, '帖子': False}
        target_id = int(target_id)
        if mode_ref[mode]:
            result = await from_record_id(target_id)
        else:
            result = await from_post_id(target_id)
        return format_analyze_result(result)
    except Exception as e:
        logger.error(traceback.format_exc())
        return '错误的语法指令'

@on_natural_language(permission=SUPERUSER | GROUP, only_short_message=False, only_to_me=False)
async def _(session: NLPSession):
    stripped_msg = session.msg.strip()
    start_seq = stripped_msg.find('http://tapsss.com/?post=')
    if start_seq == -1:
        return IntentCommand(0.0, 'analyze')
    current = start_seq + 24
    post_id = ''
    while current < len(stripped_msg) and stripped_msg[current] in '0123456789':
        post_id += stripped_msg[current]
        current += 1
    post_id = int(post_id) # forcibly convert to int
    return IntentCommand(100.0, 'analyze', current_arg='post %d' % (post_id))
