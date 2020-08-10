from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP

@on_command('guide', aliases=('指南'), permission=SUPERUSER | GROUP, only_to_me=False)
async def guide(session: CommandSession):
    guide_info = "用户指南详见: https://t0nyx1ang.github.io/mswar-bot/"
    backup_link = "如果上述网址无法打开，可以访问备用链接: https://github.com/T0nyX1ang/mswar-bot/blob/master/docs/usage.md"
    await session.send(guide_info)
    await session.send(backup_link)
