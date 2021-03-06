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

import itertools
import random
import traceback
import nonebot
from ftptsgame import FTPtsGame
from nonebot.log import logger
from .config import FTPtsConfig

global_config = nonebot.get_driver().config
plugin_config = FTPtsConfig(**global_config.dict())
max_number = plugin_config.ftpts_max_number
target = plugin_config.ftpts_target
random_threshold = plugin_config.ftpts_random_threshold
problem_database = list(itertools.combinations_with_replacement(range(0, max_number + 1), 5))

app_pool = {}  # a pool for all ftpts apps
addscore_pool = {}  # a pool for all addscore parameters


def init(universal_id: str):
    """Initialize the ftpts app."""
    if universal_id not in app_pool:
        app_pool[universal_id] = FTPtsGame()

    if app_pool[universal_id].is_playing():
        raise PermissionError('Game has started.')


def current(universal_id: str) -> dict:
    """Get the problem's information."""
    elapsed = app_pool[universal_id].get_elapsed_time()
    elapsed_time = elapsed.seconds + elapsed.microseconds / 1000000
    info = {
        'problem': app_pool[universal_id].get_current_problem(),
        'target': app_pool[universal_id].get_current_target(),
        'total': app_pool[universal_id].get_total_solution_number(),
        'current': app_pool[universal_id].get_current_solution_number(),
        'solutions': app_pool[universal_id].get_current_solutions(),
        'stats': app_pool[universal_id].get_current_player_statistics(),
        'remaining': [],
        'elapsed': elapsed_time,
    }
    return info


def start(universal_id: str, addscore: bool = True, enforce_random: bool = False) -> dict:
    """Start the game."""
    found = False
    threshold = random_threshold + enforce_random  # make sure the threshold greater than 1 if enforced
    real = target + random.randint(-18, 18) * (random.random() < threshold)
    while not found:
        problem = random.choice(problem_database)
        try:
            app_pool[universal_id].generate_problem(problem, real)
            found = True
        except Exception:
            found = False
    app_pool[universal_id].start()
    addscore_pool[universal_id] = addscore
    return current(universal_id)


def stop(universal_id: str) -> dict:
    """Stop the game."""
    info = current(universal_id)
    info['remaining'] = app_pool[universal_id].get_remaining_solutions()
    info['addscore'] = addscore_pool[universal_id]
    app_pool[universal_id].stop()
    return info


def solve(universal_id: str, expr: str, player_id: str, _id: int) -> dict:
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

    info = current(universal_id)
    info['hint'] = hint
    info['interval'] = solution_time
    return info


def status(universal_id: str) -> bool:
    """Get the status of the current game."""
    if universal_id in app_pool:
        return app_pool[universal_id].is_playing()
    else:
        return False
