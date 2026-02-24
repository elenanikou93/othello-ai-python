import copy
import tkinter as tk
from tkinter import messagebox

class Othello:
    def __init__(self, human_player="X", max_depth=3):
        # Game logic
        self.board = [[" " for _ in range(8)] for _ in range(8)]
        self.board[3][3] = "O"
        self.board[3][4] = "X"
        self.board[4][3] = "X"
        self.board[4][4] = "O"

        self.human_player = human_player
        self.ai_player = "O" if human_player == "X" else "X"
        self.current_player = "X"  # πάντα ξεκινάμε με X
        self.max_depth = max_depth

        # Χρώματα ανάλογα με τον παίκτη
        self.human_color = "black" if self.human_player == "X" else "white"
        self.ai_color = "white" if self.human_player == "X" else "black"

        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Othello")
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.score_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.score_label.grid(row=0, column=0, columnspan=8)
        
        for r in range(8):
            for c in range(8):
                btn = tk.Button(self.root, width=4, height=2, command=lambda r=r, c=c: self.player_move(r, c))
                btn.grid(row=r+1, column=c)
                self.buttons[r][c] = btn

        self.update_board()

        # Αν ο human είναι O, η AI (X) παίζει πρώτη
        if self.human_player == "O":
            self.root.after(200, self.computer_turn)

    # --- Game logic functions ---
    def count_score(self):
        x_count = sum(row.count("X") for row in self.board)
        o_count = sum(row.count("O") for row in self.board)
        return x_count, o_count

    def is_valid_move(self, row, col, player):
        if not (0 <= row < 8 and 0 <= col < 8) or self.board[row][col] != " ":
            return False
        opponent = "O" if player == "X" else "X"
        directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            has_opponent_piece = False
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == opponent:
                    has_opponent_piece = True
                elif self.board[r][c] == player:
                    if has_opponent_piece:
                        return True
                    break
                else:
                    break
                r += d_row
                c += d_col
        return False

    def flip_pieces(self, row, col, player):
        opponent = "O" if player == "X" else "X"
        directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        self.board[row][col] = player
        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            flip_positions = []
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == opponent:
                    flip_positions.append((r,c))
                elif self.board[r][c] == player:
                    for fr, fc in flip_positions:
                        self.board[fr][fc] = player
                    break
                else:
                    break
                r += d_row
                c += d_col

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def has_valid_moves(self, player):
        for r in range(8):
            for c in range(8):
                if self.is_valid_move(r, c, player):
                    return True
        return False

    def game_over(self):
        return not self.has_valid_moves("X") and not self.has_valid_moves("O")

    def evaluate(self):
        x_score, o_score = self.count_score()
        return x_score - o_score

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.game_over():
            return self.evaluate(), None
        best_move = None
        player = self.current_player
        if maximizing_player:
            max_eval = float('-inf')
            for r in range(8):
                for c in range(8):
                    if self.is_valid_move(r, c, player):
                        board_copy = copy.deepcopy(self.board)
                        self.flip_pieces(r, c, player)
                        self.switch_player()
                        eval_score, _ = self.minimax(depth-1, alpha, beta, False)
                        self.board = board_copy
                        self.switch_player()
                        if eval_score > max_eval:
                            max_eval = eval_score
                            best_move = (r, c)
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for r in range(8):
                for c in range(8):
                    if self.is_valid_move(r, c, player):
                        board_copy = copy.deepcopy(self.board)
                        self.flip_pieces(r, c, player)
                        self.switch_player()
                        eval_score, _ = self.minimax(depth-1, alpha, beta, True)
                        self.board = board_copy
                        self.switch_player()
                        if eval_score < min_eval:
                            min_eval = eval_score
                            best_move = (r, c)
                        beta = min(beta, eval_score)
                        if beta <= alpha:
                            break
            return min_eval, best_move

    def computer_move(self):
        _, move = self.minimax(self.max_depth, float('-inf'), float('inf'), True)
        return move

    # --- GUI functions ---
    def update_board(self):
        for r in range(8):
            for c in range(8):
                btn = self.buttons[r][c]
                if self.board[r][c] == self.human_player:
                    btn.config(bg=self.human_color, state="disabled")
                elif self.board[r][c] == self.ai_player:
                    btn.config(bg=self.ai_color, state="disabled")
                else:
                    btn.config(bg="blue", state="normal")

        # Σκορ σωστά για human/AI
        x_score, o_score = self.count_score()
        human_score = x_score if self.human_player == "X" else o_score
        ai_score = o_score if self.human_player == "X" else x_score
        self.score_label.config(text=f"Score: You = {human_score} | AI = {ai_score}")

    def player_move(self, row, col):
        if self.is_valid_move(row, col, self.human_player):
            self.flip_pieces(row, col, self.human_player)
            self.switch_player()
            self.update_board()
            self.root.after(200, self.computer_turn)

    def computer_turn(self):
        if not self.game_over() and self.has_valid_moves(self.ai_player):
            move = self.computer_move()
            if move:
                r, c = move
                self.flip_pieces(r, c, self.ai_player)
                self.switch_player()
                self.update_board()
        if self.game_over():
            x_score, o_score = self.count_score()
            if x_score > o_score:
                messagebox.showinfo("Game Over", f"X wins! {x_score} - {o_score}")
            elif o_score > x_score:
                messagebox.showinfo("Game Over", f"O wins! {o_score} - {x_score}")
            else:
                messagebox.showinfo("Game Over", f"It's a tie! {x_score} - {o_score}")

    def run(self):
        self.root.mainloop()


# --- GUI setup for player choice and depth ---
def start_othello():
    def start_game():
        human_player = piece_var.get()
        max_depth = int(depth_var.get())
        if human_player not in ["X", "O"]:
            messagebox.showerror("Error", "Choose X or O!")
            return
        if max_depth < 1 or max_depth > 3:
            messagebox.showerror("Error", "Depth must be 1, 2, or 3!")
            return
        setup_root.destroy()
        game = Othello(human_player=human_player, max_depth=max_depth)
        game.run()

    setup_root = tk.Tk()
    setup_root.title("Othello Setup")

    tk.Label(setup_root, text="Choose your piece:", font=("Arial", 12)).pack(padx=100, pady=10)
    piece_var = tk.StringVar(value="X")
    tk.Radiobutton(setup_root, text="X (Black)", variable=piece_var, value="X", font=("Arial", 10)).pack()
    tk.Radiobutton(setup_root, text="O (White)", variable=piece_var, value="O", font=("Arial", 10)).pack()

    tk.Label(setup_root, text="Select AI max depth (1-3):", font=("Arial", 12)).pack(padx=5, pady=10)
    depth_var = tk.Spinbox(setup_root, from_=1, to=3, width=7)
    depth_var.pack()

    tk.Button(setup_root, text="Start Game", font=("Arial", 12), command=start_game).pack(pady=30)
    setup_root.mainloop()


if __name__ == "__main__":
    start_othello()
