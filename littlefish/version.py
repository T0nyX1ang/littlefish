"""
Print the version of littlefish.

[Deprecation] This plugin is deprecated now.
"""

import os
import httpx
import semver
from nonebot.log import logger

version_directory = os.path.join(os.getcwd(), 'VERSION')

with open(version_directory, 'r', encoding='utf-8') as f:
    version = str(f.read()).strip()


async def get_server_version():
    """Get the version of littlefish on Github."""
    url = 'https://api.github.com/repos/T0nyX1ang/littlefish/releases'
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url=url)
            data = r.json()[0]  # get the latest version
            server_version = data['tag_name']
            if semver.compare(version, server_version) < 0:
                logger.warning('New version [%s] available.' % server_version)
                return
            logger.info('Version check completed, littlefish is up to date.')
    except Exception:
        logger.warning('Version check failed, please check your network.')
