"""
Commands for superuser only.

Please handle these commands with great care.
"""

import traceback

from nonebot.adapters import Event
from nonebot.log import logger
from nonebot_plugin_alconna import on_alconna, Alconna, Args, Arparma

from littlefish._db import commit, load, save
from littlefish._game import MemberManager
from littlefish._policy.rule import check, is_in_group

save_to_disk = on_alconna(Alconna(['save', '存档']), rule=check('supercmd'))

repeater_status = on_alconna(Alconna(['repeaterstatus', '复读状态']), rule=check('supercmd') & check('exclaim') & is_in_group)

alc_bwchanger = Alconna(['blockword', '复读屏蔽词'], Args['option', ['+', '-']]['word', str])
block_word_changer = on_alconna(alc_bwchanger, rule=check('supercmd') & check('exclaim') & is_in_group)

alc_rpchanger = Alconna(['repeaterparam', '复读参数'], Args['mutate_prob', int]['cut_in_prob', int])
repeater_param_changer = on_alconna(alc_rpchanger, rule=check('supercmd') & check('exclaim') & is_in_group)

alc_cschanger = Alconna(['changescore42', '改变42点得分'], Args['target', int]['option', ['+', '-']]['change', int])
calc42_score_changer = on_alconna(alc_cschanger, rule=check('supercmd') & check('exclaim'))


@save_to_disk.handle()
async def _():
    """Save the database on disk manually."""
    result = await commit()
    if result:
        await save_to_disk.send(message='存档成功~')
    else:
        await save_to_disk.send(message='存档失败，请检查日志文件~')


@repeater_status.handle()
async def _(event: Event):
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
    block_status = f'复读状态: [{combo}]-[{left_increment}|{msg_base}|{right_increment}]-[{mutate_prob}%|{cut_in_prob}%]\n'
    block_word = f'当前屏蔽词: {block_message}'
    await repeater_status.send(message=block_status + block_word)


@block_word_changer.handle()
async def _(event: Event, result: Arparma):
    """Handle the blockword command."""
    universal_id = str(event.self_id) + str(event.group_id)
    wordlist = load(universal_id, 'block_wordlist')
    wordlist = set(wordlist) if wordlist else set()
    operation = {
        '+': lambda x: wordlist.add(x),
        '-': lambda x: wordlist.remove(x),
    }

    operator = result.option
    operand = str(result.word)
    try:
        operation[operator](operand)  # add or remove the word
        save(universal_id, 'block_wordlist', list(wordlist))
        await block_word_changer.send(message='复读屏蔽词更新成功~')
    except Exception:
        logger.error(traceback.format_exc())
        await block_word_changer.send(message='复读屏蔽词更新失败，请检查日志文件~')


@repeater_param_changer.handle()
async def _(event: Event, result: Arparma):
    """Set the parameters of the repeater."""
    universal_id = str(event.self_id) + str(event.group_id)
    mutate_prob = min(max(result.mutate_prob, 0), 100)
    cut_in_prob = min(max(result.cut_in_prob, 0), 100)

    save(universal_id, 'mutate_probability', mutate_prob)
    save(universal_id, 'cut_in_probability', cut_in_prob)
    message = f'复读参数设定成功，当前变形概率为{mutate_prob}%，打断概率为{cut_in_prob}%'
    await repeater_param_changer.send(message=message)


@calc42_score_changer.handle()
async def _(event: Event, result: Arparma):
    """Change the calc42 game's score of a person manually."""
    universal_id = str(event.self_id) + str(event.group_id)
    member_manager = MemberManager(universal_id)
    multiplier = {'+': 1, '-': -1}

    target = str(result.target)
    option = result.option
    change = result.change
    before, after = member_manager.change_game_score(target, '42score', change * multiplier[option])
    message = f'42点得分修改成功({before} -> {after})'
    await calc42_score_changer.send(message=message)
