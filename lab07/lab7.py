import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from scipy.linalg import eig
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Марковская модель погоды - Визуализация в реальном времени")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')

        self.states = [1, 2, 3]
        self.names = {1: "Ясно", 2: "Облачно", 3: "Пасмурно"}
        self.colors = {1: "#f1c40f", 2: "#95a5a6", 3: "#34495e"}
        self.icons = {1: "☀️", 2: "☁️", 3: "☁️🌧"}

        self.P = np.array([[-0.4, 0.3, 0.1], [0.4, -0.8, 0.4], [0.1, 0.4, -0.5]]) + np.eye(3)
        self.P = self.P / self.P.sum(axis=1, keepdims=True)

        eigvals, eigvecs = eig(self.P.T)
        self.pi = np.real(eigvecs[:, np.isclose(eigvals, 1)]).flatten()
        self.pi /= self.pi.sum()

        self.history = []
        self.current_state = 1
        self.simulation_running = False
        self.speed = 0.5
        self.days_to_simulate = 100

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_panel = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)

        title = tk.Label(control_panel, text="МАРКОВСКАЯ МОДЕЛЬ\nПОГОДЫ",
                         font=('Arial', 16, 'bold'), bg='#34495e', fg='white')
        title.pack(pady=20, padx=20)

        params_frame = tk.LabelFrame(control_panel, text="Параметры",
                                     font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        params_frame.pack(pady=10, padx=15, fill=tk.X)

        tk.Label(params_frame, text="Количество дней:", bg='#34495e', fg='white').pack(pady=5)
        self.days_entry = tk.Entry(params_frame, width=10, font=('Arial', 12))
        self.days_entry.insert(0, "100")
        self.days_entry.pack(pady=5)

        tk.Label(params_frame, text="Скорость (дней/сек):", bg='#34495e', fg='white').pack(pady=5)
        self.speed_scale = tk.Scale(params_frame, from_=0.1, to=5, orient=tk.HORIZONTAL,
                                    resolution=0.1, bg='#34495e', fg='white', length=150)
        self.speed_scale.set(1)
        self.speed_scale.pack(pady=5)

        btn_frame = tk.Frame(control_panel, bg='#34495e')
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(btn_frame, text="▶ СТАРТ", command=self.start_simulation,
                                   bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                   width=12, height=2)
        self.start_btn.pack(pady=5)

        self.pause_btn = tk.Button(btn_frame, text="⏸ ПАУЗА", command=self.pause_simulation,
                                   bg='#e67e22', fg='white', font=('Arial', 12, 'bold'),
                                   width=12, height=2, state=tk.DISABLED)
        self.pause_btn.pack(pady=5)

        self.stop_btn = tk.Button(btn_frame, text="⏹ СТОП", command=self.stop_simulation,
                                  bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                                  width=12, height=2, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

        tk.Button(btn_frame, text="💾 СОХРАНИТЬ", command=self.save_data,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                  width=12, height=1).pack(pady=10)

        stats_frame = tk.LabelFrame(control_panel, text="Текущая статистика",
                                    font=('Arial', 10, 'bold'), bg='#34495e', fg='white')
        stats_frame.pack(pady=10, padx=15, fill=tk.X)

        self.stats_text = tk.Text(stats_frame, height=12, width=25,
                                  font=('Courier', 9), bg='#2c3e50', fg='white')
        self.stats_text.pack(pady=5, padx=5)

        viz_panel = tk.Frame(main_frame, bg='#2c3e50')
        viz_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.weather_frame = tk.Frame(viz_panel, bg='#ecf0f1', relief=tk.RAISED, bd=3)
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.weather_icon = tk.Label(self.weather_frame, text="☀️", font=('Arial', 120),
                                     bg='#ecf0f1')
        self.weather_icon.pack(expand=True, pady=50)

        self.weather_label = tk.Label(self.weather_frame, text="Ясно",
                                      font=('Arial', 24, 'bold'), bg='#ecf0f1')
        self.weather_label.pack(pady=20)

        self.day_counter = tk.Label(self.weather_frame, text="День: 0 / 0",
                                    font=('Arial', 14), bg='#ecf0f1')
        self.day_counter.pack(pady=10)

        graph_frame = tk.Frame(viz_panel, bg='white')
        graph_frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(8, 4), dpi=80, facecolor='#ecf0f1')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax.set_title("История погоды", fontsize=12, fontweight='bold')
        self.ax.set_xlabel("День")
        self.ax.set_ylabel("Состояние")
        self.ax.set_yticks(self.states)
        self.ax.set_yticklabels([self.names[s] for s in self.states])
        self.ax.grid(True, alpha=0.3)

        self.update_stats_display()

    def start_simulation(self):
        try:
            self.days_to_simulate = int(self.days_entry.get())
            if self.days_to_simulate <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите корректное количество дней")
            return

        self.simulation_running = True
        self.current_state = 1
        self.history = [self.current_state]

        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)

        self.update_weather_display()
        self.animate_simulation()

    def animate_simulation(self):
        if not self.simulation_running:
            return

        if len(self.history) < self.days_to_simulate:
            probs = self.P[self.current_state - 1]
            next_state = np.random.choice(self.states, p=probs)

            self.history.append(next_state)
            self.current_state = next_state

            self.update_weather_display()
            self.update_graph()
            self.update_stats_display()

            speed = self.speed_scale.get()
            delay = int(1 / speed * 1000)

            self.root.after(delay, self.animate_simulation)
        else:
            self.simulation_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            messagebox.showinfo("Завершено", f"Моделирование завершено!\nДней: {self.days_to_simulate}")
            self.show_final_statistics()

    def update_weather_display(self):
        state = self.current_state
        self.weather_icon.config(text=self.icons[state])
        self.weather_label.config(text=self.names[state])

        if state == 1:
            self.weather_frame.config(bg='#ffeaa7')
            self.weather_icon.config(bg='#ffeaa7')
            self.weather_label.config(bg='#ffeaa7')
            self.day_counter.config(bg='#ffeaa7')
        elif state == 2:
            self.weather_frame.config(bg='#b2bec3')
            self.weather_icon.config(bg='#b2bec3')
            self.weather_label.config(bg='#b2bec3')
            self.day_counter.config(bg='#b2bec3')
        else:
            self.weather_frame.config(bg='#636e72')
            self.weather_icon.config(bg='#636e72')
            self.weather_label.config(bg='#636e72')
            self.day_counter.config(bg='#636e72')

        self.day_counter.config(text=f"День: {len(self.history)} / {self.days_to_simulate}")

    def update_graph(self):
        self.ax.clear()
        days_to_show = min(len(self.history), 100)
        self.ax.plot(self.history[-days_to_show:], 'b-', linewidth=1.5,
                     marker='o', markersize=3, color='#3498db')
        self.ax.set_yticks(self.states)
        self.ax.set_yticklabels([self.names[s] for s in self.states])
        self.ax.set_xlabel("День (последние дни)", fontsize=10)
        self.ax.set_ylabel("Состояние погоды", fontsize=10)
        self.ax.set_title(f"История погоды (последние {days_to_show} дней)",
                          fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(0, days_to_show)
        self.fig.tight_layout()
        self.canvas.draw()

    def update_stats_display(self):
        if len(self.history) == 0:
            return

        emp = [np.sum(np.array(self.history) == s) / len(self.history) for s in self.states]

        current = self.current_state

        stats = f"Всего дней: {len(self.history)}\n"
        stats += f"Текущий день: {len(self.history)}\n"
        stats += f"{'-' * 20}\n"
        stats += f"Текущая погода:\n{self.names[current]}\n"
        stats += f"{'-' * 20}\n"
        stats += "Распределение:\n"
        for i, s in enumerate(self.states):
            stats += f"{self.names[s]}: {emp[i]:.2%}\n"

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)

    def pause_simulation(self):
        self.simulation_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

    def stop_simulation(self):
        self.simulation_running = False
        self.history = []
        self.current_state = 1
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)

        self.weather_icon.config(text="☀️")
        self.weather_label.config(text="Ясно")
        self.weather_frame.config(bg='#ecf0f1')
        self.weather_icon.config(bg='#ecf0f1')
        self.weather_label.config(bg='#ecf0f1')
        self.day_counter.config(bg='#ecf0f1')
        self.day_counter.config(text="День: 0 / 0")
        self.ax.clear()
        self.canvas.draw()
        self.update_stats_display()

    def save_data(self):
        if len(self.history) == 0:
            messagebox.showwarning("Нет данных", "Сначала выполните моделирование!")
            return

        path = filedialog.askdirectory(title="Выберите папку для сохранения")
        if path:
            import os
            emp = [np.sum(np.array(self.history) == s) / len(self.history) for s in self.states]

            with open(os.path.join(path, "statistics.txt"), 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("СТАТИСТИКА МАРКОВСКОЙ МОДЕЛИ ПОГОДЫ\n")
                f.write("=" * 70 + "\n\n")

                f.write("ОСНОВНАЯ ИНФОРМАЦИЯ:\n")
                f.write(f"  Всего дней: {len(self.history)}\n")
                f.write(f"  Количество состояний: {len(self.states)}\n\n")

                f.write("МАТРИЦА ПЕРЕХОДНЫХ ВЕРОЯТНОСТЕЙ:\n")
                f.write("        Ясно    Облачно  Пасмурно\n")
                for i, state_name in enumerate(self.names.values()):
                    f.write(f"{state_name:8} ")
                    for j in range(3):
                        f.write(f"{self.P[i][j]:8.3f} ")
                    f.write("\n")
                f.write("\n")

                f.write("ТЕОРЕТИЧЕСКОЕ РАСПРЕДЕЛЕНИЕ (стационарное):\n")
                for i, state_name in enumerate(self.names.values()):
                    f.write(f"  {state_name:10}: {self.pi[i]:8.2%}\n")
                f.write("\n")

                f.write("ЭМПИРИЧЕСКОЕ РАСПРЕДЕЛЕНИЕ (по результатам моделирования):\n")
                for i, state_name in enumerate(self.names.values()):
                    diff = emp[i] - self.pi[i]
                    f.write(f"  {state_name:10}: {emp[i]:8.2%} (отклонение: {diff:+.2%})\n")
                f.write("\n")

                f.write("СРАВНИТЕЛЬНЫЙ АНАЛИЗ:\n")
                f.write("-" * 70 + "\n")
                f.write(f"{'Состояние':15} {'Теоретическая':>15} {'Эмпирическая':>15} {'Разница':>15}\n")
                f.write("-" * 70 + "\n")
                for i, state_name in enumerate(self.names.values()):
                    f.write(f"{state_name:15} {self.pi[i]:14.2%} {emp[i]:14.2%} {emp[i] - self.pi[i]:+14.2%}\n")
                f.write("-" * 70 + "\n\n")

                f.write("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:\n")
                transitions = np.zeros((3, 3))
                for i in range(len(self.history) - 1):
                    from_state = self.history[i] - 1
                    to_state = self.history[i + 1] - 1
                    transitions[from_state][to_state] += 1

                row_sums = transitions.sum(axis=1, keepdims=True)
                transitions_norm = np.divide(transitions, row_sums, where=row_sums != 0)

                f.write("\nЭмпирические переходные вероятности:\n")
                f.write("        Ясно    Облачно  Пасмурно\n")
                for i, state_name in enumerate(self.names.values()):
                    f.write(f"{state_name:8} ")
                    for j in range(3):
                        f.write(f"{transitions_norm[i][j]:8.3f} ")
                    f.write("\n")

                f.write("\n" + "=" * 70 + "\n")

            messagebox.showinfo("Успех", f"Данные сохранены в TXT файлах в папке:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()