import customtkinter as ctk
import random
import numpy as np

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def expert_move(n):
    return 1 if n % 3 == 0 else min(2, n % 3)


# Learning AI using Q-Learning

class QLearning:
    def __init__(self):
        self.Q_table = np.zeros((2, 11))
        self.epsilon = 0.1
        self.alpha = 0.3

    def get_learning_action(self, state):
        if state <= 0:
            return 0
        if state == 1:
            return 1
        a = random.randint(0, 1)
        if random.uniform(0, 1) > self.epsilon and self.Q_table[0, state] != self.Q_table[1, state]:
            a = np.argmax(self.Q_table[:, state])
        return min(a + 1, min(2, state))

    def q_learning_step(self, prev_state, prev_action, state, r):
        prev_action_id = prev_action - 1
        if prev_action_id >= 0 and state >= 0:
            best_action_id = np.argmax(self.Q_table[:, state])
            self.Q_table[prev_action_id, prev_state] += self.alpha * (
                    r + self.Q_table[best_action_id, state] - self.Q_table[prev_action_id, prev_state])


class NimGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simple Game NIM")
        self.geometry("600x400")

        self.pile_size = 10
        self.current_player = "human"
        self.game_active = False
        self.rl_player = QLearning()

        self.configure_grid()
        self.create_widgets()
        self.start_new_game()

    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_widgets(self):
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="nsew")

        self.title_label = ctk.CTkLabel(self.header, text="NIM Game", font=("Arial Black", 18), text_color="#00ff88")
        self.title_label.pack(side=ctk.LEFT, padx=10)

        self.mode_selector = ctk.CTkSegmentedButton(self.header, values=["Random", "Expert", "Learning AI"],
                                                    command=self.start_new_game)
        self.mode_selector.pack(side=ctk.RIGHT, padx=10)
        self.mode_selector.set("Random")

        self.canvas = ctk.CTkCanvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        self.btn1 = ctk.CTkButton(self.control_frame, text="TAKE 1", command=lambda: self.human_move(1),
                                  fg_color="#1e90ff")
        self.btn2 = ctk.CTkButton(self.control_frame, text="TAKE 2", command=lambda: self.human_move(2),
                                  fg_color="#00ff88")
        self.btn1.pack(side=ctk.LEFT, padx=10)
        self.btn2.pack(side=ctk.LEFT, padx=10)

        self.status_bar = ctk.CTkLabel(self, text="Ready to play", anchor="w", font=("Arial", 12), text_color="#aaaaaa")
        self.status_bar.grid(row=3, column=0, sticky="ew")

    def draw_stones(self):
        self.canvas.delete("all")
        stone_size = 30
        spacing = 40
        start_x = (600 - (self.pile_size * spacing)) // 2
        color = "#0099ff"
        for i in range(self.pile_size):
            x = start_x + i * spacing
            y = 150
            self.canvas.create_oval(x, y, x + stone_size, y + stone_size, fill=color, outline="#666666", width=2)

    def start_new_game(self):
        self.pile_size = 10
        self.current_player = random.choice(["human", "computer"])
        self.game_active = True
        self.draw_stones()
        self.update_status()

        if self.current_player == "computer":
            self.after(1000, self.computer_move)

    def update_status(self):
        self.status_bar.configure(
            text=f"Remaining stones: {self.pile_size} | Round: {self.current_player.capitalize()}")

    def human_move(self, n):
        if self.game_active and self.current_player == "human" and n <= self.pile_size:
            self.pile_size -= n
            self.draw_stones()
            self.check_winner()
            self.current_player = "computer"
            self.update_status()
            self.after(1000, self.computer_move)

    def computer_move(self):
        if not self.game_active or self.pile_size <= 0:
            return

        mode = self.mode_selector.get().lower()
        prev_state = self.pile_size

        if mode == "random":
            move = random.choice([1, 2]) if self.pile_size > 1 else 1
        elif mode == "expert":
            move = expert_move(self.pile_size)
        else:
            move = self.rl_player.get_learning_action(self.pile_size)

        move = max(1, min(move, 2, self.pile_size))

        self.pile_size -= move
        self.draw_stones()

        if mode == "learning":
            reward = -1 if self.pile_size == 0 else 0
            self.rl_player.q_learning_step(prev_state, move, self.pile_size, reward)

        self.check_winner()
        self.current_player = "human"
        self.update_status()

    def check_winner(self):
        if self.pile_size == 0:
            self.game_active = False
            winner = "AI" if self.current_player == "computer" else "Player"
            self.show_victory(winner)

    def show_victory(self, winner):
        victory_win = ctk.CTkToplevel(self)
        victory_win.title("Victory !")

        x = self.winfo_x()
        y = self.winfo_y()
        width = self.winfo_width()
        height = self.winfo_height()

        toplevel_width = 300
        toplevel_height = 150
        x_pos = x + (width - toplevel_width) // 2
        y_pos = y + (height - toplevel_height) // 2

        victory_win.geometry(f"{toplevel_width}x{toplevel_height}+{x_pos}+{y_pos}")

        victory_win.attributes("-topmost", True)

        ctk.CTkLabel(victory_win, text=f"🏆 {winner} has won !", font=("Impact", 20), text_color="#ffd700").pack(pady=20)
        ctk.CTkButton(victory_win, text="New game", command=lambda: [victory_win.destroy(), self.start_new_game()],
                      fg_color="#00cc00").pack(pady=10)


if __name__ == "__main__":
    app = NimGUI()
    app.mainloop()
