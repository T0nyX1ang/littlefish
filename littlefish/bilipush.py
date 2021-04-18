"""
A method to push live message in groups.

The information includes:
nickname, liveroom_url, liveroom_title of a subscribed user.

The command requires to be invoked in groups.
"""

import httpx
import nonebot
import traceback
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from littlefish._policy import check, broadcast
from littlefish._db import load, save


async def get_user_info(uid: str) -> dict:
    """Get the bilibili user info from UID."""
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com/'}
    url = 'https://api.bilibili.com/x/space/acc/info?mid=%s' % uid
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url=url, headers=headers)
            data = r.json()['data']
            result = {}
            result['name'] = data['name']
            result['live_room_url'] = data['live_room']['url']
            result['live_status'] = bool(data['live_room']['liveStatus'])
            result['live_title'] = data['live_room']['title']
            return result
    except Exception:
        logger.error(traceback.format_exc())
        # return a default message if the bot fails to fetch the information
        default = {
            'name': '',
            'live_room_url': '',
            'live_status': False,
            'live_title': '',
        }
        return default


async def push_live_message(bot: Bot, universal_id: str):
    """Push the live message."""
    group_id = int(universal_id[len(str(bot.self_id)):])
    subscribed_list = load(universal_id, 'subscribed_list')
    if not subscribed_list:
        subscribed_list = {}
        save(universal_id, 'subscribed_list', subscribed_list)

    print(subscribed_list)
    uids = tuple(subscribed_list.keys())
    if not uids:
        return

    uid = uids[0]  # get the first item in the subscribed list
    status = await get_user_info(uid)
    if status['live_status'] and not subscribed_list[uid]:
        url_msg = '订阅用户%s开播了~\n' % status['name']
        share_msg = '[CQ:share,url=%s,title=订阅用户%s开播了~,content=%s]' % (status['live_room_url'], status['name'],
                                                                       status['live_title'])
        message = url_msg + share_msg
        # post the subscribe message
        await bot.send_group_msg(group_id=group_id, message=message)

    subscribed_list.pop(uid)  # pop the first item in the subscribed list
    subscribed_list[uid] = status['live_status']  # update the live status and move the item to the end
    print(subscribed_list)
    save(universal_id, 'subscribed_list', subscribed_list)


subscriber = on_command(cmd='subscribe ', aliases={'订阅用户 '}, rule=check('bilipush'))


@subscriber.handle()
async def subscriber_update(bot: Bot, event: Event, state: dict):
    """Handle the subscribe command."""
    universal_id = str(event.self_id) + str(event.group_id)
    subscribed_list = load(universal_id, 'subscribed_list')
    if not subscribed_list:
        subscribed_list = {}
        save(universal_id, 'subscribed_list', subscribed_list)

    operation = {
        '+': lambda x: subscribed_list.setdefault(x, False),
        '-': lambda x: subscribed_list.pop(x),
    }

    arg = str(event.message).strip()
    try:
        operator = arg[0]
        operand = str(int(arg[1:].strip()))
        operation[operator](operand)  # add or remove the word
        save(universal_id, 'subscribed_list', subscribed_list)
        await bot.send(event=event, message='订阅用户信息更新成功~')
    except Exception:
        logger.error(traceback.format_exc())
        await bot.send(event=event, message='订阅用户信息更新失败，请检查日志文件~')


@broadcast('bilipush')
async def bilipush_broadcast(bot_id: str, group_id: str):
    """Push the live message."""
    bot = nonebot.get_bots()[bot_id]
    universal_id = str(bot_id) + str(group_id)
    try:
        await push_live_message(bot, universal_id)
    except Exception:
        logger.error(traceback.format_exc())
