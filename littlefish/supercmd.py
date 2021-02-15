"""
Commands for superuser only.

Please handle these commands with great care.
"""

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import SUPERUSER
from littlefish._db import commit, load
from littlefish._policy import check

save = on_command(cmd='save', aliases={'存档'}, permission=SUPERUSER,
                  rule=check('supercmd'))

repeater_status = on_command(cmd='repeaterstatus', aliases={'复读状态'},
                             permission=SUPERUSER, rule=check('supercmd'))

set_repeater_param = on_command(cmd='repeaterparam', aliases={'设定复读参数'},
                                permission=SUPERUSER, rule=check('supercmd'))


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
    mutate_prob = load(universal_id, 'mutate_probability')
    cut_in_prob = load(universal_id, 'cut_in_probability')

    message = '复读状态: [%s]-[%s|%s|%s]-[%d%%|%d%%]' % (
        combo, left_increment, msg_base, right_increment,
        mutate_prob, cut_in_prob
    )

    await bot.send(event=event, message=message)


@set_repeater_param.handle()
async def set_repeater_param(bot: Bot, event: Event, state: dict):
    """Set the parameters of the repeater."""
    universal_id = str(event.self_id) + str(event.group_id)
    try:
        load(universal_id, 'mutate_probability')
        load(universal_id, 'cut_in_probability')
        args = map(int, str(event.message).split())
        mutate_prob = min(max(next(args), 0), 100)
        cut_in_prob = min(max(next(args), 0), 100)
        save(universal_id, 'mutate_probability', mutate_prob)
        save(universal_id, 'cut_in_probability', cut_in_prob)
    except Exception:
        await bot.send(event=event, message='复读参数设定失败，请重试')
