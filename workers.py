# Импортируем нужные нам модули
import imutils
import cv2
import numpy as np
from avg_colour import BackgroundColorDetector
# Обозначаем переменные
FRAMES_TO_PERSIST = 10
MIN_SIZE_FOR_MOVEMENT = 2000
MOVEMENT_DETECTED_PERSISTENCE = 100
first_frame = None
next_frame = None
font = cv2.FONT_HERSHEY_SIMPLEX
delay_counter = 0
flag_count = 0
flag_back = None
mp_counter = 0
flag = True
# Запускаем видео
cap = cv2.VideoCapture('test.mkv')

while(cap.isOpened()):
    flag_count += 1
    transient_movement_flag = False

    ret, frame = cap.read()
    # каждые 200 кадров проверяем цвет фона
    if flag_count == 200:
        flag = True

    if flag == True:
        f = BackgroundColorDetector(frame).detect()
        try:
            if (sum1 - sum(list(f))) > 50:
                flag_back = True
        except:
            pass
        sum1 = sum(list(f))
        flag = False
        flag_count = 0

    # Ресайзим и сохраняем бинаризованное изображение
    frame = imutils.resize(frame, width=750)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Удаляем шумы
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None: first_frame = gray
    delay_counter += 1
    if delay_counter > FRAMES_TO_PERSIST:
        delay_counter = 0
        first_frame = next_frame
    next_frame = gray
    # Сравниваем кадры для нахождения разницы и находим контуры
    frame_delta = cv2.absdiff(first_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts, f = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Цикл по контурам
    for c in cnts:
        # Сохраняем все найденные контуры
        (x, y, w, h) = cv2.boundingRect(c)
        #  Если контуры маленькие игнорим их, если нет, значит это движение
        if cv2.contourArea(c) > MIN_SIZE_FOR_MOVEMENT:
            transient_movement_flag = True
            # Рисуем прямоугольники у движущихся объектов
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Если что-то двинулось - обновляем счетчик
    if transient_movement_flag == True:
        movement_persistent_flag = True
        mp_counter = MOVEMENT_DETECTED_PERSISTENCE

    # Если человек меняет фон или что-то двигает, значит он работает
    if mp_counter > 0 or flag_back == True:
        text = "Working " + str(mp_counter)
        mp_counter -= 1
    else:
        text = "Resting"
    # Работаем со шрифтом
    cv2.putText(frame, str(text), (10, 35), font, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
    # черно-белый анализ кадра
    frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR)
    # выводим все, что сделали
    cv2.imshow("frame", np.hstack((frame_delta, frame)))
    ch = cv2.waitKey(1)
    if ch & 0xFF == ord('q'):
        break

cv2.waitKey(0)
cv2.destroyAllWindows()
cap.release()