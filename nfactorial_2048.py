import curses
import random
import sys

LOGO = " _____  _____    ___  _____ \n" \
       "/ __  \\|  _  |  /   ||  _  |\n" \
       "`' / /'| |/' | / /| | \\ V / \n" \
       "  / /  |  /| |/ /_| | / _ \\ \n" \
       "./ /___\\ |_/ /\\___  || |_| |\n" \
       "\\_____/ \\___/     |_/\\_____/\n"
LOGO_COLOR = 1

TILE_COLORS = {
    2: (curses.COLOR_BLACK, curses.COLOR_WHITE),
    4: (curses.COLOR_BLACK, curses.COLOR_YELLOW),
    8: (curses.COLOR_BLACK, curses.COLOR_BLUE),
    16: (curses.COLOR_BLACK, curses.COLOR_GREEN),
    32: (curses.COLOR_BLACK, curses.COLOR_MAGENTA),
    64: (curses.COLOR_BLACK, curses.COLOR_CYAN),
    128: (curses.COLOR_RED, curses.COLOR_CYAN),
    256: (curses.COLOR_RED, curses.COLOR_GREEN),
    512: (curses.COLOR_RED, curses.COLOR_YELLOW),
    1024: (curses.COLOR_RED, curses.COLOR_BLUE),
    2048: (curses.COLOR_RED, curses.COLOR_MAGENTA),
    4096: (curses.COLOR_RED, curses.COLOR_CYAN),
    8192: (curses.COLOR_RED, curses.COLOR_WHITE)
}

LEVELS = (("Master - 3x3", 3, 3),
          ("Normal - 4x4", 4, 4),
          ("Easy - 5x5", 5, 5),
          ("Relax - 6x6", 6, 6))


def get_tile_color_pair(tile):
    return curses.color_pair(8192 if tile >= 8192 else tile)


def add_cstr(stdscr, y, str):
    stdscr.addstr(y, 0, str.center(curses.COLS))


class NFactorial2048:
    @classmethod
    def empty_board(cls, height, width):
        return [[0] * width for _ in range(height)]

    def fill_random_empty_tile(self, value):
        empty_tiles = [(row, col)
                       for row, row_tiles in enumerate(self.board)
                       for col, tile in enumerate(row_tiles)
                       if tile == 0]

        if not empty_tiles:
            return

        x, y = random.choice(empty_tiles)
        self.board[x][y] = value

    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.board_window = curses.newwin(
            height * 2 + 1, width * 7 + 1,
            (curses.LINES - height * 2 - 1) // 2,
            (curses.COLS - width * 7 - 1) // 2)
        self.board = NFactorial2048.empty_board(height, width)
        for _ in range(2):
            # choose 2 with 75% probability and 4 with 25% probability
            self.fill_random_empty_tile(random.choice([2, 2, 2, 4]))

        self.state = "PLAYING"

    def draw(self):
        self.board_window.clear()
        for i in range(self.width):
            for j in range(self.height):
                self.board_window.addstr(i * 2, j * 7, "+------")
                self.board_window.addch(i * 2 + 1, j * 7, "|")
                if self.board[i][j] != 0:
                    self.board_window.addstr(
                        i * 2 + 1, j * 7 + 1,
                        str(self.board[i][j]).center(6),
                        get_tile_color_pair(self.board[i][j]))
            self.board_window.addch(i * 2, self.height * 7, "+")
            self.board_window.addch(i * 2 + 1, self.height * 7, "|")
        for j in range(self.height):
            self.board_window.addstr(self.width * 2, j * 7, "+------")
        self.board_window.insch(self.width * 2, self.height * 7, "+")
        self.board_window.refresh()

    def compress(self):
        for i in range(self.height):
            k = 0
            for j in range(self.width):
                if self.board[i][j] != 0:
                    self.board[i][k] = self.board[i][j]
                    if j != k:
                        self.board[i][j] = 0
                    k += 1
        return self

    def merge(self):
        for i in range(self.height):
            for j in range(self.width - 1):
                value = self.board[i][j]
                if value == self.board[i][j + 1] and value != 0:
                    self.board[i][j] = self.board[i][j] * 2
                    self.board[i][j + 1] = 0
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
        return self.compress().merge().compress()

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

        new_tile = random.choice([2] * 6 + [4])
        self.fill_random_empty_tile(new_tile)
        self.draw()

        won = False
        game_continues = False
        for i in range(self.width):
            for j in range(self.height):
                if self.board[i][j] >= 2048:
                    won = True
                if self.board[i][j] == 0 or \
                        i > 0 and self.board[i - 1][j] == self.board[i][j] or \
                        j > 0 and self.board[i][j - 1] == self.board[i][j]:
                    game_continues = True

        if game_continues:
            self.state = "PLAYING"
            if won:
                self.state = "WON AND CAN CONTINUE"
        else:
            self.state = "LOST"
            if won:
                self.state = "WON AND CANNOT CONTINUE"


def game(stdscr, level):
    stdscr.clear()
    stdscr.refresh()

    nfactorial2048 = NFactorial2048(*LEVELS[level][1:])
    nfactorial2048.draw()

    add_cstr(stdscr, curses.LINES - 2,
             "PRESS Q TO QUIT, ARROW KEYS OR WASD TO MOVE THE TILES")

    continue_game_after_win = False
    while True:
        key = stdscr.getkey()
        if key == "KEY_UP" or key.lower() == "w":
            nfactorial2048.move("UP")
        elif key == "KEY_DOWN" or key.lower() == "s":
            nfactorial2048.move("DOWN")
        elif key == "KEY_LEFT" or key.lower() == "a":
            nfactorial2048.move("LEFT")
        elif key == "KEY_RIGHT" or key.lower() == "d":
            nfactorial2048.move("RIGHT")
        elif key.lower() == "q":
            return False
        else:
            continue

        if nfactorial2048.state == "LOST" or \
                nfactorial2048.state == "WON AND CANNOT CONTINUE":
            add_cstr(stdscr, 2, "GAME OVER!")
            add_cstr(stdscr, curses.LINES - 2,
                     "PRESS Q TO QUIT OR ANY OTHER KEY TO RESTART")
            stdscr.refresh()
            curses.napms(1500)
            key = stdscr.getkey()
            return key.lower() != "q"
        elif nfactorial2048.state == "WON AND CAN CONTINUE":
            if continue_game_after_win:
                continue
            add_cstr(stdscr, 2, "YOU WON!")
            add_cstr(stdscr, curses.LINES - 2,
                     "PRESS Q TO QUIT OR ANY OTHER KEY TO CONTINUE")
            stdscr.refresh()
            curses.napms(1500)
            key = stdscr.getkey()
            if key.lower() == "q":
                return False
            else:
                continue_game_after_win = True


def check_window_size():
    return curses.LINES >= 24 and curses.COLS >= 80


def main(stdscr):
    if not check_window_size():
        raise curses.error("Please resize the terminal to at least 80x24.")

    curses.curs_set(0)

    curses.init_pair(LOGO_COLOR, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    for tile, color in TILE_COLORS.items():
        curses.init_pair(tile, *color)

    level = 1
    while True:
        stdscr.clear()
        stdscr.move(0, 0)
        for tile in LOGO.splitlines():
            stdscr.addstr(tile.center(curses.COLS),
                          curses.color_pair(LOGO_COLOR))
        stdscr.addstr(7, 0, "SELECT DIFFICULTY LEVEL".center(curses.COLS))
        stdscr.addstr(22, 0, "PRESS Q TO QUIT THE GAME".center(curses.COLS))

        x = (curses.COLS - 25) // 2
        for tile, j in enumerate(LEVELS):
            if tile == level:
                attr = curses.A_REVERSE
            else:
                attr = curses.A_NORMAL

            stdscr.addstr(tile * 3 + 9, x, ("+" + "-" * 23 + "+"), attr)
            stdscr.addstr(
                tile * 3 + 10,
                x,
                ("|" + j[0].center(23) + "|"),
                attr)
            stdscr.addstr(tile * 3 + 11, x, ("+" + "-" * 23 + "+"), attr)

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
        pass
