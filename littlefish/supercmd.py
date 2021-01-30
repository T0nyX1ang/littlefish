"""
Commands for superuser only.

Please handle these commands with great care.
"""

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import SUPERUSER
from littlefish._db import commit

save = on_command(cmd='save', aliases={'存档'}, permission=SUPERUSER)


@save.handle()
async def save(bot: Bot, event: Event, state: dict):
    """Save the database on disk manually."""
    result = await commit()
    if result:
        await bot.send(event=event, message='存档成功~')
    else:
        await bot.send(event=event, message='存档失败，请检查日志文件~')
