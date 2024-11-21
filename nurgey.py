import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading

# Инициализация движка pyttsx3
engine = pyttsx3.init()

# Функция озвучивания счёта повторений
def speak_count(count):
    engine.say(count)
    engine.runAndWait()

# Функция озвучивания количества подходов
def speak_repit(repit):
    engine.say(f"Подход {repit}")
    engine.runAndWait()

# Функция для вычисления угла между тремя точками
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

# Основная функция для отслеживания упражнений
def left_2h():
    # Инициализация инструментов MediaPipe
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Открытие видеопотока
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Переменные для отслеживания
    counter = 0
    stage = None
    repit = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Обработка кадра
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                # Извлечение ключевых точек
                landmarks = results.pose_landmarks.landmark

                # Координаты левой и правой руки
                left = {
                    'shoulder': [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                    'elbow': [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
                    'wrist': [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                }
                right = {
                    'shoulder': [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
                    'elbow': [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y],
                    'wrist': [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                }

                # Расчёт углов для обеих рук
                left_angle = calculate_angle(left['shoulder'], left['elbow'], left['wrist'])
                right_angle = calculate_angle(right['shoulder'], right['elbow'], right['wrist'])

                # Логика счёта повторений: обе руки должны быть подняты
                if left_angle > 160 and right_angle > 160:
                    stage = "down"
                if left_angle < 30 and right_angle < 30 and stage == "down":
                    stage = "up"
                    counter += 1
                    print(f"Повторение: {counter}")
                    threading.Thread(target=speak_count, args=(counter,)).start()

                    if counter == 10:  # Каждые 10 повторений = 1 подход
                        counter = 0
                        repit += 1
                        print(f"Подход: {repit}")
                        threading.Thread(target=speak_repit, args=(repit,)).start()

                # Отображение углов на экране
                left_elbow_pos = tuple(np.multiply(left['elbow'], [640, 480]).astype(int))
                right_elbow_pos = tuple(np.multiply(right['elbow'], [640, 480]).astype(int))
                cv2.putText(image, f"L: {int(left_angle)}", left_elbow_pos,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(image, f"R: {int(right_angle)}", right_elbow_pos,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            except Exception as ex:
                print(f"Ошибка: {ex}")

            # Интерфейс
            cv2.rectangle(image, (0, 0), (270, 78), (245, 117, 16), -1)
            cv2.putText(image, 'REPS', (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(image, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            cv2.putText(image, 'STAGE', (65, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(image, stage if stage else '-', (90, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            cv2.putText(image, 'REPEAT', (580, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(image, str(repit), (580, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

            # Рисование позы
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            cv2.imshow('Mediapipe Feed', image)

            # Выход при нажатии 'q' или 'Esc'
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q') or key == 27:  # 27 — код клавиши Esc
                break

    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()

# Запуск функции
