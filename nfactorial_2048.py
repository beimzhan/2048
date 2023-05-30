import copy
import curses
import json
import random
import sys

LEVEL_NAMES = [
    "Master - 3x3",
    "Normal - 4x4",
    "Easy - 5x5",
    "Relax - 6x6"
]
LEVELS = [(3, 3), (4, 4), (5, 5), (6, 6)]

COLOR_PAIRS = {
    1:  (curses.COLOR_YELLOW, curses.COLOR_BLACK),
    2:  (curses.COLOR_WHITE, curses.COLOR_BLUE),
    3:  (curses.COLOR_WHITE, curses.COLOR_GREEN),
    4:  (curses.COLOR_WHITE, curses.COLOR_MAGENTA),
    5:  (curses.COLOR_WHITE, curses.COLOR_CYAN),
    6:  (curses.COLOR_WHITE, curses.COLOR_RED),
    7:  (curses.COLOR_WHITE, curses.COLOR_YELLOW),
    8:  (curses.COLOR_BLACK, curses.COLOR_WHITE),
    9:  (curses.COLOR_BLACK, curses.COLOR_BLUE),
    10: (curses.COLOR_BLACK, curses.COLOR_GREEN),
    11: (curses.COLOR_BLACK, curses.COLOR_MAGENTA),
    12: (curses.COLOR_BLACK, curses.COLOR_CYAN),
    13: (curses.COLOR_BLACK, curses.COLOR_RED),
    14: (curses.COLOR_BLACK, curses.COLOR_YELLOW),
    15: (curses.COLOR_WHITE, curses.COLOR_BLACK),
    16: (curses.COLOR_WHITE, curses.COLOR_BLUE),
    17: (curses.COLOR_WHITE, curses.COLOR_GREEN),
    18: (curses.COLOR_WHITE, curses.COLOR_MAGENTA),
    19: (curses.COLOR_WHITE, curses.COLOR_CYAN),
    20: (curses.COLOR_WHITE, curses.COLOR_RED)
}

LOGO = " _____  _____    ___  _____ \n" \
       "/ __  \\|  _  |  /   ||  _  |\n" \
       "`' / /'| |/' | / /| | \\ V / \n" \
       "  / /  |  /| |/ /_| | / _ \\ \n" \
       "./ /___\\ |_/ /\\___  || |_| |\n" \
       "\\_____/ \\___/     |_/\\_____/\n"

LOGO_COLOR = 1

TILE_COLORS = {
    2: 2,
    4: 3,
    8: 4,
    16: 5,
    32: 6,
    64: 7,
    128: 8,
    256: 9,
    512: 10,
    1024: 11,
    2048: 12,
    4096: 13,
    8192: 14,
    16384: 15,
    32768: 16,
    65536: 17,
    131072: 18,
    262144: 19,
    524288: 20
}


class Board2048:
    def __init__(self, height, width, board=None):
        self.score = 0

        self.height = height
        self.width = width

        if board:
            self.board = copy.deepcopy(board)
        else:
            self.board = [[0] * width for _ in range(height)]
            for _ in range(2):
                self.add_tile_to_random_empty_cell()

        self.evaluate_state()

    def add_tile_to_random_empty_cell(self):
        empty_cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row][col] == 0:
                    empty_cells.append((row, col))

        if empty_cells:
            x, y = random.choice(empty_cells)
            self.board[x][y] = random.choice([2] * 6 + [4])

    def compress(self):
        self.compressed = False
        for i in range(self.height):
            k = 0
            for j in range(self.width):
                if self.board[i][j] != 0:
                    self.board[i][k] = self.board[i][j]
                    if j != k:
                        self.board[i][j] = 0
                        self.compressed = True
                    k += 1
        return self

    def merge(self):
        self.merged = False
        for i in range(self.height):
            for j in range(self.width - 1):
                value = self.board[i][j]
                if value == self.board[i][j + 1] and value != 0:
                    self.board[i][j] = self.board[i][j] * 2
                    self.board[i][j + 1] = 0
                    self.score += self.board[i][j]
                    self.merged = True
        return self

    def reverse(self):
        for i in range(self.height):
            self.board[i].reverse()
        return self

    def transpose(self):
        for i in range(self.height):
            for j in range(i, self.width):
                self.board[i][j], self.board[j][i] = \
                    self.board[j][i], self.board[i][j]
        return self

    def move_left(self):
        self.compress().merge()
        self.moved = self.compressed or self.merged
        return self.compress()

    def move_right(self):
        return self.reverse().move_left().reverse()

    def move_up(self):
        return self.transpose().move_left().transpose()

    def move_down(self):
        return self.transpose().move_right().transpose()

    def move(self, direction):
        if direction == "UP":
            self.move_up()
        elif direction == "DOWN":
            self.move_down()
        elif direction == "LEFT":
            self.move_left()
        elif direction == "RIGHT":
            self.move_right()

        if not self.moved:
            return

        self.add_tile_to_random_empty_cell()

        self.evaluate_state()

    def evaluate_state(self):    
        is_game_won = False
        will_game_continue = False
        for i in range(self.width):
            for j in range(self.height):
                if self.board[i][j] >= 2048:
                    is_game_won = True
                if self.board[i][j] == 0 or \
                        i > 0 and self.board[i - 1][j] == self.board[i][j] or \
                        j > 0 and self.board[i][j - 1] == self.board[i][j]:
                    will_game_continue = True

        if will_game_continue:
            self.state = "PLAYING"
            if is_game_won:
                self.state = "WON AND CAN CONTINUE"
        else:
            self.state = "LOST"
            if is_game_won:
                self.state = "WON AND CANNOT CONTINUE"

    def get_random_move(self):
        all_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        while all_moves:
            search_board = Board2048(self.height, self.width, self.board)

            random_move = all_moves.pop(random.randint(0, len(all_moves) - 1))
            search_board.move(random_move)

            if search_board.moved:
                return random_move

        return "UP"

    def get_best_move(self):
        all_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        scores = [0 for _ in range(4)]

        for i, direction in enumerate(all_moves):
            initial_board = Board2048(self.height, self.width, self.board)
            initial_board.move(direction)

            if not initial_board.moved:
                continue

            scores[i] += initial_board.score
            for _ in range(20): # searches per move
                j = 1
                search_board = copy.deepcopy(initial_board)

                while search_board.moved and j < 10: # search length
                    random_move = search_board.get_random_move()
                    search_board.move(random_move)

                    if search_board.moved:
                        scores[i] += search_board.score
                        j += 1

        return all_moves[max(range(4), key=lambda i: scores[i])]


class NFactorial2048(Board2048):
    def __init__(self, level_name, height, width):
        super().__init__(height, width)

        self.level_name = level_name

        self.board_window = curses.newwin(
            height * 2 + 1, width * 9 + 1,
            (curses.LINES - height * 2 - 1) // 2,
            (curses.COLS - width * 9 - 1) // 2)

    def draw(self):
        self.board_window.clear()
        for i in range(self.width):
            for j in range(self.height):
                tile = self.board[i][j]
                self.board_window.addstr(i * 2, j * 9, "+--------")
                self.board_window.addch(i * 2 + 1, j * 9, "|")
                if tile != 0:
                    self.board_window.addstr(
                        i * 2 + 1, j * 9 + 1,
                        str(tile).center(8),
                        curses.color_pair(TILE_COLORS.get(tile, 20)))
            self.board_window.addch(i * 2, self.height * 9, "+")
            self.board_window.addch(i * 2 + 1, self.height * 9, "|")
        for j in range(self.height):
            self.board_window.addstr(self.width * 2, j * 9, "+--------")
        self.board_window.insch(self.width * 2, self.height * 9, "+")
        self.board_window.refresh()

    def move(self, direction):
        super().move(direction)
        self.draw()

    def make_best_move(self):
        self.move(self.get_best_move())

    def get_highscores(self):
        try:
            with open("highscores.json", "r") as f:
                return json.load(f)
        except BaseException:
            return {}

    def get_highscore(self):
        highscore_from_file = self.get_highscores().get(self.level_name, 0)
        if self.score > highscore_from_file:
            return self.score
        else:
            return highscore_from_file

    def save_score(self):
        highscores = self.get_highscores()
        highscores[self.level_name] = self.get_highscore()
        try:
            with open("highscores.json", "w") as f:
                json.dump(highscores, f)
        except BaseException:
            pass

    def show_score(self, stdscr):
        stdscr.addstr(4, 0, f"SCORE: {self.score}".center(curses.COLS // 2) +
                      f"HIGH SCORE: {self.get_highscore()}".center(curses.COLS // 2))
        stdscr.refresh()


def adcstr(stdscr, y, str):
    stdscr.addstr(y, 0, str.center(curses.COLS))


def game(stdscr, level):
    nfactorial2048 = NFactorial2048(LEVEL_NAMES[level], *LEVELS[level])

    stdscr.clear()

    nfactorial2048.show_score(stdscr)
    nfactorial2048.draw()

    bot_play = False
    continue_game_after_win = False
    while True:
        stdscr.move(2, 0)
        stdscr.clrtoeol()
        adcstr(stdscr, curses.LINES - 2,
               "PRESS Q TO QUIT, ARROW KEYS OR WASD TO MOVE THE TILES")

        if bot_play:
            adcstr(stdscr, curses.LINES - 4,
                   "BOT PLAY IS ON. PRESS B TO TURN IT OFF.")
        else:
            adcstr(stdscr, curses.LINES - 4, "PRESS B TO TOGGLE BOT PLAY")

        if bot_play:
            stdscr.nodelay(True)
            curses.napms(250)
        else:
            stdscr.nodelay(False)

        try:
            key = stdscr.getkey()
        except BaseException:  # if no key is pressed
            key = ""

        if key.lower() == "q":
            return False
        if key.lower() == "b":
            bot_play = not bot_play
            continue
        elif bot_play and key == "":
            nfactorial2048.make_best_move()
        elif not bot_play:
            if key == "KEY_UP" or key.lower() == "w":
                nfactorial2048.move("UP")
            elif key == "KEY_DOWN" or key.lower() == "s":
                nfactorial2048.move("DOWN")
            elif key == "KEY_LEFT" or key.lower() == "a":
                nfactorial2048.move("LEFT")
            elif key == "KEY_RIGHT" or key.lower() == "d":
                nfactorial2048.move("RIGHT")
            else:
                continue

        nfactorial2048.show_score(stdscr)

        if nfactorial2048.state == "LOST" or \
                nfactorial2048.state == "WON AND CANNOT CONTINUE":
            nfactorial2048.save_score()

            adcstr(stdscr, 2, "GAME OVER!")
            adcstr(stdscr, curses.LINES - 2,
                   "PRESS Q TO QUIT OR ANY OTHER KEY TO RESTART")
            stdscr.refresh()
            curses.napms(1500)
            stdscr.nodelay(False)
            key = stdscr.getkey()
            return key.lower() != "q"
        elif nfactorial2048.state == "WON AND CAN CONTINUE":
            if continue_game_after_win:
                continue
            adcstr(stdscr, 2, "YOU WON!")
            adcstr(stdscr, curses.LINES - 2,
                   "PRESS Q TO QUIT OR ANY OTHER KEY TO CONTINUE")
            stdscr.refresh()
            curses.napms(1500)
            stdscr.nodelay(False)
            key = stdscr.getkey()
            if key.lower() == "q":
                return False
            else:
                continue_game_after_win = True


def logo_show(stdscr):
    stdscr.move(0, 0)
    for i in LOGO.splitlines():
        stdscr.addstr(i.center(curses.COLS),
                      curses.color_pair(LOGO_COLOR))


def main(stdscr):
    if curses.LINES < 24 or curses.COLS < 80:
        raise curses.error("Please resize the terminal to at least 80x24.")

    curses.curs_set(0)

    for pair, (fg, bg) in COLOR_PAIRS.items():
        curses.init_pair(pair, fg, bg)

    level = 1
    while True:
        stdscr.clear()
        logo_show(stdscr)
        adcstr(stdscr, 7, "SELECT DIFFICULTY LEVEL")
        adcstr(stdscr, 22, "PRESS Q TO QUIT THE GAME")

        x = (curses.COLS - 25) // 2
        for i, level_name in enumerate(LEVEL_NAMES):
            if i == level:
                attr = curses.A_REVERSE
            else:
                attr = curses.A_NORMAL

            stdscr.addstr(i * 3 + 9, x, ("+" + "-" * 23 + "+"), attr)
            stdscr.addstr(
                i * 3 + 10,
                x,
                ("|" + level_name.center(23) + "|"),
                attr)
            stdscr.addstr(i * 3 + 11, x, ("+" + "-" * 23 + "+"), attr)

        key = stdscr.getkey()
        if key == "KEY_UP":
            level = (level - 1) % len(LEVELS)
        elif key == "KEY_DOWN":
            level = (level + 1) % len(LEVELS)
        elif key == "\n":
            continue_game = game(stdscr, level)
            if not continue_game:
                break
        elif key.lower() == 'q':
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(2)
