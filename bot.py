import os
import sys
import nonebot
try:
	import config
except ImportError:
	import nonebot.default_config
	config = nonebot.default_config

if len(config.SUPERUSERS) > 1:
	print('Only one superuser is allowed.')
	sys.exit()

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(os.path.join(os.path.dirname(__file__), 'mswar', 'plugins'), 'mswar.plugins')
    nonebot.run()
