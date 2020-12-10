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
of the item, currently it could be 1 (for admiration) or 2 (for cheers).
If you think the item is a body, enter 1 or 2; if you think the item
is an ending, enter -1 or -2. Last, enter another separator, and enter 
whether the item is an image, 0 for no, and 1 for yes. If you handles 
nicely, the database will be working after a reload of this module.

Warnings:
Make sure you have at least 1 image if you want to set the parameter
include_image to True. The message will not be sent if no images are
found. You can see the logs for more infomation.
"""

import csv
import os
import random
import nonebot
from .config import Config
from nonebot.log import logger

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())
resource_location = os.path.join(os.getcwd(),
                                  plugin_config.resource_location)

try:
    resource_database = []
    logger.info('Constructing resource database ...')
    with open(resource_location, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=plugin_config.resource_separator)
        for line in csv_reader:
            logger.debug('Loading resource: %s, TYPE=%s, IMG=%s' % tuple(line))
            resource_database.append(line)
except Exception:
    resource_database = []
    logger.warning('Failed to load resource database, feature limited.')


def _get_body(_type: str, _image: str):
    """A database filter to generate required message body."""
    body_all = [
        row[0] for row in resource_database
        if _type == row[1] and _image == row[2]
    ]
    return random.choice(body_all) if body_all else '太强了'


def _get_ending(_type: str):
    """A database filter to generate required message ending."""
    ending_all = [
        row[0] for row in resource_database if row[1] == f'-{_type}'
    ]
    return random.choice(ending_all) if ending_all else '！'


def exclaim_msg(person: str, _type: str, include_image: bool):
    """
    Get exclaiming message from the database.
    
    This should be the only function being called when this package
    is imported. The message will be made up of 3 parts: person,
    body and ending. If the include_image parameter is set to True,
    an image will be sent. Please note that the resource should be
    specified explicitly, and the message won't be sent successfully
    if the resource file is empty.
    """
    if not person:
        person = '大佬'  # default person

    if include_image and random.randint(0, 1):
        image_data = _get_body(_type=_type, _image='1')
        image_path = os.path.join(os.getcwd(), image_data)
        message = f'[CQ:image,file=file:///{image_path}]'
        return message  # return the image only

    msg_body = _get_body(_type=_type, _image='0')
    msg_ending = _get_ending(_type=_type)
    # beautify visualizations
    return person + ' ' * (person[-1].isascii() and 
                           msg_body[0].isascii()) + msg_body + msg_ending
