"""
Commands for superuser only.

Please handle these commands with great care.
"""

import traceback
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from littlefish._db import commit, load, save
from littlefish._policy import check

save_to_disk = on_command(cmd='save', aliases={'存档'}, rule=check('supercmd'))

repeater_status = on_command(cmd='repeaterstatus ', aliases={'复读状态 '},
                             rule=check('supercmd') & check('group'))

block_word = on_command(cmd='blockword ', aliases={'复读屏蔽词 '},
                        rule=check('supercmd') & check('group'))

set_repeater_param = on_command(cmd='repeaterparam ', aliases={'复读参数 '},
                                rule=check('supercmd') & check('group'))


@save_to_disk.handle()
async def save_to_disk(bot: Bot, event: Event, state: dict):
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
    block_wordlist = load(universal_id, 'block_wordlist')
    if not combo:
        combo = 0

    if not mutate_prob:
        mutate_prob = 5

    if not cut_in_prob:
        cut_in_prob = 5

    block_message = '空' if not block_wordlist else ', '.join(block_wordlist)
    message = '复读状态: [%d]-[%s|%s|%s]-[%d%%|%d%%]\n当前屏蔽词: %s' % (
        combo, left_increment, msg_base, right_increment,
        mutate_prob, cut_in_prob, block_message
    )

    await bot.send(event=event, message=message)


@block_word.handle()
async def block_word(bot: Bot, event: Event, state: dict):
    """Handle the blockword command."""
    universal_id = str(event.self_id) + str(event.group_id)
    wordlist = load(universal_id, 'block_wordlist')
    wordlist = set(wordlist) if wordlist else set()
    operation = {
        '+': lambda x: wordlist.add(x),
        '-': lambda x: wordlist.remove(x),
    }

    arg = str(event.message).strip()
    operator = arg[0]
    operand = arg[1:].strip()
    try:
        operation[operator](operand)  # add or remove the word
        save(universal_id, 'block_wordlist', list(wordlist))
        await bot.send(event=event, message='复读屏蔽词更新成功~')
    except Exception:
        logger.error(traceback.format_exc())
        await bot.send(event=event, message='复读屏蔽词更新失败，请检查日志文件~')


@set_repeater_param.handle()
async def set_repeater_param(bot: Bot, event: Event, state: dict):
    """Set the parameters of the repeater."""
    universal_id = str(event.self_id) + str(event.group_id)
    try:
        args = map(int, str(event.message).split())
        mutate_prob = min(max(next(args), 0), 100)
        cut_in_prob = min(max(next(args), 0), 100)
        save(universal_id, 'mutate_probability', mutate_prob)
        save(universal_id, 'cut_in_probability', cut_in_prob)
        message = '复读参数设定成功，当前变形概率为%d%%，打断概率为%d%%' % (
            mutate_prob, cut_in_prob
        )
        await bot.send(event=event, message=message)
    except Exception:
        await bot.send(event=event, message='复读参数设定失败，请重试')
