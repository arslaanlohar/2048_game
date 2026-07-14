"""
2048 Game — Python + Tkinter
-----------------------------
Controls: Arrow keys (Up/Down/Left/Right) to move tiles.
Merge equal tiles to reach 2048 (and beyond!).

Run with: python game_2048.py
"""

import tkinter as tk
import random

GRID_SIZE = 4
CELL_SIZE = 100
CELL_PAD = 10

# ---- Dark theme, blue tile palette ----
APP_BG = "#0d1117"           # overall window background
WINDOW_BG = "#161b22"        # board frame background
EMPTY_CELL_BG = "#1f2733"    # empty cell background
PANEL_BG = "#12233d"         # score/best boxes

TILE_COLORS = {
    0: "#1f2733",
    2: "#1b3a5c",
    4: "#1c4a73",
    8: "#155d8a",
    16: "#0e73a3",
    32: "#0089bd",
    64: "#00a0d6",
    128: "#00b7e8",
    256: "#25c9f0",
    512: "#4fdcff",
    1024: "#7ce8ff",
    2048: "#aef4ff",
}
TILE_COLORS_DEFAULT = "#e0fbff"  # for values beyond 2048

TEXT_COLORS = {
    2: "#eaf6ff",
    4: "#eaf6ff",
    8: "#eaf6ff",
    16: "#eaf6ff",
    32: "#eaf6ff",
    64: "#eaf6ff",
    128: "#0d1117",
    256: "#0d1117",
    512: "#0d1117",
    1024: "#0d1117",
    2048: "#0d1117",
}
TEXT_COLOR_DEFAULT = "#0d1117"

FONT_NAME = "Helvetica"


class Game2048:
    def __init__(self, master):
        self.master = master
        self.master.title("2048")
        self.master.resizable(False, False)

        self.score = 0
        self.best_score = 0

        # Top bar: title + score
        self.top_frame = tk.Frame(master, bg=APP_BG)
        self.top_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = tk.Label(
            self.top_frame, text="2048", font=(FONT_NAME, 36, "bold"),
            bg=APP_BG, fg="#4fdcff"
        )
        title_label.pack(side="left")

        score_frame = tk.Frame(self.top_frame, bg=PANEL_BG, width=90, height=55,
                                highlightbackground="#25c9f0", highlightthickness=1)
        score_frame.pack(side="right", padx=5)
        score_frame.pack_propagate(False)
        tk.Label(score_frame, text="SCORE", font=(FONT_NAME, 10, "bold"),
                 bg=PANEL_BG, fg="#7ce8ff").pack(pady=(5, 0))
        self.score_label = tk.Label(score_frame, text="0", font=(FONT_NAME, 16, "bold"),
                                     bg=PANEL_BG, fg="white")
        self.score_label.pack()

        best_frame = tk.Frame(self.top_frame, bg=PANEL_BG, width=90, height=55,
                               highlightbackground="#25c9f0", highlightthickness=1)
        best_frame.pack(side="right", padx=5)
        best_frame.pack_propagate(False)
        tk.Label(best_frame, text="BEST", font=(FONT_NAME, 10, "bold"),
                 bg=PANEL_BG, fg="#7ce8ff").pack(pady=(5, 0))
        self.best_label = tk.Label(best_frame, text="0", font=(FONT_NAME, 16, "bold"),
                                    bg=PANEL_BG, fg="white")
        self.best_label.pack()

        # Instructions / New game button
        control_frame = tk.Frame(master, bg=APP_BG)
        control_frame.pack(fill="x", padx=20)

        tk.Label(control_frame, text="Join the tiles, get to 2048!",
                 font=(FONT_NAME, 12), bg=APP_BG, fg="#8ea3b8").pack(side="left")

        new_game_btn = tk.Button(control_frame, text="New Game", font=(FONT_NAME, 11, "bold"),
                                  bg="#0089bd", fg="white", relief="flat",
                                  activebackground="#00a0d6", activeforeground="white",
                                  command=self.restart, padx=10, pady=5, cursor="hand2")
        new_game_btn.pack(side="right", pady=10)

        # Game board canvas (also hosts the game-over overlay)
        board_size = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PAD
        self.board_size = board_size
        self.canvas = tk.Canvas(master, width=board_size, height=board_size,
                                 bg=WINDOW_BG, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # Status label for win messages (below the board)
        self.status_label = tk.Label(master, text="", font=(FONT_NAME, 14, "bold"),
                                      bg=APP_BG, fg="#4fdcff")
        self.status_label.pack(pady=(0, 15))

        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.tiles = {}  # (row, col) -> (rect_id, text_id)
        self.game_over = False
        self.won = False

        self.master.bind("<Up>", lambda e: self.move("Up"))
        self.master.bind("<Down>", lambda e: self.move("Down"))
        self.master.bind("<Left>", lambda e: self.move("Left"))
        self.master.bind("<Right>", lambda e: self.move("Right"))
        self.master.bind("<w>", lambda e: self.move("Up"))
        self.master.bind("<s>", lambda e: self.move("Down"))
        self.master.bind("<a>", lambda e: self.move("Left"))
        self.master.bind("<d>", lambda e: self.move("Right"))

        self.draw_empty_grid()
        self.start_game()

    # ---------- Drawing ----------

    def cell_coords(self, row, col):
        x0 = CELL_PAD + col * (CELL_SIZE + CELL_PAD)
        y0 = CELL_PAD + row * (CELL_SIZE + CELL_PAD)
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        return x0, y0, x1, y1

    def draw_empty_grid(self):
        self.canvas.delete("all")
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x0, y0, x1, y1 = self.cell_coords(row, col)
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=EMPTY_CELL_BG,
                                              outline=WINDOW_BG, width=0)

    def draw_tiles(self):
        self.canvas.delete("tile")
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = self.grid[row][col]
                if value == 0:
                    continue
                x0, y0, x1, y1 = self.cell_coords(row, col)
                color = TILE_COLORS.get(value, TILE_COLORS_DEFAULT)
                text_color = TEXT_COLORS.get(value, TEXT_COLOR_DEFAULT)
                font_size = 32 if value < 100 else (28 if value < 1000 else 22)
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="",
                                              tags="tile")
                self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(value),
                                         font=(FONT_NAME, font_size, "bold"),
                                         fill=text_color, tags="tile")

    def draw_game_over_overlay(self):
        """Draw a bold, unmissable red GAME OVER banner directly on the canvas."""
        size = self.board_size
        # dim overlay across the whole board
        self.canvas.create_rectangle(0, 0, size, size, fill="#000000",
                                      stipple="gray50", outline="", tags="overlay")
        self.canvas.create_text(size / 2, size / 2 - 20, text="GAME OVER",
                                 font=(FONT_NAME, 34, "bold"), fill="#ff3b3b",
                                 tags="overlay")
        self.canvas.create_text(size / 2, size / 2 + 25, text="Click 'New Game' to try again",
                                 font=(FONT_NAME, 13, "bold"), fill="#ffffff",
                                 tags="overlay")

    def update_score_labels(self):
        self.score_label.config(text=str(self.score))
        if self.score > self.best_score:
            self.best_score = self.score
        self.best_label.config(text=str(self.best_score))

    # ---------- Game logic ----------

    def start_game(self):
        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0
        self.game_over = False
        self.won = False
        self.status_label.config(text="")
        self.canvas.delete("overlay")
        self.add_random_tile()
        self.add_random_tile()
        self.draw_tiles()
        self.update_score_labels()

    def restart(self):
        self.start_game()

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                        if self.grid[r][c] == 0]
        if not empty_cells:
            return
        r, c = random.choice(empty_cells)
        self.grid[r][c] = 4 if random.random() < 0.1 else 2

    def compress(self, row):
        """Slide non-zero values to the left, keep order."""
        new_row = [v for v in row if v != 0]
        new_row += [0] * (GRID_SIZE - len(new_row))
        return new_row

    def merge(self, row):
        """Merge equal adjacent values moving left, add to score."""
        for i in range(GRID_SIZE - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                self.score += row[i]
                if row[i] == 2048:
                    self.won = True
                row[i + 1] = 0
        return row

    def move_row_left(self, row):
        row = self.compress(row)
        row = self.merge(row)
        row = self.compress(row)
        return row

    def move(self, direction):
        if self.game_over:
            return

        old_grid = [row[:] for row in self.grid]

        if direction == "Left":
            self.grid = [self.move_row_left(row) for row in self.grid]

        elif direction == "Right":
            self.grid = [self.move_row_left(row[::-1])[::-1] for row in self.grid]

        elif direction == "Up":
            transposed = self.transpose(self.grid)
            transposed = [self.move_row_left(row) for row in transposed]
            self.grid = self.transpose(transposed)

        elif direction == "Down":
            transposed = self.transpose(self.grid)
            transposed = [self.move_row_left(row[::-1])[::-1] for row in transposed]
            self.grid = self.transpose(transposed)

        moved = old_grid != self.grid

        if moved:
            self.add_random_tile()
            self.draw_tiles()
            self.update_score_labels()

            if self.won:
                self.status_label.config(text="🎉 You reached 2048! Keep going or start a new game.",
                                          fg="#4fdcff")

            if not self.has_moves_left():
                self.game_over = True
                self.status_label.config(text="")
                self.draw_game_over_overlay()

    def transpose(self, grid):
        return [list(row) for row in zip(*grid)]

    def has_moves_left(self):
        # Any empty cell?
        for row in self.grid:
            if 0 in row:
                return True
        # Any adjacent equal cells (horizontally or vertically)?
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                value = self.grid[r][c]
                if c + 1 < GRID_SIZE and self.grid[r][c + 1] == value:
                    return True
                if r + 1 < GRID_SIZE and self.grid[r + 1][c] == value:
                    return True
        return False


def main():
    root = tk.Tk()
    root.configure(bg=APP_BG)
    Game2048(root)
    root.mainloop()


if __name__ == "__main__":
    main()
