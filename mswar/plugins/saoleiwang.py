from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import is_enabled
from .global_value import CURRENT_ENABLED
import nonebot
import requests
import bs4
import traceback

@on_command('saolei', aliases=('雷网'), permission=SUPERUSER | GROUP, only_to_me=False)
async def saolei(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    saolei_id = session.get('saolei_id')
    if saolei_id:
        await session.send('http://saolei.wang/Player/Index.asp?Id=%s' % (saolei_id))

@saolei.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['saolei_id'] = stripped_arg
        else:
            session.finish()

@on_command('dailystarsaolei', aliases=('每日一星', '雷网每日一星'), permission=SUPERUSER | GROUP, only_to_me=False)
async def dailystarsaolei(session: CommandSession):
    if not is_enabled(session.event):
        session.finish('小鱼睡着了zzz~')

    daily_star_info = await get_daily_star()
    await session.send(daily_star_info)

async def get_daily_star() -> str:
    r = requests.get('http://saolei.wang/Player/Star.asp') # request
    p = r.content.decode('gbk', errors='replace') # page
    b = bs4.BeautifulSoup(p, features='lxml') # structured page

    t = b.tr.text.replace('访问我的地盘', '').replace('给我发短消息', '').replace('\n', ' ').replace('\r', ' ').replace('\t', '').strip() # simplify
    t_new = t.replace(' | ', '|').replace(' |', '|').replace('| ', '|')
    while t_new != t:
        t = t_new
        t_new = t_new.replace(' | ', '|').replace(' |', '|').replace('| ', '|') # more simplications

    result = '雷网每日一星:\n' + t.replace('    ', '\n').replace('   ', '\n').replace('  ', '\n').replace(' ↑', ' ↑').replace(' ↓', ' ↓').replace(' →', ' →').replace(' ', '\n').replace('　', '\n').replace('|', ' | ') # re-align
    return result

@nonebot.scheduler.scheduled_job('cron', hour=0, minute=1, second=30, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    message = await get_daily_star()
    try:
        for group_id in CURRENT_ENABLED.keys():
            if CURRENT_ENABLED[group_id]:
                await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        logger.error(traceback.format_exc())
