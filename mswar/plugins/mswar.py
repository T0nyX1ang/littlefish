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

    current = 0
    while current < len(split_action) - 2:
        if split_action[current][0] == 2 and split_action[current + 1][0] == 3:
            if split_action[current + 2][0] == 1 and split_action[current + 1][1] == split_action[current + 2][1] and split_action[current + 1][2] == split_action[current + 2][2] \
                and split_action[current][1] == split_action[current + 2][1] and split_action[current][2] == split_action[current + 2][2]:
                # this indicates the action is valid
                split_action[current + 2][0] = 4
                current += 3
            else:
                # this indicates the action is invalid
                split_action[current][0] = -1
                split_action[current + 1][0] = -1
                current += 2  
        else:
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
    result['row'] = get_row(board)
    result['column'] = get_column(board)

    marker = [[False for col in range(0, get_column(board))] for row in range(0, get_row(board))]
    result['mines'] = get_mines(board, marker)
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
    result['est'] = result['rtime'] / result['solved_bv'] * result['bv']
    result['rqp'] = (result['rtime'] + 1) / result['bvs']
    result['qg'] = result['rtime'] ** 1.7 / result['solved_bv']
    result['cls'] = result['cl'] / result['rtime']
    result['ces'] = result['ce'] / result['rtime']
    result['corr'] = (result['ce'] - result['wasted_flagging']) / result['cl']
    result['thrp'] = result['solved_bv'] / result['ce']
    result['ioe'] = result['solved_bv'] / result['cl']
    result['iome'] = result['solved_bv'] / result['path']

    return result