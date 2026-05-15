import tkinter as TK
import threading
import time
import sys

# GAME LOGIC
ROWS = 6
COLS = 7
EMPTY = 0
HUMAN = 1
AI = 2

def create_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]

def is_valid_coloumn(board, col):
    return 0 <= col < COLS and board[0][col] == EMPTY

def get_valid_columns(board):
    return [col for col in range(COLS) if is_valid_coloumn(board, col)]

def get_next_open_row(board, col);
    for row in range(ROWS -1, -1, -1):
        if board[row][col] == EMPTY:
            return row
        return -1
    
def drop_piece(board, col, player):
    row = get_next_open_row(board, col)
    if row == -1:
        return -1
    board[row][col] = player
    return row

def undo_move(board, col):
    for row in range(ROWS):
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            return row
    return -1

def check_winner(board, player):
    #Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                return True
    
    #Vertical
    for col in range(COLS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == player for i in range(4)):
                return True
    
    # Diagonal/
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if all(board[row + i][col + i] == player for i in range(4)):
                return True
    
    #Diagnol\
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if all(board[row - i][col + i] == player for i in range(4)):
                return True
            
    return False

def get_winning_cells(board, player):
    #Horizontal 
    for row in range(ROWS):
        for col in range(COLS - 3):
            cells = [(row, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
            
    #Vertical
    for col in range(COLS):
        for row in range(ROWS - 3):
            cells=[(row + i, col) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
            
    #Diagnol /
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            cells = [(row + i, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
            
    #Diagnol \
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            cells = ([row - i, col + i] for i in range(4))
            if all(board[r][c] == player for r, c in cells):
                return cells
    
    return []

def is_terminal(board):
    return (
        check_winner(board, HUMAN)
        or check_winner(board, AI)
        or len(get_valid_columns(board)) == 0
    )

def print_board(board,winning_cells=None):
    winning_cells = winning_cells or []
    print()
    print(" "+" ".join(str(c) for c in range(COLS)))
    print(" "+"-----" * COLS)
    symbols = {EMPTY: ".", HUMAN: "0", AI: "X"}

    for row in range(ROWS):
        row_str = "| "
        for col in range(COLS):
            cell =board[row][col]
            sym = symbols[cell]
            if (row,col) in winning_cells:
                sym = "*"
            row_str += sym + " |" if col < COLS - 1 else sym

        print(row_str)

    print(" " + "-----" * COLS)
    print()



