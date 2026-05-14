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
