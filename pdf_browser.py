"""
    author: Isoland
    date: 2023.01.12
"""


# import libraries
import cv2
import numpy as np
import mediapipe as mp
import math
import time
import win32con
import ctypes
import win32api



# Capture video
cap = cv2.VideoCapture(0)

# mediapipe configuration
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    model_complexity = 0,
    static_image_mode = False, 
    max_num_hands = 2, 
    min_detection_confidence = 0.5, 
    min_tracking_confidence = 0.5
)

# screen parameters
screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


def get_direction(prev_x, prev_y, x, y):
    if prev_x * prev_y == 0:
        return -1
    delta_x = x - prev_x
    delta_y = y - prev_y
    if abs(delta_y) < 75 and abs(delta_x) < 75:
        return -1
    if delta_x == 0:
        direction = 1 if delta_y > 0 else -1
    else: 
        slope = delta_y / delta_x
        print("proper line, {}", slope)
        if -1 < slope <= 1:
            direction = 2 * delta_x / abs(delta_x)
        else: 
            direction = delta_y / abs(delta_y)
    return int(direction)+2

def control(direction):
    key_code = [37, 38, 0, 40, 39]
    mvka = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(key_code[direction], 0, 0, 0)
    win32api.keybd_event(key_code[direction], 0, win32con.KEYEVENTF_KEYUP, 0)

on = False
L1=0
L2=0
prev_direc = -1
new_command = True
while True:
    ret, frame = cap.read()

    # process each frame
    frame = cv2.flip(frame, 1)

    # process frame
    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame)

    
    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        # iterate through hands
        for hand_landmarks in results.multi_hand_landmarks:
            x_list=[]
            y_list=[]

            for hand_landmark in hand_landmarks.landmark:
                x_list.append(hand_landmark.x)
                y_list.append(hand_landmark.y)

            index_finger_X = int(x_list[8] * screen_width)
            index_finger_Y = int(y_list[8] * screen_height)
            mid_finger_X = int(x_list[12] * screen_width)
            mid_finger_Y = int(y_list[12] * screen_height)
            x = (index_finger_X+mid_finger_X)/2
            y = (index_finger_Y+mid_finger_Y)/2

            finger_dis = math.hypot((index_finger_X-mid_finger_X), (index_finger_Y-mid_finger_Y))

            # whether termination
            if finger_dis < 30:
                if new_command:
                    prev_x = x
                    prev_y = y
                    new_command = False
                    time.sleep(0.3)
                else:
                    direction = get_direction(prev_x, prev_y, x, y)
                    cv2.line(frame, (int(prev_x), int(prev_y)), (int(x),int(y)), (255,0,0), 10, cv2.LINE_4)
                    if direction != -1:
                        control(direction)
                        new_command = True
                        time.sleep(1)
                        
            else:
                new_command = True
            break
    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break



# release resources
cap.release()
cv2.destoryAllWindows()



