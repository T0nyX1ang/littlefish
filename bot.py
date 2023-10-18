"""
This is the initialization file.

You don't have to execute this file manually. Instead, you should
execute `nb run` command instead.
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
