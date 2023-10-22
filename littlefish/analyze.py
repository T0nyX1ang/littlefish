"""
Analyze a minesweeper game from post_id or record_id.

Available information:
* board info, action info.
"""

import time
import traceback

from nonebot import on_keyword
from nonebot.adapters import Event
from nonebot.log import logger
from nonebot_plugin_alconna import on_alconna, Alconna, Args, Arparma

from littlefish._mswar.api import get_record
from littlefish._mswar.references import level_ref
from littlefish._policy.rule import check


def format_record(record: dict) -> str:
    """Formatter for information."""
    line = [
        f"playerID: {record['uid']} ({level_ref[record['level']]}{record['rank']})",
        f"mode: {'UPK ' * record['upk']}{record['difficulty']} ({record['style']})",
        f"time/est: {record['rtime']:.3f}/{record['est']:.3f}",
        f"bv/bvs: {record['solved_bv']}/{record['bv']:.3f}, {record['bvs']:.3f}",
        f"ce/ces: {record['ce']:.3f}, {record['ces']:.3f}",
        f"cl/cls: {record['cl']:.3f}, {record['cls']:.3f}",
        f"l/fl/r/d: {record['left']}, {record['flags']}, {record['right']}, {record['double']}",
        f"op/is: {record['solved_op']}/{record['op']}, {record['is']}",
        f"path: {record['path']:.3f}",
        f"ioe/iome: {record['ioe']:.3f}, {record['iome']:.3f}",
        f"corr/thrp: {record['corr']:.3f}, {record['thrp']:.3f}",
        f"rqp/qg: {record['rqp']:.3f}, {record['qg']:.3f}",
    ]

    if record['difficulty'] in ['beg', 'int', 'exp-h', 'exp-v']:
        line.append(f"stnb: {record['stnb']:.3f}")

    result_message = ""
    for each_line in line:
        result_message = result_message + each_line + "\n"
    return result_message.strip()


record_ref = {'record': False, 'r': False, '录像': False, 'post': True, 'p': True, '帖子': True}
analyzer = on_alconna(Alconna(['analyze', '分析'], Args["use_post_id", record_ref]["id", int]), rule=check('analyze'))

record_pusher = on_keyword(keywords={'http://tapsss.com'}, rule=check('analyze'), priority=10, block=True)


@analyzer.handle()
async def _(result: Arparma):
    """Handle the analyze command."""
    use_post_id = result.use_post_id
    _id = result.id

    try:
        record_info = await get_record(_id, use_post_id)
        await analyzer.send(message=format_record(record_info))
    except TypeError:
        # indicates the message can't be found from the remote server
        await analyzer.send(message='无法查询到录像信息')


@record_pusher.handle()
async def _(event: Event):
    """Handle the analyze command by URL shares."""
    msg = str(event.message).strip()
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
            await record_pusher.finish(message=format_record(record_info))
        except TypeError:
            logger.error(traceback.format_exc())
            remaining_retries -= 1
            time.sleep(1)
