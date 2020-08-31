from nonebot import on_command, CommandSession, scheduler
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from apscheduler.triggers.date import DateTrigger
from .exclaim import get_admire_message
from .core import is_enabled, text_to_picture, get_member_name
from .global_value import CURRENT_ENABLED, CURRENT_42_APP, CURRENT_42_PROB_LIST, CURRENT_GROUP_MEMBERS, GAME_FREQUENCY
import nonebot
import datetime
import traceback

def print_current_problem(group_id):
    a, b, c, d, e = CURRENT_42_APP[group_id].get_current_problem()
    message = '本次42点的题目为: %d %d %d %d %d' % (a, b, c, d, e)
    return message

def print_current_solutions(group_id):
    current_solutions = CURRENT_42_APP[group_id].get_current_solutions()
    line = []
    if len(current_solutions) > 0:
        players = CURRENT_42_APP[group_id].get_current_player_statistics()
        line.append('有效求解:')
        for i in range(0, len(current_solutions)):
            line.append('[%d] %s > %s' % (i + 1, current_solutions[i], get_member_name(group_id, str(players[i][0]))))
    else:
        line.append('当前暂无有效求解')
    message = ''
    for each_line in line:
        message = message + each_line + '\n'
    return message.strip()

def get_deadline(group_id):
    total_number = CURRENT_42_APP[group_id].get_total_solution_number()
    return 300 * (1 + (total_number - 1) // 10) if total_number <= 40 else 1200

def get_leader_id(group_id):
    players = CURRENT_42_APP[group_id].get_current_player_statistics()
    return players[-1][0] if players else -1

def get_current_stats(group_id):
    problem_message = print_current_problem(group_id)
    solution_message = print_current_solutions(group_id)
    result_message = ''
    stat_message = problem_message + '\n' + solution_message + '\n' + result_message
    return stat_message.strip()

def print_results(group_id):
    current_solution_number = CURRENT_42_APP[group_id].get_current_solution_number()
    total_solution_number = CURRENT_42_APP[group_id].get_total_solution_number()
    deadline = get_deadline(group_id)
    total_time, total_solutions = 0, 0
    
    bonus = 10 if current_solution_number == total_solution_number else 0 # AK Score

    players = CURRENT_42_APP[group_id].get_current_player_statistics()
    
    player_scores = {}
    player_solutions = {}

    for each_item in players:
        player_id, solution_time = each_item
        if player_id not in player_scores:
            player_scores[player_id] = bonus
            player_solutions[player_id] = 0

        solution_time_in_seconds = solution_time.seconds + solution_time.microseconds / 1000000
        total_time = solution_time_in_seconds
        total_solutions += 1
        player_solutions[player_id] += 1

        # Accumulate time score
        player_scores[player_id] += int(5 * total_time / deadline)

        if total_solutions == current_solution_number:
            player_scores[player_id] += int(20 * total_solutions / total_solution_number)
        elif total_solutions == 1:
            player_scores[player_id] += 10
        else:
            player_scores[player_id] += int(10 * total_solutions / total_solution_number)

    ordered_players = sorted(player_solutions, key=lambda k: player_solutions[k], reverse=True)

    # 50% AK bonus
    if player_solutions[ordered_players[0]] * 2 > total_solution_number:
        player_scores[ordered_players[0]] += total_solution_number

    line = []
    line.append('--- 本题统计 ---')
    line.append('求解完成度: %d/%d' % (current_solution_number, total_solution_number))
    line.append('积分倍率: %d' % (GAME_FREQUENCY))

    for person in ordered_players:
        if person > 0:
            line.append(get_member_name(group_id, str(person)) + ' %d解/+%d' % (player_solutions[person], player_scores[person]))
            CURRENT_GROUP_MEMBERS[group_id][str(person)]['42score'] += player_scores[person] * GAME_FREQUENCY

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'

    return result_message.strip()

async def ready_finish_game(group_id):
    bot = nonebot.get_bot()
    try:
        if CURRENT_42_APP[group_id].is_playing():
            delta = datetime.timedelta(seconds=60)
            trigger = DateTrigger(run_date=datetime.datetime.now() + delta)
            scheduler.add_job(
                func=finish_game,
                trigger=trigger,
                args=(group_id, ),
                misfire_grace_time=30,
            )
            await bot.send_group_msg(group_id=group_id, message='剩余60秒，冲鸭~')
    except Exception as e:
        logger.error(traceback.format_exc())

async def finish_game(group_id):
    bot = nonebot.get_bot()
    try:
        if CURRENT_42_APP[group_id].is_playing():
            leader_id = get_leader_id(group_id)
            await bot.send_group_msg(group_id=group_id, message='[CQ:image,file=%s]' % text_to_picture(get_current_stats(group_id)))
            if leader_id > 0:
                await bot.send_group_msg(group_id=group_id, message=print_results(group_id))
                winning_message = MessageSegment.at(leader_id) + ' 恭喜取得本次42点接力赛胜利, ' + get_admire_message()
                await bot.send_group_msg(group_id=group_id, message=winning_message)
            CURRENT_42_APP[group_id].stop()
    except Exception:
        logger.error(traceback.format_exc())
        if CURRENT_42_APP[group_id].is_playing():
            CURRENT_42_APP[group_id].stop()

@on_command('calc42', aliases=('42点'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    math_expr = session.get('math_expr')
    current_sender = session.event['sender']['user_id']
    group_id = session.event['group_id']

    if CURRENT_42_APP[group_id].is_playing():
        try:
            current_deadline = get_deadline(group_id)
            total_elapsed = CURRENT_42_APP[group_id].get_elapsed_time()
            left = current_deadline - total_elapsed.seconds

            elapsed = CURRENT_42_APP[group_id].solve(math_expr, current_sender)
            finish_time = elapsed.seconds + elapsed.microseconds / 1000000

            admire_message = get_admire_message()

            message = MessageSegment.at(current_sender) + ' 恭喜完成第%d个解，完成时间: %.3f秒，剩余时间: %d秒，%s' % (CURRENT_42_APP[group_id].get_current_solution_number(), finish_time, left, admire_message)
            await session.send(message)

            if CURRENT_42_APP[group_id].get_current_solution_number() == CURRENT_42_APP[group_id].get_total_solution_number():
                await finish_game(group_id) # Then game is over now
            else:
                await session.send('[CQ:image,file=%s]' % text_to_picture(get_current_stats(group_id)))
        except OverflowError:
            await session.send('公式过长')
        except SyntaxError:
            await session.send('公式错误')
        except ValueError:
            await session.send('数字错误')
        except ArithmeticError as ae:
            await session.send('答案错误[%s]' % (str(ae)))
        except LookupError as le:
            await session.send('答案与[%s]重复' % (str(le)))
        except Exception:
            await session.send('未知错误')
            logger.error(traceback.format_exc())

@calc42.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['math_expr'] = stripped_arg
        else:
            session.finish()

@on_command('calc42help', aliases=('42点规则', '42点说明'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42help(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    message = '''42点游戏规则:
    (1)每日某些小时的42分42秒, 会给出5个位于0至13之间的整数，
    玩家需要将这五个整数(可以调换顺序)通过四则运算与括号相连，
    使得结果等于42.
    (2)回答时以"calc42"或"42点"开头，加入空格，并给出算式. 
    如果需要查询等价解说明，请输入"42点等价解"或"等价解说明". 
    如果需要查询得分说明，请输入"42点得分说明".
    (3)将根据每个问题解的个数决定结算时间，10个解对应5分钟的
    结算时间，20分钟封顶，即min{20, 5*([(x-1)/10]+1)}.
    (4)游戏频率:8-23时中每%d小时进行一次游戏.''' % (GAME_FREQUENCY)
    example_message = '示例: (问题) 1 3 3 8 2,\n(正确的回答) calc42/42点 (1+3+3)*(8-2),\n(错误的回答) calc422^8!3&3=1.'
    await session.send('[CQ:image,file=%s]' % text_to_picture(message + '\n' + example_message))

@on_command('calc42equal', aliases=('42点等价解', '等价解说明'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42equal(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    equivalent_message = '''关于等价解的说明:
    (1)四则运算的性质得出的等价是等价解;
    (2)中间结果出现0，可以利用加减移动到式子的任何地方;
    (3)中间结果出现1，可以利用乘除移动到式子的任何地方;
    (4)等值子式的交换不认为是等价;
    (5)2*2与2+2不认为是等价.'''
    await session.send('[CQ:image,file=%s]' % text_to_picture(equivalent_message))

@on_command('calc42score', aliases=('42点得分说明',), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42score(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    score_message = '''关于得分的说明:
    (1)每题的得分由"时间分"和"求解分"共同决定;
    (2)时间分:按照(5*当前完成时间/总限时)向下取整计分;
    (3)求解分:首杀记10分，接力赛胜利按(20*当前解数/总共解数)
    向下取整记分，其余求解按照(10*当前解数/总共解数)向下取整记分,
    如果题目只有一个解，只按接力赛胜利积分，不计算首杀分数;
    (4)如果题目被完全求解(AK)，求解该题目全员额外加10分;
    (5)如果题目多于一半的解均被某名玩家求出，该名玩家额外加(总共
    解数)分;
    (6)积分会根据游戏频率进行相应加倍.
    (7)显示积分时会进行归一化;'''
    await session.send('[CQ:image,file=%s]' % text_to_picture(score_message))

@on_command('score42', aliases=('42点积分', '42点得分'), permission=SUPERUSER | GROUP, only_to_me=False)
async def score42(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    group_id = session.event['group_id']
    current_sender = session.event['sender']['user_id']
    ranking = sorted(CURRENT_GROUP_MEMBERS[group_id], key=lambda x: CURRENT_GROUP_MEMBERS[group_id][x]['42score'], reverse=True)

    player_id = str(current_sender)
    if player_id not in ranking:
        await session.send('当前积分: 0，暂无排名')
    else:
        result = 0
        for i in range(0, len(ranking)):
            if player_id == ranking[i]:
                result = i
                break
        score = CURRENT_GROUP_MEMBERS[group_id][ranking[result]]['42score']
        max_score = CURRENT_GROUP_MEMBERS[group_id][ranking[0]]['42score']
        if result == 0:
            admire_message = get_admire_message()
            await session.send('当前积分: %.1f，排名: %d，%s' % (100.0, result + 1, admire_message))
        else:
            upper_score = CURRENT_GROUP_MEMBERS[group_id][ranking[result - 1]]['42score']
            distance = upper_score - score
            await session.send('当前积分: %.1f，排名: %d，距上一名%.1f分，冲鸭!' % (score / max_score * 100, result + 1, distance / max_score * 100))

@on_command('ranking42', aliases=('42点排名', '42点排行', '42点排行榜'), permission=SUPERUSER | GROUP, only_to_me=False)
async def ranking42(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    group_id = session.event['group_id']
    ranking = sorted(CURRENT_GROUP_MEMBERS[group_id], key=lambda x: CURRENT_GROUP_MEMBERS[group_id][x]['42score'], reverse=True)
    line = ['42点积分排行榜:', '最高得分: %d' % (CURRENT_GROUP_MEMBERS[group_id][ranking[0]]['42score']), '-- 归一化得分 --']
    if ranking:
        for i in range(0, len(ranking)):
            if i < 10:
                line.append('[%d] %.1f - %s' % (
                    i + 1, 
                    CURRENT_GROUP_MEMBERS[group_id][ranking[i]]['42score'] / CURRENT_GROUP_MEMBERS[group_id][ranking[0]]['42score'] * 100, 
                    get_member_name(group_id=group_id, user_id=ranking[i])
                ))
    else:
        line.append('当前暂无排名')

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'

    await session.send(result_message.strip())

@nonebot.scheduler.scheduled_job('cron', hour='8-23/%d' % (GAME_FREQUENCY), minute=42, second=42, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    try:
        for group_id in CURRENT_ENABLED.keys():
            if CURRENT_ENABLED[group_id] and not CURRENT_42_APP[group_id].is_playing():
                CURRENT_42_APP[group_id].generate_problem('probability', prob=CURRENT_42_PROB_LIST[group_id].values())
                CURRENT_42_APP[group_id].start()
                message = print_current_problem(group_id)
                deadline = get_deadline(group_id) - 60
                await bot.send_group_msg(group_id=group_id, message=message)

                current_problem = CURRENT_42_APP[group_id].get_current_problem()
                for val in CURRENT_42_PROB_LIST[group_id].keys():
                    if val == str(current_problem):
                        CURRENT_42_PROB_LIST[group_id][val] = 0
                    elif CURRENT_42_PROB_LIST[group_id][val] < 2000:
                        CURRENT_42_PROB_LIST[group_id][val] = CURRENT_42_PROB_LIST[group_id][val] + 1 

                delta = datetime.timedelta(seconds=deadline)
                trigger = DateTrigger(run_date=datetime.datetime.now() + delta)
                scheduler.add_job(
                    func=ready_finish_game,
                    trigger=trigger,
                    args=(group_id, ),
                    misfire_grace_time=30,
                )
    except Exception as e:
        logger.error(traceback.format_exc())
        if CURRENT_42_APP[group_id].is_playing():
            CURRENT_42_APP[group_id].stop()
