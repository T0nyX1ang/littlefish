"""This is the initialization file.

Please note that this file is for production.

Please run this file by typing: py -3 bot.py on Windows,
and python3 bot.py on *nix. Make sure you have installed
all the dependencies and fonts required before you run this program.
"""

import nonebot
from nonebot.log import logger, default_format
from nonebot.adapters.cqhttp import Bot

logger.add("logs/errors_{time}.log", rotation="00:00", diagnose=False, level="ERROR", format=default_format)

nonebot.init(debug=False)
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", Bot)
nonebot.load_plugin('nonebot_plugin_apscheduler')
nonebot.load_plugins('littlefish')

if __name__ == '__main__':
    nonebot.run()
