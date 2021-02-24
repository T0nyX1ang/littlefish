"""
Basic operations of ftpts(calc42) game.

Available operations:
* initialize the game.
* start the game.
* put forward a solution for the game.
* stop the game.
* get the playing status of the game.
* get the current problem
"""

import datetime
import itertools
import nonebot
import random
import traceback
from .config import FTPtsConfig
from ftptsgame import FTPtsGame
from nonebot.log import logger

global_config = nonebot.get_driver().config
plugin_config = FTPtsConfig(**global_config.dict())
max_number = plugin_config.ftpts_max_number
target = plugin_config.ftpts_target
allowed_hours = plugin_config.ftpts_allowed_hours
problem_database = list(
    itertools.combinations_with_replacement(range(0, max_number + 1), 5))

app_pool = {}


def init(universal_id: str):
    """Initialize the ftpts app."""
    if universal_id not in app_pool:
        app_pool[universal_id] = FTPtsGame(target)

    if app_pool[universal_id].is_playing():
        raise PermissionError('Game has started.')

    hour_now = datetime.datetime.now().hour
    if hour_now not in allowed_hours:
        raise PermissionError('Not in gaming time.')


def _info(universal_id: str) -> dict:
    """Get the problem's information. Protected method."""
    elapsed = app_pool[universal_id].get_elapsed_time()
    elapsed_time = elapsed.seconds + elapsed.microseconds / 1000000
    info = {
        'problem': app_pool[universal_id].get_current_problem(),
        'target': target,
        'total': app_pool[universal_id].get_total_solution_number(),
        'current': app_pool[universal_id].get_current_solution_number(),
        'elapsed': elapsed_time,
    }
    return info


def start(universal_id: str) -> dict:
    """Start the game."""
    found = False
    while not found:
        problem = random.choice(problem_database)
        try:
            app_pool[universal_id].generate_problem(problem)
            found = True
        except Exception:
            found = False
    app_pool[universal_id].start()
    return _info(universal_id)


def stop(universal_id: str) -> dict:
    """Stop the game."""
    info = _info(universal_id)
    info['stats'] = app_pool[universal_id].get_current_player_statistics()
    info['remaining'] = app_pool[universal_id].get_remaining_solutions()
    app_pool[universal_id].stop()
    return info


def solve(universal_id: str, expr: str, player_id: str) -> dict:
    """Put forward a solution during the game."""
    hint = ''
    solution_time = 0
    try:
        elapsed = app_pool[universal_id].solve(expr, player_id)
        solution_time = elapsed.seconds + elapsed.microseconds / 1000000
    except (OverflowError, SyntaxError, ValueError):
        hint = '输入错误'
    except ArithmeticError as ae:
        hint = '答案错误[%s]' % (str(ae))
    except LookupError as le:
        hint = '答案与[%s]重复' % (str(le))
    except Exception:
        hint = '未知错误'
        logger.error(traceback.format_exc())

    info = _info(universal_id)
    info['hint'] = hint
    info['interval'] = solution_time
    return info


def status(universal_id: str) -> bool:
    """Get the status of the current game."""
    if universal_id in app_pool:
        return app_pool[universal_id].is_playing()
    else:
        return False
