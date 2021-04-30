"""
User defined plugin rules and policies.

Features:
* on_raw_keyword: check the raw message contains the target keyword
* on_simple_command: check the command contains no parameters
"""

from nonebot import on_message
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.adapters.cqhttp import Bot, Event


def on_raw_keyword(keyword: str, rule: Rule = None, **kwargs) -> Matcher:
    """Ensure the raw message contains the target keyword."""

    def raw_keyword(keyword: str) -> Rule:
        """Ensure the raw message contains the target keyword."""

        async def _raw_keyword(bot: Bot, event: Event, state: dict) -> bool:
            """A rule wrapper for each command."""
            return keyword in str(event.message)

        return Rule(_raw_keyword)

    return on_message(raw_keyword(keyword) & rule, **kwargs)


def on_simple_command(cmd: str, aliases: set = None, rule: Rule = None, **kwargs) -> Matcher:
    """Recognize a command that does not contain any parameters."""

    def simple_command(cmd: str, aliases: set = None) -> Rule:
        """Recognize a command that does not contain any parameters."""
        commands = set([cmd]) | (aliases or set())  # generate the commands

        async def _simple_command(bot: Bot, event: Event, state: dict) -> bool:
            """A rule wrapper for each command."""
            return str(event.message).strip() in commands

        return Rule(_simple_command)

    return on_message(simple_command(cmd, aliases) & rule, **kwargs)
