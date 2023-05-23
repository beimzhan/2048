import curses
import random

LOGO = " _____  _____    ___  _____ \n" \
       "/ __  \\|  _  |  /   ||  _  |\n" \
       "`' / /'| |/' | / /| | \\ V / \n" \
       "  / /  |  /| |/ /_| | / _ \\ \n" \
       "./ /___\\ |_/ /\\___  || |_| |\n" \
       "\\_____/ \\___/     |_/\\_____/\n"
LOGO_COLOR = 1

LEVELS = (("Master - 3x3", 3, 3),
          ("Normal - 4x4", 4, 4),
          ("Easy - 5x5", 5, 5),
          ("Relax - 6x6", 6, 6))

class NFactorial2048:
    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.board_window = curses.newwin(height*2+1, width*7+1, 0, 0)
        self.board = [[0] * height for _ in range(width)]
        for _ in range(2):
            while True:
                x = random.randint(0, height-1)
                y = random.randint(0, width-1)
                if self.board[x][y] == 0:
                    # choose 2 with 75% probability and 4 with 25% probability
                    self.board[x][y] = random.choice([2, 2, 2, 4])
                    break

    def draw(self):
        self.board_window.clear()
        for i in range(self.width):
            for j in range(self.height):
                self.board_window.addstr(i*2, j*7, "+------")
                self.board_window.addch(i*2+1, j*7, "|")
                if self.board[i][j] != 0:
                    self.board_window.addstr(
                        i*2+1, j*7+1, str(self.board[i][j]).center(6))
            self.board_window.addch(i*2, self.height*7, "+")
            self.board_window.addch(i*2+1, self.height*7, "|")
        for j in range(self.height):
            self.board_window.addstr(self.width*2, j*7, "+------")
        self.board_window.addstr(self.width*2, self.height*7, "+")
        self.board_window.refresh()

def main(stdscr):
    curses.cbreak()
    curses.curs_set(0)

    curses.init_pair(LOGO_COLOR, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    stdscr.move(0, 0)
    for i in LOGO.splitlines():
        stdscr.addstr(i.center(curses.COLS), curses.color_pair(LOGO_COLOR))
    stdscr.addstr(7, 0, "SELECT DIFFICULTY LEVEL".center(curses.COLS))
    stdscr.addstr(22, 0, "PRESS Q TO QUIT THE GAME".center(curses.COLS))
    stdscr.refresh()

    level_window = \
        curses.newwin(13, 25, 9, (curses.COLS-25)//2)
    level_window.keypad(True)

    level = 1
    while True:
        for i, j in enumerate(LEVELS):
            if i == level:
                attr = curses.A_REVERSE
            else:
                attr = curses.A_NORMAL

            level_window.addstr(i*3, 0, ("+" + "-" * 23 + "+"), attr)
            level_window.addstr(i*3+1, 0, ("|" + j[0].center(23) + "|"),  attr)
            level_window.addstr(i*3+2, 0, ("+" + "-" * 23 + "+"), attr)
        level_window.refresh()

        key = level_window.getkey()
        if key == "KEY_UP":
            if level > 0:
                level -= 1
            else:
                level = len(LEVELS) - 1
        elif key == "KEY_DOWN":
            if level < len(LEVELS) - 1:
                level += 1
            else:
                level = 0
        elif key == 'Q':
            break

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
