from nonebot import on_command, CommandSession, scheduler
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from apscheduler.triggers.date import DateTrigger
from ftptsgame.exceptions import FTPtsGameError
from .exclaim import get_admire_message
from .core import is_enabled, text_to_picture
from .global_value import CURRENT_ENABLED, CURRENT_42_APP, CURRENT_42_RANKING
import nonebot
import hashlib
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
        line.append('有效求解:')
        for i in range(0, len(current_solutions) // 2):
            line.append('[%d] %s [%d] %s' % (2 * i + 1, current_solutions[2 * i].ljust(30), 2 * i + 2, current_solutions[2 * i + 1]))
        if len(current_solutions) % 2 == 1:
            line.append('[%d] %s' % (len(current_solutions), current_solutions[-1]))
    else:
        line.append('当前暂无有效求解')
    message = ''
    for each_line in line:
        message = message + each_line + '\n'
    return message.strip()

def print_results(group_id):
    current_solution_number = CURRENT_42_APP[group_id].get_current_solution_number()
    total_solution_number = CURRENT_42_APP[group_id].get_total_solution_number()
    line = []
    line.append('--- 本题统计 ---')
    line.append('求解完成度: %d/%d' % (current_solution_number, total_solution_number))
    
    bonus = 10 if current_solution_number == total_solution_number else 0 # AK Score

    players = CURRENT_42_APP[group_id].get_current_player_statistics()

    for player in players:
        player_id = str(player)

        if player_id not in CURRENT_42_RANKING[group_id]:
            CURRENT_42_RANKING[group_id][player_id] = 0
        
        CURRENT_42_RANKING[group_id][player_id] += bonus

        for problem in players[player]:
            if problem == 1:
                CURRENT_42_RANKING[group_id][player_id] += 10
            elif problem == current_solution_number:
                CURRENT_42_RANKING[group_id][player_id] += int(20 * problem / total_solution_number)
            else:
                CURRENT_42_RANKING[group_id][player_id] += int(10 * problem / total_solution_number)

    ordered_players = sorted(players, key=lambda k: len(players[k]), reverse=True)

    # 50% AK bonus
    if players[ordered_players[0]] * 2 >= total_solution_number:
        CURRENT_42_RANKING[group_id][player_id] += 5

    for person in ordered_players:
        if person > 0:
            line.append(str(MessageSegment.at(person)) + ' 完成%d个解' % (len(players[person])))

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'

    return result_message.strip()

def get_deadline(group_id):
    total_number = CURRENT_42_APP[group_id].get_total_solution_number()
    return 300 * (1 + (total_number - 1) // 10) if total_number <= 40 else 1200

def get_leader_id(group_id):
    players = CURRENT_42_APP[group_id].get_current_player_statistics()
    return max(players, key=lambda k: max(players[k])) if players else -1

def get_current_stats(group_id):
    problem_message = print_current_problem(group_id)
    solution_message = print_current_solutions(group_id)
    result_message = ''
    stat_message = problem_message + '\n' + solution_message + '\n' + result_message
    return stat_message.strip()

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
                id=str(group_id),
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
            await bot.send_group_msg(group_id=group_id, message=print_results(group_id))
            if leader_id > 0:
                winning_message = MessageSegment.at(leader_id) + ' 恭喜取得本次42点接力赛胜利, ' + get_admire_message()
                await bot.send_group_msg(group_id=group_id, message=winning_message)
            CURRENT_42_APP[group_id].stop()
    except Exception as e:
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
            elapsed = CURRENT_42_APP[group_id].solve(math_expr, current_sender)
            admire_message = get_admire_message()
            finish_time = 86400 * elapsed.days + elapsed.seconds + elapsed.microseconds / 1000000
            message = MessageSegment.at(current_sender) + ' 恭喜完成第%d个解，完成时间: %.3f秒，%s' % (CURRENT_42_APP[group_id].get_current_solution_number(), finish_time, admire_message)
            await session.send(message)

            await session.send('[CQ:image,file=%s]' % text_to_picture(get_current_stats(group_id)))

            player_id = str(current_sender)

            if player_id not in CURRENT_42_RANKING[group_id]:
                CURRENT_42_RANKING[group_id][player_id] = 0

            # Accumulate time score
            if finish_time / current_deadline <= 0.2:
                CURRENT_42_RANKING[group_id][player_id] += 5
            elif 0.2 < finish_time / current_deadline <= 0.5:
                CURRENT_42_RANKING[group_id][player_id] += 3
            elif 0.5 < finish_time / current_deadline <= 0.8:
                CURRENT_42_RANKING[group_id][player_id] += 2
            else:
                CURRENT_42_RANKING[group_id][player_id] += 1

            if CURRENT_42_APP[group_id].get_current_solution_number() == CURRENT_42_APP[group_id].get_total_solution_number():
                await finish_game(group_id) # Then game is over now
        except FTPtsGameError as ge:
            errno, hint = ge.get_details()
            message = ''
            if errno // 16 == 0:
                return
            elif errno == 0x10:
                message = '公式过长'
            elif errno == 0x11:
                message = '公式错误'
            elif errno == 0x12:
                message = '符号错误'
            elif errno == 0x13:
                message = '被除数为0'
            elif errno == 0x14:
                message = '数字错误'
            elif errno == 0x15:
                message = '数字错误'
            elif errno == 0x20:
                message = '答案错误[%s]' % (str(hint))
            elif errno == 0x21:
                message = '答案与[%s]重复' % (str(hint))
            await session.send(message)
        except Exception as e:
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

    current_sender = session.event['sender']['user_id']
    message = '''42点游戏规则:
    (1)每日8-23时的42分42秒, 我会给出5个位于0至13之间的整数，
    玩家需要将这五个整数(可以调换顺序)通过四则运算与括号相连，
    使得结果等于42.
    (2)回答时以"calc42"或"42点"开头，加入空格，并给出算式. 
    如果需要查询等价解说明，请输入"42点等价解"或"等价解说明". 
    如果需要查询得分说明，请输入"42点得分说明".
    (3)将根据每个问题解的个数决定结算时间，10个解对应5分钟的
    结算时间，20分钟封顶，即min{20, 5*([(x-1)/10]+1)}.'''
    example_message = '示例: (问题) 1 3 3 8 2,\n(正确的回答) calc42/42点 (1+3+3)/(8-2),\n(错误的回答) calc422^8!3&3=1.'
    await session.send('[CQ:image,file=%s]' % text_to_picture(message + '\n' + example_message))

@on_command('calc42equal', aliases=('42点等价解', '等价解说明'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42equal(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    current_sender = session.event['sender']['user_id']
    equivalent_message = '''关于等价解的说明:
    (1)四则运算的性质得出的等价是等价解.
    (2)中间结果出现0，可以利用加减移动到式子的任何地方.
    (3)中间结果出现1，可以利用乘除移动到式子的任何地方.
    (4)等值子式的交换不认为是等价.
    (5)2*2与2+2不认为是等价.'''
    await session.send('[CQ:image,file=%s]' % text_to_picture(equivalent_message))

@on_command('calc42score', aliases=('42点得分说明',), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42score(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    current_sender = session.event['sender']['user_id']
    score_message = '''关于得分的说明:
    (1)每题的得分由"时间分"和"求解分"共同决定.
    (2)时间分:计算当前完成时间与限时的比值，
    比值小于0.2计5分，0.2-0.5记3分，0.5-0.8记2分，大于0.8记1分;
    (3)求解分:首杀记10分，接力赛胜利按(20*当前解数/总共解数)
    向下取整记分，其余求解按照(10*当前解数/总共解数)向下取整记分;
    (4)如果题目被完全求解(AK)，求解该题目全员额外加10分.
    (5)显示积分时会进行归一化.'''
    session.send('[CQ:image,file=%s]' % text_to_picture(score_message))

@on_command('score42', aliases=('42点积分', '42点得分'), permission=SUPERUSER | GROUP, only_to_me=False)
async def score42(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    group_id = session.event['group_id']
    current_sender = session.event['sender']['user_id']
    ranking = sorted(CURRENT_42_RANKING[group_id], key=lambda x: CURRENT_42_RANKING[group_id][x], reverse=True)

    player_id = str(current_sender)
    if player_id not in ranking:
        await session.send('当前积分: 0，暂无排名')
    else:
        result = 0
        for i in range(0, len(ranking)):
            if player_id == ranking[i]:
                result = i
                break
        score = CURRENT_42_RANKING[group_id][ranking[result]]
        max_score = CURRENT_42_RANKING[group_id][ranking[0]]
        if result == 0:
            admire_message = get_admire_message()
            await session.send('当前积分: %.1f，排名: %d，%s' % (100.0, result + 1, admire_message))
        else:
            upper_score = CURRENT_42_RANKING[group_id][ranking[result - 1]]
            distance = upper_score - score
            await session.send('当前积分: %.1f，排名: %d，距上一名%.1f分，冲鸭!' % (score / max_score * 100, result + 1, distance / max_score * 100))

@on_command('ranking42', aliases=('42点排名', '42点排行', '42点排行榜'), permission=SUPERUSER | GROUP, only_to_me=False)
async def ranking42(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    group_id = session.event['group_id']
    ranking = sorted(CURRENT_42_RANKING[group_id], key=lambda x: CURRENT_42_RANKING[group_id][x], reverse=True)
    line = ['42点积分排行榜:', '最高得分: %d' % (CURRENT_42_RANKING[group_id][ranking[0]]), '-- 归一化得分 --']
    if ranking:
        for i in range(0, len(ranking)):
            if i < 10:
                try:
                    member_info = await session.bot.get_group_member_info(group_id=group_id, user_id=int(ranking[i]))
                except Exception as e:
                    logger.warning('The user [%s] might not inside this group now.' % (ranking[i]))
                    member_info = None
                line.append('[%d] %.1f - %s' % (
                    i + 1, 
                    CURRENT_42_RANKING[group_id][ranking[i]] / CURRENT_42_RANKING[group_id][ranking[0]] * 100, 
                    member_info['card'] if member_info else '匿名大佬'
                ))
    else:
        line.append('当前暂无排名')

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'

    await session.send(result_message.strip())

@nonebot.scheduler.scheduled_job('cron', hour='8-23', minute=42, second=42, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    try:
        for group_id in CURRENT_ENABLED.keys():
            if CURRENT_ENABLED[group_id] and not CURRENT_42_APP[group_id].is_playing():
                CURRENT_42_APP[group_id].generate_problem('database', minimum_solutions=1)
                CURRENT_42_APP[group_id].start()
                message = print_current_problem(group_id)
                deadline = get_deadline(group_id) - 60
                await bot.send_group_msg(group_id=group_id, message=message)

                delta = datetime.timedelta(seconds=deadline)
                trigger = DateTrigger(run_date=datetime.datetime.now() + delta)
                scheduler.add_job(
                    func=ready_finish_game,
                    trigger=trigger,
                    args=(group_id, ),
                    misfire_grace_time=30,
                    id=str(group_id),
                )
    except Exception as e:
        logger.error(traceback.format_exc())
        if CURRENT_42_APP[group_id].is_playing():
            CURRENT_42_APP[group_id].stop()
