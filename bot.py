"""
This is the initialization file.

Please run this file by typing: py -3 bot.py on Windows,
and python3 bot.py on *nix. Make sure you have installed
all the dependencies required before you run this program.
"""

import nonebot
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebot.log import logger, default_format
from fastapi.staticfiles import StaticFiles

nonebot.init()

logger.add("logs/errors_{time}.log", rotation="00:00", diagnose=False, level="ERROR", format=default_format)

driver = nonebot.get_driver()
driver.register_adapter(ConsoleAdapter)
driver.register_adapter(OnebotV11Adapter)
server = driver.server_app
server.mount("/docs", StaticFiles(directory='site', html=True), name="littlefish-docs")

nonebot.load_from_toml('pyproject.toml')

if __name__ == "__main__":
    nonebot.run()
