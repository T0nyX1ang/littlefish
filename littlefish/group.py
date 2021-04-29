"""
Group relevant commands.

Available features:
* check before a user joins the group
* say hello when a user joins the group
* say goodbye when a user leaves the group
* update group members' information (invoked every 4 hours automatically)
* set block wordlist when repeating

The command requires to be invoked in groups.
"""

import traceback
import nonebot
from nonebot import on_command, on_notice, on_request
from nonebot.adapters.cqhttp import (
    Bot,
    Event,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupRequestEvent,
)
from nonebot.log import logger
from littlefish._exclaim import exclaim_msg
from littlefish._mswar.api import get_user_info
from littlefish._mswar.references import level_ref
from littlefish._policy import check, broadcast, empty
from littlefish._db import save, load


async def update_group_members(bot: Bot, group_id: str):
    """Update group members' information and store it to the database."""
    logger.info('Updating group [%s] members ...' % group_id)
    universal_id = str(bot.self_id) + str(group_id)
    group_members_list = await bot.get_group_member_list(group_id=group_id)
    for m in group_members_list:
        group_member_info = await bot.get_group_member_info(group_id=group_id, user_id=m['user_id'])

        user_id = str(group_member_info['user_id'])

        # load the original information from the database
        members = load(universal_id, 'members')
        if not members:
            members = {}

        if user_id not in members:
            members[user_id] = {}
        members[user_id]['id'] = group_member_info['title']
        members[user_id]['nickname'] = group_member_info['nickname']
        members[user_id]['card'] = group_member_info['card']
        members[user_id].setdefault('42score', 0)

        # save the updated information to the database
        save(universal_id, 'members', members)


user_validator = on_request(priority=10, block=True, rule=check('group', GroupRequestEvent) & check('info', GroupRequestEvent))

say_hello = on_notice(priority=10, block=True, rule=check('group', GroupIncreaseNoticeEvent))

say_goodbye = on_notice(priority=10, block=True, rule=check('group', GroupDecreaseNoticeEvent))

black_room = on_command(cmd='blackroom ', aliases={'进入小黑屋 '}, rule=check('group'))

user_updater = on_command(cmd='updateuser', aliases={'更新群成员'}, rule=check('group') & check('supercmd') & empty())


@user_validator.handle()
async def validate_user(bot: Bot, event: Event, state: dict):
    """Handle the validate_user command. Admin privilege required."""
    if event.sub_type != 'add':
        return  # ignore invitations

    try:
        comment = str(event.comment)
        player_id = int(comment[comment.find('答案') + 3:].strip())
        user_info = await get_user_info(player_id, simple=True)
        message = '%s[%d](%s%d)申请加群了~' % (
            user_info['nickname'],
            user_info['uid'],
            level_ref[user_info['level']],
            user_info['rank'],
        )
        if 0 <= user_info['rank'] <= 2:
            raise PermissionError('Insufficient level.')
        await bot.send(event=event, message=message)
    except Exception:
        reason = '该联萌ID不符合要求，请检查输入~'
        await bot.set_group_add_request(flag=event.flag, sub_type='add', approve=False, reason=reason)


@say_hello.handle()
async def say_hello_on_entering(bot: Bot, event: Event, state: dict):
    """Handle the say_hello command."""
    universal_id = str(event.self_id) + str(event.group_id)
    join_id = f'{event.user_id}'
    members = load(universal_id, 'members')

    if event.user_id == event.self_id:  # the bot can not respond to itself
        return

    if join_id in members:  # this means the user has been a group member before
        await bot.send(event=event, message='欢迎大佬回归，希望大佬天天破pb~')
        return  # preserve former information

    await bot.send(event=event, message='欢迎大佬，希望大佬天天破pb~')

    # Creating a new user
    try:
        await update_group_members(bot, event.group_id)
    except Exception:
        logger.error(traceback.format_exc())


@say_goodbye.handle()
async def say_goodbye_on_leaving(bot: Bot, event: Event, state: dict):
    """Handle the say_goodbye command. Admin privilege required."""
    universal_id = str(event.self_id) + str(event.group_id)
    leave_id = f'{event.user_id}'
    members = load(universal_id, 'members')

    uid = members[leave_id]['id'] if leave_id in members and members[leave_id]['id'] else '未知'

    if event.user_id != event.self_id:  # the bot can not respond to itself
        await bot.send(event=event, message='有群员[Id: %s]跑路了QAQ' % uid)


@black_room.handle()
async def enter_black_room(bot: Bot, event: Event, state: dict):
    """Handle the blackroom command."""
    group_id = event.group_id
    user_id = event.user_id
    try:
        duration = int(str(event.message).strip())
    except Exception:
        await bot.send(event=event, message=exclaim_msg('', '3', False, 1))
        return

    # convert the duration in seconds
    duration = duration * 60 if 1 <= duration <= 43200 else 600
    try:
        await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=duration)
    except Exception:
        await bot.send(event=event, message='权限不足，无法使用小黑屋~')


@user_updater.handle()
async def update_user(bot: Bot, event: Event, state: dict):
    """Handle the updateuser command."""
    try:
        await update_group_members(bot, event.group_id)
        await bot.send(event=event, message='群成员信息更新成功~')
    except Exception:
        await bot.send(event=event, message='群成员信息更新失败，请检查日志文件~')


@broadcast('group')
async def _(bot_id: str, group_id: str):
    """Scheduled group member information update."""
    bot = nonebot.get_bots()[bot_id]
    try:
        await update_group_members(bot, group_id)
    except Exception:
        logger.error(traceback.format_exc())
