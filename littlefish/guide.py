"""
A simple guide for reference.

A guide, a backup guide, an app package link and a minesweeping guide link
is included here.

The command requires to be invoked in groups.
"""

from nonebot.adapters.cqhttp import Bot, Event, Message
from littlefish._policy.rule import check
from littlefish._policy.plugin import on_simple_command

guide = on_simple_command(cmd='guide', aliases={'指南'}, rule=check('guide'))

source_code = on_simple_command(cmd='source', aliases={'源码'}, rule=check('guide'))

get_package = on_simple_command(cmd='getpackage', aliases={'安装包', '安装链接'}, rule=check('guide'))

ms_guide = on_simple_command(cmd='msguide', aliases={'扫雷指南'}, rule=check('guide'))

push_line = on_simple_command(cmd='pushline', aliases={'推送线'}, rule=check('guide'))

guide_42 = on_simple_command(cmd='guide42', aliases={'42点说明'}, rule=check('guide') & check('calc42'))


@guide.handle()
async def show_guide(bot: Bot, event: Event, state: dict):
    """Show guide page for littlefish."""
    guide_message = '[CQ:share,url=%s,title=用户指南]' % 'https://littlefish.vercel.app/guide/normal/'
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
    guide42_link_meesage = '[CQ:share,url=%s,title=42点指南]' % 'https://littlefish.vercel.app/guide/normal/#42'
    await bot.send(event=event, message=Message(guide42_link_meesage))
