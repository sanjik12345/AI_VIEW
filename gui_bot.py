import sys
import json
import re
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QWidget
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder


# Функция для предобработки текста
def preprocess_text(text):
    text = text.lower()  # Приведение текста к нижнему регистру
    text = re.sub(r'[^\w\s]', '', text)  # Удаление знаков препинания
    text = re.sub(r'\d+', '', text)  # Удаление чисел
    text = text.strip()  # Удаление лишних пробелов
    return text


# Загрузка данных
try:
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Файл data.json не найден. Убедитесь, что он находится в текущей директории.")
    sys.exit(1)

if not data:
    print("Файл data.json пустой или не содержит данных.")
    sys.exit(1)

questions = [preprocess_text(item['question']) for item in data]
answers = [item['answer'] for item in data]

# Токенизация вопросов
tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=5000, oov_token="<OOV>")
tokenizer.fit_on_texts(questions)

# Кодирование ответов
label_encoder = LabelEncoder()
label_encoder.fit(answers)

# Загрузка модели
try:
    model = tf.keras.models.load_model('best_model.keras')  # Используем .keras
except (OSError, ValueError):
    print("Ошибка при загрузке модели best_model.keras. Проверьте файл.")
    sys.exit(1)


# Функция для получения ответа
def predict_answer(question):
    try:
        question = preprocess_text(question)
        seq = tokenizer.texts_to_sequences([question])
        padded = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=30, padding='post')
        pred = model.predict(padded)
        answer_index = np.argmax(pred)
        return label_encoder.inverse_transform([answer_index])[0]
    except Exception as e:
        return f"Извините, произошла ошибка: {e}"


# Графический интерфейс
class ChatBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Оффлайн Чат-бот")
        self.setGeometry(100, 100, 400, 500)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Вывод диалога
        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        layout.addWidget(self.chat_output)

        # Поле ввода текста
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Введите сообщение...")
        layout.addWidget(self.chat_input)

        # Кнопка отправки
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.handle_message)
        layout.addWidget(self.send_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_message(self):
        user_input = self.chat_input.text()
        if user_input:
            self.chat_output.append(f"Вы: {user_input}")
            response = predict_answer(user_input)
            self.chat_output.append(f"Бот: {response}")
            self.chat_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatBotApp()
    chatbot.show()
    sys.exit(app.exec_())
