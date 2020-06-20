from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.message import MessageSegment
import random

def get_admire_message(person):
    exaggeration = [
        # !
        '!',
        '!!',
        '!!!',
        # face: /fad
        MessageSegment.face(41),
        MessageSegment.face(41) + MessageSegment.face(41), 
        MessageSegment.face(41) + MessageSegment.face(41) + MessageSegment.face(41),
        # face: /kel
        MessageSegment.face(111),
        MessageSegment.face(111) + MessageSegment.face(111), 
        MessageSegment.face(111) + MessageSegment.face(111) + MessageSegment.face(111), 
        # face: /hec
        MessageSegment.face(144),
        MessageSegment.face(144) + MessageSegment.face(144), 
        MessageSegment.face(144) + MessageSegment.face(144) + MessageSegment.face(144), 
    ]
    if not person:
        person = '大佬'
    message = [
        '%s太强了' % (person),
        '%s tql' % (person) if person and str.isascii(person[-1]) else '%stql' % (person),
        '%s NB' % (person) if person and str.isascii(person[-1]) else '%sNB' % (person),
        '%s🐮🍺' % (person),
        '%s冲鸭' % (person),
    ]
    return MessageSegment.text(random.choice(message)) + random.choice(exaggeration)

@on_command('praise', aliases=('膜', '膜拜'), permission=SUPERUSER | GROUP, only_to_me=False)
async def praise(session: CommandSession):
    person = session.get('person')
    admire_message = get_admire_message(person)
    await session.send(admire_message)

@praise.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['person'] = stripped_arg
        else:
            session.state['person'] = ''
        return

@on_command('admire', aliases=('狂膜'), permission=SUPERUSER | GROUP, only_to_me=False)
async def admire(session: CommandSession):
    person = session.get('person')
    admire_message = get_admire_message(person)
    for i in range(0, 2):
        await session.send(admire_message)

@admire.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['person'] = stripped_arg
        else:
            session.state['person'] = ''
        return
