from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP

@on_command('guide', aliases=('指南'), permission=SUPERUSER | GROUP, only_to_me=False)
async def guide(session: CommandSession):
    guide_info = "用户指南详见: https://t0nyx1ang.github.io/mswar-bot/"
    await session.send(guide_info)

@on_command('backupguide', aliases=('备用指南'), permission=SUPERUSER | GROUP, only_to_me=False)
async def backupguide(session: CommandSession):
    backup_link = "备用链接: https://github.com/T0nyX1ang/mswar-bot/blob/master/docs/usage.md"
    await session.send(backup_link)

@on_command('getpackage', aliases=('安装包', '安装链接'), permission=SUPERUSER | GROUP, only_to_me=False)
async def getpackage(session: CommandSession):
	package_link = "下载链接(小米浏览器需选择源文件下载): http://tapsss.com"
	await session.send(package_link)
