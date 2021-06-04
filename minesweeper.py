
import random
import re


class Board:
    def __init__(self, size, num_bombs):
        # parameter size defines how long one side of our board is
        # parameter num_bombs defines how many bombs we want to plant
        self.size = size
        self.num_bombs = num_bombs

        # helper function to create board
        self.board = self.make_new_board()  # make board and plant the bombs
        self.assign_values_to_board()  # assign values to each tile

        # initialize a set to keep track of which locations we've uncovered
        # (row,col) tuples are saved into this set
        self.dug = set()  # if we dig at 0, 0, then self.dug = {(0,0)}

    def make_new_board(self):
        # construct a new board based on the size and number of bombs
        # generate a new board using a nested list comprehension
        board = [[None for _ in range(self.size)]
                 for _ in range(self.size)]
        # this creates an array like this:
        # [[None, None, ..., None],
        #  [None, None, ..., None],
        #  [...                  ],
        #  [None, None, ..., None]]

        # plant the bombs randomly
        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            # return a random integer N between values 0 and total number of tiles on the board (-1 because indices start with 0)
            index = random.randint(0, self.size**2 - 1)
            # to get the row of the index we check how many times "size" goes into index
            row = index // self.size
            # to get the column of the index we check the remainder
            col = index % self.size

            if board[row][col] == '*':
                # continue if we already have a bomb planted
                continue

            board[row][col] = '*'  # plant the bomb
            bombs_planted += 1

        return board

    def assign_values_to_board(self):
        # we will assign a number 0-8 for all the empty spaces
        # the digit will represent how many neighboring bombs there are
        # we will precompute these so it saves computing resource later in the program
        for r in range(self.size):
            for c in range(self.size):
                # if tile is a bomb, continue
                if self.board[r][c] == '*':
                    continue
                self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def get_num_neighboring_bombs(self, row, col):
        # iterate through each of the neighboring positions to check if there is a bomb
        # top left: (row-1, col-1)
        # top middle: (row-1, col)
        # top right: (row-1, col+1)
        # left: (row, col-1)
        # right: (row, col+1)
        # bottom left: (row+1, col-1)
        # bottom middle: (row+1, col)
        # bottom right: (row+1, col+1)

        num_neighboring_bombs = 0
        # max and min functions make sure we don't go off the board
        # +1 at the end because "range" doesn't get to the last number
        for r in range(max(0, row-1), min(self.size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.size-1, col+1)+1):
                if r == row and c == col:
                    # our original location, don't check
                    continue
                if self.board[r][c] == '*':
                    num_neighboring_bombs += 1

        return num_neighboring_bombs

    def dig(self, row, col):
        # dig at board[row][col]
        # return True if successful dig, False if bomb dug

        # scenarios:
        # hit a bomb -> game over
        # dig at location with neighboring bombs -> finish dig
        # dig at location with no neighboring bombs -> recursively dig neighbors

        self.dug.add((row, col))  # keep track that we dug here

        if self.board[row][col] == '*':
            return False  # game over
        elif self.board[row][col] > 0:
            return True

        # no neighnoring bombs: self.board[row][col] == 0
        for r in range(max(0, row-1), min(self.size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.size-1, col+1)+1):
                if (r, c) in self.dug:
                    continue  # don't dig where you've already dug
                self.dig(r, c)

        return True

    def __str__(self):
        # this python function prints out what the function returns
        # return a string that shows the board to the player
        # what the user will see:
        visible_board = [[None for _ in range(self.size)]
                         for _ in range(self.size)]
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) in self.dug:
                    visible_board[row][col] = str(self.board[row][col])
                else:
                    visible_board[row][col] = ' '

        # put this together in a string
        string_representation = ''
        # get max column widths for printing
        widths = []
        for idx in range(self.size):
            columns = map(lambda x: x[idx], visible_board)
            widths.append(len(max(columns, key=len)))

        # print the csv strings
        indices = [i for i in range(self.size)]
        indices_row = '   '
        cells = []
        for idx, col in enumerate(indices):
            format = '%-' + str(widths[idx]) + "s"
            cells.append(format % (col))
        indices_row += '  '.join(cells)
        indices_row += '  \n'

        for i in range(len(visible_board)):
            row = visible_board[i]
            string_representation += f'{i} |'
            cells = []
            for idx, col in enumerate(row):
                format = '%-' + str(widths[idx]) + "s"
                cells.append(format % (col))
            string_representation += ' |'.join(cells)
            string_representation += ' |\n'

        str_len = int(len(string_representation) / self.size)
        string_representation = indices_row + '-'*str_len + \
            '\n' + string_representation + '-'*str_len

        return string_representation

# play the game


def play(size=10, num_bombs=10):
    # Step 1: create the board and plant the bombs
    board = Board(size, num_bombs)

    # Step 2: show the user the board and ask for where they want to dig
    # Step 3a: if location is a bomb, show game over message
    # Step 3b: if location is not a bomb, dig recursively until each square is at least next to a bomb
    # Step 4: repeat steps 2 and 3a/b until there are no more places to dig -> VICTORY!
    safe = True

    while len(board.dug) < board.size ** 2 - num_bombs:
        print(board)
        # 0,0 or 0, 0 or 0,    0
        user_input = re.split(',(\\s)*',
                              input("Where would you like to dig? Input as row,col: "))  # '0, 3'
        row, col = int(user_input[0]), int(user_input[-1])
        if row < 0 or row >= board.size or col < 0 or col >= size:
            print("Invalid location. Try again.")
            continue

        # if it's valid, we dig
        safe = board.dig(row, col)
        if not safe:
            # dug a bomb ahhhhhhh
            break  # (game over rip)

    # 2 ways to end loop, lets check which one
    if safe:
        print("CONGRATULATIONS! YOU WON!")
    else:
        print("GAME OVER!! LOSER!")
        # reveal whole board
        board.dug = [(r, c) for r in range(board.size)
                     for c in range(board.size)]
        print(board)


if __name__ == '__main__':  # good practice :)
    play()
