"""
A policy module which will handle the rules of the commands.

The module will load the policy file by the location.
About the policy file:
The policy file should be a valid json file, which contains the
following information. Please note that the json file should not
contain any annotations.
{
    "bot_id": {
        // config for this bot
        "group_id": {
            // config for this group
            "command": {
                "+": [1, 2, 3], // this should be the whitelist
                "-": [4, 5, 6], // this should be the blacklist
                "@": { *APScheduler-like config* } // this should be the broadcast option
            }
            // config for another command
        }
        "another_group_id": {
            // config for another group
        }
    }
    "another_bot_id": {
        "another_group_id": {
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
the command on the whitelist/blacklist level. About the broadcasting
feature, you need to enable it manually in the configuration, or it
is disabled by default. About the empty feature, you can enforce 0
arguments in a command.

How to use?
The checker is a nonebot.internal.rule.Rule class, you can use it in any
commands containing the keyword argument 'rule'. The policy config will
be reloaded on every startup of the bot itself. The broadcast is wrapped
as a normal decorator, you need to decorate the function only.

Additional features:
* Get validated (bot_id, group_id) tuples.
* Create/Revoke a temporary policy: this will create/revoke a temporary
policy into the memory, but not saved into the policy file on disk.
* Check if the command is invoked in a group.
"""

import json
import os
import nonebot
from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.rule import Rule
from nonebot_plugin_apscheduler import scheduler

from .config import PolicyConfig

global_config = nonebot.get_driver().config
plugin_config = PolicyConfig(**global_config.dict())
policy_config_location = os.path.join(os.getcwd(), plugin_config.policy_config_location)

try:
    with open(policy_config_location, 'r', encoding='utf-8') as f:
        policy_config = json.loads(f.read())
        logger.info('Policy file is loaded ...')
        logger.debug(f'Policy control data: {policy_config}')
except Exception:
    policy_config = {}
    logger.warning('Failed to load policy file, using empty policy file ...')


def valid(command_name: str) -> list:
    """Get all valid [bot_id, group_id] tuple for policy control."""
    return [(bid, gid)
            for bid in policy_config.keys()
            for gid in policy_config[bid].keys()
            if command_name in policy_config[bid][gid]]


class PolicyRule:
    """Check the policy of each command by name."""

    __slots__ = ('command_name',)

    def __init__(self, command_name: str):
        """Initialize the rule."""
        self.command_name = command_name

    async def __call__(self, event: Event) -> bool:
        """Rule wrapper for "check" item in the policy control."""
        logger.debug(f'Checking command: [{self.command_name}].')

        try:
            # Fetch information from event
            bid = f'{event.self_id}'
            sid = f'{event.get_user_id()}'
            gid = f'{event.group_id}'

            # Check the whitelist policy by name.
            in_whitelist = ('+' not in policy_config[bid][gid][self.command_name] or
                            sid in policy_config[bid][gid][self.command_name]['+'])

            # Check the blacklist policy by name.
            not_in_blacklist = ('-' not in policy_config[bid][gid][self.command_name] or
                                sid not in policy_config[bid][gid][self.command_name]['-'])

            # Combine the whitelist and blacklist together
            return in_whitelist and not_in_blacklist
        except Exception:
            return True


def check(command_name: str) -> Rule:
    """Check the policy of each command by name."""
    return Rule(PolicyRule(command_name))


def broadcast(command_name: str, identifier: str = '@') -> bool:
    """Check the policy of each broadcast by name."""
    _name, _idt = command_name, identifier

    def _broadcast(func):
        """Rule wrapper for "broadcast" item in the policy control."""
        logger.debug(f'Checking broadcast: [{_name}].')
        for bid, gid in valid(_name):
            try:
                scheduler.add_job(func=func,
                                  args=(bid, gid),
                                  trigger='cron',
                                  id=f'{_name}_{_idt}_broadcast_{bid}_{gid}',
                                  misfire_grace_time=30,
                                  replace_existing=True,
                                  **policy_config[bid][gid][_name][_idt])
                logger.debug(f'Created broadcast [{_name}] with bot [{bid}] in group [{gid}].')
            except Exception:
                logger.debug(f'Skipped broadcast [{_name}] with bot [{bid}] in group [{gid}].')

    return _broadcast


async def is_in_group(event: Event) -> bool:
    """Check if the command is invoked in a group."""
    return hasattr(event, 'group_id')
