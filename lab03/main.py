import tkinter as tk
from tkinter import ttk
import numpy as np
import random
from enum import Enum


class CellState(Enum):
    EMPTY = 0
    TREE = 1
    BURNING = 2


class ForestFireSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Лесные пожары - Клеточный автомат")

        self.grid_size = 50
        self.cell_size = 7
        self.f_prob = 0.0001
        self.p_prob = 0.01

        self.wind_direction = "right"
        self.wind_strength = 1.5
        self.temperature = 25.0
        self.humidity = 50.0

        self.colors = {
            CellState.EMPTY: "#8B7355",
            CellState.TREE: "#228B22",
            CellState.BURNING: "#FF4500"
        }

        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        self.running = False
        self.update_delay = 100

        self.setup_ui()
        self.init_random_grid()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.canvas = tk.Canvas(canvas_frame,
                                width=self.grid_size * self.cell_size,
                                height=self.grid_size * self.cell_size,
                                bg="white")
        self.canvas.pack()

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="Старт", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Стоп", command=self.stop_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сброс", command=self.reset_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Шаг", command=self.simulation_step).pack(side=tk.LEFT, padx=5)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        params_frame = ttk.LabelFrame(bottom_frame, text="Параметры", padding="10")
        params_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(params_frame, text="Вероятность пожара (f):").pack(anchor=tk.W)
        f_controls_frame = ttk.Frame(params_frame)
        f_controls_frame.pack(fill=tk.X, pady=(0, 10))
        self.f_prob_var = tk.DoubleVar(value=self.f_prob)
        f_scale = ttk.Scale(f_controls_frame, from_=0.0001, to=0.01, variable=self.f_prob_var,
                            orient=tk.HORIZONTAL, command=self.update_f_prob)
        f_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.f_prob_label = ttk.Label(f_controls_frame, text=f"{self.f_prob:.4f}")
        self.f_prob_label.pack(side=tk.LEFT)

        ttk.Label(params_frame, text="Рост деревьев (p):").pack(anchor=tk.W)
        p_controls_frame = ttk.Frame(params_frame)
        p_controls_frame.pack(fill=tk.X)
        self.p_prob_var = tk.DoubleVar(value=self.p_prob)
        p_scale = ttk.Scale(p_controls_frame, from_=0.001, to=0.1, variable=self.p_prob_var,
                            orient=tk.HORIZONTAL, command=self.update_p_prob)
        p_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.p_prob_label = ttk.Label(p_controls_frame, text=f"{self.p_prob:.4f}")
        self.p_prob_label.pack(side=tk.LEFT)

        weather_frame = ttk.LabelFrame(bottom_frame, text="Погодные факторы", padding="10")
        weather_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(weather_frame, text="Направление ветра:").pack(anchor=tk.W)
        self.wind_dir_var = tk.StringVar(value=self.wind_direction)
        wind_combo = ttk.Combobox(weather_frame, textvariable=self.wind_dir_var,
                                  values=["right", "left", "up", "down"], state="readonly")
        wind_combo.pack(fill=tk.X, pady=(0, 10))
        wind_combo.bind("<<ComboboxSelected>>", self.update_wind_direction)

        ttk.Label(weather_frame, text="Сила ветра:").pack(anchor=tk.W)
        wind_strength_frame = ttk.Frame(weather_frame)
        wind_strength_frame.pack(fill=tk.X, pady=(0, 10))
        self.wind_strength_var = tk.DoubleVar(value=self.wind_strength)
        wind_scale = ttk.Scale(wind_strength_frame, from_=1.0, to=3.0, variable=self.wind_strength_var,
                               orient=tk.HORIZONTAL, command=self.update_wind_strength)
        wind_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.wind_strength_label = ttk.Label(wind_strength_frame, text=f"{self.wind_strength:.4f}")
        self.wind_strength_label.pack(side=tk.LEFT)

        ttk.Label(weather_frame, text="Температура (°C):").pack(anchor=tk.W)
        temp_frame = ttk.Frame(weather_frame)
        temp_frame.pack(fill=tk.X, pady=(0, 10))
        self.temp_var = tk.DoubleVar(value=self.temperature)
        temp_scale = ttk.Scale(temp_frame, from_=-10, to=50, variable=self.temp_var,
                               orient=tk.HORIZONTAL, command=self.update_temperature)
        temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.temp_label = ttk.Label(temp_frame, text=f"{self.temperature:.4f}")
        self.temp_label.pack(side=tk.LEFT)

        ttk.Label(weather_frame, text="Влажность (%):").pack(anchor=tk.W)
        humidity_frame = ttk.Frame(weather_frame)
        humidity_frame.pack(fill=tk.X)
        self.humidity_var = tk.DoubleVar(value=self.humidity)
        humidity_scale = ttk.Scale(humidity_frame, from_=0, to=100, variable=self.humidity_var,
                                   orient=tk.HORIZONTAL, command=self.update_humidity)
        humidity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.humidity_label = ttk.Label(humidity_frame, text=f"{self.humidity:.4f}")
        self.humidity_label.pack(side=tk.LEFT)

        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding="10")
        stats_frame.pack(fill=tk.X)

        self.stats_text = tk.StringVar()
        ttk.Label(stats_frame, textvariable=self.stats_text).pack()

    def init_random_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if random.random() < 0.4:
                    self.grid[i, j] = CellState.TREE.value
                else:
                    self.grid[i, j] = CellState.EMPTY.value

    def update_f_prob(self, value):
        self.f_prob = self.f_prob_var.get()
        self.f_prob_label.config(text=f"{self.f_prob:.4f}")

    def update_p_prob(self, value):
        self.p_prob = self.p_prob_var.get()
        self.p_prob_label.config(text=f"{self.p_prob:.4f}")

    def update_wind_direction(self, event):
        self.wind_direction = self.wind_dir_var.get()

    def update_wind_strength(self, value):
        self.wind_strength = self.wind_strength_var.get()
        self.wind_strength_label.config(text=f"{self.wind_strength:.4f}")

    def update_temperature(self, value):
        self.temperature = self.temp_var.get()
        self.temp_label.config(text=f"{self.temperature:.4f}")

    def update_humidity(self, value):
        self.humidity = self.humidity_var.get()
        self.humidity_label.config(text=f"{self.humidity:.4f}")

    def calculate_fire_spread_probability(self, dx, dy):
        prob = 1.0

        if self.temperature > 30:
            prob *= 1.5
        elif self.temperature > 20:
            prob *= 1.2
        elif self.temperature < 0:
            prob *= 0.5

        if self.humidity > 80:
            prob *= 0.3
        elif self.humidity > 60:
            prob *= 0.5
        elif self.humidity > 40:
            prob *= 0.8
        elif self.humidity < 20:
            prob *= 1.3

        wind_dirs = {
            "right": (0, 1),
            "left": (0, -1),
            "up": (-1, 0),
            "down": (1, 0)
        }

        wind_dx, wind_dy = wind_dirs[self.wind_direction]

        if dx * wind_dx > 0 or dy * wind_dy > 0:
            prob *= self.wind_strength
        elif dx * wind_dx < 0 or dy * wind_dy < 0:
            prob *= (2 - self.wind_strength)

        return max(0.1, min(2.0, prob))

    def simulation_step(self):
        new_grid = self.grid.copy()

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == CellState.BURNING.value:
                    new_grid[i, j] = CellState.EMPTY.value

                elif self.grid[i, j] == CellState.TREE.value:
                    burning_neighbor = False

                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size:
                                if self.grid[ni, nj] == CellState.BURNING.value:
                                    spread_prob = self.calculate_fire_spread_probability(di, dj)
                                    if random.random() < spread_prob * 0.3:
                                        burning_neighbor = True
                                        break
                        if burning_neighbor:
                            break

                    if burning_neighbor:
                        new_grid[i, j] = CellState.BURNING.value
                    else:
                        lightning_prob = self.f_prob
                        if self.temperature > 30 and self.humidity < 30:
                            lightning_prob *= 2.0
                        elif self.humidity > 70:
                            lightning_prob *= 0.5

                        if random.random() < lightning_prob:
                            new_grid[i, j] = CellState.BURNING.value

                elif self.grid[i, j] == CellState.EMPTY.value:
                    if random.random() < self.p_prob:
                        new_grid[i, j] = CellState.TREE.value

        self.grid = new_grid
        self.draw_grid()
        self.update_statistics()

        if self.running:
            self.root.after(self.update_delay, self.simulation_step)

    def draw_grid(self):
        self.canvas.delete("all")

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                state = CellState(self.grid[i, j])
                color = self.colors[state]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

        wind_x = self.grid_size * self.cell_size - 20
        wind_y = 20
        arrow_dirs = {
            "right": (wind_x, wind_y, wind_x + 15, wind_y),
            "left": (wind_x, wind_y, wind_x - 15, wind_y),
            "up": (wind_x, wind_y, wind_x, wind_y - 15),
            "down": (wind_x, wind_y, wind_x, wind_y + 15)
        }
        arrow = arrow_dirs[self.wind_direction]
        self.canvas.create_line(arrow[0], arrow[1], arrow[2], arrow[3],
                                arrow=tk.LAST, fill="black", width=5)

    def update_statistics(self):
        tree_count = np.sum(self.grid == CellState.TREE.value)
        burning_count = np.sum(self.grid == CellState.BURNING.value)
        empty_count = np.sum(self.grid == CellState.EMPTY.value)
        total = self.grid_size * self.grid_size

        self.stats_text.set(f"Деревья: {tree_count} ({tree_count / total * 100:.1f}%) | "
                            f"Горит: {burning_count} ({burning_count / total * 100:.1f}%) | "
                            f"Пусто: {empty_count} ({empty_count / total * 100:.1f}%)")

    def start_simulation(self):
        self.running = True
        self.simulation_step()

    def stop_simulation(self):
        self.running = False

    def reset_simulation(self):
        self.running = False
        self.init_random_grid()
        self.draw_grid()
        self.update_statistics()


def main():
    root = tk.Tk()
    app = ForestFireSimulation(root)
    app.draw_grid()
    app.update_statistics()
    root.mainloop()


if __name__ == "__main__":
    main()