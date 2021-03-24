"""
A game to calculate 42 with 5 numbers between 0 and 13.

The rules can be found by invoking 'guide42' in groups.

The command requires to be invoked in groups.
"""

import nonebot
import traceback
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event, Message
from nonebot.log import logger
from littlefish._exclaim import exclaim_msg
from littlefish._policy import check, broadcast, empty, create, revoke
from littlefish._db import load, save
from littlefish._game.ftpts import init, start, solve, stop, current, status

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler


def get_member_name(universal_id: str, user_id: str) -> str:
    """Get member name."""
    members = load(universal_id, 'members')
    if not members:
        return '匿名大佬'

    return members[user_id]['card'] if members[user_id]['card'] else members[user_id]['nickname']


def print_current_problem(info: dict) -> str:
    """Print the current problem."""
    a, b, c, d, e = info['problem']
    return '本次%d点的题目为: %d %d %d %d %d' % (info['target'], a, b, c, d, e)


def get_deadline(total_number: int) -> int:
    """Get the deadline of current game."""
    return 180 * (1 + (total_number - 1) // 5) if total_number <= 20 else 900


def get_results(universal_id, result: dict) -> str:
    """Print the result of the game."""
    deadline = get_deadline(result['total'])

    bonus = 10 * (result['current'] == result['total'])  # AK Score
    victory_coeff = 1 - 1 / result['total']

    players = result['stats']
    scores, solutions, achievements = {}, {}, {}

    for i in range(len(players)):
        player_id, elapsed = players[i]

        # get player bouns score
        scores.setdefault(player_id, bonus)

        # get player solution
        solutions.setdefault(player_id, 0)

        # get player achievements
        achievements.setdefault(player_id, '')

        # calculate solution time
        time_elapsed = elapsed.seconds + elapsed.microseconds / 1000000
        solutions[player_id] += 1

        # Accumulate score
        time_ratio = time_elapsed / deadline
        solution_ratio = (i + 1) / result['total']

        t_score = 5 - int(5 * time_ratio)
        n_score = int(10 * (solution_ratio**(2 - time_ratio)))
        f_bonus = 5 * (i == 0)
        v_bonus = int(n_score * victory_coeff * (result['current'] == i + 1))
        scores[player_id] += (t_score + n_score + f_bonus + v_bonus)

    if players:
        achievements[players[0][0]] += 'F'
        achievements[players[-1][0]] += 'V'

    ordered = sorted(solutions, key=lambda k: solutions[k], reverse=True)

    # 50% AK bonus
    if ordered and solutions[ordered[0]] * 2 > result['total']:
        scores[ordered[0]] += solutions[ordered[0]]
        achievements[ordered[0]] += 'H'

    result_message = '本局%s点游戏结束~\n' % result['target']
    result_message += '求解完成度: %d/%d\n' % (result['current'], result['total'])
    result_message += '积分倍率: %d\n' % result['addscore']

    for player in ordered:
        members = load(universal_id, 'members')
        name = get_member_name(universal_id, player)
        result_message += '%s: %d解/+%d %s\n' % (name, solutions[player], scores[player], achievements[player])
        members[player]['42score'] += (scores[player] * result['addscore'])
        save(universal_id, 'members', members)

    return result_message.strip()


async def start_game(bot: Bot, universal_id: str, addscore: bool = True, enforce_random = False):
    """Start the calc42 game."""
    group_id = int(universal_id[len(str(bot.self_id)):])
    init(universal_id)
    result = start(universal_id, addscore, enforce_random)
    message = print_current_problem(result)
    deadline = get_deadline(result['total'])
    scheduler.add_job(
        func=finish_game,
        trigger='interval',
        seconds=deadline,
        args=(bot, universal_id),
        misfire_grace_time=30,
        id='calc42_process_%s' % universal_id,
        replace_existing=True,
    )
    scheduler.add_job(
        func=timeout_reminder,
        trigger='interval',
        seconds=deadline - 60,
        args=(bot, universal_id),
        misfire_grace_time=30,
        id='calc42_timeout_reminder_%s' % universal_id,
        replace_existing=True,
    )

    try:
        await bot.send_group_msg(group_id=group_id, message=message)
    except Exception:
        logger.error(traceback.format_exc())
        scheduler.remove_job('calc42_timeout_reminder_%s' % universal_id)
        scheduler.remove_job('calc42_process_%s' % universal_id)
        revoke('calc42_temp', str(bot.self_id), str(group_id))
        stop()  # stop the app instantly


async def timeout_reminder(bot: Bot, universal_id: str):
    """Reminder of the calc42 game."""
    group_id = int(universal_id[len(str(bot.self_id)):])
    if status(universal_id):
        try:
            message = '距离本局游戏结束还有60秒，冲鸭~'
            await bot.send_group_msg(group_id=group_id, message=message)
        except Exception:
            logger.error(traceback.format_exc())


async def finish_game(bot: Bot, universal_id: str):
    """Finish the calc42 game."""
    scheduler.remove_job('calc42_timeout_reminder_%s' % universal_id)
    scheduler.remove_job('calc42_process_%s' % universal_id)
    group_id = int(universal_id[len(str(bot.self_id)):])
    revoke('calc42_temp', str(bot.self_id), str(group_id))
    if status(universal_id):
        result = stop(universal_id)
        game_results = get_results(universal_id, result)
        try:
            await bot.send_group_msg(group_id=group_id, message=game_results)
            await show_solutions(bot, universal_id, result)
        except Exception:
            logger.error(traceback.format_exc())


async def show_solutions(bot: Bot, universal_id: str, result: dict):
    """Generate a message node from all solutions."""
    group_id = int(universal_id[len(str(bot.self_id)):])
    message = []
    for message_id in result['solve_id']:
        message.append({'type': 'node', 'data': {'id': message_id}})

    for remaining in result['remaining']:
        message.append({
            'type': 'node',
            'data': {
                'name': '小鱼',
                'uin': bot.self_id,
                'content': remaining,
            }
        })

    if message:
        await bot.send_group_forward_msg(group_id=group_id, messages=Message(message))


problem_solver = on_command(cmd='calc42 ', aliases={'42点 '}, rule=check('calc42'))

score_viewer = on_command(cmd='score42', aliases={'42点得分', '42点积分'}, rule=check('calc42') & empty())

rank_viewer = on_command(cmd='rank42', aliases={'42点排名', '42点排行'}, rule=check('calc42') & empty())

manual_player = on_command(cmd='manual42 ', aliases={'手动42点 '}, rule=check('calc42') & check('calc42_temp'))


@problem_solver.handle()
async def solve_problem(bot: Bot, event: Event, state: dict):
    """Handle the calc42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    if not status(universal_id):
        return

    user_id = f'{event.user_id}'
    expr = str(event.message).strip()
    message = ''

    result = solve(universal_id, expr, user_id, event.message_id)
    if result['hint']:
        message = result['hint']
    else:
        elapsed = int(result['elapsed'])
        left = get_deadline(result['total']) - elapsed
        message = '恭喜[%s]完成第%d/%d个解，完成时间: %.3f秒，剩余时间: %d秒~' % (get_member_name(
            universal_id, user_id), result['current'], result['total'], result['interval'], left)

    is_finished = (result['current'] == result['total'])
    message += (not is_finished) * ('\n%s' % print_current_problem(result))

    await bot.send(event=event, message=message)

    if is_finished:
        await finish_game(bot, universal_id)


@score_viewer.handle()
async def view_score(bot: Bot, event: Event, state: dict):
    """Handle the score42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    user_id = f'{event.user_id}'
    members = load(universal_id, 'members')
    ranking = sorted(members, key=lambda x: (members[x]['42score'], x), reverse=True)

    result = 0
    for i in range(0, len(ranking)):
        if user_id == ranking[i]:
            result = i
            break

    score = members[user_id]['42score']
    if result == 0:
        await bot.send(event=event, message='当前积分: %d，排名: %d，' % (score, result + 1) + exclaim_msg('大佬', '1', False))
    else:
        upper_score = members[ranking[result - 1]]['42score']
        distance = upper_score - score
        await bot.send(event=event,
                       message='当前积分: %d，排名: %d，距上一名%d分，' % (score, result + 1, distance) + exclaim_msg('大佬', '2', False))


@rank_viewer.handle()
async def view_rank(bot: Bot, event: Event, state: dict):
    """Handle the rank42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    members = load(universal_id, 'members')
    ranking = sorted(members, key=lambda x: (members[x]['42score'], x), reverse=True)

    if not ranking:
        await bot.send(event=event, message='当前暂无排名~')
        return

    rank_message = '42点积分排行榜:\n最高得分: %d\n-- 归一化得分 --\n' % (members[ranking[0]]['42score'])

    for i in range(0, len(ranking)):
        if i < 10 and members[ranking[i]]['42score'] > 0:
            rank_message += '[%d] %.1f - %s\n' % (i + 1, members[ranking[i]]['42score'] / members[ranking[0]]['42score'] * 100,
                                                  get_member_name(universal_id, ranking[i]))

    await bot.send(event=event, message=rank_message.strip())


@manual_player.handle()
async def manual_calc42(bot: Bot, event: Event, state: dict):
    """Control the calc42 game manually."""
    universal_id = str(event.self_id) + str(event.group_id)
    option = str(event.message).strip()

    if option == '++':
        await start_game(bot, universal_id, False, True)
        create('calc42_temp', str(event.self_id), str(event.group_id), {'+': [event.user_id]})
    elif option == '+':
        await start_game(bot, universal_id, False)
        create('calc42_temp', str(event.self_id), str(event.group_id), {'+': [event.user_id]})
    elif option == '-':
        await finish_game(bot, universal_id)


@broadcast('calc42')
async def calc42_broadcast(bot_id: str, group_id: str):
    """Boardcast a calc42 game."""
    bot = nonebot.get_bots()[bot_id]
    universal_id = str(bot_id) + str(group_id)
    try:
        # this means no one can terminate the routined calc42 game
        await start_game(bot, universal_id)
        create('calc42_temp', str(bot.self_id), str(group_id), {'+': []})
    except Exception:
        logger.error(traceback.format_exc())
