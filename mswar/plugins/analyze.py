from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from urllib.parse import quote, unquote
from .core import fetch, is_online
from .mswar import get_board, get_action, get_result
from base64 import b64decode
import gzip

def from_record_id(record_id: int) -> str:      
    record_file = fetch(page='/MineSweepingWar/game/record/get', query='recordId=%d' % (record_id))
    board = get_board(record_file['data']['map'].split('-')[0: -1])
    action = get_action(gzip.decompress(b64decode(record_file['data']['handle'])).decode().split('-'))
    return get_result(board, action)

def from_post_id(post_id: int) -> str:
    # First get the record ID, then use the former function to analyze.
    record_id = fetch(page='/MineSweepingWar/post/get', query='postId=%d' % (post_id))['data']['recordId']
    return from_record_id(record_id)

def format_analyze_result(result):
    line_1 = 'mode: %dx%d + %d' % (result['row'], result['column'], result['mines'])
    line_2 = 'time/est: %.3f/%.3f' % (result['rtime'], result['est'])
    line_3 = 'bv/bvs: %d/%d, %.3f' % (result['bv'], result['solved_bv'], result['bvs'])
    line_4 = 'op/is: %d/%d, %d' % (result['op'], result['solved_op'], result['is'])
    line_5 = 'l/r/d/fl: %d, %d, %d, %d' % (result['left'], result['right'], result['double'], result['flags'])
    line_6 = 'ces/cls: %.3f, %.3f' % (result['ces'], result['cls'])
    line_7 = 'rqp/qg: %.3f, %.3f' % (result['rqp'], result['qg'])
    line_8 = 'corr/thrp: %.3f, %.3f' % (result['corr'], result['thrp'])
    line_9 = 'path: %.3f' % (result['path'])
    line_10 = 'ioe/iome: %.3f, %.3f' % (result['ioe'], result['iome'])
    result_message = line_1 + '\n' + line_2 + '\n' + line_3 + '\n' + line_4 + '\n' + line_5 + '\n' + line_6 + '\n' + line_7 + '\n' + line_8 + '\n' + line_9 + '\n' + line_10
    return result_message

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
            result = from_record_id(target_id)
        else:
            result = from_post_id(target_id)
        return format_analyze_result(result)
    except Exception as e:
        return '错误的语法指令(error: %s)' % repr(e)