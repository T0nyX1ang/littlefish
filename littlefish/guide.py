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

bigtable = on_simple_command(cmd='msbigtable', aliases={'联萌大表'}, rule=check('guide'))


@guide.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle guide command."""
    guide_message = '[CQ:share,url=%s,title=用户指南]' % 'https://littlefish.tonyxiang.site/guide/normal.html'
    await guide.send(message=Message(guide_message))


@source_code.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle source code command."""
    source_code_message = '[CQ:share,url=%s,title=小鱼源码]' % 'https://github.com/T0nyX1ang/littlefish'
    await source_code.send(message=Message(source_code_message))


@get_package.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle get package command."""
    app_link_message = '[CQ:share,url=%s,title=联萌下载地址]' % 'http://tapsss.com'
    await get_package.send(message=Message(app_link_message))


@ms_guide.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle minesweeping guide command."""
    ms_guide_link_message = '[CQ:share,url=%s,title=扫雷指南]' % 'http://tapsss.com/?post=189646'
    await ms_guide.send(message=Message(ms_guide_link_message))


@push_line.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle push line guide command."""
    push_link_message = '[CQ:share,url=%s,title=纪录推送标准]' % 'http://tapsss.com/?post=388962'
    await push_line.send(message=Message(push_link_message))


@guide_42.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle calc42 game command."""
    gd42_link_message = '[CQ:share,url=%s,title=42点指南]' % (
        'https://littlefish.tonyxiang.site/guide/normal.html#%E7%AE%97-42-%E7%82%B9')
    await guide_42.send(message=Message(gd42_link_message))


@bigtable.handle()
async def _(bot: Bot, event: Event, state: dict):
    """Handle bigtable command."""
    bigtable_link_message = '[CQ:share,url=%s,title=联萌大表]' % 'http://39.96.36.29:8000/bigtable/'
    await bigtable.send(message=Message(bigtable_link_message))
