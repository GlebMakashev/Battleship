import os, random, threading
import tkinter as tk
from tkinter import messagebox

BG_MAIN = "#070a13"         
FG_TEXT = "#ffffff"         
ACCENT_BLUE = "#38bdf8"     
ACCENT_DARK_BLUE = "#1e293b" 
BG_EMPTY_CELL = "#0f172a"   
COLOR_EASY = "#4ade80"      
COLOR_MEDIUM = "#fb923c"    
COLOR_HARD = "#f87171"      
COLOR_SHIP = "#334155"      

class SeaBattleGame:
    def __init__(self, root, difficulty):
        self.root = root
        self.difficulty = difficulty
        self.root.title("Морской Бой против ИИ")
        self.root.configure(bg=BG_MAIN)
        
        self.player_field = []
        self.computer_field = []
        for _ in range(10):
            p_row = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            c_row = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            self.player_field.append(list(p_row))
            self.computer_field.append(list(c_row))
        
        self.player_buttons = [[None] * 10 for _ in range(10)]
        self.computer_buttons = [[None] * 10 for _ in range(10)]
        
        self.score = 0
        self.last_hit = None  
        
        self.create_interface()
        self.generate_fleet(self.player_field)
        self.generate_fleet(self.computer_field)
        self.show_player_ships()

    def create_interface(self):
        title_label = tk.Label(self.root, text="МОРСКОЙ БОЙ", font=("Segoe UI", 22, "bold"), fg=ACCENT_BLUE, bg=BG_MAIN)
        title_label.pack(pady=5)
        
        self.score_label = tk.Label(self.root, text=f"ОЧКИ: {self.score}", font=("Segoe UI", 14, "bold"), fg="#f59e0b", bg=BG_MAIN)
        self.score_label.pack(pady=5)
        
        fields_frame = tk.Frame(self.root, bg=BG_MAIN)
        fields_frame.pack(padx=20, pady=5)
        
        player_frame = tk.Frame(fields_frame, bg=BG_MAIN)
        player_frame.pack(side=tk.LEFT, padx=30)
        tk.Label(player_frame, text="ВАШ ФЛОТ", font=("Segoe UI", 12, "bold"), fg=FG_TEXT, bg=BG_MAIN).pack(pady=5)
        self.draw_grid(player_frame, is_player=True)
        
        computer_frame = tk.Frame(fields_frame, bg=BG_MAIN)
        computer_frame.pack(side=tk.LEFT, padx=30)
        tk.Label(computer_frame, text="РАДАР ВРАГА", font=("Segoe UI", 12, "bold"), fg=ACCENT_BLUE, bg=BG_MAIN).pack(pady=5)
        self.draw_grid(computer_frame, is_player=False)
        
        self.turn_label = tk.Label(self.root, text="Ваш ход", font=("Segoe UI", 14, "bold"), fg=COLOR_EASY, bg=BG_MAIN)
        self.turn_label.pack(pady=5)
        
        self.status_label = tk.Label(self.root, text="", font=("Segoe UI", 12, "bold"), fg="#94a3b8", bg=BG_MAIN)
        self.status_label.pack(pady=5)

    def draw_grid(self, parent_frame, is_player):
        grid_frame = tk.Frame(parent_frame, bg=BG_MAIN)
        grid_frame.pack()
        letters = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", "К"]
        
        for col_idx, letter in enumerate(letters, 1):
            tk.Label(grid_frame, text=letter, font=("Segoe UI", 10, "bold"), fg=ACCENT_BLUE, bg=BG_MAIN, width=3).grid(row=0, column=col_idx)
            
        for row_idx in range(10):
            tk.Label(grid_frame, text=str(row_idx + 1), font=("Segoe UI", 10, "bold"), fg=ACCENT_BLUE, bg=BG_MAIN, width=3).grid(row=row_idx + 1, column=0)
            for col_idx in range(10):
                border_color = BG_MAIN if is_player else ACCENT_BLUE
                btn = tk.Button(
                    grid_frame, bg=BG_EMPTY_CELL, fg=FG_TEXT, font=("Segoe UI", 10, "bold"), width=3, height=1, bd=1, 
                    relief="solid", highlightbackground=border_color, activebackground=ACCENT_BLUE
                )
                btn.grid(row=row_idx + 1, column=col_idx + 1, padx=1, pady=1)
                if not is_player:
                    btn.config(command=lambda r=row_idx, c=col_idx: self.player_shoot(r, c))
                    self.computer_buttons[row_idx][col_idx] = btn
                else:
                    self.player_buttons[row_idx][col_idx] = btn
    def can_place_ship(self, field, row, col, size, direction):
        for i in range(size):
            r = row + (i if direction == "vertical" else 0)
            c = col + (0 if direction == "vertical" else i)
            if r < 0 or r >= 10 or c < 0 or c >= 10: return False
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    check_r, check_c = r + dr, c + dc
                    if 0 <= check_r < 10 and 0 <= check_c < 10:
                        if field[check_r][check_c] != 0: return False
        return True

    def generate_fleet(self, field):
        ship_sizes = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)
        for size in ship_sizes:
            placed = False
            while not placed:
                direction = random.choice(("horizontal", "vertical"))
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                if self.can_place_ship(field, row, col, size, direction):
                    for i in range(size):
                        r = row + (i if direction == "vertical" else 0)
                        c = col + (0 if direction == "vertical" else i)
                        field[r][c] = 1
                    placed = True

    def show_player_ships(self):
        for r in range(10):
            for c in range(10):
                if self.player_field[r][c] == 1:
                    self.player_buttons[r][c].config(bg=COLOR_SHIP)

    def get_computer_shot_coords(self):
        if self.difficulty == "hard" and random.random() < 0.25:
            targets = []
            for r in range(10):
                for c in range(10):
                    if self.player_field[r][c] == 1: targets.append((r, c))
            if targets: return random.choice(targets)

        if (self.difficulty == "medium" or self.difficulty == "hard") and self.last_hit:
            r, c = self.last_hit
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < 10 and 0 <= nc < 10 and (self.player_field[nr][nc] == 0 or self.player_field[nr][nc] == 1):
                    return nr, nc

        if self.difficulty == "hard":
            cells = []
            for r in range(10):
                for c in range(10):
                    if (r + c) % 2 == 0 and (self.player_field[r][c] == 0 or self.player_field[r][c] == 1):
                        cells.append((r, c))
            if cells: return random.choice(cells)

        while True:
            row, col = random.randint(0, 9), random.randint(0, 9)
            if self.player_field[row][col] == 0 or self.player_field[row][col] == 1: return row, col

    def computer_turn(self):
        while True:
            row, col = self.get_computer_shot_coords()
            btn = self.player_buttons[row][col]
            
            if self.player_field[row][col] == 1:
                btn.config(bg=COLOR_HARD, text="💥", fg=FG_TEXT)
                self.player_field[row][col] = 3
                self.last_hit = (row, col)
                self.status_label.config(text="Попал", fg=COLOR_HARD)
                continue
            else:
                btn.config(bg=ACCENT_DARK_BLUE, text="✕", fg="#64748b")
                self.player_field[row][col] = 2
                # ИСПРАВЛЕНО: Теперь пишет четко "Не попал"
                self.status_label.config(text="Не попал", fg="#94a3b8")
                
                self.turn_label.config(text="Ваш ход", fg=COLOR_EASY)
                self.enable_computer_field(True, show_radar=True)
                break

    def enable_computer_field(self, enable, show_radar=False):
        state_mode = tk.NORMAL if enable else tk.DISABLED
        border_color = ACCENT_BLUE if (enable and show_radar) else ACCENT_DARK_BLUE
        for r in range(10):
            for c in range(10):
                if self.computer_field[r][c] == 0 or self.computer_field[r][c] == 1:
                    self.computer_buttons[r][c].config(state=state_mode, highlightbackground=border_color)

    def player_shoot(self, row, col):
        btn = self.computer_buttons[row][col]
        if self.computer_field[row][col] == 1:
            btn.config(bg=COLOR_HARD, text="💥", fg=FG_TEXT, state=tk.DISABLED)
            self.computer_field[row][col] = 3
            self.score += 100
            self.score_label.config(text=f"ОЧКИ: {self.score}")
            self.status_label.config(text="Попал", fg=COLOR_EASY)
        else:
            btn.config(bg=ACCENT_DARK_BLUE, text="✕", fg="#64748b", state=tk.DISABLED)
            self.computer_field[row][col] = 2
            self.status_label.config(text="Не попал", fg="#94a3b8")
            
            self.turn_label.config(text="Ходит противник", fg=COLOR_MEDIUM)
            self.enable_computer_field(False, show_radar=False)
            self.root.after(1200, self.computer_turn)

def start_selected_game(lvl):
    start_window.destroy()
    game_window = tk.Tk()
    app = SeaBattleGame(game_window, lvl)
    game_window.mainloop()

start_window = tk.Tk()
start_window.title("Настройки боя")
start_window.geometry("360x340")
start_window.configure(bg=BG_MAIN)

tk.Label(start_window, text="МОРСКОЙ БОЙ", font=("Segoe UI", 20, "bold"), fg=ACCENT_BLUE, bg=BG_MAIN).pack(pady=25)
tk.Label(start_window, text="Выберите уровень сложности ИИ:", font=("Segoe UI", 11), fg=FG_TEXT, bg=BG_MAIN).pack(pady=5)

tk.Button(start_window, text="Легкий (Easy)", font=("Segoe UI", 11, "bold"), bg=COLOR_EASY, fg=BG_MAIN, width=22, bd=0, pady=6, command=lambda: start_selected_game("easy")).pack(pady=8)
tk.Button(start_window, text="Средний (Medium)", font=("Segoe UI", 11, "bold"), bg=COLOR_MEDIUM, fg=BG_MAIN, width=22, bd=0, pady=6, command=lambda: start_selected_game("medium")).pack(pady=8)
tk.Button(start_window, text="Сложный (Hard)", font=("Segoe UI", 11, "bold"), bg=COLOR_HARD, fg=BG_MAIN, width=22, bd=0, pady=6, command=lambda: start_selected_game("hard")).pack(pady=8)

start_window.mainloop()
