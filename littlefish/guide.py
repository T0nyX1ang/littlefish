"""
A simple guide for reference.

A guide, a backup guide, an app package link and a minesweeping guide link
is included here.

The command requires to be invoked in groups.
"""

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event, Message
from littlefish._policy import check, empty

guide = on_command(cmd='guide', aliases={'指南'}, rule=check('guide') & empty())

source_code = on_command(cmd='source', aliases={'源码'}, rule=check('guide') & empty())

get_package = on_command(cmd='getpackage', aliases={'安装包', '安装链接'}, rule=check('guide') & empty())

ms_guide = on_command(cmd='msguide', aliases={'扫雷指南'}, rule=check('guide') & empty())

push_line = on_command(cmd='pushline', aliases={'推送线'}, rule=check('guide') & empty())

guide_42 = on_command(cmd='guide42', aliases={'42点说明'}, rule=check('guide') & check('calc42') & empty())


@guide.handle()
async def show_guide(bot: Bot, event: Event, state: dict):
    """Show guide page for littlefish."""
    guide_message = '[CQ:share,url=%s,title=用户指南]' % 'https://littlefish.vercel.app/guide/normal.html'
    await bot.send(event=event, message=Message(guide_message))


@source_code.handle()
async def show_source(bot: Bot, event: Event, state: dict):
    """Show source code page for littlefish."""
    source_code_message = '[CQ:share,url=%s,title=小鱼源码]' % 'https://github.com/T0nyX1ang/littlefish'
    await bot.send(event=event, message=Message(source_code_message))


@get_package.handle()
async def show_app_link(bot: Bot, event: Event, state: dict):
    """Show app package package."""
    app_link_message = '[CQ:share,url=%s,title=联萌下载地址]' % 'http://tapsss.com'
    await bot.send(event=event, message=Message(app_link_message))


@ms_guide.handle()
async def show_msguide(bot: Bot, event: Event, state: dict):
    """Show minesweeping guide."""
    ms_guide_link_message = '[CQ:share,url=%s,title=扫雷指南]' % 'http://tapsss.com/?post=189646'
    await bot.send(event=event, message=Message(ms_guide_link_message))


@push_line.handle()
async def show_push_line(bot: Bot, event: Event, state: dict):
    """Show minesweeping guide."""
    push_link_message = '[CQ:share,url=%s,title=纪录推送标准]' % 'http://tapsss.com/?post=388962'
    await bot.send(event=event, message=Message(push_link_message))


@guide_42.handle()
async def show_guide_42(bot: Bot, event: Event, state: dict):
    """Show minesweeping guide."""
    guide42_link_meesage = '[CQ:share,url=%s,title=42点指南]' % (
        'https://littlefish.vercel.app/guide/normal.html#%E7%AE%9742%E7%82%B9')
    await bot.send(event=event, message=Message(guide42_link_meesage))
