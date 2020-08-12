from nonebot import on_natural_language, NLPSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from urllib.parse import quote, unquote
from .analyze import from_record_id, format_analyze_result, generate_board_picture
from .core import fetch, is_enabled
from .exclaim import get_admire_message, get_cheer_message
import time
import traceback

def format_user_result(result: dict) -> str:
    level_ref = {0: '-', 1: 'E', 2: 'D', 3: 'C', 4: 'B', 5: 'A', 6: 'S', 7: 'SS', 8: 'SSS', 9: '★', 10: '★★', -1: '雷帝'}
    result_message = ''
    if result['level'] != 0:
        result_message = '当前评价: %s 级, 排位第 %d 名' % (level_ref[result['level']], result['rank'])
    else:
        result_message = '未加入排名, 无评价'
    return result_message

async def from_post_id_with_user(post_id: int) -> str:
    # First get the record ID, then use the former function to analyze.
    retries, fetched, result = 10, False, {}
    while not fetched and retries > 0:
        record_result = await fetch(page='/MineSweepingWar/post/get', query='postId=%d' % (post_id))
        if 'data' in record_result and record_result['data'] and ('recordId' and 'user' and 'recordType') in record_result['data'] and record_result['data']['recordType'] != 0: 
            result = await from_record_id(record_result['data']['recordId'])
            result['name'] = record_result['data']['user']['nickName']
            result['level'] = record_result['data']['user']['timingLevel']
            result['rank'] = record_result['data']['user']['timingRank']
            fetched = True
        else:
            retries -= 1
            time.sleep(1)
    if retries == 0:
        raise ConnectionError('Unable to get record ID from post ID.')
    return result

@on_natural_language(permission=SUPERUSER | GROUP, only_short_message=False, only_to_me=False)
async def _(session: NLPSession):
    stripped_msg = session.msg.strip()
    keywords = stripped_msg.find('http://tapsss.com')
    start_seq = stripped_msg.find('post=')
    if keywords == -1 or start_seq == -1 or not is_enabled(session.event):
        return
    current = start_seq + 5
    post_id = ''
    while current < len(stripped_msg) and stripped_msg[current] in '0123456789':
        post_id += stripped_msg[current]
        current += 1
    try:
        post_id = int(post_id) # forcibly convert to int
        result = await from_post_id_with_user(post_id)
        await session.send('[CQ:image,file=%s]' % generate_board_picture(result))
        await session.send(format_analyze_result(result))
        if '时间纪录' in stripped_msg:
            await session.send(format_user_result(result))
        if ('恭喜' and '刷新' and '纪录') in stripped_msg:
            await session.send(get_admire_message(result['name'], without_picture=False))
        if result['solved_bv'] < result['bv']:
            await session.send(get_cheer_message(result['name']))
    except Exception as e:
        logger.error(traceback.format_exc())
