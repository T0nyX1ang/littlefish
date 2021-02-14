"""
Commands for superuser only.

Please handle these commands with great care.
"""

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import SUPERUSER
from littlefish._db import commit, load

save = on_command(cmd='save', aliases={'存档'}, permission=SUPERUSER)

repeater_status = on_command(cmd='repeaterstatus', aliases={'复读状态'},
                             permission=SUPERUSER)


@save.handle()
async def save(bot: Bot, event: Event, state: dict):
    """Save the database on disk manually."""
    result = await commit()
    if result:
        await bot.send(event=event, message='存档成功~')
    else:
        await bot.send(event=event, message='存档失败，请检查日志文件~')


@repeater_status.handle()
async def repeater_status(bot: Bot, event: Event, state: dict):
    """Print the status of the repeater."""
    universal_id = str(event.self_id) + str(event.group_id)
    msg_base = load(universal_id, 'current_msg_base')
    left_increment = load(universal_id, 'current_left_increment')
    right_increment = load(universal_id, 'current_right_increment')
    combo = load(universal_id, 'current_combo')

    message = '复读状态: [%s]-(%s)+[%s]+(%s)' % (
        combo, left_increment, msg_base, right_increment
    )

    await bot.send(event=event, message=message)
