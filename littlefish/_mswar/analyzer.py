"""
An analyzer for minesweeping game.

Please note that this module needs to be maintained or
refactored properly.

The analyzer will analyze available information during a game.
Available information:
* mode.
* time/est.
* solved_bv/bv/bvs.
* ce/ces.
* cl/cls.
* l/fl/r/d.
* path.
* op/is.
* ioe/iome.
* qg/rqp.
* corr/thrp.
* stnb (in a standard game)
"""

import math

def adjacent(row, col):
    yield row - 1, col - 1
    yield row, col - 1
    yield row + 1, col - 1
    yield row - 1, col
    yield row + 1, col
    yield row - 1, col + 1
    yield row, col + 1
    yield row + 1, col + 1

def get_board(board_detail):
    board = []
    for each_row in board_detail:
        row = list(each_row)
        board.append(row)
    return board

def get_row(board):
    return len(board)

def get_column(board):
    return len(board[0])

def get_mines(board, marker):
    mines = 0
    for row in range(0, get_row(board)):
        for col in range(0, get_column(board)):
            if board[row][col] == '9':
                mines += 1
                marker[row][col] = True
    return mines

def get_difficulty(row, column, mines):
    size = (row, column, mines)
    if size == (8, 8, 10):
        return 'beg'
    elif size == (16, 16, 40):
        return 'int'
    elif size == (16, 30, 99):
        return 'exp-h'
    elif size == (30, 16, 99):
        return 'exp-v'
    else:
        return '%dx%d + %d' % size

def get_openings(board, marker):
    openings = 0
    rows = get_row(board)
    cols = get_column(board)
    for row in range(0, rows):
        for col in range(0, cols):
            if board[row][col] == '0' and not marker[row][col]:
                openings += 1
                marker[row][col] = True
                stack = [('0', row, col)]
                while len(stack) > 0:
                    cur_num, cur_row, cur_col = stack.pop()
                    marker[cur_row][cur_col] = True
                    # open again if find an opening
                    if cur_num == '0': 
                        for each_coord in adjacent(cur_row, cur_col):
                            ready_row, ready_col = each_coord
                            if 0 <= ready_row < rows and 0 <= ready_col < cols and not marker[ready_row][ready_col]:
                                ready_num = board[ready_row][ready_col]
                                stack.append((ready_num, ready_row, ready_col))
                                marker[ready_row][ready_col] = True
    return openings

def get_isolated_bv(board, marker):
    isolated_bv = 0
    for row in range(0, get_row(board)):
        for col in range(0, get_column(board)):
            if not marker[row][col]:
                isolated_bv += 1
    return isolated_bv

def get_islands(board, marker):
    islands = 0
    rows = get_row(board)
    cols = get_column(board)
    for row in range(0, rows):
        for col in range(0, cols):
            if not marker[row][col]:
                islands += 1
                marker[row][col] = True
                stack = [(row, col)]
                while len(stack) > 0:
                    cur_row, cur_col = stack.pop()
                    marker[cur_row][cur_col] = True
                    # search again if find an adjacent isolated bv 
                    for each_coord in adjacent(cur_row, cur_col):
                        ready_row, ready_col = each_coord
                        if 0 <= ready_row < rows and 0 <= ready_col < cols and not marker[ready_row][ready_col]:
                            stack.append((ready_row, ready_col))
                            marker[ready_row][ready_col] = True
    return islands

def get_action(action_detail):
    split_action = []
    for each_action in action_detail:
        operation, row, column, current_time = each_action.split(':')
        split_action.append([int(operation), int(row), int(column), int(current_time)])

    current, threshold = 0, 3
    while current < len(split_action):
        # find out the release key
        if (split_action[current][0] == 3):
            tag_row = split_action[current][1]
            tag_col = split_action[current][2]
            release = current
            # find out the assurance final key
            if release < len(split_action):
                final = release + 1
                while final < len(split_action) and (split_action[final][3] - split_action[release][3] <= threshold) and (split_action[final][0] != 1 or split_action[final][1] != tag_row or split_action[final][2] != tag_col):
                    final += 1
                if final < len(split_action) and (split_action[final][3] - split_action[release][3] <= threshold):
                    split_action[final][0] = 4
                else:
                    final = release - 1
                    while final >= 0 and (split_action[release][3] - split_action[final][3] <= threshold) and (split_action[final][0] != 1 or split_action[final][1] != tag_row or split_action[final][2] != tag_col):
                        final -= 1
                    if final >= 0 and (split_action[release][3] - split_action[final][3] <= threshold):
                        split_action[final][0] = 4
        current += 1
    return split_action

def get_rtime(action):
    return action[-1][3] / 1000

def get_path(action):
    path = 0
    current, last = 0, 0
    while current < len(action):
        if action[current][0] in [0, 1, 4]:
            path += math.sqrt((action[current][1] - action[last][1]) ** 2 + (action[current][2] - action[last][2]) ** 2)
            last = current
        current += 1
    return path

def get_clicks(action):
    left, double, right = 0, 0, 0
    for current in range(0, len(action)):
        if action[current][0] == 0:
            left += 1
        elif action[current][0] == 1:
            right += 1
        elif action[current][0] == 4:
            double += 1

    return left, right, double

def get_effective_operations(board, action):
    rows = get_row(board)
    cols = get_column(board)
    current_status = [[0 for col in range(0, get_column(board))] for row in range(0, get_row(board))]
    effective, flags, unflags, misflags, misunflags, solved = 0, 0, 0, 0, 0, {'op': 0, 'bv': 0}

    def deal_with_op(row, col):
        number = board[row][col]
        if number == '0':
            solved['op'] += 1
            solved['bv'] += 1
        elif number != '9':
            if '0' not in [board[each_coord[0]][each_coord[1]] for each_coord in adjacent(row, col) if 0 <= each_coord[0] < rows and 0 <= each_coord[1] < cols]:
                solved['bv'] += 1

        stack = [(number, row, col)]
        while len(stack) > 0:
            cur_num, cur_row, cur_col = stack.pop()

            if cur_num == '9':
                current_status[cur_row][cur_col] = -2
            
            # open again if find an opening
            if cur_num == '0': 
                for each_coord in adjacent(cur_row, cur_col):
                    ready_row, ready_col = each_coord
                    if 0 <= ready_row < rows and 0 <= ready_col < cols and not current_status[ready_row][ready_col] and board[ready_row][ready_col] != '9':
                        ready_num = board[ready_row][ready_col]
                        stack.append((ready_num, ready_row, ready_col))
                        current_status[ready_row][ready_col] = 1

    for current in range(0, len(action)):
        act_no, row, col, time = action[current]

        if act_no == 0:
            # deal with opening
            if current_status[row][col] == 0:
                effective += 1
                current_status[row][col] = 1
                deal_with_op(row, col)
            
        elif act_no == 1:
            # deal with flagging and unflagging
            effective += 1
            if current_status[row][col] == 0:
                flags += 1
                current_status[row][col] = -1
                if board[row][col] != '9':
                    misflags += 1
            elif current_status[row][col] == -1:
                flags -= 1
                current_status[row][col] = 0
                if board[row][col] == '9':
                    misunflags += 1
                else:
                    unflags += 1

        elif act_no == 4:
            # deal with chording
            adjacent_mines, adjacent_unopen = 0, 0
            for each_coord in adjacent(row, col):
                ready_row, ready_col = each_coord
                if 0 <= ready_row < rows and 0 <= ready_col < cols and current_status[ready_row][ready_col] == -1:
                    adjacent_mines += 1
                elif 0 <= ready_row < rows and 0 <= ready_col < cols and current_status[ready_row][ready_col] == 0:
                    adjacent_unopen += 1

            if adjacent_mines == int(board[row][col]) and adjacent_mines > 0 and adjacent_unopen:
                effective += 1
                for each_coord in adjacent(row, col):
                    ready_row, ready_col = each_coord
                    if 0 <= ready_row < rows and 0 <= ready_col < cols:
                        if not current_status[ready_row][ready_col] and board[ready_row][ready_col] != '9':
                            current_status[ready_row][ready_col] = 1
                            deal_with_op(ready_row, ready_col)
                        elif current_status[ready_row][ready_col] == -1 and board[ready_row][ready_col] != '9':
                            current_status[ready_row][ready_col] = -3

    return effective, flags, unflags + misflags + misunflags, solved['op'], solved['bv'], current_status

def get_board_result(board):
    result = {}
    result['board'] = board
    result['row'] = get_row(board)
    result['column'] = get_column(board)

    marker = [[False for col in range(0, get_column(board))] for row in range(0, get_row(board))]
    result['mines'] = get_mines(board, marker)
    result['difficulty'] = get_difficulty(result['row'], result['column'], result['mines'])
    result['op'] = get_openings(board, marker)
    result['bv'] = result['op'] + get_isolated_bv(board, marker)
    result['is'] = get_islands(board, marker)
    return result    

def get_result(board, action):
    result = get_board_result(board)
    
    result['rtime'] = get_rtime(action)
    result['path'] = get_path(action)

    result['left'], result['right'], result['double'] = get_clicks(action)
    result['cl'] = result['left'] + result['right'] + result['double']
    result['ce'], result['flags'], result['wasted_flagging'], result['solved_op'], result['solved_bv'], result['current_status'] = get_effective_operations(board, action)

    result['fmode'] = 'FL' if result['right'] > 0 else 'NF'
    result['bvs'] = result['solved_bv'] / result['rtime']
    result['est'] = result['rtime'] / result['solved_bv'] * result['bv'] if result['solved_bv'] else math.inf
    result['rqp'] = (result['rtime'] + 1) / result['bvs'] if result['solved_bv'] else math.inf
    result['qg'] = result['rtime'] ** 1.7 / result['solved_bv'] if result['solved_bv'] else math.inf
    result['cls'] = result['cl'] / result['rtime']
    result['ces'] = result['ce'] / result['rtime']
    result['corr'] = (result['ce'] - result['wasted_flagging'] - (result['solved_bv'] != result['bv'])) / result['cl']
    result['thrp'] = result['solved_bv'] / result['ce']
    result['ioe'] = result['solved_bv'] / result['cl']
    result['iome'] = result['solved_bv'] / result['path'] if result['solved_bv'] else 0.0 # if path is 0, solved_bv must be 0 

    mode_ref = {'beg': 1, 'int': 2, 'exp-v': 3, 'exp-h': 3}
    if result['difficulty'] in mode_ref:
        mode = mode_ref[result['difficulty']]
        result['stnb'] = (87.420 * (mode ** 2) - 155.829 * mode + 115.708) / (result['qg'] * math.sqrt(result['solved_bv'] / result['bv'])) if result['solved_bv'] else 0.0

    return result
