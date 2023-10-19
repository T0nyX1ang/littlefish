"""
A method to push live message in groups.

The information includes:
nickname, liveroom_url, liveroom_title of a subscribed user.

The command requires to be invoked in groups.
"""

import traceback
import httpx
import nonebot
from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from littlefish._policy.rule import check, broadcast, is_in_group
from littlefish._db import load, save

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler


def _initialize_subscribed_list(universal_id: str, _type: str):
    """Initialize the subscribed list."""
    subscribed_list = load(universal_id, _type, {})
    return subscribed_list


async def get_user_info(uid: str) -> dict:
    """Get the bilibili user info from UID."""
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com/'}
    url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
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
    subscribed_list = _initialize_subscribed_list(universal_id, 'subscribed_list')
    global_subscribed_list = _initialize_subscribed_list('0', 'global_subscribed_list')

    uids = tuple(subscribed_list.keys())
    if not uids:
        return

    uid = uids[0]  # get the first item in the subscribed list

    if uid in global_subscribed_list:
        status = global_subscribed_list[uid]['status']  # fetch the status from the global list
    else:
        status = await get_user_info(uid)  # fetch the status first
        global_subscribed_list[uid] = {}
        global_subscribed_list[uid]['status'] = status  # assign the status to the global list

    # refresh the active counter
    global_subscribed_list[uid]['active'] = 5

    status = await get_user_info(uid)
    if status['live_status'] and not subscribed_list[uid]:
        # convert f-string
        url_msg = f"订阅用户{status['name']}开播了~\n"
        title_msg = f"直播标题: {status['live_title']}\n"
        share_msg = f"直播地址: {status['live_room_url']}"
        message = url_msg + title_msg + share_msg
        # post the subscribe message
        await bot.send_group_msg(group_id=group_id, message=message)

    subscribed_list.pop(uid)  # pop the first item in the subscribed list
    subscribed_list[uid] = status['live_status']  # update the live status and move the item to the end
    save(universal_id, 'subscribed_list', subscribed_list)
    save('0', 'global_subscribed_list', global_subscribed_list)


subscriber = on_command(cmd='subscribe', aliases={'订阅用户'}, force_whitespace=True, rule=check('bilipush') & is_in_group)


@subscriber.handle()
async def _(event: Event):
    """Handle the subscribe command."""
    universal_id = str(event.self_id) + str(event.group_id)
    subscribed_list = load(universal_id, 'subscribed_list', {})

    operation = {
        '+': lambda x: subscribed_list.setdefault(x, False),
        '-': lambda x: subscribed_list.pop(x),
    }

    arg = str(event.message).strip()
    try:
        operator = arg[1]
        operand = str(int(arg[2:].strip()))
        operation[operator](operand)  # add or remove the word
        save(universal_id, 'subscribed_list', subscribed_list)
        await subscriber.send(message='订阅用户信息更新成功~')
    except Exception:
        logger.error(traceback.format_exc())
        await subscriber.send(message='订阅用户信息更新失败，请检查日志文件~')


@broadcast('bilipush')
async def _(bot_id: str, group_id: str):
    """Push the live message."""
    try:
        bot = nonebot.get_bots()[bot_id]
        universal_id = str(bot_id) + str(group_id)
        await push_live_message(bot, universal_id)
    except Exception:
        logger.error(traceback.format_exc())


@scheduler.scheduled_job('cron', second='10,30,50', misfire_grace_time=5)
async def update_live_info():
    """Update the live info of bilipush every 20 seconds."""
    # the global subscribed list, contains full information
    global_subscribed_list = _initialize_subscribed_list('0', 'global_subscribed_list')

    uid = None
    for uid in tuple(global_subscribed_list.keys()):
        if global_subscribed_list[uid]['active'] <= 0:  # inactive check
            global_subscribed_list.pop(uid)  # pop the uid if it's not active
            uid = None
            continue
        break

    if not uid:
        return  # if no uid is left after the active check, or the subscribed list doesn't contain any uid.

    info = global_subscribed_list.pop(uid)  # pop the first item in the subscribed list
    global_subscribed_list[uid] = info
    global_subscribed_list[uid]['active'] -= 1  # decrease the active counter
    global_subscribed_list[uid]['status'] = await get_user_info(uid)  # update the status
    save('0', 'global_subscribed_list', global_subscribed_list)
