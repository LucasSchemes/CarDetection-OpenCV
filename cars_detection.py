import cv2 as cv
import numpy as np
import argparse

# centro do retângulo
def calculate_center(x1, y1, x2, y2):
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by OpenCV. You can process both videos and images.')
parser.add_argument('--input', type=str, help='Path to a video or a sequence of image.', default='videoteste.mp4')
parser.add_argument('--algo', type=str, help='Background subtraction method (KNN, MOG2).', default='MOG2')
args = parser.parse_args()

# BGS - parâmetros
if args.algo == 'MOG2':
    backSub = cv.createBackgroundSubtractorMOG2(history=220, varThreshold=15, detectShadows=True)
else:
    backSub = cv.createBackgroundSubtractorKNN()

capture = cv.VideoCapture(cv.samples.findFileOrKeep(args.input))
if not capture.isOpened():
    print('Unable to open: ' + args.input)
    exit(0)

capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

car_count_total = 0  
min_area = 500  
line_y_top_bottom = 350 
line_x_right_left = 1250  
offset = 10  # tolerância para detectar a passagem pela linha
min_lifespan = 10  # Número mínimo de frames consecutivos para considerar um carro real
min_frames_between_counts = 20  # Intervalo mínimo entre contagens de um mesmo carro
max_movement_distance = 50  # distância máxima entre frames -> movimento contínuo
max_speed_threshold = 30  # velocidade máxima 

car_passed = []  
object_lifetimes = {}  # duração de cada objeto e histórico de posições

kernel_open = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))  # Kernel para abertura
kernel_close = cv.getStructuringElement(cv.MORPH_RECT, (15, 15))  # Kernel para fechamento

while True:
    ret, frame = capture.read()
    if frame is None:
        break

    # Máscara de background
    fgMask = backSub.apply(frame)

    # Remover sombras 
    _, fgMask = cv.threshold(fgMask, 254, 255, cv.THRESH_BINARY)

    # remover ruídos
    fgMask = cv.morphologyEx(fgMask, cv.MORPH_OPEN, kernel_open)
    fgMask = cv.morphologyEx(fgMask, cv.MORPH_CLOSE, kernel_close)

    # contornos
    contours, _ = cv.findContours(fgMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    detections = []
    for contour in contours:
        area = cv.contourArea(contour)
        if area > min_area: 
            x, y, w, h = cv.boundingRect(contour)

            
            aspect_ratio = w / float(h)
            if 0.4 < aspect_ratio < 1.5:  # proporção
                detections.append([x, y, x + w, y + h])

    
    cv.line(frame, (0, line_y_top_bottom), (frame.shape[1], line_y_top_bottom), (0, 0, 255), 2)  # Linha horizontal
    cv.line(frame, (line_x_right_left, 0), (line_x_right_left, frame.shape[0]), (0, 255, 0), 2)  # Linha vertical

    # múltiplas detecções
    for detection in detections:
        x1, y1, x2, y2 = detection
        center_x, center_y = calculate_center(x1, y1, x2, y2)

        object_id = len(object_lifetimes)
        for obj_id in object_lifetimes:
            object_center_x, object_center_y = object_lifetimes[obj_id][0][-1]  # Última posição

            # Verificar se é o mesmo objeto -> distância máxima 
            if abs(center_x - object_center_x) < max_movement_distance and abs(center_y - object_center_y) < max_movement_distance:
                object_id = obj_id
                break

        # Histórico do objeto
        if object_id not in object_lifetimes:
            object_lifetimes[object_id] = [[], 0, -min_frames_between_counts]  #lista de posições, vida útil e último frame contado

        object_lifetimes[object_id][1] += 1 
        object_lifetimes[object_id][0].append((center_x, center_y))  #nova posição no histórico

        # Histórico -> máximo de 5 posições
        if len(object_lifetimes[object_id][0]) > 5:
            object_lifetimes[object_id][0].pop(0)

        # Movimento contínuo
        if object_lifetimes[object_id][1] < min_lifespan:
            continue  # Ignorar detecções que não têm movimento contínuo

        # Média das posições para suavizar
        average_x = int(np.mean([pos[0] for pos in object_lifetimes[object_id][0]]))
        average_y = int(np.mean([pos[1] for pos in object_lifetimes[object_id][0]]))

        if len(object_lifetimes[object_id][0]) >= 2:
            last_pos = object_lifetimes[object_id][0][-2]
            speed = np.sqrt((average_x - last_pos[0]) ** 2 + (average_y - last_pos[1]) ** 2)
            if speed > max_speed_threshold:
                continue  # Se o objeto se moveu muito rápido -> provavelmente ruído

        # Verificar se o objeto já passou pela linha e garantir tempo mínimo entre contagens
        if object_lifetimes[object_id][1] > min_lifespan and \
           (object_lifetimes[object_id][1] - object_lifetimes[object_id][2] > min_frames_between_counts):
            if (average_y > line_y_top_bottom - offset and average_y < line_y_top_bottom + offset) or \
               (average_x > line_x_right_left - offset and average_x < line_x_right_left + offset):
                if object_id not in car_passed:
                    car_count_total += 1
                    car_passed.append(object_id)
                    object_lifetimes[object_id][2] = object_lifetimes[object_id][1]  # Atualiza último frame contado
                    print(f"Carro cruzou uma das linhas. Total: {car_count_total}")

    
        cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

   
    cv.rectangle(frame, (10, 2), (200, 20), (255, 255, 255), -1)
    cv.putText(frame, 'Total Car Count: {}'.format(car_count_total), (15, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

   
    cv.imshow('Frame', frame)
    cv.imshow('FG Mask', fgMask)

   
    keyboard = cv.waitKey(30)
    if keyboard == ord('q') or keyboard == 27:
        break

capture.release()
cv.destroyAllWindows()
