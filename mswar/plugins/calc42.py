from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .admire import get_admire_message
import nonebot
import random
import ast
import time

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
                print(math_expr_value, user_input_numbers)
                if abs(math_expr_value - 42.0) < 1e-6 and sorted(user_input_numbers) == CURRENT_42_PROBLEM:
                    CURRENT_42_PROBLEM_SOLVED = True
                    return True

        return False
    except Exception as e:
        logger.warning(traceback.format_exc())  
        return False

@on_command('calc42', aliases=('42点'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42(session: CommandSession):
    math_expr = session.get('math_expr')
    if validate_calc42(math_expr):
        global CURRENT_42_PROBLEM_TIME
        finish_time = time.time() - CURRENT_42_PROBLEM_TIME
        admire_message = get_admire_message()
        message = '完成时间: %.3f秒, %s' % (finish_time, admire_message)
        await session.send(message)

@calc42.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['math_expr'] = stripped_arg
        else:
            session.finish()

@on_command('calc42help', aliases=('42点规则'), permission=SUPERUSER | GROUP, only_to_me=False)
async def calc42help(session: CommandSession):
    message = '42点游戏规则(暂定): 每日8-23时的42分, 我会给出5个位于0至13之间的整数, 你需要将这五个整数(可以调换顺序)通过四则运算与括号相连, 使得结果等于42. 回答时以"calc42"或"42点"开头, 加入空格, 并给出算式.'
    example_message = '示例: (问题) 1 3 3 8 2, (正确的回答) calc42/42点 (1 + 3 + 3) / (8 - 2), (错误的回答) calc422^8!3&3=1.'
    await session.send(message + '\n' + example_message)

@nonebot.scheduler.scheduled_job('cron', hour='8-23', minute=42, second=0, misfire_grace_time=30)
async def _():
    global CURRENT_42_PROBLEM
    global CURRENT_42_PROBLEM_SOLVED
    global CURRENT_42_PROBLEM_TIME
    bot = nonebot.get_bot()
    CURRENT_42_PROBLEM = [random.randint(0, 13) for _ in range(0, 5)]
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
