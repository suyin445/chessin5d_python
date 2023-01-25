import pygame
import os
import chessin5d

IMAGE = {'black_king': pygame.image.load(os.path.join('chesspng', 'lxh_yiheihua.png')),
         'black_queen': pygame.image.load(os.path.join('chesspng', 'blackqueen.png')),
         'black_rook': pygame.image.load(os.path.join('chesspng', 'blackrook.png')),
         'black_knight': pygame.image.load(os.path.join('chesspng', 'blackknight.png')),
         'black_bishop': pygame.image.load(os.path.join('chesspng', 'blackbishop.png')),
         'black_pawn': pygame.image.load(os.path.join('chesspng', 'blackpawn.png')),
         'white_king': pygame.image.load(os.path.join('chesspng', 'lxh.png')),
         'white_queen': pygame.image.load(os.path.join('chesspng', 'whitequeen.png')),
         'white_rook': pygame.image.load(os.path.join('chesspng', 'whiterook.png')),
         'white_knight': pygame.image.load(os.path.join('chesspng', 'whiteknight.png')),
         'white_bishop': pygame.image.load(os.path.join('chesspng', 'whitebishop.png')),
         'white_pawn': pygame.image.load(os.path.join('chesspng', 'whitepawn.png')),
         'frame': pygame.image.load(os.path.join('chesspng', 'frame.png')),
         'frame_chosen': pygame.image.load(os.path.join('chesspng', 'frame_chosen.png')),
         'frame_available': pygame.image.load(os.path.join('chesspng', 'frame_available.png')),
         'boardframe_black': pygame.image.load(os.path.join('chesspng', 'boardframe_black.png')),
         'boardframe_white': pygame.image.load(os.path.join('chesspng', 'boardframe_white.png')),
         'boardframe_black_not_available': pygame.image.load(os.path.join('chesspng', 'boardframe_black_not_available.png')),
         'boardframe_white_not_available': pygame.image.load(os.path.join('chesspng', 'boardframe_white_not_available.png')),
         'can_over': pygame.image.load(os.path.join('chesspng', 'can_over.png')),
         'cannot_over': pygame.image.load(os.path.join('chesspng', 'cannot_over.png'))}
IMAGE_SMALL = {}
for i in IMAGE:
    if i.find('board') != -1:
        IMAGE_SMALL[i] = pygame.transform.scale(IMAGE[i], (205, 205))
    elif i.find('over') != -1:
        IMAGE_SMALL[i] = pygame.transform.scale(IMAGE[i], (120, 60))
    else:
        IMAGE_SMALL[i] = pygame.transform.scale(IMAGE[i], (25, 25))

pygame.init()

class Chessin5d:
    def __init__(self, image, window_size = None):
        if window_size is None:
            window_size = (1300, 800)
        self.window_size = window_size
        self.image = image
        self.window = pygame.display.set_mode(self.window_size)
        self.chessin5d = chessin5d.State()
        self.startxy = (25, 100)
        self.boardlist = {}
        self.position = [0,1]
        self.chosen = None
        self.available = {}
        self.lxh_mode = False
        pygame.display.set_caption('冷筱华，我真的好喜欢你啊！为了你，我要写5dc AI！')

    def draw_window(self):
        self.window.fill((200, 200, 200))
        if self.chessin5d.end_turn:
            self.window.blit(self.image['can_over'], (550, 20))
        else:
            self.window.blit(self.image['cannot_over'], (550, 20))
        for i in self.boardlist:
            self.boardlist[i].show()
        pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()
        run = True

        while run:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or pygame.K_f:
                        if self.chessin5d.end_turn:
                            self.chessin5d.onemove([8,8,8,8,8,8,8,8])
                    elif event.key == pygame.K_w:
                        if self.lxh_mode:
                            self.position[1] += 1
                        else:
                            self.position[1] -= 1
                    elif event.key == pygame.K_s:
                        if self.lxh_mode:
                            self.position[1] -= 1
                        else:
                            self.position[1] += 1
                    elif event.key == pygame.K_a:
                        if self.lxh_mode:
                            self.position[0] -= 1
                        else:
                            self.position[0] += 1
                    elif event.key == pygame.K_d:
                        if self.lxh_mode:
                            self.position[0] += 1
                        else:
                            self.position[0] -= 1
                    self.boardlist = {}

            self.show_board()
            self.draw_window()

        pygame.quit()

    def board_set(self, coordinate, board, xy, chosen_chess, available, board_available):
        if board != None:
            self.boardlist[coordinate] = Chessboard(self.window, board, pygame.Rect(xy[0],xy[1],200,200), self.image, chosen_chess, available, board_available)

    def show_board(self):
        for x in range(5):
            for y in range(3):
                chosen_chess, available = None, None
                now_position = [self.position[1] - y, self.position[0] + x]
                board_available = 0
                if now_position[0] not in self.chessin5d.available_timeline:
                    board_available += 2
                if divmod(now_position[1], 2)[1] == 1:
                    board_available += 1
                if self.chosen is not None:
                    if now_position == self.chosen[:2]:
                        chosen_chess = self.chosen[2:]
                    if tuple(now_position) in self.available:
                        available = self.available[tuple(now_position)]
                self.board_set((x,y), self.chessin5d.getboard(*now_position),
                               (self.startxy[0] + 225 * x, self.startxy[1] + 225 * y),
                               chosen_chess, available, board_available)

    def mouse(self):
        mouse_botton = pygame.mouse.get_pressed()
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
                    self.chessin5d.onemove([8, 8, 8, 8, 8, 8, 8, 8])
            else:
                self.handle(chess_coordinate)

    def getchess(self, xy):
        if xy[0] > 550 and xy[0] < 670 and xy[1] > 20 and xy[1] < 80:
            return 'over'
        board_x = divmod(xy[0] - self.startxy[0], 225)
        board_y = divmod(xy[1] - self.startxy[1], 225)
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
                    self.chessin5d.onemove([*self.chosen, *chess_coordinate])
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
    def __init__(self, window, board_state, position_rect, image, chosen_chess = None, available = None, board_available = 0):
        self.window = window
        self.board_state = board_state
        self.position_rect = position_rect
        self.position = (self.position_rect.x, self.position_rect.y)
        self.chosen_chess = chosen_chess
        self.board_image = []
        self.image = image
        self.available = [] if available is None else available
        self.debug = None
        self.board_available = board_available
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
        chesslist = list(self.image.keys())
        return chesslist[chessid]

    def show(self):
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
                else:
                    self.window.blit(self.image['frame'], rect)
        boardframe_list = ['boardframe_black', 'boardframe_white', 'boardframe_black_not_available',
                           'boardframe_white_not_available']
        rect = [i - 3 for i in self.position]
        self.window.blit(self.image[boardframe_list[self.board_available]], rect)

a = Chessin5d(image= IMAGE_SMALL)
a.run()