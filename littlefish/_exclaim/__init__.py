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
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message
from .config import ResourceConfig

global_config = nonebot.get_driver().config
plugin_config = ResourceConfig(**global_config.dict())
resource_location = os.path.join(os.getcwd(), plugin_config.resource_location)
frequent_face_id = list(set(plugin_config.frequent_face_id))

resource_database = {}
logger.info('Constructing resource database ...')
with open(resource_location, 'r', encoding='utf-8') as f:
    csv_reader = csv.reader(f, delimiter=plugin_config.resource_separator)
    for line in csv_reader:
        try:
            _resource, _type, _img, _weight = line
            # convert the data to required format, the item will be skipped if it doesn't meet the requirements
            _img = bool(int(_img))
            _weight = max(1, int(_weight))
            logger.debug('Loading resource: %s, TYPE=%s, IMG=%s, WEIGHT=%s' % (_resource, _type, _img, _weight))
            # convert the CSV format raw database to dict format database
            resource_database.setdefault(_type, {})  # select the type as the key of the database
            resource_database[_type].setdefault('total_weight', 0)
            resource_database[_type].setdefault('total_image_weight', 0)
            resource_database[_type].setdefault('data', [])
            resource_database[_type]['total_weight'] += _weight
            resource_database[_type]['total_image_weight'] += _weight * _img
            resource_database[_type]['data'].append((_resource, _img, _weight))
        except Exception:
            logger.error('Failed to load current resource: RAW=%s.' % line)

# sort the database to make the image and non-image resources split apart
for _type in resource_database:
    resource_database[_type]['data'].sort(key=lambda x: x[1])


def _get_msg_from_database(_type: str, _image: bool = False) -> str:
    """Get message from the resource database."""
    try:
        selection = resource_database[_type]
    except Exception:
        logger.warning('Unable to find the item in the resource database.')
        return ''
    key = random.randint(1, selection['total_weight'] - (not _image) * selection['total_image_weight'])
    for v in selection['data']:
        key -= v[2]
        if key <= 0:
            return v
    return ''


def exclaim_msg(person: str, _type: str, include_image: bool, max_repeat: int = 3) -> Message:
    """
    Get exclaiming message from the database.

    The exclaiming message will be made up of 3 basic parts: person,
    body and ending (with a maximum repetition). If the include_image
    parameter is set to True, an image will be included in the selection.
    Please note that the resource should be specified explicitly, and
    the message won't be sent successfully if the resource file is empty.
    """
    msg_body_selection = _get_msg_from_database(_type=_type, _image=include_image)
    msg_ending_selection = _get_msg_from_database(_type=f'-{_type}')

    if not (msg_body_selection and msg_ending_selection):  # indicates the search fails
        return Message('小鱼词穷了QAQ~')

    if msg_body_selection[1]:  # indicates an image
        image_data = msg_body_selection[0]
        image_path = os.path.join(os.getcwd(), image_data)
        message = f'[CQ:image,file=file:///{image_path}]'
        return Message(message)  # return the image only

    msg_body = msg_body_selection[0]
    msg_ending = msg_ending_selection[0] * random.randint(1, max_repeat)

    # beautify visualizations
    if not person:
        return Message(msg_body + msg_ending)
    return Message(person + ' ' * (person[-1].isascii() and msg_body[0].isascii()) + msg_body + msg_ending)


def slim_msg(message: str) -> Message:
    """Slim a message."""
    for seg in Message(message):
        if seg.type == 'image' and 'url' in seg.data:
            seg.data.pop('url')  # remove the 'url' key
    return Message(message)


def replace_redbag_msg(message: str) -> Message:
    """Replace the red bag message as the bot can not send red bags."""
    msg = Message(message)
    if len(msg) != 1:
        return msg

    seg = msg[0]
    if seg.type == 'redbag':
        # replace redbag with a custom message
        seg.type = 'text'
        title = seg.data.pop('title')
        seg.data['text'] = '我发了一个[%s红包]，请下载最新版扫雷联萌领取~' % title
    msg[0] = seg
    return msg


def mutate_msg(message: str, mutate: bool = False) -> Message:
    """Mutate a message."""
    msg = replace_redbag_msg(message)
    if not mutate:
        return msg  # just wrap the message

    place = random.choice(range(0, len(msg)))
    seg = msg[place]
    if seg.type == 'text':
        number = random.choice('一' * 42 + '二三四五六七八九')
        plain = seg.data['text'].replace('一', number)
        start, stop = sorted(random.sample(range(0, len(plain)), 2))
        stop = start + (stop - start) * (plain == seg.data['text'])  # reverse the text if the number is not replaced
        target = plain[start:stop]
        result = plain[:start] + target[::-1] + plain[stop:]
        seg.data['text'] = result
    elif seg.type == 'face':
        # select a different face
        seg.data['id'] = random.choice(frequent_face_id)
    msg[place] = seg

    return Message(msg)
