"""
A exclaim module which handles the words to express in several situations.

The module will load the exclaim resource location by the location.
About the resource file:
The resource file should be in CSV format, and contains at least three
columns (separated by '|'), which indicates the item's name, type and
whether it is an image file. An example is as follows:

tql|1|0
！|-1|
[CQ:face,id=41]|-1|
hurry up|2|0
💪|-2|
resource/exclaim/1.gif|1|1

How to create a resource database manually?
First, enter the item's name, it can be plain texts, or CQ codes if
it's not an image, and it must be a relative path to the working dir-
ectory if it's an image. Then, enter a separator, and enter the type
of the item, currently it could be 1 (for admiration), 2 (for cheers)
, 3 (for errors), 4 (for cut-ins) or 10-19 (for daily routines).

Then, enter a separator and a weight to determine the probability
of selection. If you think the item is a body, enter a positive integer;
if you think the item is an ending, enter a negative integer (according
to type).

Last, enter another separator, and enter whether the item is an image,
enter 0 for no, and 1 for yes. If you handles nicely, the database will
be working after a reload of this module.

Warnings:
Make sure you have at least 1 image if you want to set the parameter
include_image to True. The message will not be sent if no images are
found. You can see the logs for more infomation.

About slimming message:
It will find out all the 'image' tags, and removing all of the 'url' key
from it to slim the message.

About mutating message:
It will randomly select a segment of the message, if the tag of the segment
is 'text', the text part will be randomly reversed; if the tag of the
segment is 'face', the id part will be randomly replaced; otherwise the
segment will remain unchanged.
"""

import csv
import os
import random
import nonebot
from .config import ResourceConfig
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message

global_config = nonebot.get_driver().config
plugin_config = ResourceConfig(**global_config.dict())
resource_location = os.path.join(os.getcwd(), plugin_config.resource_location)
frequent_face_id = list(set(plugin_config.frequent_face_id))

try:
    resource_database = []
    logger.info('Constructing resource database ...')
    with open(resource_location, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=plugin_config.resource_separator)
        for line in csv_reader:
            logger.debug('Loading resource: %s, TYPE=%s, IMG=%s, WEIGHT=%s' % tuple(line))
            resource_database.append(line)
except Exception:
    resource_database = []
    logger.warning('Failed to load resource database, feature limited.')


def _get_body(_type: str, _image: str):
    """A database filter to generate required message body."""
    body_all = [[row[0]] * int(row[3]) for row in resource_database if _type == row[1] and _image == row[2]]
    return random.choice(sum(body_all, [])) if body_all else '太强了'


def _get_ending(_type: str):
    """A database filter to generate required message ending."""
    ending_all = [[row[0]] * int(row[3]) for row in resource_database if row[1] == f'-{_type}']
    return random.choice(sum(ending_all, [])) if ending_all else '！'


def exclaim_msg(person: str, _type: str, include_image: bool, max_repeat: int = 3):
    """
    Get exclaiming message from the database.

    This should be the only function being called when this package
    is imported. The message will be made up of 3 parts: person,
    body and ending (with a maximum repetition). If the include_image
    parameter is set to True, an image will be sent. Please note that
    the resource should be specified explicitly, and the message won't
    be sent successfully if the resource file is empty.
    """

    if include_image and random.randint(0, 1):
        image_data = _get_body(_type=_type, _image='1')
        image_path = os.path.join(os.getcwd(), image_data)
        message = f'[CQ:image,file=file:///{image_path}]'
        return Message(message)  # return the image only

    msg_body = _get_body(_type=_type, _image='0')
    msg_ending = _get_ending(_type=_type) * random.randint(1, max_repeat)

    # beautify visualizations
    if not person:
        return Message(msg_body + msg_ending)

    return Message(person + ' ' * (person[-1].isascii() and msg_body[0].isascii()) + msg_body + msg_ending)


def slim_msg(message: str):
    """Slim a message."""
    for seg in Message(message):
        if seg.type == 'image' and 'url' in seg.data:
            seg.data.pop('url')  # remove the 'url' key
    return Message(message)


def mutate_msg(message: str, mutate: bool = False):
    """Mutate a message."""
    msg = Message(message)
    if not mutate:
        return msg  # just wrap the message

    place = random.choice(range(0, len(msg)))
    seg = msg[place]
    if seg.type == 'text':
        # reverse the text
        plain = seg.data['text']
        start, stop = sorted(random.sample(range(0, len(plain)), 2))
        target = plain[start:stop]
        result = plain[:start] + target[::-1] + plain[stop:]
        seg.data['text'] = result
    elif seg.type == 'face':
        # select a different face
        seg.data['id'] = random.choice(frequent_face_id)
    msg[place] = seg

    return Message(msg)
