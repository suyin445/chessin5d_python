import pygame
import os
import chessin5d
import copy

IMAGE = {i[:-4]: pygame.image.load(os.path.join('chesspng', i)) for i in os.listdir('.\chesspng')}
IMAGE_RESIZED = {}
for i in IMAGE:
    if i.find('boardf') != -1:
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (205, 205))
    elif i.find('over') != -1:
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (120, 60))
    elif i.find('diy') != -1:
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (90, 40))
    elif i.find('change') != -1:
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (90, 40))
    elif i.find('not_move_') != -1:
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (90, 40))
    elif i.find('recall') != -1:
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (50, 40))
    elif i == 'background':
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (1300, 800))
    else:
        IMAGE_RESIZED[i] = pygame.transform.scale(IMAGE[i], (25, 25))

pygame.init()

class Chessin5dUI:
    def __init__(self, image, window_size = None):
        if window_size is None:
            window_size = (1300, 800)
        self.window_size = window_size
        self.image = image
        self.window = pygame.display.set_mode(self.window_size)
        self.chessin5d = chessin5d.State()
        self.startxy = (25, 90)
        self.boardlist = {}
        self.position = [0,1]
        self.chosen = None
        self.available = {}
        self.reverse = False
        self.diy = False
        self.board_change = False
        self.diy_chosen = None
        self.notmove = False
        self.history = []
        self.font = pygame.font.SysFont('FangSong', 20, bold= True)
        pygame.display.set_caption('老抽冷筱华')
        pygame.display.set_icon(self.image['lxh'])

    def draw_window(self):
        self.window.blit(self.image['background'], (0, 0))

        if self.history:
            self.window.blit(self.image['can_recall'], (1100, 20))
        else:
            self.window.blit(self.image['cannot_recall'], (1100, 20))

        if self.diy:
            self.window.blit(self.image['diy_on'], (50, 20))
            if self.board_change:
                self.window.blit(self.image['board_change_on'], (150, 20))
            else:
                self.window.blit(self.image['board_change_off'], (150, 20))
        else:
            self.window.blit(self.image['diy_off'], (50, 20))

        if self.chessin5d.end_turn:
            self.window.blit(self.image['can_over'], (550, 20))
        else:
            self.window.blit(self.image['cannot_over'], (550, 20))

        if self.notmove:
            self.window.blit(self.image['not_move_on'], (1200, 20))
        else:
            self.window.blit(self.image['not_move_off'], (1200, 20))

        for i in self.boardlist:
            self.boardlist[i].show()

        for x in range(5):
            text = self.font.render(str(self.position[0] + x), True, (243, 243, 0), None)
            self.window.blit(text, (120 + 250 * x, 310))
        for y in range(3):
            text = self.font.render(str(self.position[1] - y), True, (243, 243, 0), None)
            self.window.blit(text, (8, 179 + 250 * y))
        pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()
        run = True

        while run:
            clock.tick(60)
            chesstype = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_f:
                        if self.chessin5d.end_turn and not self.board_change:
                            self.history.append(copy.deepcopy(self.chessin5d))
                            self.chessin5d.onemove([0,-1,0,0,0,0,0,0])

                    elif event.key == pygame.K_w:
                        if self.reverse:
                            self.position[1] -= 1
                        else:
                            self.position[1] += 1
                    elif event.key == pygame.K_s:
                        if self.reverse:
                            self.position[1] += 1
                        else:
                            self.position[1] -= 1
                    elif event.key == pygame.K_a:
                        if self.reverse:
                            self.position[0] += 1
                        else:
                            self.position[0] -= 1
                    elif event.key == pygame.K_d:
                        if self.reverse:
                            self.position[0] -= 1
                        else:
                            self.position[0] += 1
                    elif event.key == pygame.K_1:
                        chesstype = 1
                    elif event.key == pygame.K_2:
                        chesstype = 2
                    elif event.key == pygame.K_3:
                        chesstype = 3
                    elif event.key == pygame.K_4:
                        chesstype = 4
                    elif event.key == pygame.K_5:
                        chesstype = 5
                    elif event.key == pygame.K_6:
                        chesstype = 6
                    self.boardlist = {}

            if self.diy:
                self.chosen = self.diy_chosen[:4] if self.diy_chosen else None
            if self.diy_chosen and chesstype:
                tmp = self.diy_chosen
                self.history.append(copy.deepcopy(self.chessin5d))
                self.chessin5d.state[tmp[0]][tmp[1]][tmp[2]][tmp[3]] = tmp[4] * 6 + chesstype
                self.diy_chosen = None
                chesstype = None
            self.show_board()
            self.draw_window()

        pygame.quit()

    def board_set(self, coordinate, board, xy, chosen_chess, available, not_move, board_available, now_position):
        if board != None:
            self.boardlist[coordinate] = Chessboard(
                self.window, board, pygame.Rect(xy[0],xy[1],200,200), self.image,
                chosen_chess, available, board_available, not_move, now_position)

    def show_board(self):
        for x in range(5):
            for y in range(3):
                chosen_chess, available, not_move = None, None, None
                now_position = [self.position[1] - y, self.position[0] + x]
                board_available = 0
                if tuple(now_position) in self.chessin5d.not_moved and self.notmove:
                    not_move = self.chessin5d.not_moved[tuple(now_position)]
                if now_position[0] not in self.chessin5d.available_timeline:
                    board_available += 2
                if divmod(now_position[1], 2)[1] == 1:
                    board_available += 1
                if self.chosen is not None:
                    if now_position == self.chosen[:2]:
                        chosen_chess = self.chosen[2:]
                    if tuple(now_position) in self.available and not self.diy:
                        available = self.available[tuple(now_position)]
                self.board_set((x,y), self.chessin5d.getboard(*now_position),
                               (self.startxy[0] + 250 * x, self.startxy[1] + 250 * y),
                               chosen_chess, available, not_move, board_available, now_position)

    def mouse(self):
        mouse_botton = pygame.mouse.get_pressed()
        if self.diy:
            self.boardlist = {}
            chess_coordinate = self.getchess(pygame.mouse.get_pos())
            if chess_coordinate == 'diy':
                self.chessin5d.reset_aftermove()
                self.diy = False
                self.board_change = False
                self.diy_chosen = None
                self.chosen = None
            elif chess_coordinate == 'board_change':
                self.board_change = not self.board_change
            elif chess_coordinate == 'not_move':
                self.notmove = not self.notmove
            elif chess_coordinate == 'recall':
                if self.history:
                    self.chessin5d = self.history.pop()
                    self.boardlist = {}
            else:
                if self.board_change:
                    if mouse_botton[0]: # 增加棋盘
                        if chess_coordinate[0] in self.chessin5d.state:
                            if chess_coordinate[1] == len(self.chessin5d.state[chess_coordinate[0]]):
                                self.history.append(copy.deepcopy(self.chessin5d))
                                self.chessin5d.state[chess_coordinate[0]].append(
                                    self.chessin5d.state[chess_coordinate[0]][chess_coordinate[1] - 1])

                        else:
                            self.history.append(copy.deepcopy(self.chessin5d))
                            if chess_coordinate[0] < 0:
                                self.chessin5d.whiteline += 1
                                self.chessin5d.state[-self.chessin5d.whiteline] = [None] * (chess_coordinate[1])
                                self.chessin5d.state[-self.chessin5d.whiteline].append(
                                    [[0 for i in range(8)] for j in range(8)])
                            else:
                                self.chessin5d.blackline += 1
                                self.chessin5d.state[self.chessin5d.blackline] = [None] * (chess_coordinate[1])
                                self.chessin5d.state[self.chessin5d.blackline].append(
                                    [[0 for i in range(8)] for j in range(8)])

                    elif mouse_botton[2]: # 删除棋盘
                        if chess_coordinate[0] in self.chessin5d.state:
                            if chess_coordinate[1] == len(self.chessin5d.state[chess_coordinate[0]]) - 1:
                                def popline(chessin5d,line):
                                    self.history.append(copy.deepcopy(self.chessin5d))
                                    chessin5d.state.pop(line)
                                    if line < 0:
                                        chessin5d.whiteline -= 1
                                        print(chessin5d.whiteline)
                                    else:
                                        chessin5d.blackline -= 1
                                        print(chessin5d.blackline)


                                if chess_coordinate[1] == 0:
                                    if chess_coordinate[0] != 0:
                                        popline(self.chessin5d, chess_coordinate[0])
                                elif self.chessin5d.state[chess_coordinate[0]][chess_coordinate[1] - 1] is None:
                                    popline(self.chessin5d, chess_coordinate[0])
                                else:
                                    self.history.append(copy.deepcopy(self.chessin5d))
                                    self.chessin5d.state[chess_coordinate[0]].pop()

                else:
                    board = self.chessin5d.getboard(*chess_coordinate[:2])
                    if self.notmove:
                        if mouse_botton[2]:
                            if tuple(chess_coordinate[:2]) in self.chessin5d.not_moved:
                                if chess_coordinate[2:] in self.chessin5d.not_moved[tuple(chess_coordinate[:2])]:
                                    self.history.append(copy.deepcopy(self.chessin5d))
                                    if len(self.chessin5d.not_moved[tuple(chess_coordinate[:2])]) == 1:
                                        self.chessin5d.not_moved.pop(tuple(chess_coordinate[:2]))
                                    else:
                                        self.chessin5d.not_moved[tuple(chess_coordinate[:2])].remove(chess_coordinate[2:])

                        elif mouse_botton[0]:
                            checklist = [1,3,6,7,9,12]
                            if tuple(chess_coordinate[:2]) in self.chessin5d.not_moved:
                                if chess_coordinate[2:] not in self.chessin5d.not_moved[tuple(chess_coordinate[:2])] and\
                                    board[chess_coordinate[2]][chess_coordinate[3]] in checklist:
                                    self.history.append(copy.deepcopy(self.chessin5d))
                                    self.chessin5d.not_moved[tuple(chess_coordinate[:2])].append(chess_coordinate[2:])

                            else:
                                if board is not None and board[chess_coordinate[2]][chess_coordinate[3]] in checklist:
                                    if board[chess_coordinate[2]][chess_coordinate[3]] != 0:
                                        self.history.append(copy.deepcopy(self.chessin5d))
                                        self.chessin5d.not_moved[tuple(chess_coordinate[:2])] = [chess_coordinate[2:]]

                    else:
                        if board is None:
                            self.diy_chosen = None
                            return False
                        if mouse_botton[2]: # 白棋
                            self.diy_chosen = chess_coordinate
                            self.diy_chosen.append(1)
                        elif mouse_botton[0]: # 黑棋
                            self.diy_chosen = chess_coordinate
                            self.diy_chosen.append(0)
        else:
            if mouse_botton[2]:
                if self.chosen is not None:
                    self.unchoose()
            if mouse_botton[0]:
                chess_coordinate = self.getchess(pygame.mouse.get_pos())
                if chess_coordinate is None:
                    if self.chosen is not None:
                        self.unchoose()
                elif chess_coordinate == 'over':
                    if self.chessin5d.end_turn:
                        self.history.append(copy.deepcopy(self.chessin5d))
                        self.chessin5d.onemove([0, -1, 0, 0, 0, 0, 0, 0])

                elif chess_coordinate == 'diy':
                    self.diy = True

                elif chess_coordinate == 'not_move':
                    self.notmove = not self.notmove
                elif chess_coordinate == 'board_change':
                    return False
                elif chess_coordinate == 'recall':
                    if self.history:
                        self.chessin5d = self.history.pop()
                        self.boardlist = {}
                else:
                    self.handle(chess_coordinate)

    def getchess(self, xy):
        if xy[0] > 50 and xy[0] < 140 and xy[1] > 20 and xy[1] < 60:
            return 'diy'
        if xy[0] > 550 and xy[0] < 670 and xy[1] > 20 and xy[1] < 80:
            return 'over'
        if xy[0] > 150 and xy[0] < 240 and xy[1] > 20 and xy[1] < 60:
            return 'board_change'
        if xy[0] > 1200 and xy[0] < 1290 and xy[1] > 20 and xy[1] < 60:
            return 'not_move'
        if xy[0] > 1100 and xy[0] < 1150 and xy[1] > 20 and xy[1] < 60:
            return 'recall'

        board_x = divmod(xy[0] - self.startxy[0], 250)
        board_y = divmod(xy[1] - self.startxy[1], 250)
        if board_x[1] >= 200 or board_y[1] >= 200:
            return None
        board_x, chess_x = tuple(board_x)
        board_y, chess_y = tuple(board_y)
        chess_x = chess_x // 25
        chess_y = chess_y // 25
        return [self.position[1] - board_y, self.position[0] + board_x, chess_y, chess_x]

    def handle(self,chess_coordinate):
        if self.chosen is None:
            self.chosen = chess_coordinate
            self.choose()
        else:
            if tuple(chess_coordinate[:2]) in self.available:
                if chess_coordinate[2:] in self.available[tuple(chess_coordinate[:2])]:
                    self.history.append(copy.deepcopy(self.chessin5d))
                    if not self.chessin5d.onemove([*self.chosen, *chess_coordinate]):
                        self.history.pop()
                    self.unchoose()

    def choose(self):
        temp = self.chessin5d.get_available(self.chosen)
        if temp is None:
            self.unchoose()
        else:
            for i in temp:
                board_co = tuple(i[:2])
                if board_co not in self.available:
                    self.available[board_co] = []
                self.available[board_co].append(i[2:])
        self.boardlist = {}

    def unchoose(self):
        self.chosen = None
        self.available = {}
        self.boardlist = {}

class Chessboard:
    def __init__(self, window, board_state, position_rect, image, chosen_chess = None, available = None, board_available = 0, not_move = None, now_position = None):
        self.window = window
        self.board_state = board_state
        self.position_rect = position_rect
        self.position = (self.position_rect.x, self.position_rect.y)
        self.chosen_chess = chosen_chess
        self.board_image = []
        self.image = image
        self.available = [] if available is None else available
        self.board_available = board_available
        self.not_move = [] if not_move is None else not_move
        self.now_position = now_position
        self.chesspng = ['black_king','black_queen','black_rook','black_knight','black_bishop',
         'black_pawn','white_king','white_queen','white_rook','white_knight','white_bishop','white_pawn']
        for i in range(8):
            temp1 = []
            for j in range(8):
                temp1.append((self.chess_type(self.board_state[i][j]),
                              pygame.Rect(self.position[0] + 25* j, self.position[1] + 25* i, 25, 25)))
            self.board_image.append(temp1)

    def chess_type(self, chessid):
        if chessid == 0:
            return 'blank'
        chessid -= 1
        return self.chesspng[chessid]

    def show(self):
        boardframe_list = ['boardframe_black', 'boardframe_white', 'boardframe_black_not_available',
                           'boardframe_white_not_available']
        rect = [i - 3 for i in self.position]
        self.window.blit(self.image['boardframe_black'], rect)
        self.window.blit(self.image[boardframe_list[self.board_available]], rect)
        for i in range(8):
            for j in range(8):
                image, rect = self.board_image[i][j]
                if image != 'blank':
                    image = self.image[image]
                    rect = (rect.x, rect.y)
                    self.window.blit(image, rect)
                if [i, j] == self.chosen_chess:
                    self.window.blit(self.image['frame_chosen'], rect)
                elif [i,j] in self.available:
                    self.window.blit(self.image['frame_available'], rect)
                elif [i,j] in self.not_move:
                    self.window.blit(self.image['frame_not_move'], rect)



a = Chessin5dUI(image= IMAGE_RESIZED)
a.run()