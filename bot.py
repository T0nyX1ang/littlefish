"""
This is the initialization file.

Please note that this file is for production.

Please run this file by typing: py -3 bot.py on Windows,
and python3 bot.py on *nix. Make sure you have installed
all the dependencies and fonts required before you run this program.
"""

import nonebot
import time
from nonebot.log import logger, default_format
from nonebot.adapters.cqhttp import Bot

run_time = time.time()
time_sec = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(run_time))
time_msec = '%03d' % ((run_time - int(run_time)) * 1000)
file_time_tag = time_sec + '-' + time_msec

logger.add("logs/%s-errors.log" % file_time_tag,
           rotation="00:00",
           diagnose=False,
           level="ERROR",
           format=default_format)

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", Bot)
nonebot.load_plugin('nonebot_plugin_apscheduler')
nonebot.load_plugins('littlefish')

if __name__ == '__main__':
    nonebot.run()
