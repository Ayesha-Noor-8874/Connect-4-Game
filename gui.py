import tkinter as tk
from tkinter import messagebox
import project_code as game

# ---------------- WINDOW ----------------

window = tk.Tk()
window.title("Connect 4")
window.geometry("700x650")
window.config(bg="black")

# ---------------- GAME SETTINGS ----------------

ROWS = 6
COLS = 7
CELL_SIZE = 100

board = game.create_board()
game_over = False

# ---------------- CANVAS ----------------

canvas = tk.Canvas(
    window,
    width=COLS * CELL_SIZE,
    height=ROWS * CELL_SIZE,
    bg="pink"
)

canvas.pack(pady=20)

# ---------------- DRAW BOARD ----------------

def draw_board():

    canvas.delete("all")

    for row in range(ROWS):
        for col in range(COLS):

            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE

            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            # Empty circle
            color = "white"

            if board[row][col] == game.HUMAN:
                color = "green"

            elif board[row][col] == game.AI:
                color = "red"

            canvas.create_oval(
                x1 + 10,
                y1 + 10,
                x2 - 10,
                y2 - 10,
                fill=color
            )

# ---------------- HUMAN MOVE ----------------

def handle_click(event):

    global game_over

    if game_over:
        return

    col = event.x // CELL_SIZE

    if game.is_valid_column(board, col):

        game.drop_piece(board, col, game.HUMAN)

        draw_board()

        # Human win
        if game.check_winner(board, game.HUMAN):

            messagebox.showinfo("Game Over", "You Win!")
            game_over = True
            return

        # Draw
        if len(game.get_valid_columns(board)) == 0:

            messagebox.showinfo("Game Over", "Draw!")
            game_over = True
            return

        # ---------------- AI MOVE ----------------

        ai_col = game.get_ai_move(board)

        if ai_col is not None:

            game.drop_piece(board, ai_col, game.AI)

            draw_board()

            # AI win
            if game.check_winner(board, game.AI):

                messagebox.showinfo("Game Over", "AI Wins!")
                game_over = True
                return

            # Draw
            if len(game.get_valid_columns(board)) == 0:

                messagebox.showinfo("Game Over", "Draw!")
                game_over = True
                return

# ---------------- MOUSE CLICK ----------------

canvas.bind("<Button-1>", handle_click)

# ---------------- START ----------------

draw_board()

window.mainloop()