"""Make the bot more responsive to words."""

from nonebot import on_command, on_endswith
from nonebot.permission import GROUP
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._policy import check
from littlefish._exclaim import exclaim_msg


admire = on_command(cmd='admire', aliases={'膜'},
                    permission=GROUP, rule=check('exclaim'))

praise = on_command(cmd='praise', aliases={'狂膜'},
                    permission=GROUP, rule=check('exclaim'))

cheer = on_command(cmd='cheer', aliases={'加油'},
                   permission=GROUP, rule=check('exclaim'))

cheer_ending = on_endswith(msg='加油', permission=GROUP,
                           rule=check('exclaim'), priority=10)


@admire.handle()
async def admire(bot: Bot, event: Event, state: dict):
    """Admire the person."""
    person = str(event.message).strip()
    await bot.send(event=event, message=exclaim_msg(person, '1', True))


@praise.handle()
async def praise(bot: Bot, event: Event, state: dict):
    """Praise the person."""
    person = str(event.message).strip()
    message = exclaim_msg(person, '1', False)
    await bot.send(event=event, message=message)
    await bot.send(event=event, message=message)


@cheer.handle()
async def cheer(bot: Bot, event: Event, state: dict):
    """Cheer the person."""
    person = str(event.message).strip()
    await bot.send(event=event, message=exclaim_msg(person, '2', True))


@cheer_ending.handle()
async def cheer_ending(bot: Bot, event: Event, state: dict):
    """Cheer the person with the ending."""
    person = str(event.message).strip()[:-2]
    await bot.send(event=event, message=exclaim_msg(person, '2', False))
