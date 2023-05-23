import curses
import random

class Nfactorial2048:
    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.board = [[0] * length for _ in range(width)]

        for _ in range(2):
            while True:
                x = random.randint(0, length-1)
                y = random.randint(0, width-1)
                if self.board[x][y] == 0:
                    # choose 2 with 75% probability and 4 with 25% probability
                    self.board[x][y] = random.choice([2, 2, 2, 4])
                    break

    def draw(self, board_window):
        board_window.clear()
        for i in range(self.width):
            for j in range(self.length):
                board_window.addstr(i*2, j*7, "+------")
                board_window.addch(i*2+1, j*7, "|")
                if self.board[i][j] != 0:
                    board_window.addstr(i*2+1, j*7+1, str(self.board[i][j]).center(6))
            board_window.addch(i*2, self.length*7, "+")
            board_window.addch(i*2+1, self.length*7, "|")
        for j in range(self.length):
            board_window.addstr(self.width*2, j*7, "+------")
        board_window.addstr(self.width*2, self.length*7, "+")
        board_window.refresh()

def main(stdscr):
    curses.curs_set(0)

    nfactorial2048 = Nfactorial2048(length=4, width=4)
    nfactorial2048.draw(stdscr)

    stdscr.getkey()

if __name__=="__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
