"""
An analyzer for minesweeping game.

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
* stnb (in a standard game).
"""

import math


def _divide(a: float, b: float) -> float:
    """Safely divide two numbers without throwing a ZeroDivisionError."""
    try:
        return a / b  # normal division
    except ZeroDivisionError:
        return 0.0 if a == 0 else math.inf  # include special cases for infinity (a / 0 = inf) and zero (0 / 0 = 0)


class Board(object):
    """Generate the board data from input."""

    def __init__(self, board: list):
        """Initialize the board."""
        self.result = {}
        self.result['mines'] = 0
        self.board = []
        self.marker = []
        for each_row in board:
            mark = [1 if v == '9' else 0 for v in each_row]
            self.marker.append(mark)  # construct the marks of the board
            self.board.append(each_row)  # convert the 1D raw board to 2D board
            self.result['mines'] += sum(mark)

        # get the information about row, columns
        self.result['row'] = len(self.board)
        self.result['column'] = len(self.board[0])
        self.result['difficulty'] = self.get_difficulty()
        self.result['op'] = self.get_openings_or_islands(self.is_opening)
        self.result['bv'] = self.result['op'] + self.result['row'] * self.result['column'] - sum(sum(self.marker, []))
        self.result['is'] = self.get_openings_or_islands(self.is_not_opening_or_mine)

    def is_opening(self, row: int, col: int) -> str:
        """Judge the current position is an opening."""
        return self.board[row][col] == '0'

    def is_not_opening_or_mine(self, row: int, col: int) -> str:
        """Judge the current position is not an opening or a mine."""
        return self.board[row][col] not in '09'

    def get_difficulty(self) -> str:
        """Get the difficulty of a board."""
        size = (self.result['row'], self.result['column'], self.result['mines'])
        difficulty_ref = {(8, 8, 10): 'beg', (16, 16, 40): 'int', (16, 30, 99): 'exp-h', (30, 16, 99): 'exp-v'}
        try:
            return difficulty_ref[size]
        except Exception:
            return '%dx%d+%d' % size

    def filtered_adjacent(self, row: int, col: int, filters: tuple = (0,)):
        """Yield filtered adjacent coordinates."""
        adjacent = [(row - 1, col - 1), (row, col - 1), (row + 1, col - 1), (row - 1, col), (row + 1, col), (row - 1, col + 1),
                    (row, col + 1), (row + 1, col + 1)]
        for r, c in adjacent:
            if 0 <= r < self.result['row'] and 0 <= c < self.result['column'] and self.marker[r][c] in filters:
                yield r, c

    def recur_mark(self, row: int, col: int, condition: bool):
        """Mark an area recursively."""
        self.marker[row][col] = 1
        if condition(row, col):
            for next_row, next_col in self.filtered_adjacent(row, col):
                self.marker[next_row][next_col] = 1
                self.recur_mark(next_row, next_col, condition)

    def get_openings_or_islands(self, condition: bool) -> int:
        """Get opening or islands of a board."""
        items = 0
        for v in range(self.result['row'] * self.result['column']):
            row = v // self.result['column']
            col = v % self.result['column']
            if not self.marker[row][col] and condition(row, col):
                items += 1
                self.recur_mark(row, col, condition)
        return items

    def get_result(self) -> dict:
        """Get the result in dict format."""
        return self.result


class Record(Board):
    """Generate record data from board and action."""

    def __init__(self, board: list, action: list, initial: list = None):
        """Initialize the record."""
        super(Record, self).__init__(board)
        self._threshold = 3  # the threshold between press and release
        self.marker = [[0 for col in range(self.result['column'])] for row in range(self.result['row'])]
        self.action = action
        for current in range(len(self.action)):
            self.__refine_action(current)
        self.result['rtime'] = self.action[-1][3] / 1000
        self.get_action_detail()
        self.result['flags'], self.result['unflags'], self.result['misflags'], self.result['misunflags'] = 0, 0, 0, 0
        self.result['ce'], self.result['solved_bv'], self.result['solved_op'] = 0, 0, 0
        self.prepare_initial_board(initial)
        self.stepwise = [self.marker]
        for current in range(len(self.action)):
            self.replay_stepwise(current)
            self.stepwise.append(self.marker)  # record each step
        self.get_record_detail()

    def __find_final(self, start: int, direction: int, row: int, col: int) -> int:
        """Find out the assurance final key and show whether a valid key is found. The direction should be +1 or -1."""
        final = start + direction
        while 0 <= final < len(
                self.action) and (self.action[final][3] - self.action[start][3]) * direction <= self._threshold and not (
                    self.action[final][0] == 1 and self.action[final][1] == row and self.action[final][2] == col):
            final += direction
        return final, 0 <= final < len(
            self.action) and (self.action[final][3] - self.action[start][3]) * direction <= self._threshold

    def __refine_action(self, current):
        """
        Refine the action to distinguish the actions that are really useful in a record.

        Find out the core keys in press (2) and release (3), and rename them to another opcode (4) for further use.
        """
        if self.action[current][0] != 3:
            return  # only focus on release key

        tag_row, tag_col = self.action[current][1:3]
        release = current

        # find out the assurance final key
        final, found = self.__find_final(release, +1, tag_row, tag_col)  # move forwards
        if found:
            self.action[final][0] = 4
        else:
            final, found = self.__find_final(release, -1, tag_row, tag_col)  # move backwards
            if found:
                self.action[final][0] = 4

    def __deal_with_click(self, row: int, col: int) -> bool:
        """Deal with clicking operation (corresponding to opcode 0)."""
        if self.marker[row][col] != 0:  # the block is opened
            return False  # do nothing, the click is ineffective

        # the block is not opened otherwise
        if self.board[row][col] == '9':  # step on a mine, oops
            self.marker[row][col] = -2  # mark the blast with a special number
        elif self.board[row][col] == '0':  # step on an opening, ^wow^
            self.result['solved_bv'] += 1
            self.result['solved_op'] += 1
            self.marker[row][col] = 1
            self.recur_mark(row, col, self.is_opening)  # mark everything is the opening
        else:  # normal click, nothing happens
            # bv is added when the click is not on the edge of an opening
            self.result['solved_bv'] += ('0' not in [self.board[r][c] for r, c in self.filtered_adjacent(row, col)])
            self.marker[row][col] = 1

        return True  # any direct click is effective

    def __deal_with_flag(self, row: int, col: int):
        """Deal with flagging operation (corresponding to opcode 1)."""
        if self.marker[row][col] == 0:  # flagging
            self.result['flags'] += 1  # count flags
            self.marker[row][col] = -1  # mark the flag
            self.result['misflags'] += self.board[row][col] != '9'  # count misflags
        elif self.marker[row][col] == -1:  # unflagging
            misunflag_tag = self.board[row][col] == '9'
            self.result['flags'] -= 1  # count flags
            self.marker[row][col] = 0  # unmark the flag
            self.result['misunflags'] += misunflag_tag  # count misunflags
            self.result['unflags'] += (not misunflag_tag)  # count unflags (opposite to misunflags)

        return True  # any direct click is effective

    def __deal_with_chord(self, row: int, col: int):
        """Deal with chording operation (corresponding to opcode 4)."""
        adjacent_flagged = list(self.filtered_adjacent(row, col, (-1,)))
        adjacent_unopened = list(self.filtered_adjacent(row, col))
        if len(adjacent_flagged) != int(self.board[row][col]) or len(adjacent_flagged) == 0 or len(adjacent_unopened) == 0:
            # trivial case, the chord operation is ineffective here
            return False

        for r, c in adjacent_unopened:
            self.__deal_with_click(r, c)  # do the job as a click

        for r, c in adjacent_flagged:
            # if misjudge, mark with a special number (-3), otherwise remain the original status (-1)
            self.marker[r][c] -= 2 * (self.board[r][c] != '9')

        return True

    def get_action_detail(self):
        """Get total path length (Euclidean), clicks (L, R, D, total), clicks per second (cls), and style from action."""
        self.result['path'], self.result['left'], self.result['right'], self.result['double'], current, last = 0, 0, 0, 0, 0, 0
        while current < len(self.action):
            if self.action[current][0] in [0, 1, 4]:
                self.result['path'] += math.sqrt((self.action[current][1] - self.action[last][1])**2 +
                                                 (self.action[current][2] - self.action[last][2])**2)  # Euclidean path
                self.result['left'] += (self.action[current][0] == 0)  # left clicks (open)
                self.result['right'] += (self.action[current][0] == 1)  # right clicks (flag)
                self.result['double'] += (self.action[current][0] == 4)  # double clicks (chord)
                last = current
            current += 1
        self.result['cl'] = self.result['left'] + self.result['right'] + self.result['double']
        self.result['style'] = 'FL' if self.result['right'] > 0 else 'NF'

    def prepare_initial_board(self, initial: list):
        """Prepare the initial board with raw data."""
        if not initial:
            self.result['upk'] = False
            return  # no need to prepare the initial board if there is not data

        self.result['upk'] = True

        for v in range(self.result['row'] * self.result['column']):
            row = v // self.result['column']
            col = v % self.result['column']
            if initial[row][col] == '1':
                self.__deal_with_click(row, col)  # calculate initial values

        self.marker = [[int(v) for v in each_row] for each_row in initial]  # reset the marker by raw data

    def replay_stepwise(self, current):
        """Replay the game stepwise to gather detailed information."""
        opcode, row, col, _ = self.action[current]
        if opcode == 0:
            self.result['ce'] += self.__deal_with_click(row, col)
        elif opcode == 1:
            self.result['ce'] += self.__deal_with_flag(row, col)
        elif opcode == 4:
            self.result['ce'] += self.__deal_with_chord(row, col)

    def get_record_detail(self):
        """Get detailed information about the record."""
        self.result['bvs'] = _divide(self.result['solved_bv'], self.result['rtime'])
        self.result['cls'] = _divide(self.result['cl'], self.result['rtime'])
        self.result['est'] = _divide(self.result['rtime'], self.result['solved_bv']) * self.result['bv']
        self.result['rqp'] = _divide(self.result['rtime'] + 1, self.result['bvs'])
        self.result['qg'] = _divide(self.result['rtime']**1.7, self.result['solved_bv'])
        self.result['iome'] = _divide(self.result['solved_bv'], self.result['path'])
        self.result['ces'] = _divide(self.result['ce'], self.result['rtime'])
        self.result['corr'] = _divide(
            self.result['ce'] - self.result['misflags'] - self.result['unflags'] - self.result['misunflags'] -
            (self.result['bv'] != self.result['solved_bv']), self.result['cl'])
        self.result['thrp'] = _divide(self.result['solved_bv'], self.result['ce'])
        self.result['ioe'] = _divide(self.result['solved_bv'], self.result['cl'])

        mode_ref = {'beg': 1, 'int': 2, 'exp-v': 3, 'exp-h': 3}
        if self.result['difficulty'] in mode_ref:
            mode = mode_ref[self.result['difficulty']]
            self.result['stnb'] = _divide(87.420 * (mode**2) - 155.829 * mode + 115.708,
                                          self.result['qg'] * math.sqrt(self.result['solved_bv'] / self.result['bv']))
