import tkinter as TK
import sys

# SECTION 1 — CONSTANTS

ROWS  = 6
COLS  = 7
EMPTY = 0
HUMAN = 1
AI    = 2

WIN_SCORE    =  100
LOSE_SCORE   = -100
THREE_IN_ROW =  10
TWO_IN_ROW   =   5
BLOCK_THREE  = -80
CENTER_BONUS =   3
CENTER_COL   = COLS // 2
AI_DEPTH     = 5


# SECTION 2 — GAME LOGIC

def create_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]


def is_valid_column(board, col):
    return 0 <= col < COLS and board[0][col] == EMPTY


def get_valid_columns(board):
    return [col for col in range(COLS) if is_valid_column(board, col)]


def get_next_open_row(board, col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return -1                          # FIX 1: return -1 is now OUTSIDE the loop


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
    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                return True
    # Vertical
    for col in range(COLS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == player for i in range(4)):
                return True
    # Diagonal /
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if all(board[row + i][col + i] == player for i in range(4)):
                return True
    # Diagonal \
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if all(board[row - i][col + i] == player for i in range(4)):
                return True
    return False


def get_winning_cells(board, player):
    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            cells = [(row, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    # Vertical
    for col in range(COLS):
        for row in range(ROWS - 3):
            cells = [(row + i, col) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    # Diagonal /                       FIX 2: was range(3, ROWS), correct is range(ROWS - 3)
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            cells = [(row + i, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    # Diagonal \
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            cells = [(row - i, col + i) for i in range(4)]
            if all(board[r][c] == player for r, c in cells):
                return cells
    return []


def is_terminal(board):
    return (
        check_winner(board, HUMAN)
        or check_winner(board, AI)
        or len(get_valid_columns(board)) == 0
    )

# SECTION 3 — AI LOGIC  (Minimax + Alpha-Beta Pruning)

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

    # Horizontal windows
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = board[row][col: col + 4]
            score += _score_window(window, AI)

    # Vertical windows
    for col in range(COLS):
        for row in range(ROWS - 3):
            window = [board[row + i][col] for i in range(4)]
            score += _score_window(window, AI)

    # Diagonal / windows
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [board[row + i][col + i] for i in range(4)]  # FIX 3: was 'windows'
            score += _score_window(window, AI)

    # Diagonal \ windows
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [board[row - i][col + i] for i in range(4)]
            score += _score_window(window, AI)

    return score


def _center_priority(col):
    return CENTER_COL - abs(col - CENTER_COL)


def minimax(board, depth, alpha, beta, maximising):
    valid_cols = get_valid_columns(board)

    # Base cases
    if is_terminal(board):
        if check_winner(board, AI):
            return None, WIN_SCORE * 1000 + depth
        if check_winner(board, HUMAN):
            return None, LOSE_SCORE * 1000 - depth
        return None, 0                             # FIX 4: was just 'return None'

    if depth == 0:
        return None, _evaluate_board(board)

    # FIX 5: was 'keys=' (TypeError), correct keyword is 'key='
    # Also negated so highest-priority column comes first
    ordered_cols = sorted(valid_cols, key=lambda c: -_center_priority(c))

    if maximising:
        best_score = float("-inf")
        best_col   = ordered_cols[0]
        for col in ordered_cols:
            drop_piece(board, col, AI)
            _, score = minimax(board, depth - 1, alpha, beta, False)
            undo_move(board, col)
            if score > best_score:
                best_score = score
                best_col   = col
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        return best_col, best_score

    else:
        best_score = float("inf")
        best_col   = ordered_cols[0]
        for col in ordered_cols:
            drop_piece(board, col, HUMAN)
            _, score = minimax(board, depth - 1, alpha, beta, True)
            undo_move(board, col)
            if score < best_score:
                best_score = score
                best_col   = col
            beta = min(beta, best_score)
            if alpha >= beta:
                break
        return best_col, best_score              # FIX 6: was (best_score, best_col)


def get_ai_move(board, depth=AI_DEPTH):
    # FIX 7: alpha was float("inf"), must be float("-inf")
    col, _ = minimax(board, depth, float("-inf"), float("inf"), True)
    return col


# SECTION 4 — DISPLAY

SYM = {EMPTY: ".", HUMAN: "O", AI: "X"}


def print_board(board, winning_cells=None):
    win_set = set(map(tuple, winning_cells)) if winning_cells else set()
    sep     = "  +" + "---+" * COLS

    print()
    print("    " + "   ".join(str(c) for c in range(COLS)))
    print(sep)
    for r in range(ROWS):
        row_str = "  |"
        for c in range(COLS):
            sym = "*" if (r, c) in win_set else SYM[board[r][c]]
            row_str += f" {sym} |"
        print(row_str)
    print(sep)
    print()


def print_header():
    print()
    print("=" * 50)
    print("    CONNECT-4  |  Human (O) vs AI (X)")
    print("=" * 50)
    print("  Enter a column number (0-6) to drop your piece.")
    print("  First to get 4 in a row wins!")
    print("=" * 50)



# SECTION 5 — GAME RUNNER

def get_human_column(board):
    valid = get_valid_columns(board)
    while True:
        try:
            raw = input("  Your move - enter column (0-6): ").strip()
            col = int(raw)
            if col in valid:
                return col
            elif 0 <= col < COLS:
                print(f"  Column {col} is full. Try one of: {valid}")
            else:
                print(f"  Invalid. Choose from: {valid}")
        except ValueError:
            print("  Please enter a number between 0 and 6.")
        except (EOFError, KeyboardInterrupt):
            print("\n  Game interrupted. Goodbye!")
            sys.exit(0)


def play_game(depth=AI_DEPTH):
    board          = create_board()
    current_player = HUMAN
    game_over      = False

    print_header()
    print_board(board)

    # FIX 8: entire game loop was missing — added while loop so turns alternate properly
    while not game_over:

        if current_player == HUMAN:
            col = get_human_column(board)
            drop_piece(board, col, HUMAN)
            print(f"\n  You played column {col}.")
            print_board(board)

            if check_winner(board, HUMAN):
                winning = get_winning_cells(board, HUMAN)
                print_board(board, winning)
                print("  ★  Congratulations - You Win!  ★")
                game_over = True

            elif not get_valid_columns(board):
                print("  It's a draw! Well played.")
                game_over = True

            else:
                current_player = AI

        else:
            print(f"  AI is thinking (depth={depth})...")
            col = get_ai_move(board, depth)
            drop_piece(board, col, AI)
            print(f"  AI drops in column {col}.")
            print_board(board)

            if check_winner(board, AI):
                winning = get_winning_cells(board, AI)
                print_board(board, winning)
                print("  ✗  AI wins! Better luck next time.")
                game_over = True

            elif not get_valid_columns(board):
                print("  It's a draw!")
                game_over = True

            else:
                current_player = HUMAN

    print()
    try:
        again = input("  Play again? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        again = "n"

    if again == "y":
        play_game(depth)
    else:
        print("  Thanks for playing. Goodbye!")


# MAIN
if __name__ == "__main__":
    depth = AI_DEPTH
    if len(sys.argv) > 1:
        try:
            d = int(sys.argv[1])
            if 1 <= d <= 10:
                depth = d
                print(f"  AI search depth set to {depth}.")
            else:
                print("  Depth must be 1-10. Using default (5).")
        except ValueError:
            print("  Invalid argument. Using default depth (5).")
    play_game(depth)