import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.stats import chi2


class Lab6_1_UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная 6.1 - Имитационное моделирование ДСВ")
        self.setFixedSize(900, 700)

        self.probs = [0.2, 0.3, 0.4, 0.1]
        self.x_values = np.array([1, 2, 3, 4, 5])
        self.prob5_value = 0.0

        self.N = 100

        self.init_ui()
        self.calculate_theoretical()
        self.update_prob5()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        probs_layout = QHBoxLayout()
        probs_layout.addWidget(QLabel("Prob 1:"))
        self.prob1_input = QLineEdit("0.2")
        self.prob1_input.setFixedWidth(60)
        self.prob1_input.textChanged.connect(self.on_probability_changed)
        probs_layout.addWidget(self.prob1_input)

        probs_layout.addWidget(QLabel("Prob 2:"))
        self.prob2_input = QLineEdit("0.3")
        self.prob2_input.setFixedWidth(60)
        self.prob2_input.textChanged.connect(self.on_probability_changed)
        probs_layout.addWidget(self.prob2_input)

        probs_layout.addWidget(QLabel("Prob 3:"))
        self.prob3_input = QLineEdit("0.4")
        self.prob3_input.setFixedWidth(60)
        self.prob3_input.textChanged.connect(self.on_probability_changed)
        probs_layout.addWidget(self.prob3_input)

        probs_layout.addWidget(QLabel("Prob 4:"))
        self.prob4_input = QLineEdit("0.1")
        self.prob4_input.setFixedWidth(60)
        self.prob4_input.textChanged.connect(self.on_probability_changed)
        probs_layout.addWidget(self.prob4_input)

        probs_layout.addWidget(QLabel("Prob 5:"))
        self.prob5_input = QLineEdit("0.0")
        self.prob5_input.setFixedWidth(60)
        self.prob5_input.setReadOnly(True)
        self.prob5_input.setStyleSheet("QLineEdit { background-color: #f0f0f0; color: #666; }")
        probs_layout.addWidget(self.prob5_input)

        probs_layout.addStretch()

        probs_layout.addWidget(QLabel("Number of experiments:"))
        self.n_input = QLineEdit("100")
        self.n_input.setFixedWidth(80)
        probs_layout.addWidget(self.n_input)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.run_experiment)
        self.start_btn.setFixedWidth(80)
        probs_layout.addWidget(self.start_btn)

        main_layout.addLayout(probs_layout)

        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        main_layout.addWidget(self.canvas)

        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_layout = QHBoxLayout(info_frame)

        self.avg_label = QLabel("Average: -- (error = --%)")
        self.avg_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.avg_label)

        self.var_label = QLabel("Variance: -- (error = --%)")
        self.var_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.var_label)

        self.chi2_label = QLabel("Chi-squared: --")
        self.chi2_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.chi2_label)

        main_layout.addWidget(info_frame)

        self.statusBar().showMessage("Готов")

    def on_probability_changed(self):
        self.update_prob5()
        self.calculate_theoretical()

    def update_prob5(self):
        try:
            p1 = float(self.prob1_input.text() or "0")
            p2 = float(self.prob2_input.text() or "0")
            p3 = float(self.prob3_input.text() or "0")
            p4 = float(self.prob4_input.text() or "0")

            sum_prob = p1 + p2 + p3 + p4

            if sum_prob > 1.0:
                self.prob5_input.setText("ERROR!")
                self.prob5_input.setStyleSheet(
                    "QLineEdit { background-color: #ffcccc; color: red; font-weight: bold; }")
                self.statusBar().showMessage("ОШИБКА: Сумма вероятностей Prob 1-4 не может превышать 1!")
                self.start_btn.setEnabled(False)
                return
            else:
                self.prob5_value = 1.0 - sum_prob
                self.prob5_input.setText(f"{self.prob5_value:.4f}")
                self.prob5_input.setStyleSheet("QLineEdit { background-color: #f0f0f0; color: #666; }")
                self.statusBar().showMessage(f"Prob 5 = {self.prob5_value:.4f} (1 - сумма Prob 1-4)")
                self.start_btn.setEnabled(True)

        except ValueError:
            self.prob5_input.setText("ERROR!")
            self.statusBar().showMessage("ОШИБКА: Введите корректные числа!")
            self.start_btn.setEnabled(False)

    def calculate_theoretical(self):
        try:
            p1 = float(self.prob1_input.text() or "0")
            p2 = float(self.prob2_input.text() or "0")
            p3 = float(self.prob3_input.text() or "0")
            p4 = float(self.prob4_input.text() or "0")
            p5 = self.prob5_value

            all_probs = np.array([p1, p2, p3, p4, p5])

            non_zero_mask = all_probs > 0
            self.x_values_full = np.array([1, 2, 3, 4, 5])
            self.x_values = self.x_values_full[non_zero_mask]
            self.probs_full = all_probs[non_zero_mask]

            self.probs_full = self.probs_full / np.sum(self.probs_full)

            self.Ex_theor = np.sum(self.probs_full * self.x_values)
            self.Dx_theor = np.sum(self.probs_full * (self.x_values - self.Ex_theor) ** 2)

        except:
            pass

    def generate_sample(self, N, x_vals, p_vals):
        cum_probs = np.cumsum(p_vals)
        sample = np.zeros(N, dtype=int)
        for i in range(N):
            alpha = np.random.random()
            k = np.searchsorted(cum_probs, alpha, side='left')
            sample[i] = x_vals[k]
        return sample

    def run_experiment(self):
        self.update_prob5()

        try:
            N = int(self.n_input.text())
            if N <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите положительное число экспериментов")
            return

        if len(self.x_values) == 0 or np.sum(self.probs_full) == 0:
            QMessageBox.warning(self, "Ошибка", "Нет значений с положительной вероятностью!")
            return

        sample = self.generate_sample(N, self.x_values, self.probs_full)

        n_i = np.array([np.sum(sample == x) for x in self.x_values])
        p_hat = n_i / N

        Ex_hat = np.sum(p_hat * self.x_values)
        Dx_hat = np.sum(p_hat * self.x_values ** 2) - Ex_hat ** 2

        delta_E_abs = abs(Ex_hat - self.Ex_theor)
        delta_D_abs = abs(Dx_hat - self.Dx_theor)
        delta_E_rel = (delta_E_abs / abs(self.Ex_theor) * 100) if self.Ex_theor != 0 else 0
        delta_D_rel = (delta_D_abs / abs(self.Dx_theor) * 100) if self.Dx_theor != 0 else 0

        chi2_stat = np.sum(n_i ** 2 / (N * self.probs_full)) - N

        df = len(self.x_values) - 1
        alpha = 0.05
        chi2_crit = chi2.ppf(1 - alpha, df)

        self.avg_label.setText(f"Average: {Ex_hat:.3f} (error = {delta_E_rel:.1f}%)")
        self.var_label.setText(f"Variance: {Dx_hat:.3f} (error = {delta_D_rel:.1f}%)")

        chi2_text = f"Chi-squared: {chi2_stat:.2f}"
        if chi2_stat > chi2_crit:
            chi2_text += f" > {chi2_crit:.3f} is true"
            self.chi2_label.setStyleSheet("color: red; font-size: 14px; font-weight: bold;")
        else:
            chi2_text += f" ≤ {chi2_crit:.3f} is false"
            self.chi2_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")

        self.chi2_label.setText(chi2_text)

        self.update_chart()

        self.statusBar().showMessage(f"Эксперимент завершен: N={N}, χ²={chi2_stat:.2f}")

    def update_chart(self):
        self.ax.clear()

        p1 = float(self.prob1_input.text() or "0")
        p2 = float(self.prob2_input.text() or "0")
        p3 = float(self.prob3_input.text() or "0")
        p4 = float(self.prob4_input.text() or "0")
        p5 = self.prob5_value

        all_probs_theor = np.array([p1, p2, p3, p4, p5])

        N = int(self.n_input.text())
        sample = self.generate_sample(N, self.x_values_full, all_probs_theor)

        n_i_full = np.array([np.sum(sample == x) for x in [1, 2, 3, 4, 5]])
        p_hat_full = n_i_full / N

        x_pos = np.arange(5)
        width = 0.35

        bars1 = self.ax.bar(x_pos - width / 2, p_hat_full, width, label='Эмпирические freq.',
                            color='blue', alpha=0.7)
        bars2 = self.ax.bar(x_pos + width / 2, all_probs_theor, width, label='Теоретические freq.',
                            color='orange', alpha=0.7)

        self.ax.set_xticks(x_pos)
        self.ax.set_xticklabels(['1', '2', '3', '4', '5'])
        self.ax.set_ylabel('freq.')
        self.ax.set_xlabel('x')
        self.ax.set_title('Сравнение эмпирического и теоретического распределений')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        max_y = max(max(p_hat_full), max(all_probs_theor)) * 1.2
        self.ax.set_ylim(0, max_y)

        for bar in bars1:
            height = bar.get_height()
            if height > 0.01:
                self.ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                             f'{height:.3f}', ha='center', va='bottom', fontsize=8)

        for bar in bars2:
            height = bar.get_height()
            if height > 0.01:
                self.ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                             f'{height:.3f}', ha='center', va='bottom', fontsize=8)

        self.canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = Lab6_1_UI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()