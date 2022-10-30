"""
A game to calculate 42 with 5 numbers between 0 and 13.

The rules can be found by invoking 'guide42' in groups.

The command requires to be invoked in groups.
"""

import traceback
import nonebot
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event, Message, GroupMessageEvent
from nonebot.log import logger
from littlefish._policy.rule import check, broadcast
from littlefish._policy.plugin import on_simple_command
from littlefish._game import MemberManager, GameManager
from littlefish._game.ftpts import init, start, solve, stop, status, current

hint_timeout = 60
scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler
manager = GameManager(game_type='calc42')


def print_current_problem(info: dict) -> str:
    """Print the current problem."""
    a, b, c, d, e = info['problem']
    return '本次%s点的题目为: %d %d %d %d %d' % (info['target'], a, b, c, d, e)


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
        time_ratio, solution_ratio = time_elapsed / deadline, (i + 1) / result['total']
        t_score, n_score = 5 * (1 - time_ratio), 10 * (solution_ratio**(2 - time_ratio))
        f_bonus, v_bonus = 5 * (i == 0), n_score * victory_coeff * (result['current'] == i + 1)
        scores[player_id] += t_score + n_score + f_bonus + v_bonus

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

    member_manager = MemberManager(universal_id)

    for player in ordered:
        name = member_manager.get_member_name(player)
        result_message += '%s: %d解/+%d %s\n' % (name, solutions[player], int(scores[player]), achievements[player])
        member_manager.change_game_score(player, '42score', int(scores[player] * result['addscore']))
        member_manager.change_game_score(player, '42score_daily', int(scores[player] * result['addscore']))

    return result_message.strip()


async def start_game(bot: Bot, universal_id: str, addscore: bool = True, enforce_random: bool = False):
    """Start the calc42 game."""
    group_id = int(universal_id[len(str(bot.self_id)):])
    init(universal_id)

    if status(universal_id):
        return  # stop the process if the game has started

    problem = start(universal_id, addscore, enforce_random)
    message = print_current_problem(problem)
    deadline = get_deadline(problem['total'])

    try:
        manager.add_scheduler(bot, universal_id, finish_game, deadline)
        manager.add_scheduler(bot, universal_id, timeout_reminder, deadline - hint_timeout)
        await bot.send_group_msg(group_id=group_id, message=message)
    except Exception:
        logger.error(traceback.format_exc())
        manager.remove_schedulers(universal_id)
        manager.reset_invoker(universal_id)
        stop(universal_id)  # stop the app instantly


async def timeout_reminder(bot: Bot, universal_id: str):
    """Reminder of the calc42 game."""
    group_id = int(universal_id[len(str(bot.self_id)):])
    if status(universal_id):
        info = current(universal_id)
        try:
            message = '距离本局%d点游戏结束还有%s秒，冲鸭~' % (info['target'], hint_timeout)
            await bot.send_group_msg(group_id=group_id, message=message)
        except Exception:
            logger.error(traceback.format_exc())


async def finish_game(bot: Bot, universal_id: str):
    """Finish the calc42 game."""
    manager.remove_schedulers(universal_id)
    group_id = int(universal_id[len(str(bot.self_id)):])
    manager.reset_invoker(universal_id)
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
    member_manager = MemberManager(universal_id)

    message = []
    for i in range(result['current']):
        user_id = result['stats'][i][0]
        name = member_manager.get_member_name(user_id)
        message.append({'type': 'node', 'data': {'name': name, 'uin': user_id, 'content': result['solutions'][i]}})

    for remaining in result['remaining']:
        message.append({'type': 'node', 'data': {'name': '小鱼', 'uin': bot.self_id, 'content': remaining}})

    if message:
        await bot.send_group_forward_msg(group_id=group_id, messages=Message(message))


problem_solver = on_command(cmd='calc42 ', aliases={'42点 '}, rule=check('calc42', GroupMessageEvent))

manual_player = on_command(cmd='manual42 ', aliases={'手动42点 '}, rule=check('calc42', GroupMessageEvent))

score_viewer = on_simple_command(cmd='score42', aliases={'42点得分', '42点积分'}, rule=check('calc42', GroupMessageEvent))

rank_viewer = on_simple_command(cmd='rank42', aliases={'42点排名', '42点排行'}, rule=check('calc42', GroupMessageEvent))

daily_rank_viewer = on_simple_command(cmd='dailyrank42',
                                      aliases={'42点今日排名', '42点今日排行'},
                                      rule=check('calc42', GroupMessageEvent))


@problem_solver.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle the calc42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    member_manager = MemberManager(universal_id)
    if not status(universal_id):
        return

    user_id = f'{event.user_id}'
    expr = str(event.message).strip()
    message = ''

    result = solve(universal_id, expr, user_id)
    if result['hint']:
        message = result['hint']
    else:
        elapsed = int(result['elapsed'])
        left = get_deadline(result['total']) - elapsed
        message = '恭喜[%s]完成第%d/%d个解，完成时间: %.3f秒，剩余时间: %d秒~' % (member_manager.get_member_name(user_id), result['current'],
                                                               result['total'], result['interval'], left)

    is_finished = (result['current'] == result['total'])
    message += (not is_finished) * ('\n%s' % print_current_problem(result))

    await problem_solver.send(message=message)

    if is_finished:
        await finish_game(bot, universal_id)


@manual_player.handle()
async def manual_calc42(bot: Bot, event: Event, state: dict):
    """Control the calc42 game manually."""
    universal_id = str(event.self_id) + str(event.group_id)
    if status(universal_id) and event.user_id != manager.get_invoker(universal_id):
        # stop the manual command if the invokers are not matched, only check when the game is started
        return

    option = str(event.message).strip()

    if option == '++':
        await start_game(bot, universal_id, False, True)
        manager.set_invoker(universal_id, event.user_id)
    elif option == '+':
        await start_game(bot, universal_id, False)
        manager.set_invoker(universal_id, event.user_id)
    elif option == '-':
        await finish_game(bot, universal_id)


@score_viewer.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle the score42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    user_id = f'{event.user_id}'
    member_manager = MemberManager(universal_id)
    await score_viewer.send(message=member_manager.get_member_stats(user_id, '42score'))


@rank_viewer.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle the rank42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    member_manager = MemberManager(universal_id)
    await rank_viewer.send(message=member_manager.get_game_rank('42score'))


@daily_rank_viewer.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle the dailyrank42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    member_manager = MemberManager(universal_id)
    await daily_rank_viewer.send(message=member_manager.get_game_rank('42score_daily'))


@broadcast('calc42')
async def _(bot_id: str, group_id: str):
    """Scheduled calc42 game broadcast."""
    bot = nonebot.get_bots()[bot_id]
    universal_id = str(bot_id) + str(group_id)
    if status(universal_id) and manager.get_invoker(universal_id) != -1:
        # forcibly stop the game when the routined game is started
        await finish_game(bot, universal_id)

    try:
        # this means no one can terminate the routined calc42 game
        await start_game(bot, universal_id)
        manager.set_invoker(universal_id)
    except Exception:
        logger.error(traceback.format_exc())


@broadcast('calc42', identifier='@daily')
async def _(bot_id: str, group_id: str):
    """Scheduled calc42 daily rank broadcast."""
    universal_id = str(bot_id) + str(group_id)
    member_manager = MemberManager(universal_id)
    member_manager.reset_game_score('42score_daily')
