"""
This is the initialization file.

Please run this file by typing: py -3 bot.py on Windows,
and python3 bot.py on *nix. Make sure you have installed
all the dependencies required before you run this program.
If you want to enable the developing mode, please add a --dev
option after the original command.

In the developing mode, the logging will not be saved to disk,
the logging level will be DEBUG level, the auto-reloading feature
will be enabled and a test frontend for the bot will be created.
Please disable developing mode if you want to run the bot in
a stable environment.
"""

import argparse
import nonebot
from nonebot.log import logger, default_format
from nonebot.adapters.cqhttp import Bot

parser = argparse.ArgumentParser(description='A bot for minesweeper league.')
parser.add_argument('--dev', action='store_true', default=False, help='Enable the developing mode')
args = parser.parse_args()

if not args.dev:  # save the logs to disk in non-developing mode
    logger.add("logs/errors_{time}.log", rotation="00:00", diagnose=False, level="ERROR", format=default_format)

nonebot.init(debug=args.dev)
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", Bot)
nonebot.load_plugin('nonebot_plugin_apscheduler')
nonebot.load_plugins('littlefish')

if args.dev:
    app = nonebot.get_asgi()  # load the ASGI app
    nonebot.load_builtin_plugins()  # load the builtin plugins as well
    nonebot.load_plugin('nonebot_plugin_test')  # enable the test frontend in developing mode

if __name__ == '__main__':
    nonebot.run(app='bot:app' * args.dev)
