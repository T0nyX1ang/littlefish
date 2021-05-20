"""
Basic operations for the bot's games.

The plugin includes:
* Global operations of all games (searching names, getting scores and viewing ranks).
* Global schedulers of all games (start arbitrary schedulers and remove them)
* Basic operations of ftpts(calc42) game.

The plugin requires the database plugin (littlefish._db) to work normally.
"""

import nonebot
from nonebot.adapters.cqhttp import Bot
from littlefish._db import load


def get_member_name(universal_id: str, user_id: str) -> str:
    """Get member name in a certain group with a certain bot."""
    try:
        members = load(universal_id, 'members')
        return members[user_id]['card'] if members[user_id]['card'] else members[user_id]['nickname']
    except Exception:
        return '匿名大佬'


def get_member_stats(universal_id: str, user_id: str, rank_item: str) -> tuple:
    """Get a member's score and rank of a certain game in a certain group with a certain bot."""
    members = load(universal_id, 'members')
    ranking = sorted(members, key=lambda x: (members[x][rank_item], x), reverse=True)
    result = 0
    for user in ranking:
        result += 1
        if user_id == user:
            break

    score = members[user_id][rank_item]
    if result == 1:
        return '排名: %d\n积分: %d' % (result, score)

    upper_score = members[ranking[result - 2]][rank_item]
    distance = upper_score - score
    return '排名: %d\n积分: %d\n距上一名: %d' % (result, score, distance)


def get_game_rank(universal_id: str, rank_item: str) -> str:
    """Get a member's rank of a certain game in a certain group with a certain bot."""
    members = load(universal_id, 'members')
    ranking = sorted(members, key=lambda x: (members[x][rank_item], x), reverse=True)
    rank_message = ''

    i = 0
    while i < min(10, len(ranking)) and members[ranking[i]][rank_item] > 0:
        rank_message += '%d: %s - %d\n' % (i + 1, get_member_name(universal_id, ranking[i]), members[ranking[i]][rank_item])
        i += 1

    if i == 0:
        return '当前暂无该项排名~'

    return rank_message.strip()


class GameManager(object):
    """A manager for all games."""

    def __init__(self, game_type):
        """Initialize the manager."""
        self.scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler
        self.game_type = game_type
        self.invoker = {}

    def add_scheduler(self, bot: Bot, universal_id: str, scheduler_func: callable, scheduler_interval: int):
        """Initialize the scheduler for a certain game."""
        self.scheduler.add_job(
            func=scheduler_func,
            trigger='interval',
            seconds=scheduler_interval,
            args=(bot, universal_id),
            misfire_grace_time=30,
            id='%s_%s_%s' % (self.game_type, scheduler_func.__name__, universal_id),
            replace_existing=True,
        )

    def remove_schedulers(self, universal_id: str):
        """Remove all schedulers of a certain game."""
        for job in self.scheduler.get_jobs():
            if self.game_type in job.id and universal_id in job.id:
                job.remove()  # remove the job

    def set_invoker(self, universal_id: str, invoker: int = -1):
        """Set the invoker for a certain game."""
        self.invoker[universal_id] = invoker

    def reset_invoker(self, universal_id: str):
        """Clear the invoker for a certain game."""
        self.invoker[universal_id] = -1

    def get_invoker(self, universal_id: str) -> int:
        """Get the invoker for a certain game."""
        try:
            return self.invoker[universal_id]
        except Exception:
            return -1
