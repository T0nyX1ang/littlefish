"""
Commands for superuser only.

Please handle these commands with great care.
"""

import traceback
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from littlefish._db import commit, load, save
from littlefish._policy.rule import check
from littlefish._policy.plugin import on_simple_command
from littlefish._game import MemberManager

save_to_disk = on_simple_command(cmd='save', aliases={'存档'}, rule=check('supercmd'))

repeater_status = on_simple_command(cmd='repeaterstatus', aliases={'复读状态'}, rule=check('supercmd') & check('repeat'))

block_word_changer = on_command(cmd='blockword ', aliases={'复读屏蔽词 '}, rule=check('supercmd') & check('repeat'))

repeater_param_changer = on_command(cmd='repeaterparam ', aliases={'复读参数 '}, rule=check('supercmd') & check('repeat'))

calc42_score_changer = on_command(cmd='changescore42 ', aliases={'改变42点得分 '}, rule=check('supercmd') & check('calc42'))


@save_to_disk.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Save the database on disk manually."""
    result = await commit()
    if result:
        await save_to_disk.send(message='存档成功~')
    else:
        await save_to_disk.send(message='存档失败，请检查日志文件~')


@repeater_status.handle()
async def _(bot: Bot, event: Event, state: dict):
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
    message = '复读状态: [%d]-[%s|%s|%s]-[%d%%|%d%%]\n当前屏蔽词: %s' % (combo, left_increment, msg_base, right_increment, mutate_prob,
                                                                cut_in_prob, block_message)

    await repeater_status.send(message=message)


@block_word_changer.handle()
async def _(bot: Bot, event: Event, state: dict):
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
        await block_word_changer.send(message='复读屏蔽词更新成功~')
    except Exception:
        logger.error(traceback.format_exc())
        await block_word_changer.send(message='复读屏蔽词更新失败，请检查日志文件~')


@repeater_param_changer.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Set the parameters of the repeater."""
    universal_id = str(event.self_id) + str(event.group_id)
    try:
        args = map(int, str(event.message).split())
        mutate_prob = min(max(next(args), 0), 100)
        cut_in_prob = min(max(next(args), 0), 100)
        save(universal_id, 'mutate_probability', mutate_prob)
        save(universal_id, 'cut_in_probability', cut_in_prob)
        message = '复读参数设定成功，当前变形概率为%d%%，打断概率为%d%%' % (mutate_prob, cut_in_prob)
        await repeater_param_changer.send(message=message)
    except Exception:
        await repeater_param_changer.send(message='复读参数设定失败，请重试')


@calc42_score_changer.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Change the calc42 game's score of a person manually."""
    universal_id = str(event.self_id) + str(event.group_id)
    member_manager = MemberManager(universal_id)
    args = str(event.message).split()
    multiplier = {'+': 1, '-': -1}
    try:
        user_id = str(int(args[0]))
        score = int(args[2])
        message = '42点得分修改成功(%d -> %d)' % member_manager.change_game_score(user_id, '42score', score * multiplier[args[1]])
        await calc42_score_changer.send(message=message)
    except Exception:
        await calc42_score_changer.send(message='42点得分修改失败，请重试')
