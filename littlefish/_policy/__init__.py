"""
A policy module which will handle the rules of the commands.

The module will load the policy file by the location.
About the policy file:
The policy file should be a valid json file, which contains the
following information. Please note that the json file should not
contain any annotations.
{
    bot_id: {
        // config for this bot
        group_id: {
            // config for this group
            +: [1, 2, 3], // this should be the whitelist
            -: [4, 5, 6]  // this should be the blacklist
        }
        another_group_id: {
            // config for another group
        }
    }
    another_bid: {
        another_group_id: {
            // config for another group
        }
        // config for another group
    }
    // config for another bot
}

How is it works?
The policy checker will allow/deny a command by several key-value
matches. On the bot/group level, if the bot/group key doesn't exist,
the checker will allow the command; on the whitelist/blacklist level,
if the sender appears in the whitelist AND doesn't appear in the black-
list, the checker will allow the command, or it will block the command.
Please note that, when a whitelist/blacklist key doesn' exist, the
checker will assume the whitelist/blacklist doesn't exist and allow
the command on the whitelist/blacklist level.

How to use?
The checker is wrapped as a nonebot.rule.Rule, you can use it in any
commands containing the keyword argument 'rule'. The policy config will
be reloaded on every startup of the bot itself.
"""

import nonebot
import json
import os
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.rule import Rule
from .config import Config

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())
policy_config_location = os.path.join(os.getcwd(),
                                      plugin_config.policy_config_location)

try:
    with open(policy_config_location, 'r', encoding='utf-8') as f:
        policy_config = json.loads(f.read())
        logger.info('Policy file is loaded ...')
        logger.debug('Policy control data: %s' % policy_config)
except Exception:
    policy_config = {}
    logger.warning('Failed to load policy file, using empty policy file ...')


def check(command_name: str) -> Rule:
    """Check the policy of each command by name."""
    _name = command_name

    async def _check(bot: Bot, event: Event, state: dict) -> bool:
        """A rule wrapper for each command."""
        logger.debug('Checking command: [%s].' % _name)
        bid = f'{event.self_id}'
        gid = f'{event.group_id}'
        sid = event.user_id
        try:
            # Check the whitelist policy by name.
            in_whitelist = ('+' not in policy_config[bid][gid][_name] or
                            sid in policy_config[bid][gid][_name]['+'])

            # Check the blacklist policy by name.
            in_blacklist = ('-' not in policy_config[bid][gid][_name] or
                            sid not in policy_config[bid][gid][_name]['-'])

            # Combine the whitelist and blacklist together
            return in_whitelist and in_blacklist
        except Exception:
            logger.debug('No policy config found for this command.')
            return True

    return Rule(_check)
