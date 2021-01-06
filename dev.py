"""
This is the initialization file.

Please note that this file is for development.

Please run this file by typing: py -3 dev.py on Windows,
and python3 dev.py on *nix. You need to install an additional
package named: nonebot_plugin_test and change view.py#L14 with:
from nonebot.drivers import WebSocket as BaseWebSocket
"""

import nonebot
from nonebot.adapters.cqhttp import Bot

nonebot.init()
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", Bot)
nonebot.load_plugin('nonebot_plugin_apscheduler')
nonebot.load_plugin('nonebot_plugin_test')
nonebot.load_plugins('littlefish')

if __name__ == '__main__':
    nonebot.run(app='dev:app')
