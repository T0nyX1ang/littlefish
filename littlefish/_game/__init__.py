"""
Basic operations for the bot's games.

The plugin includes:
* Global operations of all games (searching names, getting scores and viewing ranks).
* Basic operations of ftpts(calc42) game.
"""


def get_member_name(members: dict, user_id: str) -> str:
    """Get member name within a dictionary."""
    try:
        return members[user_id]['card'] if members[user_id]['card'] else members[user_id]['nickname']
    except Exception:
        return '匿名大佬'


def get_member_stats(members: dict, user_id: str, game_type: str) -> tuple:
    """Get a member's score and rank of a certain game within a dictionary."""
    ranking = sorted(members, key=lambda x: (members[x][game_type], x), reverse=True)
    result = 0
    for user in ranking:
        result += 1
        if user_id == user:
            break

    score = members[user_id][game_type]
    if result == 1:
        return '当前积分: %d，排名: %d' % (score, result)

    upper_score = members[ranking[result - 2]][game_type]
    distance = upper_score - score
    return '当前积分: %d(+%d)，排名: %d' % (score, distance, result)


def get_game_rank(members: dict, game_type: str):
    """Get a member's rank of a certain game within a dictionary."""
    ranking = sorted(members, key=lambda x: (members[x][game_type], x), reverse=True)
    rank_message = ''

    i = 0
    while i < min(10, len(ranking)) and members[ranking[i]][game_type] > 0:
        rank_message += '%d: %s - %d\n' % (i + 1, get_member_name(members, ranking[i]), members[ranking[i]][game_type])
        i += 1

    return rank_message.strip()
