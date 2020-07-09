from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from fractions import Fraction
from .admire import get_admire_message
import nonebot
import random
import ast
import time
import math
import itertools
import traceback
import hashlib

CURRENT_42_PROBLEM = {}
CURRENT_42_PROBLEM_STARTED = {}
CURRENT_42_PROBLEM_TIME = {}
CURRENT_42_PROBLEM_VALID_LIST = {}
CURRENT_42_PROBLEM_VALID_LIST['original'] = {}
CURRENT_42_PROBLEM_VALID_LIST['simplified'] = {}
CURRENT_42_PROBLEM_PERSON_LIST = {}

def expr_eval(node, simplified, orig_num):
    if isinstance(node, ast.BinOp):
        lval, left, orig_num = expr_eval(node.left, simplified, orig_num)
        op = node.op
        rval, right, orig_num = expr_eval(node.right, simplified, orig_num)

        # add parenthesis
        if isinstance(op, (ast.Mult, ast.Div)) and isinstance(node.left, ast.BinOp) and isinstance(node.left.op, (ast.Add, ast.Sub)):
            left = '(%s)' % (left)

        if isinstance(op, (ast.Mult, ast.Div)) and isinstance(node.right, ast.BinOp) and isinstance(node.right.op, (ast.Add, ast.Sub)):
            right = '(%s)' % (right)

        if isinstance(op, ast.Sub) and isinstance(node.right, ast.BinOp) and isinstance(node.right.op, (ast.Add, ast.Sub)):
            right = '(%s)' % (right)

        if isinstance(op, ast.Div) and isinstance(node.right, ast.BinOp) and isinstance(node.right.op, (ast.Mult, ast.Div)):
            right = '(%s)' % (right)

        # calculation and concatenation
        if lval == 0:
            left = '0'
        elif lval == 1:
            left = '1'

        if rval == 0:
            right = '0'
        elif rval == 1:
            right = '1'

        result, new_simplified = None, None
        if isinstance(op, ast.Add):
            result, new_simplified = lval + rval, left + '+' + right
        elif isinstance(op, ast.Sub):
            result, new_simplified = lval - rval, left + '-' + right
        elif isinstance(op, ast.Mult):
            result, new_simplified = lval * rval, left + '*' + right
        elif isinstance(op, ast.Div) and rval != 0:
            result, new_simplified = lval / rval, left + '/' + right
        elif isinstance(op, ast.Div) and rval == 0:
            raise ZeroDivisionError('Division by 0.')
        else:
            raise SyntaxError('Only Add, Sub, Mult and Div operators are supported.')

        if result == 0:
            new_simplified = '0'
        elif result == 1:
            new_simplified = '1'
        return result, new_simplified, orig_num 

    elif isinstance(node, ast.Num):
        number = node.n
        if type(number) is not int:
            raise ValueError('User input number must be integers.')
        orig_num.append(number)
        if number not in [0, 1]:
            return Fraction(number), chr(number + 97), orig_num
        else:
            return Fraction(number), str(number), orig_num
    else:
        raise SyntaxError('Only binary operators are supported.')

def judge_equivalent(problem, expr_1, expr_2):
    for _ in range(0, 10):
        for val in problem:
            random_number = random.randint(50000, 99999)
            expr_1 = expr_1.replace(chr(val + 97), str(random_number))
            expr_2 = expr_2.replace(chr(val + 97), str(random_number))

        expr_1_ast = ast.parse(expr_1, mode='eval')
        expr_2_ast = ast.parse(expr_2, mode='eval')
        try:
            if expr_eval(expr_1_ast.body, '', [])[0] == expr_eval(expr_2_ast.body, '', [])[0]:
                return True
        except Exception as e:
            logger.warning(traceback.format_exc())

    return False

def validate_calc42(math_expr, group_id):
    global CURRENT_42_PROBLEM
    global CURRENT_42_PROBLEM_VALID_LIST

    problem = CURRENT_42_PROBLEM[group_id]
    valid_list = CURRENT_42_PROBLEM_VALID_LIST['simplified'][group_id]

    try:
        math_expr = math_expr.replace(' ', '').replace('（','(').replace('）',')')

        if len(math_expr) >= 30:
            raise ValueError('Expression too long.')    

        expr_ast = ast.parse(math_expr, mode='eval')
        if isinstance(expr_ast, ast.Expression):
            math_expr_value, simplified_expr, user_input_numbers = expr_eval(expr_ast.body, '', [])
            if math_expr_value == 42 and sorted(user_input_numbers) == problem:
                for ind in range(0, len(valid_list)):
                    curr_expr = valid_list[ind]
                    if judge_equivalent(problem, simplified_expr, curr_expr):
                        return (ind + 1)
                CURRENT_42_PROBLEM_VALID_LIST['simplified'][group_id].append(simplified_expr)
                CURRENT_42_PROBLEM_VALID_LIST['original'][group_id].append(math_expr)
                return 0
            elif math_expr_value != 42:
                return -1
            else:
                return -2
        return -63

    except Exception as e:
        logger.warning(traceback.format_exc())  
        return -3

def convert_solution(group_id, index):
    global CURRENT_42_PROBLEM_VALID_LIST
    valid_expr = CURRENT_42_PROBLEM_VALID_LIST['original'][group_id][index]
    return valid_expr

@on_command('calc42', aliases=('42点'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42(session: CommandSession):
    global CURRENT_42_PROBLEM_TIME
    global CURRENT_42_PROBLEM_VALID_LIST
    global CURRENT_42_PROBLEM_STARTED

    if session.event['message_type'] == 'group':
        math_expr = session.get('math_expr')
        current_sender = session.event['sender']['user_id']
        group_id = session.event['group_id']

        if group_id in CURRENT_42_PROBLEM_STARTED and CURRENT_42_PROBLEM_STARTED[group_id]:
            result = validate_calc42(math_expr, group_id)
            
            if result == 0:
                finish_time = time.time() - CURRENT_42_PROBLEM_TIME[group_id]
                admire_message = get_admire_message()
                message = MessageSegment.at(current_sender) + ' 恭喜完成第%d个解. 完成时间: %.3f秒, %s' % (len(CURRENT_42_PROBLEM_VALID_LIST['original'][group_id]), finish_time, admire_message)
                if current_sender in CURRENT_42_PROBLEM_PERSON_LIST[group_id]:
                    CURRENT_42_PROBLEM_PERSON_LIST[group_id][current_sender] += 1
                else:
                    CURRENT_42_PROBLEM_PERSON_LIST[group_id][current_sender] = 1
                await session.send(message)
            elif result > 0:
                message = MessageSegment.at(current_sender) + ' 你的结果是正确的，但是与第%d个解[%s]重复了' % (result, convert_solution(group_id, result - 1))
                await session.send(message)
            elif result == -1:
                message = MessageSegment.at(current_sender) + ' 你的结果是错误的'
                await session.send(message)
            elif result == -2:
                message = MessageSegment.at(current_sender) + ' 你使用的数字与题目所给的不符'
                await session.send(message)
            elif result == -3:
                message = MessageSegment.at(current_sender) + ' 你的公式没法识别'
                await session.send(message)

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
    current_sender = session.event['sender']['user_id']
    message = '42点游戏规则(暂定): 每日8-23时的42分42秒, 我会给出5个位于0至13之间的整数，你需要将这五个整数(可以调换顺序)通过四则运算与括号相连，使得结果等于42. 回答时以"calc42"或"42点"开头，加入空格，并给出算式. 在当前小时的59分59秒，会统计该问题的等价解与每名玩家的求解个数. 如果需要查询等价解说明，请输入"42点等价解"或"等价解说明". 如果需要查询当前问题，请输入"当前问题"或"当前42点"，机器人会私戳当前问题.'
    example_message = '示例: (问题) 1 3 3 8 2, (正确的回答) calc42/42点 (1 + 3 + 3) / (8 - 2), (错误的回答) calc422^8!3&3=1.'
    await session.bot.send_private_msg(user_id=current_sender, message=message + '\n' + example_message)   

@on_command('calc42equal', aliases=('42点等价解', '等价解说明'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42equal(session: CommandSession):
    current_sender = session.event['sender']['user_id']
    equivalent_message = '关于等价解的说明:\n(1)四则运算的性质得出的等价是等价解;\n(2)中间结果出现0，可以利用加减移动到式子的任何地方;\n(3)中间结果出现1，可以利用乘除移动到式子的任何地方;\n(4)等值子式的交换不认为是等价;\n(5)2*2与2+2不认为是等价.'
    await session.bot.send_private_msg(user_id=current_sender, message=equivalent_message)

def check_ordered_calc42_solvable(ordered_problem, ordered_operator):
    try:
        op_table = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if abs(y) >= 1e-6 else math.inf
        }
        a, b, c, d, e = ordered_problem
        op1, op2, op3, op4 = ordered_operator

        f = [0.0] * 14
        f[0]  = op_table[op4](op_table[op3](op_table[op2](op_table[op1](a, b), c), d), e)
        f[1]  = op_table[op4](op_table[op2](op_table[op1](a, b), op_table[op3](c, d)) ,e)
        f[2]  = op_table[op4](op_table[op3](op_table[op1](a, op_table[op2](b, c)), d), e)
        f[3]  = op_table[op4](op_table[op1](a, op_table[op2](op_table[op3](b, c), d)), e)
        f[4]  = op_table[op4](op_table[op1](a, op_table[op2](b, op_table[op3](c, d))), e)
        f[5]  = op_table[op1](a, op_table[op4](op_table[op3](op_table[op2](b, c), d), e))
        f[6]  = op_table[op1](a, op_table[op3](op_table[op2](b, c), op_table[op4](d, e)))
        f[7]  = op_table[op1](a, op_table[op4](op_table[op2](b, op_table[op3](c, d)), e))
        f[8]  = op_table[op1](a, op_table[op2](b, op_table[op4](op_table[op3](c, d), e)))
        f[9]  = op_table[op1](a, op_table[op2](b, op_table[op3](c, op_table[op4](d, e))))
        f[10] = op_table[op2](op_table[op1](a, b), op_table[op4](op_table[op3](c, d), e))
        f[11] = op_table[op2](op_table[op1](a, b), op_table[op3](c, op_table[op4](d, e)))
        f[12] = op_table[op3](op_table[op1](a, op_table[op2](b, c)), op_table[op4](d, e))
        f[13] = op_table[op3](op_table[op2](op_table[op1](a, b), c), op_table[op4](d, e))

        for i in range(0, len(f)):
            if abs(f[i] - 42) < 1e-6:
                return True
        return False

    except Exception as e:
        return False

def calc42_solvable(problem):
    for ordered_problem in itertools.permutations(problem):
        for ordered_operator in itertools.product(['+', '-', '*', '/'], repeat=4):
            if check_ordered_calc42_solvable(ordered_problem, ordered_operator):
                return True
    return False

def generate_problem():
    random_numbers = [random.randint(0, 99) for _ in range(0, 5)]
    problem = []
    for val in random_numbers:
        if val in range(0, 1):
            problem.append(0)
        elif val in range(1, 8):
            problem.append(random.choice([1, 2]))
        elif val in range(8, 41):
            problem.append(random.choice([3, 4, 6, 7, 12]))
        elif val in range(41, 100):
            problem.append(random.choice([5, 8, 9, 10, 11, 13]))
    return problem

@nonebot.scheduler.scheduled_job('cron', hour='8-23', minute=42, second=42, misfire_grace_time=30)
async def _():
    global CURRENT_42_PROBLEM
    global CURRENT_42_PROBLEM_TIME
    global CURRENT_42_PROBLEM_VALID_LIST
    global CURRENT_42_PROBLEM_STARTED
    bot = nonebot.get_bot()

    try:
        groups = await bot.get_group_list() # boardcast to all groups
        for each_group in groups:
            group_id = each_group['group_id']
            problem = generate_problem()
            while not calc42_solvable(problem):
                problem = generate_problem()
            CURRENT_42_PROBLEM[group_id] = problem
            CURRENT_42_PROBLEM[group_id].sort()
            CURRENT_42_PROBLEM_TIME[group_id] = time.time()
            CURRENT_42_PROBLEM_VALID_LIST['original'][group_id] = []
            CURRENT_42_PROBLEM_VALID_LIST['simplified'][group_id] = []
            CURRENT_42_PROBLEM_PERSON_LIST[group_id] = {}
            CURRENT_42_PROBLEM_STARTED[group_id] = True
            message = '本次42点的题目为: %d %d %d %d %d' % (CURRENT_42_PROBLEM[group_id][0], 
                                                           CURRENT_42_PROBLEM[group_id][1], 
                                                           CURRENT_42_PROBLEM[group_id][2], 
                                                           CURRENT_42_PROBLEM[group_id][3], 
                                                           CURRENT_42_PROBLEM[group_id][4])
            await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        logger.error(traceback.format_exc())

def get_current_stats(group_id):
    global CURRENT_42_PROBLEM
    global CURRENT_42_PROBLEM_STARTED
    global CURRENT_42_PROBLEM_VALID_LIST
    global CURRENT_42_PROBLEM_PERSON_LIST

    line = []
    if group_id in CURRENT_42_PROBLEM and CURRENT_42_PROBLEM[group_id]:
        line.append('本次42点的题目为: %d %d %d %d %d' % (CURRENT_42_PROBLEM[group_id][0], 
                                                        CURRENT_42_PROBLEM[group_id][1], 
                                                        CURRENT_42_PROBLEM[group_id][2], 
                                                        CURRENT_42_PROBLEM[group_id][3], 
                                                        CURRENT_42_PROBLEM[group_id][4]))
        if CURRENT_42_PROBLEM_VALID_LIST['original'][group_id]:
            line.append('有效求解:')
            total = 1
            for valid_expr in CURRENT_42_PROBLEM_VALID_LIST['original'][group_id]:
                line.append('[%d] %s' % (total, valid_expr))
                total += 1
        else:
            line.append('当前暂无有效求解')

        if len(CURRENT_42_PROBLEM_VALID_LIST['original'][group_id]) > 0 and not CURRENT_42_PROBLEM_STARTED[group_id]:
            line.append('--- 本题统计 ---')
            ordered_person = sorted(CURRENT_42_PROBLEM_PERSON_LIST[group_id], key=CURRENT_42_PROBLEM_PERSON_LIST[group_id].get, reverse=True)
            for person in ordered_person:
                line.append(str(MessageSegment.at(person)) + ' 完成%d个解' % (CURRENT_42_PROBLEM_PERSON_LIST[group_id][person]))

    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'

    return result_message.strip()

@on_command('current42', aliases=('当前42点', '当前问题'), permission=SUPERUSER | GROUP, only_to_me=False)
async def current42(session: CommandSession):
    global CURRENT_42_PROBLEM_STARTED
    group_id = session.event['group_id']
    current_sender = session.event['sender']['user_id']
    if group_id in CURRENT_42_PROBLEM_STARTED and CURRENT_42_PROBLEM_STARTED[group_id]:
        message = get_current_stats(group_id)
        await session.bot.send_private_msg(user_id=current_sender, message=message)

@nonebot.scheduler.scheduled_job('cron', hour='8-23', minute=59, second=59, misfire_grace_time=30)
async def _():
    global CURRENT_42_PROBLEM_STARTED
    bot = nonebot.get_bot()
    try:
        groups = await bot.get_group_list() # boardcast to all groups
        for each_group in groups:
            group_id = each_group['group_id']
            CURRENT_42_PROBLEM_STARTED[group_id] = False
            message = get_current_stats(group_id)
            await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        logger.error(traceback.format_exc())
