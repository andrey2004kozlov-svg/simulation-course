import tkinter as tk
import random


class YesNoApp:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=20, pady=20)
        self.frame.pack()

        tk.Label(self.frame, text="Скажи 'да' или 'нет'", font=("Arial", 14, "bold")).pack(pady=5)

        self.question_entry = tk.Entry(self.frame, width=40, font=("Arial", 11))
        self.question_entry.pack(pady=5)
        self.question_entry.insert(0, "Задайте свой вопрос")

        self.answer_label = tk.Label(self.frame, text="", font=("Arial", 12), fg="blue")
        self.answer_label.pack(pady=10)

        tk.Button(self.frame, text="Получить ответ", command=self.get_answer, bg="lightblue", padx=10).pack(pady=5)

    def get_answer(self):
        answer = random.choice(["Да", "Нет"])
        self.answer_label.config(text=answer)


class Magic8BallApp:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=20, pady=20)
        self.frame.pack()

        tk.Label(self.frame, text="🎱 Шар предсказаний (Magic 8-Ball)", font=("Arial", 14, "bold")).pack(pady=5)

        self.question_entry = tk.Entry(self.frame, width=50, font=("Arial", 11))
        self.question_entry.pack(pady=5)
        self.question_entry.insert(0, "Задайте вопрос магическому шару")

        self.answer_label = tk.Label(self.frame, text="", font=("Arial", 12), fg="darkgreen", wraplength=400)
        self.answer_label.pack(pady=10)

        tk.Button(self.frame, text="Тряхнуть шар", command=self.shake_ball, bg="lightgreen", padx=10).pack(pady=5)

        self.answers = [
            ("Бесспорно", 0.08),
            ("Предрешено", 0.07),
            ("Никаких сомнений", 0.07),
            ("Определённо да", 0.07),
            ("Можешь быть уверен в этом", 0.07),
            ("Мне кажется — да", 0.06),
            ("Вероятнее всего", 0.06),
            ("Хорошие перспективы", 0.06),
            ("Знаки говорят — да", 0.06),
            ("Пока не ясно, попробуй снова", 0.05),
            ("Спроси позже", 0.05),
            ("Лучше не рассказывать", 0.05),
            ("Сейчас нельзя предсказать", 0.05),
            ("Сконцентрируйся и спроси опять", 0.05),
            ("Даже не думай", 0.04),
            ("Мой ответ — нет", 0.04),
            ("По моим данным — нет", 0.03),
            ("Перспективы не очень хорошие", 0.02),
            ("Весьма сомнительно", 0.02),
        ]

        total_prob = sum(prob for _, prob in self.answers)
        if abs(total_prob - 1.0) > 0.001:
            self.answers = [(text, prob / total_prob) for text, prob in self.answers]

    def generate(self):
        alpha = random.random()
        A = alpha
        k = 0
        while k <= len(self.answers):
            A = A - self.answers[k][1]
            if A <= 0:
                return self.answers[k][0]
            k += 1
        return self.answers[0][0]

    def shake_ball(self):
        answer = self.generate()
        self.answer_label.config(text=answer)


class Lab5App:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №5: Моделирование случайных событий")
        self.root.geometry("550x400")
        self.root.resizable(False, False)

        notebook = tk.Frame(root)
        notebook.pack(fill="both", expand=True)

        self.tab1 = tk.Frame(notebook)
        self.tab2 = tk.Frame(notebook)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="📌 Скажи 'да' или 'нет'", command=self.show_tab1, bg="#eee", padx=10).pack(
            side="left", padx=5)
        tk.Button(btn_frame, text="🎱 Шар предсказаний", command=self.show_tab2, bg="#eee", padx=10).pack(side="left",
                                                                                                         padx=5)
        self.yes_no = YesNoApp(self.tab1)
        self.magic_ball = Magic8BallApp(self.tab2)

        self.show_tab1()

    def show_tab1(self):
        self.tab2.pack_forget()
        self.tab1.pack(fill="both", expand=True)

    def show_tab2(self):
        self.tab1.pack_forget()
        self.tab2.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = Lab5App(root)
    root.mainloop()