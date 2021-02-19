"""
A method to push live message in groups.

The pusher will be activated every 20 seconds.
"""

import httpx
import nonebot
import traceback
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from littlefish._policy import check, boardcast
from littlefish._db import load, save

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler


async def get_user_info(uid: str) -> dict:
    """Get the bilibili user info from UID."""
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.bilibili.com/'
    }
    url = 'https://api.bilibili.com/x/space/acc/info?mid=%s' % uid
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url=url, headers=headers)
            data = r.json()['data']
            result = {}
            result['name'] = data['name']
            result['live_room_url'] = data['live_room']['url']
            result['live_status'] = bool(data['live_room']['liveStatus'])
            return result
    except Exception:
        logger.error(traceback.format_exc())
        # return a default message if the bot fails to fetch the information
        return {'name': '', 'live_room_url': {}, 'live_status': False}


async def push_live_message(bot: Bot, universal_id: str, group_id: int):
    """Push the live message."""
    subscribed_list = load(universal_id, 'subscribed_list')
    if not subscribed_list:
        subscribed_list = {}
        save(universal_id, 'subscribed_list', subscribed_list)

    for uid in subscribed_list.keys():
        status = await get_user_info(uid)
        if status['live_status'] and not subscribed_list[uid]:
            message = '订阅用户[%s]开播了，直播间地址: %s' % (
                status['name'], status['live_room_url']
            )
            # post the subscribe message
            await bot.send_group_msg(group_id=group_id, message=message)
        subscribed_list[uid] = status['live_status']  # update the live status
        save(universal_id, 'subscribed_list', subscribed_list)


subscriber = on_command(cmd='subscribe ', aliases={'订阅用户 '},
                        rule=check('bilipush'))


@subscriber.handle()
async def subscriber(bot: Bot, event: Event, state: dict):
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


@scheduler.scheduled_job('cron', second='*/20', misfire_grace_time=30)
@boardcast('bilipush')
async def _(allowed: list):
    for bot_id, group_id in allowed:
        bot = nonebot.get_bots()[bot_id]
        universal_id = str(bot_id) + str(group_id)
        try:
            await push_live_message(bot, universal_id, group_id)
        except Exception:
            logger.error(traceback.format_exc())
