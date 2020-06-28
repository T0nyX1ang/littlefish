from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
import nonebot
import requests
import bs4
import traceback

@on_command('dailystar', aliases=('每日一星'), permission=SUPERUSER | GROUP, only_to_me=False)
async def dailystar(session: CommandSession):
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

    result = '每日一星:\n' + t.replace('    ', '\n').replace('   ', '\n').replace('  ', '\n').replace(' ↑', ' ↑').replace(' ↓', ' ↓').replace(' →', ' →').replace(' ', '\n').replace('　', '\n').replace('|', ' | ') # re-align
    return result

@nonebot.scheduler.scheduled_job('cron', hour=0, minute=1, second=30, misfire_grace_time=30)
async def _():
    bot = nonebot.get_bot()
    message = await get_daily_star()
    try:
        groups = await bot.get_group_list() # boardcast to all groups
        for each_group in groups:
            await bot.send_group_msg(group_id=each_group['group_id'], message=message)
    except Exception as e:
        logger.error(traceback.format_exc())
