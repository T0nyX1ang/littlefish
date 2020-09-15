from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import fetch, is_enabled
from .mswar import get_board, get_action, get_result
from .global_value import THEME_RESOURCE
from base64 import b64encode, b64decode
import numpy
import cv2
import gzip
import traceback

def generate_board_picture(result: dict) -> str:
    row = result['row']
    column = result['column']
    board = result['board']
    status = result['current_status']
    for r in range(0, row):
        for c in range(0, column):
            if status[r][c] == 1:
                cur = THEME_RESOURCE[board[r][c]]
            elif status[r][c] == 0:
                if board[r][c] == '9' and result['solved_bv'] < result['bv']: # finished
                    cur = THEME_RESOURCE['mine']
                else:
                    cur = THEME_RESOURCE['normal']
            elif status[r][c] == -1:
                cur = THEME_RESOURCE['flag']
            elif status[r][c] == -2:
                cur = THEME_RESOURCE['boom']
            elif status[r][c] == -3:
                cur = THEME_RESOURCE['error']
            cimg = numpy.concatenate([cimg, cur], axis=1) if c > 0 else cur
        himg = numpy.concatenate([himg, cimg], axis=0) if r > 0 else cimg 
    _, buf = cv2.imencode('.png', himg)
    return 'base64://' + b64encode(buf).decode()

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

async def from_record_id(record_id: int) -> str:   
    record_file = await fetch(page='/MineSweepingWar/minesweeper/record/get', query='recordId=%d' % (record_id))
    board = get_board(record_file['data']['map'].split('-')[0: -1])
    action = get_action(gzip.decompress(b64decode(record_file['data']['handle'])).decode().split('-'))
    return get_result(board, action)

async def from_post_id(post_id: int) -> str:
    # First get the record ID, then use the former function to analyze.
    record_result = await fetch(page='/MineSweepingWar/post/get', query='postId=%d' % (post_id))
    if record_result['data']['recordType'] != 0:
        raise TypeError('Incorrect record type.')
    result = await from_record_id(record_result['data']['recordId'])
    return result

async def get_analyze_result(mode: str, target_id: str) -> str:
    try:
        mode_ref = {'record': True, 'r': True, '录像': True, 'post': False, 'p': False, '帖子': False}
        target_id = int(target_id)
        if mode_ref[mode]:
            result = await from_record_id(target_id)
        else:
            result = await from_post_id(target_id)
        return generate_board_picture(result), format_analyze_result(result)
    except Exception as e:
        logger.error(traceback.format_exc())
        return '无法查询到录像信息'

@on_command('analyze', aliases=('分析'), permission=SUPERUSER | GROUP, only_to_me=False)
async def analyze(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')
    mode = session.get('mode')
    target_id = session.get('id')
    analyze_result = await get_analyze_result(mode, target_id)
    await session.send('[CQ:image,file=%s]' % analyze_result[0])
    await session.send(analyze_result[1])

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
        else:
            session.finish()