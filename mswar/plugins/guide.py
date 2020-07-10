from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP

@on_command('guide', aliases=('指南'), permission=SUPERUSER | GROUP, only_to_me=False)
async def guide(session: CommandSession):
    guide_info = "目前机器人代码未开源(当前版本为v0.7.1), 用户指南详见: https://t0nyx1ang.github.io/mswar-bot/"
    await session.send(guide_info)
