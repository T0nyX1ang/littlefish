"""
Analyze a minesweeper game from post_id or record_id.

Available information:
* board info, action info.
"""

import time
import traceback
from nonebot import on_command, on_endswith
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from littlefish._mswar.api import get_record
from littlefish._mswar.references import level_ref
from littlefish._policy import check
from littlefish._exclaim import exclaim_msg


def format_record(record: dict) -> str:
    """Formatter for information."""
    line = [
        'playerID: %d (%s%d)' % (
            record['uid'],
            level_ref[record['level']],
            record['rank'],
        ),
        'mode: %s%s (%s)' % ('UPK ' * record['upk'], record['difficulty'], record['style']),
        'time/est: %.3f/%.3f' % (record['rtime'], record['est']),
        'bv/bvs: %d/%d, %.3f' % (record['solved_bv'], record['bv'], record['bvs']),
        'ce/ces: %d, %.3f' % (record['ce'], record['ces']),
        'cl/cls: %d, %.3f' % (record['cl'], record['cls']),
        'l/fl/r/d: %d, %d, %d, %d' % (record['left'], record['flags'], record['right'], record['double']),
        'op/is: %d/%d, %d' % (record['solved_op'], record['op'], record['is']),
        'path: %.3f' % (record['path']),
        'ioe/iome: %.3f, %.3f' % (record['ioe'], record['iome']),
        'corr/thrp: %.3f, %.3f' % (record['corr'], record['thrp']),
        'rqp/qg: %.3f, %.3f' % (record['rqp'], record['qg']),
    ]
    if record['difficulty'] in ['beg', 'int', 'exp-h', 'exp-v']:
        line.append('stnb: %.3f' % record['stnb'])

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


analyzer = on_command(cmd='analyze ', aliases={'分析 '}, rule=check('analyze'))
record_pusher = on_endswith(msg='', priority=10, block=True, rule=check('analyze'))


@analyzer.handle()
async def analyze(bot: Bot, event: Event, state: dict):
    """Analyze the result."""
    args = str(event.message).split()
    id_type = {'record': False, 'r': False, '录像': False, 'post': True, 'p': True, '帖子': True}

    try:
        use_post_id = id_type[args[0]]
        _id = int(args[1])
        record_info = await get_record(_id, use_post_id)
        await bot.send(event=event, message=format_record(record_info))
    except TypeError:
        # indicates the message can't be found from the remote server
        await bot.send(event=event, message='无法查询到录像信息')
    except Exception:
        logger.error(traceback.format_exc())
        await bot.send(event=event, message=exclaim_msg('', '3', False, 1))


@record_pusher.handle()
async def push_record(bot: Bot, event: Event, state: dict):
    """Push the record."""
    msg = str(event.message).strip()
    msg = msg * ('http://tapsss.com' in msg)  # ensure the keyword located in the message
    current = msg.find('post=') + 5
    post_id = '0'
    # If it can't find 'post=', current will be 4. Then the loop works fine.
    while 4 < current < len(msg) and msg[current].isdecimal():
        post_id += msg[current]
        current += 1
    post_id = int(post_id)  # convert the id to an integer

    remaining_retries = 10
    while remaining_retries > 0 and post_id > 0:  # ensures query
        try:
            record_info = await get_record(post_id)
            await bot.send(event=event, message=format_record(record_info))
            return
        except Exception:
            logger.error(traceback.format_exc())
            remaining_retries -= 1
            time.sleep(1)
