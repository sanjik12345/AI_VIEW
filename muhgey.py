import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading


def hol_tandau(e=None):
    # Функция озвучивания счёта
    def speak_count(count):
        engine = pyttsx3.init()
        engine.say(count)
        engine.runAndWait()

    # Функция озвучивания количества подходов
    def speak_repit(repit):
        engine = pyttsx3.init()
        engine.say(f"Подход {repit}")
        engine.runAndWait()

    # Функция для вычисления угла между тремя точками
    def calculate_angle(a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180 else angle

    # Настройка MediaPipe
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Инициализация камеры
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Переменные для счёта
    counter, stage, selected_hand, repit = 0, None, None, 0

    # Основной цикл обработки
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
                # Извлечение координат
                landmarks = results.pose_landmarks.landmark
                left = {
                    'shoulder': [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                    'elbow': [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
                    'wrist': [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y],
                }
                right = {
                    'shoulder': [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
                    'elbow': [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y],
                    'wrist': [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y],
                }

                # Выбор руки
                if selected_hand is None:
                    if left['wrist'][1] < left['shoulder'][1]:
                        selected_hand = "left"
                        print("Выбрана левая рука")
                    elif right['wrist'][1] < right['shoulder'][1]:
                        selected_hand = "right"
                        print("Выбрана правая рука")

                # Расчёт угла
                if selected_hand:
                    hand = left if selected_hand == "left" else right
                    angle = calculate_angle(hand['shoulder'], hand['elbow'], hand['wrist'])

                    # Логика счёта
                    if angle > 160:
                        stage = "down"
                    if angle < 30 and stage == "down":
                        stage = "up"
                        counter += 1
                        print(f"Повторение: {counter}")
                        threading.Thread(target=speak_count, args=(counter,)).start()

                        if counter == 10:
                            counter = 0
                            repit += 1
                            print(f"Подход: {repit}")
                            threading.Thread(target=speak_repit, args=(repit,)).start()

                    # Отображение угла на изображении
                    elbow_pos = tuple(np.multiply(hand['elbow'], [640, 480]).astype(int))
                    cv2.putText(image, str(int(angle)), elbow_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            except Exception as ex:
                print(f"Ошибка: {ex}")

            # Интерфейс отображения
            cv2.rectangle(image, (0, 0), (270, 78), (245, 117, 16), -1)
            cv2.rectangle(image, (565, 0), (665, 78), (245, 117, 16), -1)

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

            # Отображение изображения
            cv2.imshow('Mediapipe Feed', image)

            # Выход при нажатии 'q'
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()
