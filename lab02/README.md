Отчет. Имитационное моделирование. Лабораторная работа №2

Козлов Андрей, группа 932303

import tkinter as tk  
from tkinter import ttk  
import numpy as np  
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import time  
<br/><br/>class HeatConductionSimulation:  
def \__init_\_(self, root):  
self.root = root  
self.root.title("Теплопроводность алмазной пластины")  
self.root.geometry("1200x800")  
self.root.configure(bg='#f0f0f0')  
<br/>self.simulation_running = False  
self.cumulative_real_time = 0  
self.L, self.lam, self.rho, self.c = 1, 1000.0, 3500.0, 500.0  
self.T_l, self.T_r, self.t_max = 100.0, 50.0, 2.0  
<br/>self.create_ui()  
self.init_sim(0.0001, 0.01)  
self.upd_ui()  
<br/>def create_ui(self):  
ctrl = tk.Frame(self.root, bg='#90EE90', height=200)  
ctrl.pack(fill=tk.X, padx=10, pady=5)  
ctrl.pack_propagate(False)  
<br/>left = tk.Frame(ctrl, bg='#90EE90')  
left.pack(side=tk.LEFT, padx=10, pady=5)  
tk.Label(left, text="Исходные данные (Алмаз)", bg='#90EE90', font=('Arial', 9, 'bold')).pack(anchor='w')  
<br/>params = \[  
("L (м):", 'L', "0.1"),  
("λ (Вт/(м·К)):", 'lam', "1000.0"),  
("ρ (кг/м³):", 'rho', "3500.0"),  
("c (Дж/(кг·К)):", 'c', "500.0"),  
("Tl (°C):", 'T_l', "100.0"),  
("Tr (°C):", 'T_r', "50.0"),  
("t_max (с):", 't_max', "2.0")  
\]  
<br/>for txt, var, val in params:  
f = tk.Frame(left, bg='#90EE90')  
f.pack(anchor='w', pady=1)  
tk.Label(f, text=txt, bg='#90EE90', width=15, anchor='w').pack(side=tk.LEFT)  
e = tk.Entry(f, width=10)  
e.insert(0, val)  
e.pack(side=tk.LEFT)  
setattr(self, f'{var}\_entry', e)  
<br/>mid = tk.Frame(ctrl, bg='#90EE90')  
mid.pack(side=tk.LEFT, padx=15, pady=5)  
tk.Label(mid, text="Параметры сетки", bg='#90EE90', font=('Arial', 9, 'bold')).pack(anchor='w', pady=(0, 5))  
for txt, var, val in \[("τ (с):", 'tau', "0.0001"), ("h (м):", 'h', "0.01")\]:  
f = tk.Frame(mid, bg='#90EE90')  
f.pack(anchor='w', pady=1)  
tk.Label(f, text=txt, bg='#90EE90', width=10, anchor='w').pack(side=tk.LEFT)  
e = tk.Entry(f, width=10)  
e.insert(0, val)  
e.pack(side=tk.LEFT)  
setattr(self, f'{var}\_entry', e)  
<br/>btn_frame = tk.Frame(ctrl, bg='#90EE90')  
btn_frame.pack(side=tk.LEFT, expand=True)  
self.start_btn = tk.Button(btn_frame, text="Запуск", bg='#87CEEB', font=('Arial', 12, 'bold'),  
relief='raised', bd=3, padx=20, pady=5, command=self.toggle_sim)  
self.start_btn.pack()  
<br/>right = tk.Frame(ctrl, bg='#90EE90')  
right.pack(side=tk.RIGHT, padx=10, pady=5)  
self.lbl_center = tk.Label(right, text="Температура в центре: 20.00 °C", bg='#90EE90',  
font=('Arial', 10, 'bold'))  
self.lbl_center.pack(anchor='e')  
self.lbl_time = tk.Label(right, text="Время симуляции: 0.000 с", bg='#90EE90', font=('Arial', 10))  
self.lbl_time.pack(anchor='e')  
self.lbl_real = tk.Label(right, text="Реальное время: 0.000 с", bg='#90EE90', font=('Arial', 10))  
self.lbl_real.pack(anchor='e')  
<br/>main = tk.Frame(self.root, bg='#f0f0f0')  
main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  
<br/>graph_f = tk.Frame(main, bg='#E6F3FF')  
graph_f.pack(fill=tk.BOTH, expand=True)  
<br/>self.fig, self.ax = plt.subplots(figsize=(9, 5.5))  
self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.1)  
self.ax.set_facecolor('#E6F3FF')  
self.fig.patch.set_facecolor('#E6F3FF')  
self.ax.set(xlabel='x, м', ylabel='Температура, °C', xlim=(0, 0.1), ylim=(0, 120))  
self.ax.xaxis.label.set_color('blue')  
self.ax.yaxis.label.set_color('blue')  
for s in self.ax.spines.values():  
s.set_color('blue')  
s.set_linewidth(1)  
self.ax.tick_params(colors='blue')  
self.line, = self.ax.plot(\[\], \[\], 'r-', lw=2)  
self.canvas = FigureCanvasTkAgg(self.fig, graph_f)  
self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  
<br/>def init_sim(self, tau, h):  
self.tau, self.h = tau, h  
self.N = max(3, int(self.L / self.h) + 1)  
self.x = np.linspace(0, self.L, self.N)  
self.T = np.ones(self.N) \* 20.0  
self.T\[0\], self.T\[-1\] = self.T_l, self.T_r  
self.t = 0.0  
self.viz_step = max(1, int(0.02 / self.tau))  
self.cnt = 0  
<br/>def solve_step(self, T_cur, N, h, tau):  
A = np.full(N, self.lam / (h \* h))  
C = A.copy()  
B = np.full(N, 2 \* self.lam / (h \* h) + self.rho \* self.c / tau)  
F = -self.rho \* self.c / tau \* T_cur  
<br/>al, bt = np.zeros(N), np.zeros(N)  
al\[1\], bt\[1\] = 0.0, T_cur\[0\]  
<br/>for i in range(1, N - 1):  
d = B\[i\] - A\[i\] \* al\[i\]  
if abs(d) < 1e-15: d = 1e-15  
al\[i + 1\] = C\[i\] / d  
bt\[i + 1\] = (-F\[i\] + A\[i\] \* bt\[i\]) / d  
<br/>Tn = np.zeros(N)  
Tn\[0\], Tn\[-1\] = self.T_l, self.T_r  
for i in range(N - 2, 0, -1):  
Tn\[i\] = al\[i + 1\] \* Tn\[i + 1\] + bt\[i + 1\]  
return Tn  
<br/>def upd_ui(self):  
self.cnt += 1  
if self.cnt % self.viz_step == 0 or self.t >= self.t_max or not self.simulation_running:  
self.line.set_data(self.x, self.T)  
self.canvas.draw()  
<br/>self.lbl_center.config(text=f"Температура в центре: {self.T\[self.N // 2\]:.2f} °C")  
self.lbl_time.config(text=f"Время симуляции: {self.t:.3f} с")  
<br/>rt = self.cumulative_real_time  
if self.simulation_running:  
rt += time.time() - self.sim_start  
self.lbl_real.config(text=f"Реальное время: {rt:.3f} с")  
<br/>def read_params(self):  
try:  
self.L = float(self.L_entry.get())  
self.lam = float(self.lam_entry.get())  
self.rho = float(self.rho_entry.get())  
self.c = float(self.c_entry.get())  
self.T_l = float(self.T_l_entry.get())  
self.T_r = float(self.T_r_entry.get())  
self.t_max = float(self.t_max_entry.get())  
return True  
except ValueError:  
return False  
<br/>def toggle_sim(self):  
if not self.simulation_running:  
if not self.read_params():  
return  
<br/>try:  
tau = float(self.tau_entry.get())  
h = float(self.h_entry.get())  
if tau <= 0 or h <= 0: return  
except ValueError:  
return  
<br/>self.init_sim(tau, h)  
<br/>self.simulation_running = True  
self.start_btn.config(text="Пауза", bg='#FFB6C1')  
self.sim_start = time.time()  
self.run_loop()  
else:  
self.simulation_running = False  
self.cumulative_real_time += time.time() - self.sim_start  
self.start_btn.config(text="Запуск", bg='#87CEEB')  
<br/>def run_loop(self):  
if not self.simulation_running: return  
if self.t < self.t_max:  
self.T = self.solve_step(self.T, self.N, self.h, self.tau)  
self.t += self.tau  
self.upd_ui()  
self.root.after(1, self.run_loop)  
else:  
self.cumulative_real_time += time.time() - self.sim_start  
self.simulation_running = False  
self.start_btn.config(text="Запуск", bg='#87CEEB')  
self.upd_ui()  
<br/><br/>if \__name__ == "\__main_\_":  
root = tk.Tk()  
app = HeatConductionSimulation(root)  
root.mainloop()

<img width="892" height="516" alt="image" src="https://github.com/user-attachments/assets/1eac6401-1694-4746-8423-985d2fb8c94f" />

Вывод: непрерывно-пошаговое моделирование заметно замедляется с уменьшением шага, статистическая значимость при шаге 0.01 по времени и пространству почти не отличается от соответствующей при шаге в 0.0001
