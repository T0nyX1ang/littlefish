from nonebot import on_startup, on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP, GROUP_ADMIN
from nonebot.log import logger
from nonebot.message import MessageSegment
from .core import is_enabled
import datetime

def get_greeting_message():
    current_time = datetime.datetime.now()
    current_hour = current_time.hour

    if current_hour in [1, 2]:
        return '快去睡觉，别熬夜破pb了~'
    elif current_hour in [3, 4, 5]:
        return '小鱼睡着了zzz~'
    elif current_hour in [6, 7]:
        return '早起的鸟儿有pb破~'
    elif current_hour in [8, 9, 10]:
        return '早上好鸭~'
    elif current_hour in [11, 12]:
        return '午饭吃了吗，吃饱了才有力气破pb~'
    elif current_hour in [13, 14, 15, 16]:
        return '下午好鸭~'
    elif current_hour in [17, 18]:
        return '晚饭吃了吗，吃饱了才有力气破pb~'
    elif current_hour in [19, 20, 21, 22]:
        return '晚上好鸭~'
    elif current_hour in [23, 0]:
        return '晚安，明天也要努力破pb~'

@on_command('greeting', aliases=('小鱼', 'mswar-bot'), permission=SUPERUSER | GROUP, only_to_me=False)
async def greeting(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    greeting_message = get_greeting_message()
    await session.send(greeting_message)
