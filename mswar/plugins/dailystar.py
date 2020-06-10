from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
import requests
import bs4

@on_command('dailystar', aliases=('每日一星'), permission=SUPERUSER | GROUP, only_to_me=False)
async def dailystar(session: CommandSession):
    daily_star_info = await get_daily_star()
    await session.send(daily_star_info)

async def get_daily_star() -> str:
    r = requests.get('http://saolei.wang/Player/Star.asp') # request
    p = r.content.decode('gb2312') # page
    b = bs4.BeautifulSoup(p, features='lxml') # structured page

    t = b.tr.text.replace('访问我的地盘', '').replace('给我发短消息', '').replace('\n', ' ').replace('\r', ' ').replace('\t', '').strip() # simplify
    t_new = t.replace(' | ', '|').replace(' |', '|').replace('| ', '|')
    while t_new != t:
        t = t_new
        t_new = t_new.replace(' | ', '|').replace(' |', '|').replace('| ', '|') # more simplications

    result = t.replace('    ', '\n').replace('   ', '\n').replace('  ', '\n').replace(' ↑', ' ↑').replace(' ', '\n').replace('　', '\n').replace('|', ' | ') # re-align
    return result
