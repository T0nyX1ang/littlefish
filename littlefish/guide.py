"""
A simple guide for reference.

A guide, a backup guide, an app package link and a minesweeping guide link
is included here.
"""

from nonebot import on_fullmatch

from littlefish._policy.rule import check

guide = on_fullmatch(msg=('guide', '指南'), rule=check('guide'))

source_code = on_fullmatch(msg=('source', '源码'), rule=check('guide'))

get_package = on_fullmatch(msg=('getpackage', '安装包', '安装链接'), rule=check('guide'))

ms_guide = on_fullmatch(msg=('msguide', '扫雷指南'), rule=check('guide'))

push_line = on_fullmatch(msg=('pushline', '推送线'), rule=check('guide'))

guide_42 = on_fullmatch(msg=('guide42', '42点说明'), rule=check('guide') & check('calc42'))

bigtable = on_fullmatch(msg=('msbigtable', '联萌大表'), rule=check('guide'))


@guide.handle()
async def _():
    """Handle guide command."""
    guide_message = 'https://littlefish.tonyxiang.site/guide/normal.html'
    await guide.send(message=guide_message)


@source_code.handle()
async def _():
    """Handle source code command."""
    source_code_message = 'https://github.com/T0nyX1ang/littlefish'
    await source_code.send(message=source_code_message)


@get_package.handle()
async def _():
    """Handle get package command."""
    app_link_message = 'http://tapsss.com'
    await get_package.send(message=app_link_message)


@ms_guide.handle()
async def _():
    """Handle minesweeping guide command."""
    ms_guide_link_message = 'http://tapsss.com/?post=189646'
    await ms_guide.send(message=ms_guide_link_message)


@push_line.handle()
async def _():
    """Handle push line guide command."""
    push_link_message = 'http://tapsss.com/?post=388962'
    await push_line.send(message=push_link_message)


@guide_42.handle()
async def _():
    """Handle calc42 game command."""
    gd42_link_message = 'https://littlefish.tonyxiang.site/guide/normal/#%E7%AE%97-42-%E7%82%B9'
    await guide_42.send(message=gd42_link_message)


@bigtable.handle()
async def _():
    """Handle bigtable command."""
    bigtable_link_message = 'http://39.96.36.29:8000/bigtable/'
    await bigtable.send(message=bigtable_link_message)
