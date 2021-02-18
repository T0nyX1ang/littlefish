"""
A game to calculate 42 with 5 numbers between 0 and 13.

The command is invoked every 1 hour (can be changed) automatically.
The command requires to be invoked in groups.
"""

import itertools
import nonebot
import random
import datetime
import traceback
from apscheduler.triggers.date import DateTrigger
from ftptsgame import FTPtsGame
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from littlefish._exclaim import exclaim_msg
from littlefish._policy import check, boardcast, empty
from littlefish._db import load, save

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler
app_pool = {}
max_number = 13
max_storage_size = 500
target = 42
problem_database = list(
    itertools.combinations_with_replacement(range(0, max_number + 1), 5))


def get_member_name(universal_id: str, user_id: str) -> str:
    """Get member name."""
    members = load(universal_id, 'members')
    if not members:
        return '匿名大佬'

    return members[user_id]['card'] if members[user_id]['card'] else members[
        user_id]['nickname']


def print_current_problem(universal_id: str) -> str:
    """Print the current problem."""
    problem = app_pool[universal_id].get_current_problem()
    message = '本次42点的题目为: %d %d %d %d %d' % tuple(problem)
    return message


def _initialize_app(universal_id: str):
    """Initialize the calc42 app."""
    if universal_id not in app_pool:
        app_pool[universal_id] = FTPtsGame()

    if app_pool[universal_id].is_playing():
        raise PermissionError('Game has started.')

    frequency = load(universal_id, 'calc42_frequency')
    if not frequency:
        frequency = 1
        save(universal_id, 'calc42_frequency', frequency)

    hour_now = datetime.datetime.now().hour
    if (hour_now - 8) % frequency:
        raise PermissionError('Not in gaming time.')


def get_problem(universal_id: str):
    """Get the problem for the game."""
    def get_problem_id(problem: tuple) -> str:
        """Get the problem's unique id."""
        return f'{target}' + '%d%d%d%d%d' % problem

    previous = load(universal_id, 'old_problems')
    base = []
    if previous:
        base = previous.split('-')

    found = False
    while not found:
        problem = random.choice(problem_database)
        if get_problem_id(problem) in base:
            found = False
            continue

        try:
            app_pool[universal_id].generate_problem(problem)
            found = True
        except Exception:
            found = False

    base.append(get_problem_id(problem))
    now = '-'.join(base[-max_storage_size:])
    save(universal_id, 'old_problems', now)


def get_deadline(universal_id: str) -> int:
    """Get the deadline of a problem."""
    total_number = app_pool[universal_id].get_total_solution_number()
    return 180 * (1 + (total_number - 1) // 5) if total_number <= 20 else 900


def get_results(universal_id: str) -> str:
    """Print the result of the game."""
    current_solution_number = app_pool[
        universal_id].get_current_solution_number()
    total_solution_number = app_pool[universal_id].get_total_solution_number()
    deadline = get_deadline(universal_id)
    total_time, total_solutions = 0, 0

    bonus = 10 * (current_solution_number == total_solution_number)  # AK Score

    players = app_pool[universal_id].get_current_player_statistics()

    player_scores = {}
    player_solutions = {}
    player_achievements = {}

    for each_item in players:
        player_id, solution_time = each_item

        # get player bouns score
        player_scores.setdefault(player_id, bonus)

        # get player solution
        player_solutions.setdefault(player_id, 0)

        # get player achievements
        player_achievements.setdefault(player_id, '')

        # calculate solution time
        solution_time_in_seconds = solution_time.seconds + solution_time.microseconds / 1000000
        total_time = solution_time_in_seconds
        total_solutions += 1
        player_solutions[player_id] += 1

        # Accumulate score
        time_ratio = total_time / deadline
        solution_ratio = total_solutions / total_solution_number

        time_score = 5 - int(5 * time_ratio)
        normal_score = int(10 * (solution_ratio**(2 - time_ratio)))
        first_bonus = 5 * (total_solutions == 1)
        last_bonus = int(normal_score * (1 - 1 / total_solution_number)) * (
            current_solution_number == total_solutions)
        player_scores[player_id] += (time_score + normal_score + first_bonus +
                                     last_bonus)

    if players:
        player_achievements[players[0][0]] += 'F'
        player_achievements[players[-1][0]] += 'V'

    ordered_players = sorted(player_solutions,
                             key=lambda k: player_solutions[k],
                             reverse=True)

    # 50% AK bonus
    if ordered_players and player_solutions[
            ordered_players[0]] * 2 > total_solution_number:
        player_scores[ordered_players[0]] += player_solutions[
            ordered_players[0]]
        player_achievements[ordered_players[0]] += 'H'

    frequency = load(universal_id, 'calc42_frequency')

    line = ['本局42点游戏结束~']
    line.append('求解完成度: %d/%d' %
                (current_solution_number, total_solution_number))
    if current_solution_number < total_solution_number:
        line.append(
            '剩余解法: %s' %
            ', '.join(app_pool[universal_id].get_remaining_solutions()))
    line.append('积分倍率: %d' % frequency)

    for player in ordered_players:
        members = load(universal_id, 'members')
        name = get_member_name(universal_id, player)
        line.append('%s: %d解/+%d %s' %
                    (name, player_solutions[player], player_scores[player],
                     player_achievements[player]))
        members[player]['42score'] += player_scores[player] * frequency
        save(universal_id, 'members', members)

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'

    return result_message.strip()


async def start_game(bot: Bot, universal_id: str, group_id: int):
    """Start the calc42 game."""
    _initialize_app(universal_id)
    get_problem(universal_id)
    app_pool[universal_id].start()
    message = print_current_problem(universal_id)
    deadline = get_deadline(universal_id)
    delta = datetime.timedelta(seconds=deadline)
    trigger = DateTrigger(run_date=datetime.datetime.now() + delta)
    scheduler.add_job(
        func=finish_game,
        trigger=trigger,
        args=(bot, universal_id, group_id),
        misfire_grace_time=30,
        id='calc42_process',
        replace_existing=True,
    )
    await bot.send_group_msg(group_id=group_id, message=message)


async def finish_game(bot: Bot, universal_id: str, group_id: int):
    """Finish the calc42 game."""
    if app_pool[universal_id].is_playing():
        game_results = get_results(universal_id)
        app_pool[universal_id].stop()
        try:
            await bot.send_group_msg(group_id=group_id, message=game_results)
        except Exception as e:
            logger.error(traceback.format_exc())


solve_problem = on_command(cmd='calc42', aliases={'42点'}, rule=check('calc42'))

get_score = on_command(cmd='score42', aliases={'42点得分', '42点积分'},
                       rule=check('calc42') & empty())

get_rank = on_command(cmd='rank42', aliases={'42点排名', '42点排行'},
                      rule=check('calc42') & empty())

start_calc42 = on_command(cmd='manual42', aliases={'手动42点'},
                          rule=check('calc42.admin') & empty())

setfreq_calc42 = on_command(cmd='setfreq42', aliases={'设定42点频率'},
                            rule=check('calc42.admin'))


@solve_problem.handle()
async def solve_problem(bot: Bot, event: Event, state: dict):
    """Handle the calc42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    if not app_pool[universal_id].is_playing():
        return

    user_id = f'{event.user_id}'
    expr = str(event.message).strip()
    message = ''

    try:
        current_deadline = get_deadline(universal_id)
        total_elapsed = app_pool[universal_id].get_elapsed_time()
        left = current_deadline - total_elapsed.seconds

        elapsed = app_pool[universal_id].solve(expr, user_id)
        finish_time = elapsed.seconds + elapsed.microseconds / 1000000

        message = '恭喜%s完成第%d/%d个解，完成时间: %.3f秒，剩余时间: %d秒，' % (
            get_member_name(universal_id, user_id), 
            app_pool[universal_id].get_current_solution_number(),
            app_pool[universal_id].get_total_solution_number(), finish_time, left
        ) + exclaim_msg('大佬', '1', False)
    except OverflowError:
        message = '公式过长'
    except SyntaxError:
        message = '公式错误'
    except ValueError:
        message = '数字错误[%d %d %d %d %d]' % (
            app_pool[universal_id].get_current_problem())
    except ArithmeticError as ae:
        message = '答案错误[%s]' % (str(ae))
    except LookupError as le:
        message = '答案与[%s]重复' % (str(le))
    except Exception:
        message = '未知错误'
        logger.error(traceback.format_exc())

    await bot.send(event=event, message=message)

    if app_pool[universal_id].get_current_solution_number(
    ) == app_pool[universal_id].get_total_solution_number():
        await finish_game(bot, universal_id, event.group_id)


@get_score.handle()
async def get_score(bot: Bot, event: Event, state: dict):
    """Handle the score42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    user_id = f'{event.user_id}'
    members = load(universal_id, 'members')
    ranking = sorted(members,
                     key=lambda x: (members[x]['42score'], x),
                     reverse=True)

    result = 0
    for i in range(0, len(ranking)):
        if user_id == ranking[i]:
            result = i
            break

    score = members[user_id]['42score']
    if result == 0:
        await bot.send(event=event,
                       message='当前积分: %d，排名: %d，' % (score, result + 1) +
                       exclaim_msg('大佬', '1', False))
    else:
        upper_score = members[ranking[result - 1]]['42score']
        distance = upper_score - score
        await bot.send(event=event,
                       message='当前积分: %d，排名: %d，距上一名%d分，' %
                       (score, result + 1, distance) + 
                       exclaim_msg('大佬', '2', False))


@get_rank.handle()
async def get_rank(bot: Bot, event: Event, state: dict):
    """Handle the rank42 command."""
    universal_id = str(event.self_id) + str(event.group_id)
    members = load(universal_id, 'members')
    ranking = sorted(members,
                     key=lambda x: (members[x]['42score'], x),
                     reverse=True)

    if not ranking:
        await bot.send(event=event, message='当前暂无排名~')
        return

    line = [
        '42点积分排行榜:',
        '最高得分: %d' % (members[ranking[0]]['42score']),
        '-- 归一化得分 --'
    ]

    for i in range(0, len(ranking)):
        if i < 10 and members[ranking[i]]['42score'] > 0:
            line.append('[%d] %.1f - %s' %
                        (i + 1, members[ranking[i]]['42score'] /
                         members[ranking[0]]['42score'] * 100,
                         get_member_name(universal_id, ranking[i])))

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'

    await bot.send(event=event, message=result_message.strip())


@start_calc42.handle()
async def start_calc42(bot: Bot, event: Event, state: dict):
    """Start the calc42 game manually."""
    universal_id = str(event.self_id) + str(event.group_id)
    group_id = event.group_id
    await start_game(bot, universal_id, group_id)


@setfreq_calc42.handle()
async def setfreq_calc42(bot: Bot, event: Event, state: dict):
    """Print the status of the repeater."""
    universal_id = str(event.self_id) + str(event.group_id)
    try:
        load(universal_id, 'calc42_frequency')
        freq = int(str(event.message).strip())
        freq = min(15, max(1, freq))
        save(universal_id, 'calc42_frequency', freq)
        message = '42点频率设定成功，当前频率为%d小时/题' % freq
        await bot.send(event=event, message=message)
    except Exception:
        await bot.send(event=event, message='42点频率设定失败，请重试')


@scheduler.scheduled_job('cron', hour='8-23', minute=42, second=42,
                         misfire_grace_time=30)
@boardcast('calc42')
async def _(allowed: list):
    for bot_id, group_id in allowed:
        bot = nonebot.get_bots()[bot_id]
        universal_id = str(bot_id) + str(group_id)
        try:
            await start_game(bot, universal_id, group_id)
        except Exception:
            logger.error(traceback.format_exc())
