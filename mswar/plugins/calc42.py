from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from nonebot.message import MessageSegment
from .admire import get_admire_message
import nonebot
import random
import ast
import time
import math
import itertools

CURRENT_42_PROBLEM = None
CURRENT_42_PROBLEM_SOLVED = False
CURRENT_42_PROBLEM_TIME = 0

def expr_eval(node, orig_numbers):
    if isinstance(node, ast.BinOp):
        lval, orig_numbers = expr_eval(node.left, orig_numbers)
        op = node.op
        rval, orig_numbers = expr_eval(node.right, orig_numbers)
        if isinstance(op, ast.Add):
            return lval + rval, orig_numbers
        elif isinstance(op, ast.Sub):
            return lval - rval, orig_numbers
        elif isinstance(op, ast.Mult):
            return lval * rval, orig_numbers
        elif isinstance(op, ast.Div) and rval != 0:
            return lval / rval, orig_numbers
        else:
            raise SyntaxError('Only Add, Sub, Mult and Div operators are supported.')
    elif isinstance(node, ast.Num):
        number = node.n
        if type(number) is not int:
            raise ValueError('User input number must be integers.')
        orig_numbers.append(number)
        return number, orig_numbers
    else:
        raise SyntaxError('Only binary operators are supported.')

def validate_calc42(math_expr):
    global CURRENT_42_PROBLEM
    global CURRENT_42_PROBLEM_SOLVED    
    try:
        if not CURRENT_42_PROBLEM_SOLVED:
            math_expr = math_expr.replace(' ', '').replace('（','(').replace('）',')')

            if len(math_expr) >= 30:
                raise ValueError('Expression too long.')

            expr_ast = ast.parse(math_expr, mode='eval')
            if isinstance(expr_ast, ast.Expression):
                math_expr_value, user_input_numbers = expr_eval(expr_ast.body, [])
                if abs(math_expr_value - 42.0) < 1e-6 and sorted(user_input_numbers) == CURRENT_42_PROBLEM:
                    CURRENT_42_PROBLEM_SOLVED = True
                    return True

        return False
    except Exception as e:
        logger.warning(traceback.format_exc())  
        return False

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
        elif val in range(1, 6):
            problem.append(random.choice([1, 2]))
        elif val in range(6, 36):
            problem.append(random.choice([3, 4, 6, 7, 12]))
        elif val in range(36, 100):
            problem.append(random.choice([5, 8, 9, 10, 11, 13]))
    return problem

@on_command('calc42', aliases=('42点'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42(session: CommandSession):
    math_expr = session.get('math_expr')
    current_sender = session.event['sender']['user_id']
    
    if validate_calc42(math_expr):
        global CURRENT_42_PROBLEM_TIME
        finish_time = time.time() - CURRENT_42_PROBLEM_TIME
        admire_message = get_admire_message()
        message = MessageSegment.at(current_sender) + ' 完成时间: %.3f秒, %s' % (finish_time, admire_message)
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
    message = '42点游戏规则(暂定): 每日8-23时的42分, 我会给出5个位于0至13之间的整数, 你需要将这五个整数(可以调换顺序)通过四则运算与括号相连, 使得结果等于42. 回答时以"calc42"或"42点"开头, 加入空格, 并给出算式.'
    example_message = '示例: (问题) 1 3 3 8 2, (正确的回答) calc42/42点 (1 + 3 + 3) / (8 - 2), (错误的回答) calc422^8!3&3=1.'
    await session.send(message + '\n' + example_message)

@nonebot.scheduler.scheduled_job('cron', hour='8-23', minute=42, second=42, misfire_grace_time=30)
async def _():
    global CURRENT_42_PROBLEM
    global CURRENT_42_PROBLEM_SOLVED
    global CURRENT_42_PROBLEM_TIME
    bot = nonebot.get_bot()

    problem = generate_problem()
    while not calc42_solvable(problem):
        problem = generate_problem()
    CURRENT_42_PROBLEM = problem

    CURRENT_42_PROBLEM.sort()
    CURRENT_42_PROBLEM_SOLVED = False
    CURRENT_42_PROBLEM_TIME = time.time()
    message = '本次42点的题目为: %d %d %d %d %d' % (CURRENT_42_PROBLEM[0], CURRENT_42_PROBLEM[1], CURRENT_42_PROBLEM[2], CURRENT_42_PROBLEM[3], CURRENT_42_PROBLEM[4])
    try:
        groups = await bot.get_group_list() # boardcast to all groups
        for each_group in groups:
            await bot.send_group_msg(group_id=each_group['group_id'], message=message)
    except Exception as e:
        logger.error(traceback.format_exc())    
