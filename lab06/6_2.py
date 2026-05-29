import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from scipy.stats import chi2, norm


class NormalDistributionLab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа - Моделирование нормальной случайной величины")
        self.setFixedSize(1500, 800)

        self.mu = 0.0
        self.sigma = 1.0

        self.N = 100

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        control_panel = QHBoxLayout()

        control_panel.addWidget(QLabel("Mean:"))
        self.mean_input = QLineEdit("0.0")
        self.mean_input.setFixedWidth(80)
        control_panel.addWidget(self.mean_input)

        control_panel.addWidget(QLabel("Variance:"))
        self.var_input = QLineEdit("1.0")
        self.var_input.setFixedWidth(80)
        control_panel.addWidget(self.var_input)

        control_panel.addWidget(QLabel("Sample size:"))
        self.n_input = QLineEdit("100")
        self.n_input.setFixedWidth(100)
        control_panel.addWidget(self.n_input)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.run_experiment)
        self.start_btn.setFixedWidth(80)
        control_panel.addWidget(self.start_btn)

        control_panel.addStretch()
        main_layout.addLayout(control_panel)

        self.figure = plt.Figure(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        main_layout.addWidget(self.canvas)

        table_widget = QWidget()
        table_layout = QHBoxLayout(table_widget)

        self.left_table = QTableWidget()
        self.left_table.setColumnCount(2)
        self.left_table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.left_table.verticalHeader().setVisible(False)
        self.left_table.setColumnWidth(0, 250)
        self.left_table.setColumnWidth(1, 400)

        self.right_table = QTableWidget()
        self.right_table.setColumnCount(2)
        self.right_table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.right_table.verticalHeader().setVisible(False)
        self.right_table.setColumnWidth(0, 250)
        self.right_table.setColumnWidth(1, 400)

        self.left_table.setRowCount(4)
        self.left_table.setItem(0, 0, QTableWidgetItem("Теоретическое среднее (μ)"))
        self.left_table.setItem(1, 0, QTableWidgetItem("Эмпирическое среднее (x̄)"))
        self.left_table.setItem(2, 0, QTableWidgetItem("Относительная погрешность среднего"))
        self.left_table.setItem(3, 0, QTableWidgetItem("Теоретическая дисперсия (σ²)"))

        self.right_table.setRowCount(4)
        self.right_table.setItem(0, 0, QTableWidgetItem("Эмпирическая дисперсия (s²)"))
        self.right_table.setItem(1, 0, QTableWidgetItem("Относительная погрешность дисперсии"))
        self.right_table.setItem(2, 0, QTableWidgetItem("Chi-squared"))
        self.right_table.setItem(3, 0, QTableWidgetItem("Результат критерия"))

        for i in range(4):
            self.left_table.setItem(i, 1, QTableWidgetItem("--"))
            self.right_table.setItem(i, 1, QTableWidgetItem("--"))

        table_layout.addWidget(self.left_table)
        table_layout.addWidget(self.right_table)
        main_layout.addWidget(table_widget)

        self.statusBar().showMessage("Готов")

    def generate_normal_sample(self, N, mu, sigma):
        sample = np.random.normal(mu, sigma, N)
        return sample

    def calculate_chi2(self, sample, mu, sigma, N, num_bins=7):
        bins = np.linspace(mu - 3 * sigma, mu + 3 * sigma, num_bins + 1)

        hist, _ = np.histogram(sample, bins=bins)

        theo_probs = []
        for i in range(num_bins):
            prob = norm.cdf(bins[i + 1], mu, sigma) - norm.cdf(bins[i], mu, sigma)
            theo_probs.append(prob)

        theo_freq = np.array(theo_probs) * N

        mask = theo_freq > 0
        hist = hist[mask]
        theo_freq = theo_freq[mask]

        if len(hist) > 1:
            chi2_stat = np.sum((hist - theo_freq) ** 2 / theo_freq)
            df = len(hist) - 1 - 2
            return chi2_stat, max(df, 1)
        else:
            return 0, 1

    def run_experiment(self):
        try:
            self.mu = float(self.mean_input.text())
            self.sigma_sq = float(self.var_input.text())
            if self.sigma_sq <= 0:
                raise ValueError("Дисперсия должна быть положительной")
            self.sigma = np.sqrt(self.sigma_sq)

            self.N = int(self.n_input.text())
            if self.N <= 0:
                raise ValueError
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Введите корректные значения!\n{str(e)}")
            return

        sample = self.generate_normal_sample(self.N, self.mu, self.sigma)

        sample_mean = np.mean(sample)

        sample_var = np.var(sample)

        delta_mean_abs = abs(sample_mean - self.mu)
        delta_mean_rel = (delta_mean_abs / abs(self.mu) * 100) if self.mu != 0 else 0

        delta_var_abs = abs(sample_var - self.sigma_sq)
        delta_var_rel = (delta_var_abs / self.sigma_sq * 100) if self.sigma_sq != 0 else 0

        chi2_stat, df = self.calculate_chi2(sample, self.mu, self.sigma, self.N)
        alpha = 0.05
        chi2_crit = chi2.ppf(1 - alpha, df)

        self.left_table.setItem(0, 1, QTableWidgetItem(f"{self.mu:.6f}"))
        self.left_table.setItem(1, 1, QTableWidgetItem(f"{sample_mean:.6f}"))
        self.left_table.setItem(2, 1, QTableWidgetItem(f"{delta_mean_rel:.2f}%"))
        self.left_table.setItem(3, 1, QTableWidgetItem(f"{self.sigma_sq:.6f}"))

        self.right_table.setItem(0, 1, QTableWidgetItem(f"{sample_var:.6f}"))
        self.right_table.setItem(1, 1, QTableWidgetItem(f"{delta_var_rel:.2f}%"))

        chi2_text = f"{chi2_stat:.4f}"
        if chi2_stat > chi2_crit:
            chi2_text += f" > {chi2_crit:.3f}"
            self.right_table.setItem(2, 1, QTableWidgetItem(chi2_text))
            self.right_table.setItem(3, 1, QTableWidgetItem("Гипотеза НЕВЕРНА"))
            self.right_table.item(3, 1).setForeground(Qt.red)
        else:
            chi2_text += f" ≤ {chi2_crit:.3f}"
            self.right_table.setItem(2, 1, QTableWidgetItem(chi2_text))
            self.right_table.setItem(3, 1, QTableWidgetItem("Гипотеза НЕ ПРОТИВОРЕЧИТ ДАННЫМ"))
            self.right_table.item(3, 1).setForeground(Qt.green)

        self.update_chart(sample)

        self.statusBar().showMessage(f"Эксперимент завершен: N={self.N}, χ²={chi2_stat:.2f}")

    def update_chart(self, sample):
        self.ax.clear()

        counts, bins, patches = self.ax.hist(sample, bins=20, density=True,
                                             alpha=0.7, color='blue',
                                             label='Эмпирическая гистограмма', edgecolor='black')

        x_range = np.linspace(self.mu - 4 * self.sigma, self.mu + 4 * self.sigma, 200)
        y_theor = norm.pdf(x_range, self.mu, self.sigma)
        self.ax.plot(x_range, y_theor, 'r-', linewidth=2, label='Теоретическое нормальное распределение')

        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Плотность вероятности')
        self.ax.set_title(f'Гистограмма выборки (N={self.N})')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        x_min = min(self.mu - 4 * self.sigma, np.min(sample))
        x_max = max(self.mu + 4 * self.sigma, np.max(sample))
        self.ax.set_xlim(x_min, x_max)

        self.canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = NormalDistributionLab()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()