import copy

default_chessboard = [[3, 4, 5, 2, 1, 5, 4, 3],
                      [6, 6, 6, 6, 6, 6, 6, 6],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [12, 12, 12, 12, 12, 12, 12, 12],
                      [9, 10, 11, 8, 7, 11, 10, 9]]
default_notmove = [[0, 0], [0, 4], [0, 7], [7, 0], [7, 4], [7, 7],
                   [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7],
                   [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7]]


class State:
    def __init__(self, rule='Turn Zero', turn=1, maxround=1000):
        self.boardsize = 0
        self.pawnline = []
        self.state = []
        self.available_actions_dic = {}
        self.chess_searched = []
        self.special_operation = {0: [], 1: [], 2: []}
        # 0项表示将进行王车易位，1项表示将进行吃过路兵，2项表示将进行升变 (注意这里吃过路兵记录的是吃过路兵的兵将移动到的位置)
        self.present = 0
        self.turn = 1 if turn == 1 else 0
        self.whiteline = 0
        self.blackline = 0
        self.available_timeline = [0]
        self.end_turn = False
        self.end = False
        self.winner = 0  # 0表示未胜负，1表示平局，2表示黑胜，3表示白胜
        self.maxround = maxround

        if rule == 'Turn Zero':
            self.pawnline = [1, 6]
            self.boardsize = 8
            self.present = 1
            self.state = {0: [copy.deepcopy(default_chessboard), copy.deepcopy(default_chessboard)]}
            self.not_moved = {(0, 0): copy.deepcopy(default_notmove), (0, 1): copy.deepcopy(default_notmove)}
        else:
            raise SyntaxError

        for i in self.state:
            if i < 0:
                self.whiteline += 1
            elif i > 0:
                self.blackline += 1
        self.maxdistance = max(8, len(self.state))
        self.reset_aftermove()

    def reset_aftermove(self):

        # available_timeline的reset
        self.available_timeline = [0]
        line_number = min(self.whiteline, self.blackline)
        for i in range(line_number):
            i += 1
            self.available_timeline.append(i)
            self.available_timeline.append(-i)
        if self.whiteline > self.blackline:
            self.available_timeline.append(-line_number - 1)
        elif self.whiteline < self.blackline:
            self.available_timeline.append(line_number + 1)

        # present的reset
        self.present = len(self.state[0]) - 1
        for i in self.available_timeline:
            self.present = min(len(self.state[i]) - 1, self.present)

        # maxdistance的reset
        for timeline in self.state:
            self.maxdistance = max(len(self.state[timeline]), self.maxdistance)

        # available_actions_dic的reset
        self.available_actions_dic = {}

        # chess_searched的reset
        self.chess_searched = []

        # special_operation的reset
        self.special_operation = {0: [], 1: [], 2: []}

        # end_turn的reset
        self.end_turn = (divmod(self.present, 2)[1] != self.turn)

    def notmove_update(self, board_old, board_next, chesslist):
        board_old, board_next = tuple(board_old), tuple(board_next)
        if board_old in self.not_moved:
            board_notmove_state = self.not_moved[board_old][:]
            for i in chesslist:
                if i in board_notmove_state:
                    board_notmove_state.remove(i)
            if len(board_notmove_state) != 0:
                self.not_moved[board_next] = board_notmove_state

    def notmove_query(self, board=None, chess=None, complete_coordinate=None):
        if (board is None) and (chess is None) and (complete_coordinate is not None):
            board, chess = complete_coordinate[:2], complete_coordinate[2:]
        board = tuple(board)
        chess = list(chess)
        if board not in self.not_moved:
            return False
        if chess not in self.not_moved[board]:
            return False
        return True

    def basic_chess_available(self, chess_coordinate):
        chess = self.state
        if chess_coordinate[0] not in chess:
            return [False]
        chess = chess[chess_coordinate[0]]
        for i in range(3):
            if chess_coordinate[i + 1] < 0:
                return [False]
            if chess is None:
                return [False]
            if len(chess) > chess_coordinate[i + 1]:
                chess = chess[chess_coordinate[i + 1]]
            else:
                return [False]
        if chess == 0:
            return [False, 0]
        return [True, chess]

    def basic_next_available(self, next_coordinate, owner=None):
        next_ = self.state
        if next_coordinate[0] not in next_:
            return [False]
        next_ = next_[next_coordinate[0]]
        for i in range(3):
            if next_coordinate[i + 1] < 0:
                return [False]
        for i in range(2):
            if next_coordinate[i + 2] > self.boardsize - 1:
                return [False]
        if len(next_) > next_coordinate[1]:
            next_ = next_[next_coordinate[1]]
        else:
            return [False]
        if next_ is None:
            return [False]
        if owner is None:
            return [False]
        else:
            next_type = next_[next_coordinate[2]][next_coordinate[3]]
            if next_type == 0:
                return [True, -1]
            x = divmod(next_type - 1, 6)
            if x[0] == owner:
                return [False]
            return [True, x[1]]

    def attacked2d(self, position, owner):
        # 检查马攻击
        knight = []
        for i in [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]:
            temp1 = position[:]
            temp1[2] += i[0]
            temp1[3] += i[1]
            knight.append(temp1)
        for ii in knight:
            temp2 = self.basic_chess_available(ii)
            if temp2[0]:
                if temp2[1] != 0:
                    knight_owner, chesstype = divmod(temp2[1] - 1, 6)
                    if knight_owner == (1 - owner) and chesstype == 3:
                        return True
        # 检查直线攻击，因为王车易位才用这个函数，所以只检测竖线
        direction = 1 - (2 * owner)
        for distance in range(self.boardsize - 1):
            distance += 1
            temp3 = position[:]
            temp3[2] += distance * direction
            temp4 = self.basic_chess_available(temp3)
            if len(temp4) == 2:
                if temp4[1] != 0:
                    chess_owner, chesstype = divmod(temp4[1] - 1, 6)
                    if chess_owner == owner:
                        break
                    elif ((chesstype in [0, 1, 2]) and (distance == 1)) or ((chesstype in [1, 2]) and (distance != 1)):
                        return True
                    else:
                        break
            else:
                break
        # 检查斜线攻击
        for distance in range(self.boardsize - 1):
            distance += 1
            temp3 = position[:]
            temp3[2] += distance * direction
            temp3[3] += distance
            temp4 = self.basic_chess_available(temp3)
            if len(temp4) == 2:
                if temp4[1] != 0:
                    chess_owner, chesstype = divmod(temp4[1] - 1, 6)
                    if chess_owner == owner:
                        break
                    elif ((chesstype in [0, 1, 4, 5]) and (distance == 1)) or (
                            (chesstype in [1, 4]) and (distance != 1)):
                        return True
                    else:
                        break
            else:
                break
        return False

    def search_all_available(self, chess_coordinate):
        query = self.basic_chess_available(chess_coordinate)
        if not query[0]:
            return False
        if chess_coordinate in self.chess_searched:
            if tuple(chess_coordinate) in self.available_actions_dic:
                return True
            else:
                return False
        self.chess_searched.append(chess_coordinate)
        return_list = []
        chess = query[1]
        owner, chesstype = divmod(chess - 1, 6)

        if chesstype == 0:  # 王 king
            if self.notmove_query(complete_coordinate=chess_coordinate):  # 王车易位
                if not self.attacked2d(chess_coordinate, owner):  # 王收到2d攻击
                    coordinate = [chess_coordinate[:] for i in range(6)]
                    coordinate[0][3] = 0
                    coordinate[1][3] = 7
                    coordinate[2][3] = 2
                    coordinate[3][3] = 6

                    # 长易位
                    if self.notmove_query(complete_coordinate=coordinate[0]):
                        check_void = [chess_coordinate[:] for i in range(3)]
                        check_void[0][3] = 1
                        check_void[1][3] = 2
                        check_void[2][3] = 3
                        if [self.basic_chess_available(check_void[i]) for i in range(3)] == [[False, 0]] * 3:
                            if not self.attacked2d(check_void[2], owner):
                                action = [*chess_coordinate, *coordinate[2]]
                                self.special_operation[0].append(action)
                                return_list.append(coordinate[2])
                    # 短易位
                    if self.notmove_query(complete_coordinate=coordinate[1]):
                        check_void = [chess_coordinate[:] for i in range(2)]
                        check_void[0][3] = 5
                        check_void[1][3] = 6
                        if [self.basic_chess_available(check_void[i]) for i in range(2)] == [[False, 0]] * 2:
                            if not self.attacked2d(check_void[0], owner):
                                action = [*chess_coordinate, *coordinate[3]]
                                self.special_operation[0].append(action)
                                return_list.append(coordinate[3])
            axis = axis_choose([1, 2, 3, 4])
            for move in axis:
                query = chess_coordinate[:]
                query = movefuc(query, move)
                if self.basic_next_available(query, owner)[0]:
                    return_list.append(query)

        elif chesstype == 1:  # 后 queen
            axis = axis_choose([1, 2, 3, 4])
            for distance in range(self.maxdistance):
                distance += 1
                direction_to_del = []
                if len(axis):
                    for direction in axis:
                        query = chess_coordinate[:]
                        move = [distance * i for i in direction]
                        query = movefuc(query, move)
                        criterion = self.basic_next_available(query, owner)
                        if criterion[0]:
                            return_list.append(query)
                            if criterion[1] != -1:
                                direction_to_del.append(direction)
                        else:
                            direction_to_del.append(direction)
                    for i in direction_to_del:
                        axis.remove(i)

        elif chesstype == 2:  # 车 rook
            for direction in [[0, 0, 1, 0], [0, 0, -1, 0], [0, 0, 0, 1], [0, 0, 0, -1], [0, -1, 0, 0], [-1, 0, 0, 0],
                              [1, 0, 0, 0]]:
                for distance in range(self.maxdistance):
                    distance += 1
                    move = [distance * i for i in direction]
                    query = chess_coordinate[:]
                    query = movefuc(query, move)
                    criterion = self.basic_next_available(query, owner)
                    if criterion[0]:
                        return_list.append(query)
                        if criterion[1] != -1:
                            break
                    else:
                        break

        elif chesstype == 3:  # 马 knight
            for i in range(4):
                x = list(range(4))
                x.remove(i)
                for j in x:
                    for k in [[-1, -1], [-1, 1], [1, -1], [1, 1]]:
                        query = chess_coordinate[:]
                        move = [0, 0, 0, 0]
                        move[i] = 2 * k[0]
                        move[j] = k[1]
                        query = movefuc(query, move)
                        if self.basic_next_available(query, owner)[0]:
                            return_list.append(query)

        elif chesstype == 4:  # 象 bishop
            axis = axis_choose([2])
            for direction in axis:
                for distance in range(self.maxdistance):
                    distance += 1
                    move = [distance * i for i in direction]
                    query = chess_coordinate[:]
                    query = movefuc(query, move)
                    criterion = self.basic_next_available(query, owner)
                    if criterion[0]:
                        return_list.append(query)
                        if criterion[1] != -1:
                            break
                    else:
                        break

        elif chesstype == 5:  # 兵 pawn
            promotion = False
            if chess_coordinate[2] - self.boardsize + 2 + (self.boardsize - 3) * owner == 0:  # 升变
                promotion = True

            elif chess_coordinate[1] > 1 and chess_coordinate[2] - 4 * owner + 2 in self.pawnline:  # 吃过路兵
                checkp = []
                for i in range(4):
                    checkp.append(copy.deepcopy(chess_coordinate))
                    checkp[i][3] -= 1

                checkp[0][1] -= 1
                checkp[1][1] -= 1
                checkp[1][2] += 2 * (1 - 2 * owner)
                checkp[3][2] += 2 * (1 - 2 * owner)

                if checkp[0][3] >= 0:
                    bool_ = True
                    for i in range(4):
                        if i == 1:
                            bool_ = self.notmove_query(complete_coordinate=checkp[i]) and bool_
                        elif i == 2:
                            bool_ = (not self.basic_chess_available(checkp[i])[1] == 0) and bool_
                        else:
                            bool_ = self.basic_chess_available(checkp[i]) == [False, 0] and bool_
                    if bool_:
                        temp = checkp[2][:]
                        temp[2] += 1 - 2 * owner
                        action = [*chess_coordinate, *temp]
                        return_list.append(temp)
                        self.special_operation[1].append(action)
                for i in range(4):
                    checkp[i][3] += 2
                if checkp[0][3] < 8:
                    bool_ = True
                    for i in range(4):
                        if i == 1:
                            bool_ = self.notmove_query(complete_coordinate=checkp[i]) and bool_
                        elif i == 2:
                            bool_ = (not self.basic_chess_available(checkp[i])[1] == 0) and bool_
                        else:
                            bool_ = self.basic_chess_available(checkp[i]) == [False, 0] and bool_
                    if bool_:
                        temp = checkp[2][:]
                        temp[2] += 1 - 2 * owner
                        action = [*chess_coordinate, *temp]
                        return_list.append(temp)
                        self.special_operation[1].append(action)
            # 普通走法
            # 2d情况
            coordinate = []
            for i in range(3):
                coordinate.append(chess_coordinate[:])
                coordinate[i][2] += 1 - 2 * owner
                coordinate[i][3] += i - 1
                temp1 = self.basic_next_available(coordinate[i], owner)
                if temp1[0]:
                    if i == 1:
                        if temp1[1] == -1:
                            action = [*chess_coordinate, *coordinate[i]]
                            return_list.append(coordinate[i])
                            if promotion:
                                self.special_operation[2].append(action)
                            if self.notmove_query(complete_coordinate=chess_coordinate):
                                temp2 = chess_coordinate[:]
                                temp2[2] += 2 * (1 - 2 * owner)
                                temp3 = self.basic_next_available(temp2, owner)
                                if temp3[0]:
                                    if temp3[1] == -1:
                                        return_list.append(temp2)
                    else:
                        if temp1[1] != -1:
                            action = [*chess_coordinate, *coordinate[i]]
                            return_list.append(coordinate[i])
                            if promotion:
                                self.special_operation[2].append(action)

            # 5d情况
            coordinate = []
            for i in range(3):
                coordinate.append(chess_coordinate[:])
                coordinate[i][0] += 2 * owner - 1
                coordinate[i][1] += i - 1
                temp1 = self.basic_next_available(coordinate[i], owner)
                if temp1[0]:
                    if i == 1:
                        if temp1[1] == -1:
                            return_list.append(coordinate[i])
                            if self.notmove_query(complete_coordinate=chess_coordinate):
                                temp2 = chess_coordinate[:]
                                temp2[0] += 2 * (1 - 2 * owner)
                                temp3 = self.basic_next_available(temp2, owner)
                                if temp3[0]:
                                    if temp3[1] == 0:
                                        return_list.append(temp2)
                    else:
                        if temp1[1] != -1:
                            return_list.append(coordinate[i])

        if not return_list:
            return False
        else:
            self.available_actions_dic[tuple(chess_coordinate)] = return_list
            return True

    def basic_move_available(self, action):
        chess_coordinate = action[:4]
        next_coordinate = action[4:]
        if chess_coordinate in self.chess_searched:
            if next_coordinate in self.available_actions_dic[tuple(chess_coordinate)]:
                return True
            return False
        if self.search_all_available(chess_coordinate):
            if next_coordinate in self.available_actions_dic[tuple(chess_coordinate)]:
                return True
        return False

    def action_available(self, action):
        if len(action) != 8:
            return False
        chess_coordinate = action[:4]
        query = self.basic_chess_available(chess_coordinate)
        if query[0] is True:
            owner, chesstype = divmod(query[1] - 1, 6)
            if owner != self.turn:
                return False
        else:
            return False
        if chess_coordinate[1] + 1 != len(self.state[chess_coordinate[0]]):
            return False
        if self.turn != divmod(chess_coordinate[1], 2)[1]:
            return False
        if self.basic_move_available(action) is True:
            return True
        return False

    def onemove(self, action):
        if self.end:
            return False
        if action[1] < 0:
            if action[2] < 0:
                self.end = True
                owner = self.turn
                if self.stalemate(self.turn):
                    self.winner = 1
                else:
                    self.winner = self.winner = 3 - owner
                return True
            if self.end_turn:
                self.turn = 1 - self.turn
                self.reset_aftermove()
                return True
            return False
        if self.action_available(action) is False:
            return False
        if self.maxround < self.maxdistance:
            self.end = True
            self.winner = 1
        if self.basic_chess_available(action[4:])[1] == 7 - 6 * self.turn:
            self.end = True
            self.winner = self.turn + 2
        if len(self.state[action[4]]) == action[5] + 1:  # 不开线
            if action[0] == action[4]:  # 2d走法
                board = action[4:6]
                board[1] += 1
                chess = []
                if action in self.special_operation[0]:  # 王车易位
                    new_board = copy.deepcopy(self.state[action[0]][action[1]])
                    if action[7] == 2:  # 长易位
                        new_board[action[2]][2] = new_board[action[2]][4]
                        new_board[action[2]][3] = new_board[action[2]][0]
                        chess.extend([[action[2], 2], [action[2], 3], [action[2], 0], [action[2], 4]])
                        new_board[action[2]][0] = 0
                        new_board[action[2]][4] = 0
                    elif action[7] == 6:  # 短易位
                        new_board[action[2]][6] = new_board[action[2]][4]
                        new_board[action[2]][5] = new_board[action[2]][7]
                        chess.extend([[action[2], 5], [action[2], 6], [action[2], 4], [action[2], 7]])
                        new_board[action[2]][7] = 0
                        new_board[action[2]][4] = 0
                    else:
                        raise SyntaxError
                elif action in self.special_operation[1]:  # 吃过路兵
                    direction = action[6] - action[2]
                    new_board = copy.deepcopy(self.state[action[0]][action[1]])
                    new_board[action[6]][action[7]] = new_board[action[2]][action[3]]
                    new_board[action[6] - direction][action[7]] = 0
                    new_board[action[2]][action[3]] = 0
                elif action in self.special_operation[2]:  # 升变
                    new_board = copy.deepcopy(self.state[action[0]][action[1]])
                    new_board[action[6]][action[7]] = new_board[action[2]][action[3]] - 4
                    new_board[action[2]][action[3]] = 0
                    chess.append([action[6], action[7]])
                else:  # 普通走法
                    new_board = copy.deepcopy(self.state[action[0]][action[1]])
                    new_board[action[6]][action[7]] = new_board[action[2]][action[3]]
                    chess.extend([[action[2], action[3]], [action[6], action[7]]])
                    new_board[action[2]][action[3]] = 0
                self.state[action[0]].append(new_board)
                self.notmove_update(action[4:6], board, chess)
            else:  # 5d走法
                new_board_next = copy.deepcopy(self.state[action[4]][action[5]])
                new_board_chess = copy.deepcopy(self.state[action[0]][action[1]])
                new_board_next[action[6]][action[7]] = new_board_chess[action[2]][action[3]]
                new_board_chess[action[2]][action[3]] = 0
                self.state[action[4]].append(new_board_next)
                self.state[action[0]].append(new_board_chess)
                board = action[4:6]
                board[1] += 1
                self.notmove_update(action[4:6], board, [[action[6], action[7]]])
                board = action[:2]
                board[1] += 1
                self.notmove_update(action[:2], board, [[action[2], action[3]]])
        else:  # 开线
            chess = self.basic_chess_available(action[:4])[1]
            owner, chesstype = divmod(chess - 1, 6)
            new_board_next = copy.deepcopy(self.state[action[4]][action[5]])
            new_board_chess = copy.deepcopy(self.state[action[0]][action[1]])
            new_board_next[action[6]][action[7]] = new_board_chess[action[2]][action[3]]
            new_board_chess[action[2]][action[3]] = 0
            if owner == 1:
                self.whiteline += 1
                self.state[-self.whiteline] = [None] * (action[5] + 1)
                self.state[-self.whiteline].append(new_board_next)
                board = [-self.whiteline, action[5] + 1]
            elif owner == 0:
                self.blackline += 1
                self.state[self.blackline] = [None] * (action[5] + 1)
                self.state[self.blackline].append(new_board_next)
                board = [self.blackline, action[5] + 1]
            else:
                raise SyntaxError
            self.state[action[0]].append(new_board_chess)
            self.notmove_update(action[4:6], board, [[action[6], action[7]]])
            board = action[:2]
            board[1] += 1
            self.notmove_update(action[:2], board, [[action[2], action[3]]])
        self.reset_aftermove()
        tmp = True
        for i in self.state.values():
            if len(i) % 2 != self.turn:
                tmp = False
                break
        if tmp:
            self.turn = 1 - self.turn
            self.reset_aftermove()
        return True

    def getboard(self, timeline=0, time=0):
        if timeline in self.state:
            if time in range(len(self.state[timeline])):
                return self.state[timeline][time]
        return None

    def get_available(self, chess_coordinate):
        if chess_coordinate not in self.chess_searched:
            self.search_all_available(chess_coordinate)
        if tuple(chess_coordinate) not in self.available_actions_dic:
            return None
        return self.available_actions_dic[tuple(chess_coordinate)]

    def show(self, timeline=0, time=0):
        if timeline in self.state:
            if time < len(self.state[timeline]):
                if self.state[timeline][time] is not None:
                    for i in self.state[timeline][time]:
                        string = ''
                        for j in i:
                            if j > 9:
                                string += str(j)
                                string += ' '
                            else:
                                string += str(j)
                                string += '  '
                        print(string)
                    return True
        print('该输入棋盘空')
        return False

    def stalemate(self, owner):
        movable = self.get_all_movable(owner)
        moves = []
        if movable is not None:
            for chess in movable:
                self.search_all_available(chess)

            for chess in self.available_actions_dic:
                for next_ in self.available_actions_dic[chess]:
                    moves.append([*chess, *next_])

        if moves:
            for move in moves:
                new_board = State()
                new_board.state = copy.deepcopy(self.state)
                new_board.turn = self.turn
                new_board.whiteline = self.whiteline
                new_board.blackline = self.blackline
                new_board.not_moved = self.not_moved
                new_board.reset_aftermove()
                new_board.onemove(move)
                if new_board.turn == owner:
                    return False
                if not new_board.incheck(owner):
                    return False
            return True
        else:
            self.pass_()
            if self.incheck(owner):
                return False
            return True

    def get_all_movable(self, owner):
        movable_chess = []
        for axis1 in self.state:
            state = self.state[axis1]
            lentime = len(state) - 1
            if lentime % 2 == owner:
                state = state[lentime]
                for x in range(8):
                    for y in range(8):
                        if (state[x][y] - 1) // 6 == owner:
                            movable_chess.append([axis1, lentime, x, y])
        if not movable_chess:
            movable_chess = None
        return movable_chess

    def pass_(self):
        for timeline in self.state:
            if len(self.state[timeline]) == self.present - 1:
                self.state[timeline].append(self.state[timeline][-1])

    def incheck(self, owner):
        check_owner = 1 - owner
        movable = self.get_all_movable(check_owner)
        if movable is None:
            return False
        for chess in movable:
            if self.incheck_search(chess):
                return True
        return False

    def incheck_search(self, chess_coordinate):
        query = self.basic_chess_available(chess_coordinate)
        chess = query[1]
        owner, chesstype = divmod(chess - 1, 6)

        if chesstype == 0:  # 王 king
            axis = axis_choose([1, 2, 3, 4])
            for move in axis:
                query = chess_coordinate[:]
                query = movefuc(query, move)
                result = self.basic_next_available(query, owner)
                if result[0]:
                    if result[1] == 0:
                        return True

        elif chesstype == 1:  # 后 queen
            axis = axis_choose([1, 2, 3, 4])
            for direction in axis:
                if direction == [0, 0, 0, -1]:
                    pass
                for distance in range(self.maxdistance):
                    distance += 1
                    query = chess_coordinate[:]
                    move = [distance * i for i in direction]
                    query = movefuc(query, move)
                    criterion = self.basic_next_available(query, owner)
                    if criterion[0]:
                        if criterion[1] != -1:
                            if criterion[1] == 0:
                                return True
                            break
                    else:
                        break

        elif chesstype == 2:  # 车 rook
            for direction in [[0, 0, 1, 0], [0, 0, -1, 0], [0, 0, 0, 1], [0, 0, 0, -1], [0, -1, 0, 0], [-1, 0, 0, 0],
                              [1, 0, 0, 0]]:
                for distance in range(self.maxdistance):
                    distance += 1
                    move = [distance * i for i in direction]
                    query = chess_coordinate[:]
                    query = movefuc(query, move)
                    criterion = self.basic_next_available(query, owner)
                    if criterion[0]:
                        if criterion[1] != -1:
                            if criterion[1] == 0:
                                return True
                            break
                    else:
                        break

        elif chesstype == 3:  # 马 knight
            for i in range(4):
                x = list(range(4))
                x.remove(i)
                for j in x:
                    for k in [[-1, -1], [-1, 1], [1, -1], [1, 1]]:
                        query = chess_coordinate[:]
                        move = [0, 0, 0, 0]
                        move[i] = 2 * k[0]
                        move[j] = k[1]
                        query = movefuc(query, move)
                        result = self.basic_next_available(query, owner)
                        if result[0]:
                            if result[1] == 0:
                                return True

        elif chesstype == 4:  # 象 bishop
            axis = axis_choose([2])
            for direction in axis:
                for distance in range(self.maxdistance):
                    distance += 1
                    move = [distance * i for i in direction]
                    query = chess_coordinate[:]
                    query = movefuc(query, move)
                    criterion = self.basic_next_available(query, owner)
                    if criterion[0]:
                        if criterion[1] != -1:
                            if criterion[1] == 0:
                                return True
                            break
                    else:
                        break

        elif chesstype == 5:  # 兵 pawn
            # 普通走法
            # 2d情况
            coordinate = []
            for i in range(2):
                coordinate.append(chess_coordinate[:])
                coordinate[i][2] += 1 - 2 * owner
                coordinate[i][3] += 2 * i - 1
                temp1 = self.basic_next_available(coordinate[i], owner)
                if temp1[0]:
                    if temp1[1] == 0:
                        return True

            # 5d情况
            coordinate = []
            for i in range(2):
                coordinate.append(chess_coordinate[:])
                coordinate[i][0] += 2 * owner - 1
                coordinate[i][1] += 2 * i - 1
                temp1 = self.basic_next_available(coordinate[i], owner)
                if temp1[0]:
                    if temp1[1] == 0:
                        return True
        return False

    def get_all_legal(self):
        if self.end:
            return [[8, 8, 8, 8, 8, 8, 8, 8]]
        action_list = [[0, -1, -1, 0, 0, 0, 0, 0]]
        if self.end_turn:
            action_list.append([0, -1, 1, 0, 0, 0, 0, 0])
        movable_chess = self.get_all_movable(self.turn)
        if movable_chess:
            for chess in movable_chess:
                legal = self.get_available(chess)
                if legal:
                    for next_ in legal:
                        action_list.append([*chess, *next_])
        return action_list


def movefuc(chess, move):
    next_ = chess[:]
    if len(move) == 4:
        move[1] *= 2
        for i in range(4):
            next_[i] += move[i]
        return next_
    raise SyntaxError


def axis_choose(axis_num):
    numlist = []
    for i in range(80):
        axis_count = 0
        list = [i + 1, 0, 0, 0]
        list[1], list[0] = divmod(list[0], 3)
        list[2], list[1] = divmod(list[1], 3)
        list[3], list[2] = divmod(list[2], 3)
        list = [j - 1 for j in list]
        for k in list:
            if k != 0:
                axis_count += 1
        if axis_count in axis_num:
            numlist.append(list)
    return numlist
