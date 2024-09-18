import cv2
import numpy as np
import mss
import pytesseract
import time
from keys import PressKey, ReleaseKey, up, left, down, right, nitro

# Ustawienia Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Parametry prędkości i drogi
speedLimit = 400
lastKeypressConfig = {
    up: False,
    left: False,
    down: False,
    right: False,
}
delayBetweenInputs = 0.1
road = []
speed = 0

def extract_speed_ui(image, width, height):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    custom_config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(gray_image, config=custom_config)
    text = text.strip()
    try:
        speed = float(text)
    except ValueError:
        speed = 0.0
    return speed

def detect_blue_line(minimap):
    minimap_hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
    lower_line = np.array([90, 150, 150])
    upper_line = np.array([130, 255, 255])
    mask_line = cv2.inRange(minimap_hsv, lower_line, upper_line)
    contours, _ = cv2.findContours(mask_line, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    line_points = [tuple(point[0]) for contour in contours for point in contour]
    return line_points

def draw_player_position(minimap, blue_line_points):
    center_x = minimap.shape[1] // 2
    center_y = minimap.shape[0] // 2
    player_position = (center_x + 17, center_y + 62)
    if blue_line_points:
        for point in blue_line_points:
            cv2.circle(minimap, point, 2, (0, 255, 0), -1)
    cv2.circle(minimap, player_position, 5, (0, 0, 255), -1)

def draw_detection_area(minimap, area):
    x1, y1, w, h = area
    x2, y2 = x1 + w, y1 + h
    cv2.rectangle(minimap, (x1, y1), (x2, y2), (255, 0, 0), 2)

def changeKeyState(newPressConfig, blue_line_points):
    global speed, frame, lastKeypressConfig

    pressed = {
        up: False,
        down: False,
        left: False,
        right: False,
        nitro: False
    }

    # Sterowanie prędkością
    if speed < speedLimit * 8 / 10 and len(road) > 0 and abs(road[0]) < 2:
        PressKey(up)
        PressKey(nitro)
        ReleaseKey(down)
        pressed[up] = True
        pressed[nitro] = True
    elif speed < speedLimit:
        PressKey(up)
        ReleaseKey(down)
        ReleaseKey(nitro)
        pressed[up] = True
    elif speed < speedLimit * 12 / 10:
        ReleaseKey(up)
        ReleaseKey(down)
        ReleaseKey(nitro)
    else:
        ReleaseKey(up)
        PressKey(down)
        ReleaseKey(nitro)
        pressed[down] = True

    # Obsługa dodatkowych klawiszy: lewo, prawo
    for key in [left, right]:
        if key in newPressConfig and newPressConfig[key]:
            PressKey(key)
            pressed[key] = True
        else:
            ReleaseKey(key)
            pressed[key] = False

    # Wyświetlanie naciśniętych klawiszy na ekranie
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.8
    fontColor = (255, 255, 255)
    lineType = 3

    visualButtons = [
        ('up', (400, 450), pressed[up]),
        ('down', (400, 500), pressed[down]),
        ('left', (325, 500), pressed[left]),
        ('right', (500, 500), pressed[right]),
        ('nitro', (575, 475), pressed[nitro])
    ]

    for visual in visualButtons:
        cv2.putText(frame,
                    visual[0],
                    visual[1],
                    font,
                    fontScale,
                    (255, 0, 0) if visual[2] else fontColor,
                    lineType)

if __name__ == "__main__":
    width, height = 1920, 1080
    gameScreen = {'top': 25, 'left': 0, 'width': width, 'height': height}
    sct = mss.mss()

    while True:
        screen = np.array(sct.grab(gameScreen))
        screen = np.flip(screen[:, :, :3], 2)
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        
        aiHeight = int(height / 2)
        aiWidth = int(width / 2)
        frame = cv2.resize(screen.copy(), (aiWidth, aiHeight))

        speed_region = (38, 435, 110, 470)
        x1, y1, x2, y2 = speed_region
        speed_image = frame[y1:y2, x1:x2]

        speed = extract_speed_ui(speed_image, x2 - x1, y2 - y1)
        speed = round(speed)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        minimap_center_x = int(aiWidth * 91.5 / 100)
        minimap_center_y = int(aiHeight * 83 / 100)
        minimap_size = 34

        x1_mini = max(minimap_center_x - minimap_size, 0)
        x2_mini = min(minimap_center_x + minimap_size, aiWidth)
        y1_mini = max(minimap_center_y - minimap_size, 0)
        y2_mini = min(minimap_center_y + minimap_size, aiHeight)

        minimap = frame[y1_mini:y2_mini, x1_mini:x2_mini]
        scale_factor = 2
        minimap = cv2.resize(minimap, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

        blue_line_points = detect_blue_line(minimap)
        draw_player_position(minimap, blue_line_points)

        minimap_display = cv2.resize(minimap, (x2_mini - x1_mini, y2_mini - y1_mini))
        frame[y1_mini:y2_mini, x1_mini:x2_mini] = minimap_display

        cv2.putText(frame, f'{speed}', (78, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)

        changeKeyState({
            up: speed < speedLimit,
            down: speed >= speedLimit * 12 / 10,
            left: False,  # Przygotuj logikę do obsługi lewego kierunku
            right: False,  # Przygotuj logikę do obsługi prawego kierunku
            nitro: speed < speedLimit * 8 / 10
        }, blue_line_points)

        cv2.imshow('Full Frame', frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
