"""
Basic operations for the bot's games.

The plugin includes:
* Global operations of all games (searching names, getting scores and viewing ranks).
* Basic operations of ftpts(calc42) game.

The plugin requires the database plugin (littlefish._db) to work normally.
"""

import nonebot
from nonebot.adapters.cqhttp import Bot
from littlefish._db import load

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler


def get_member_name(universal_id: str, user_id: str) -> str:
    """Get member name in a certain group with a certain bot."""
    try:
        members = load(universal_id, 'members')
        return members[user_id]['card'] if members[user_id]['card'] else members[user_id]['nickname']
    except Exception:
        return '匿名大佬'


def get_member_stats(universal_id: str, user_id: str, game_type: str) -> tuple:
    """Get a member's score and rank of a certain game in a certain group with a certain bot."""
    members = load(universal_id, 'members')
    ranking = sorted(members, key=lambda x: (members[x][game_type], x), reverse=True)
    result = 0
    for user in ranking:
        result += 1
        if user_id == user:
            break

    score = members[user_id][game_type]
    if result == 1:
        return '排名: %d\n积分: %d' % (result, score)

    upper_score = members[ranking[result - 2]][game_type]
    distance = upper_score - score
    return '排名: %d\n积分: %d\n距上一名: %d' % (result, score, distance)


def get_game_rank(universal_id: str, game_type: str):
    """Get a member's rank of a certain game in a certain group with a certain bot."""
    members = load(universal_id, 'members')
    ranking = sorted(members, key=lambda x: (members[x][game_type], x), reverse=True)
    rank_message = ''

    i = 0
    while i < min(10, len(ranking)) and members[ranking[i]][game_type] > 0:
        rank_message += '%d: %s - %d\n' % (i + 1, get_member_name(universal_id, ranking[i]), members[ranking[i]][game_type])
        i += 1

    if i == 0:
        return '当前暂无该项排名~'

    return rank_message.strip()


def start_game_schedulers(bot: Bot, universal_id: str, game_type: str, **schedulers: dict):
    """Initialize the scheduler for a certain game."""
    for scheduler_name in schedulers:
        scheduler_func, scheduler_interval = schedulers[scheduler_name]

        scheduler.add_job(
            func=scheduler_func,
            trigger='interval',
            seconds=scheduler_interval,
            args=(bot, universal_id),
            misfire_grace_time=30,
            id='%s_%s_%s' % (game_type, scheduler_name, universal_id),
            replace_existing=True,
        )


def stop_game_schedulers(universal_id: str, game_type: str):
    """Initialize the scheduler for a certain game."""
    for job in scheduler.get_jobs():
        if game_type in job.id and universal_id in job.id:
            job.remove()  # remove the job
