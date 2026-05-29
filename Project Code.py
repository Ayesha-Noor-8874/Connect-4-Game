import tkinter as tk
from tkinter import font as tkfont
import sys
import threading

#  CONSTANTS 
ROWS       = 6
COLS       = 7
EMPTY      = 0
HUMAN      = 1
AI         = 2

WIN_SCORE    =  100
LOSE_SCORE   = -100
THREE_IN_ROW =  10
TWO_IN_ROW   =   5
BLOCK_THREE  = -80
CENTER_BONUS =   3
CENTER_COL   = COLS // 2
AI_DEPTH     = 5

#  PALETTE 
BG_DARK      = "#0d0d1a"
BG_BOARD     = "#0a1628"
BOARD_BORDER = "#1a3a6e"
GRID_COLOR   = "#0e2246"
CELL_EMPTY   = "#091020"
HOLE_SHADOW  = "#060e1c"

P1_COLOR     = "#ff3c5a"   # Human  — neon red/pink
P1_GLOW      = "#ff6b84"
P1_DARK      = "#8b1a28"

P2_COLOR     = "#f5c518"   # AI     — arcade yellow
P2_GLOW      = "#ffd94d"
P2_DARK      = "#7a6200"

WIN_FLASH    = "#ffffff"
HOVER_COLOR  = "#1e3a5f"

TEXT_BRIGHT  = "#e8f4fd"
TEXT_DIM     = "#4a6fa5"
TEXT_ACCENT  = "#7ec8e3"

CELL_SIZE    = 88
PADDING      = 20
RADIUS       = 34
ANIM_STEPS   = 14


#  GAME LOGIC 
def create_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]

def is_valid_column(board, col):
    return 0 <= col < COLS and board[0][col] == EMPTY

def get_valid_columns(board):
    return [c for c in range(COLS) if is_valid_column(board, c)]

def get_next_open_row(board, col):
    for row in range(ROWS - 1, -1, -1):
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
    for row in range(ROWS):
        for col in range(COLS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                return True
    for col in range(COLS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == player for i in range(4)):
                return True
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if all(board[row + i][col + i] == player for i in range(4)):
                return True
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if all(board[row - i][col + i] == player for i in range(4)):
                return True
    return False

def get_winning_cells(board, player):
    for row in range(ROWS):
        for col in range(COLS - 3):
            cells = [(row, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    for col in range(COLS):
        for row in range(ROWS - 3):
            cells = [(row + i, col) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            cells = [(row + i, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            cells = [(row - i, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    return []

def is_terminal(board):
    return (check_winner(board, HUMAN) or check_winner(board, AI)
            or len(get_valid_columns(board)) == 0)

# AI 
def _score_window(window, player):
    opponent    = HUMAN if player == AI else AI
    ai_count    = window.count(player)
    opp_count   = window.count(opponent)
    empty_count = window.count(EMPTY)
    score       = 0
    if ai_count == 4:
        score += WIN_SCORE
    elif ai_count == 3 and empty_count == 1:
        score += THREE_IN_ROW
    elif ai_count == 2 and empty_count == 2:
        score += TWO_IN_ROW
    if opp_count == 3 and empty_count == 1:
        score += BLOCK_THREE
    return score

def _evaluate_board(board):
    score = 0
    center_column = [board[row][CENTER_COL] for row in range(ROWS)]
    score += center_column.count(AI) * CENTER_BONUS
    for row in range(ROWS):
        for col in range(COLS - 3):
            score += _score_window(board[row][col:col + 4], AI)
    for col in range(COLS):
        for row in range(ROWS - 3):
            score += _score_window([board[row + i][col] for i in range(4)], AI)
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            score += _score_window([board[row + i][col + i] for i in range(4)], AI)
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            score += _score_window([board[row - i][col + i] for i in range(4)], AI)
    return score

def _center_priority(col):
    return CENTER_COL - abs(col - CENTER_COL)

def minimax(board, depth, alpha, beta, maximising):
    valid_cols = get_valid_columns(board)
    if is_terminal(board):
        if check_winner(board, AI):
            return None, WIN_SCORE * 1000 + depth
        if check_winner(board, HUMAN):
            return None, LOSE_SCORE * 1000 - depth
        return None, 0
    if depth == 0:
        return None, _evaluate_board(board)
    ordered_cols = sorted(valid_cols, key=lambda c: -_center_priority(c))
    if maximising:
        best_score, best_col = float("-inf"), ordered_cols[0]
        for col in ordered_cols:
            drop_piece(board, col, AI)
            _, score = minimax(board, depth - 1, alpha, beta, False)
            undo_move(board, col)
            if score > best_score:
                best_score, best_col = score, col
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        return best_col, best_score
    else:
        best_score, best_col = float("inf"), ordered_cols[0]
        for col in ordered_cols:
            drop_piece(board, col, HUMAN)
            _, score = minimax(board, depth - 1, alpha, beta, True)
            undo_move(board, col)
            if score < best_score:
                best_score, best_col = score, col
            beta = min(beta, best_score)
            if alpha >= beta:
                break
        return best_col, best_score

def get_ai_move(board, depth=AI_DEPTH):
    col, _ = minimax(board, depth, float("-inf"), float("inf"), True)
    return col


#  GUI 
class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CONNECT  4")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.board          = create_board()
        self.current_player = HUMAN
        self.game_over      = False
        self.hover_col      = None
        self.animating      = False
        self.win_flash_on   = False
        self.win_cells      = []
        self.scores         = {HUMAN: 0, AI: 0}
        self.depth          = AI_DEPTH

        self._build_ui()
        self._draw_board()

    #  Layout 
    def _build_ui(self):
        W = COLS * CELL_SIZE + PADDING * 2
        H = ROWS * CELL_SIZE + PADDING * 2

        #  Top bar 
        top = tk.Frame(self.root, bg=BG_DARK)
        top.pack(fill="x", padx=24, pady=(20, 4))

        title_lbl = tk.Label(top, text="C O N N E C T   4",
                             bg=BG_DARK, fg=TEXT_BRIGHT,
                             font=("Courier New", 22, "bold"))
        title_lbl.pack(side="left")

        score_frame = tk.Frame(top, bg=BG_DARK)
        score_frame.pack(side="right")

        self.score_p1 = tk.Label(score_frame, text="YOU  0",
                                 bg=BG_DARK, fg=P1_COLOR,
                                 font=("Courier New", 14, "bold"))
        self.score_p1.pack(side="left", padx=(0, 16))

        sep = tk.Label(score_frame, text="│",
                       bg=BG_DARK, fg=TEXT_DIM,
                       font=("Courier New", 14))
        sep.pack(side="left", padx=(0, 16))

        self.score_ai = tk.Label(score_frame, text="AI  0",
                                 bg=BG_DARK, fg=P2_COLOR,
                                 font=("Courier New", 14, "bold"))
        self.score_ai.pack(side="left")

        #  Status bar 
        self.status_var = tk.StringVar(value="▶  Your turn — click a column")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              bg="#111827", fg=TEXT_ACCENT,
                              font=("Courier New", 12),
                              anchor="center", pady=8)
        status_bar.pack(fill="x", padx=0, pady=(0, 6))

        #  Canvas 
        self.canvas = tk.Canvas(self.root, width=W, height=H,
                                bg=BG_DARK, highlightthickness=0,
                                cursor="hand2")
        self.canvas.pack(padx=24, pady=0)
        self.canvas.bind("<Motion>",   self._on_hover)
        self.canvas.bind("<Leave>",    self._on_leave)
        self.canvas.bind("<Button-1>", self._on_click)

        #  Bottom bar 
        bot = tk.Frame(self.root, bg=BG_DARK)
        bot.pack(fill="x", padx=24, pady=(8, 20))

        btn_cfg = dict(bg="#1a2744", fg=TEXT_BRIGHT,
                       font=("Courier New", 11, "bold"),
                       relief="flat", padx=16, pady=7,
                       cursor="hand2", activebackground="#2a3d6a",
                       activeforeground=TEXT_BRIGHT, bd=0)

        new_btn = tk.Button(bot, text="NEW GAME", command=self._new_game,
                            **btn_cfg)
        new_btn.pack(side="left", padx=(0, 8))

        # Depth selector
        tk.Label(bot, text="AI DEPTH:", bg=BG_DARK, fg=TEXT_DIM,
                 font=("Courier New", 10)).pack(side="right", padx=(8, 4))
        self.depth_var = tk.IntVar(value=self.depth)
        depth_spin = tk.Spinbox(bot, from_=1, to=8,
                                textvariable=self.depth_var,
                                width=3, font=("Courier New", 11, "bold"),
                                bg="#1a2744", fg=P2_COLOR,
                                buttonbackground="#1a2744",
                                relief="flat", bd=0,
                                highlightthickness=1,
                                highlightbackground=BOARD_BORDER,
                                disabledbackground="#1a2744",
                                justify="center",
                                command=self._update_depth)
        depth_spin.pack(side="right")

        # Legend
        leg = tk.Frame(bot, bg=BG_DARK)
        leg.pack(side="left", padx=16)
        for color, label in ((P1_COLOR, "You"), (P2_COLOR, "AI")):
            dot = tk.Canvas(leg, width=14, height=14,
                            bg=BG_DARK, highlightthickness=0)
            dot.create_oval(2, 2, 12, 12, fill=color, outline="")
            dot.pack(side="left", padx=(0, 4))
            tk.Label(leg, text=label, bg=BG_DARK, fg=TEXT_DIM,
                     font=("Courier New", 10)).pack(side="left", padx=(0, 12))

    #  Drawing 
    def _cell_xy(self, row, col):
        x = PADDING + col * CELL_SIZE + CELL_SIZE // 2
        y = PADDING + row * CELL_SIZE + CELL_SIZE // 2
        return x, y

    def _draw_board(self, anim_piece=None, win_override=None):
        """Redraw the entire board canvas."""
        self.canvas.delete("all")
        W = COLS * CELL_SIZE + PADDING * 2
        H = ROWS * CELL_SIZE + PADDING * 2

        #  Board background 
        self.canvas.create_rectangle(PADDING - 8, PADDING - 8,
                                     W - PADDING + 8, H - PADDING + 8,
                                     fill=BG_BOARD, outline=BOARD_BORDER,
                                     width=2)

        #  Hover highlight column 
        if self.hover_col is not None and not self.game_over and not self.animating:
            cx = PADDING + self.hover_col * CELL_SIZE
            self.canvas.create_rectangle(cx, PADDING - 8,
                                         cx + CELL_SIZE, H - PADDING + 8,
                                         fill=HOVER_COLOR, outline="")

        #  Grid lines 
        for r in range(ROWS + 1):
            y = PADDING + r * CELL_SIZE
            self.canvas.create_line(PADDING - 8, y, W - PADDING + 8, y,
                                    fill=GRID_COLOR, width=1)
        for c in range(COLS + 1):
            x = PADDING + c * CELL_SIZE
            self.canvas.create_line(x, PADDING - 8, x, H - PADDING + 8,
                                    fill=GRID_COLOR, width=1)

        win_set = set(map(tuple, win_override or self.win_cells))

        #  Cells 
        for row in range(ROWS):
            for col in range(COLS):
                cx, cy = self._cell_xy(row, col)
                piece  = self.board[row][col]
                is_win = (row, col) in win_set

                # Shadow / hole
                self.canvas.create_oval(cx - RADIUS - 2, cy - RADIUS - 2,
                                        cx + RADIUS + 2, cy + RADIUS + 2,
                                        fill=HOLE_SHADOW, outline="")

                # Piece or empty
                if piece == EMPTY:
                    fill_c = CELL_EMPTY
                    out_c  = "#0d1a30"
                elif piece == HUMAN:
                    fill_c = P1_GLOW if is_win and self.win_flash_on else P1_COLOR
                    out_c  = P1_GLOW if is_win else P1_DARK
                else:
                    fill_c = P2_GLOW if is_win and self.win_flash_on else P2_COLOR
                    out_c  = P2_GLOW if is_win else P2_DARK

                self.canvas.create_oval(cx - RADIUS, cy - RADIUS,
                                        cx + RADIUS, cy + RADIUS,
                                        fill=fill_c, outline=out_c, width=2)

                # Shine on placed pieces
                if piece != EMPTY:
                    self.canvas.create_oval(cx - RADIUS + 6, cy - RADIUS + 6,
                                            cx - RADIUS + 18, cy - RADIUS + 18,
                                            fill=("white" if piece == HUMAN
                                                  else "#fffde7"),
                                            outline="", stipple="gray25")

        #  Animated falling piece overlay 
        if anim_piece:
            col, anim_y, player = anim_piece
            cx = PADDING + col * CELL_SIZE + CELL_SIZE // 2
            fc = P1_COLOR if player == HUMAN else P2_COLOR
            oc = P1_DARK  if player == HUMAN else P2_DARK
            self.canvas.create_oval(cx - RADIUS, anim_y - RADIUS,
                                    cx + RADIUS, anim_y + RADIUS,
                                    fill=fc, outline=oc, width=2)
            self.canvas.create_oval(cx - RADIUS + 6, anim_y - RADIUS + 6,
                                    cx - RADIUS + 18, anim_y - RADIUS + 18,
                                    fill=("white" if player == HUMAN else "#fffde7"),
                                    outline="", stipple="gray25")

        # ── Column numbers hint (top edge) ──
        for col in range(COLS):
            cx = PADDING + col * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_text(cx, 10,
                                    text=str(col),
                                    fill=TEXT_DIM,
                                    font=("Courier New", 9))

    #  Hover / interaction 
    def _col_from_x(self, x):
        col = (x - PADDING) // CELL_SIZE
        if 0 <= col < COLS:
            return col
        return None

    def _on_hover(self, event):
        col = self._col_from_x(event.x)
        if col != self.hover_col:
            self.hover_col = col
            if not self.animating and not self.game_over:
                self._draw_board()

    def _on_leave(self, event):
        self.hover_col = None
        if not self.animating and not self.game_over:
            self._draw_board()

    def _on_click(self, event):
        if self.game_over or self.animating or self.current_player != HUMAN:
            return
        col = self._col_from_x(event.x)
        if col is None or not is_valid_column(self.board, col):
            return
        self._animate_drop(col, HUMAN, callback=self._after_human_drop)

    #  Animation 
    def _animate_drop(self, col, player, callback):
        self.animating = True
        target_row     = get_next_open_row(self.board, col)
        start_y        = PADDING - CELL_SIZE // 2
        target_y       = PADDING + target_row * CELL_SIZE + CELL_SIZE // 2

        step = [0]

        def tick():
            t  = step[0] / ANIM_STEPS
            # ease-out quad
            ease = 1 - (1 - t) ** 2
            cur_y = start_y + (target_y - start_y) * ease
            self._draw_board(anim_piece=(col, cur_y, player))
            step[0] += 1
            if step[0] <= ANIM_STEPS:
                self.root.after(18, tick)
            else:
                drop_piece(self.board, col, player)
                self.animating = False
                self._draw_board()
                callback(col, target_row)

        tick()

    #  Turn logic 
    def _after_human_drop(self, col, row):
        if check_winner(self.board, HUMAN):
            self.win_cells = get_winning_cells(self.board, HUMAN)
            self.scores[HUMAN] += 1
            self._update_scores()
            self.status_var.set("🎉  You win!  Congratulations!")
            self.game_over = True
            self._flash_win(8)
            return
        if not get_valid_columns(self.board):
            self.status_var.set("🤝  It's a draw!")
            self.game_over = True
            return
        self.current_player = AI
        self.status_var.set("⏳  AI is thinking…")
        self.root.after(80, self._ai_turn)

    def _ai_turn(self):
        depth = self.depth_var.get()

        def compute():
            col = get_ai_move(self.board, depth)
            self.root.after(0, lambda: self._animate_drop(
                col, AI, callback=self._after_ai_drop))

        threading.Thread(target=compute, daemon=True).start()

    def _after_ai_drop(self, col, row):
        if check_winner(self.board, AI):
            self.win_cells = get_winning_cells(self.board, AI)
            self.scores[AI] += 1
            self._update_scores()
            self.status_var.set("🤖  AI wins!  Better luck next time.")
            self.game_over = True
            self._flash_win(8)
            return
        if not get_valid_columns(self.board):
            self.status_var.set("🤝  It's a draw!")
            self.game_over = True
            return
        self.current_player = HUMAN
        self.status_var.set("▶  Your turn — click a column")

    #  Win flash 
    def _flash_win(self, n):
        self.win_flash_on = not self.win_flash_on
        self._draw_board()
        if n > 0:
            self.root.after(260, lambda: self._flash_win(n - 1))
        else:
            self.root.after(300, self._show_play_again)

    def _show_play_again(self):
        W = COLS * CELL_SIZE + PADDING * 2
        H = ROWS * CELL_SIZE + PADDING * 2
        cx, cy = W // 2, H // 2

        # dim overlay
        self.canvas.create_rectangle(0, 0, W, H,
                                     fill="#050b18", stipple="gray50",
                                     outline="", tags="overlay")
        # panel
        self.canvas.create_rectangle(cx - 185, cy - 95,
                                     cx + 185, cy + 95,
                                     fill="#0d1e3d", outline=BOARD_BORDER,
                                     width=2, tags="overlay")
        # result text
        self.canvas.create_text(cx, cy - 46,
                                text=self.status_var.get(),
                                fill=TEXT_BRIGHT,
                                font=("Courier New", 13, "bold"),
                                tags="overlay")
        # score
        self.canvas.create_text(cx, cy - 14,
                                text=f"Score  —  You {self.scores[HUMAN]}  :  {self.scores[AI]}  AI",
                                fill=TEXT_ACCENT,
                                font=("Courier New", 11),
                                tags="overlay")
        # PLAY AGAIN button
        yes_btn = tk.Button(self.canvas, text="▶  PLAY AGAIN",
                            bg=P1_COLOR, fg="white",
                            font=("Courier New", 12, "bold"),
                            relief="flat", padx=16, pady=8,
                            cursor="hand2", bd=0,
                            activebackground=P1_GLOW,
                            activeforeground="white",
                            command=self._play_again)
        self.canvas.create_window(cx - 95, cy + 50,
                                  window=yes_btn, tags="overlay")
        # QUIT button
        no_btn = tk.Button(self.canvas, text="✕  QUIT",
                           bg="#1a2744", fg=TEXT_DIM,
                           font=("Courier New", 12, "bold"),
                           relief="flat", padx=16, pady=8,
                           cursor="hand2", bd=0,
                           activebackground="#2a3d6a",
                           activeforeground=TEXT_BRIGHT,
                           command=self._quit_game)
        self.canvas.create_window(cx + 82, cy + 50,
                                  window=no_btn, tags="overlay")

    def _play_again(self):
        self.canvas.delete("overlay")
        self._new_game()

    def _quit_game(self):
        self.root.destroy()

    #  Helpers 
    def _update_scores(self):
        self.score_p1.config(text=f"YOU  {self.scores[HUMAN]}")
        self.score_ai.config(text=f"AI  {self.scores[AI]}")

    def _update_depth(self):
        self.depth = self.depth_var.get()

    def _new_game(self):
        self.board          = create_board()
        self.current_player = HUMAN
        self.game_over      = False
        self.animating      = False
        self.hover_col      = None
        self.win_cells      = []
        self.win_flash_on   = False
        self.status_var.set("▶  Your turn — click a column")
        self._draw_board()


#  MAIN 
if __name__ == "__main__":
    root = tk.Tk()
    app  = Connect4GUI(root)
    root.mainloop()