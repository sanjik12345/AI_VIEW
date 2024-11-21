import tkinter as tk
from tkinter import messagebox
from muhgey import hol_tandau
from nurgey import left_2h
from chat_bot import chatbot_app


def on_close(root):
    """Функция для обработки закрытия окна."""
    if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
        root.destroy()

def main():
    root = tk.Tk()
    root.title("AI_TRAINER")
    root.geometry("500x375")
    root.resizable(False, False)
    root.configure(bg="#1e1e1e")


    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))


    title_label = tk.Label(
        root,
        text="AI TRAINER",
        font=("Helvetica", 24, "bold"),
        fg="#00ff00",
        bg="#1e1e1e"
    )
    title_label.pack(pady=(20, 10))


    separator = tk.Frame(root, height=2, bg="#00ff00")
    separator.pack(fill="x", padx=20, pady=(0, 20))

    btn_left_2h = tk.Button(
        root,
        text="Подъем на две руки",
        command=left_2h,
        width=25,
        bg="#333333",
        fg="white",
        font=("Helvetica", 14),
        activebackground="#00ff00",  # Цвет при наведении
        activeforeground="#1e1e1e",
        bd=0,  # Убираем рамку
        relief="flat"  # Плоский стиль
    )
    btn_left_2h.pack(pady=10)

    # Вторая кнопка
    btn_hol_tandau = tk.Button(
        root,
        text="Подъем на одну руку",
        command=hol_tandau,
        width=25,
        bg="#333333",
        fg="white",
        font=("Helvetica", 14),
        activebackground="#00ff00",  # Цвет при наведении
        activeforeground="#1e1e1e",
        bd=0,  # Убираем рамку
        relief="flat"  # Плоский стиль
    )
    btn_hol_tandau.pack(pady=10)

    btn_bot = tk.Button(
        root,
        text="Тренер BOT",
        command=chatbot_app,
        width=25,
        bg="#333333",
        fg="white",
        font=("Helvetica", 14),
        activebackground="#00ff00",  # Цвет при наведении
        activeforeground="#1e1e1e",
        bd=0,  # Убираем рамку
        relief="flat"  # Плоский стиль
    )
    btn_bot.pack(pady=10)

    # Кнопка для закрытия приложения
    btn_exit = tk.Button(
        root,
        text="Закрыть приложение",
        command=lambda: on_close(root),
        width=25,
        bg="#ff3333",  # Красный цвет кнопки
        fg="white",
        font=("Helvetica", 14),
        activebackground="#ff6666",  # Цвет при наведении
        activeforeground="#1e1e1e",
        bd=0,  # Убираем рамку
        relief="flat"  # Плоский стиль
    )
    btn_exit.pack(pady=10)

    # Декоративная подпись
    footer_label = tk.Label(
        root,
        text="Train Smart, Stay Strong!",
        font=("Helvetica", 10, "italic"),
        fg="#555555",
        bg="#1e1e1e"
    )
    footer_label.pack(side="bottom", pady=(10, 20))

    # Запуск основного цикла
    root.mainloop()


if __name__ == "__main__":
    main()
