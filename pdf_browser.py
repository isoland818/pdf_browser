"""
    author: Isoland
    date: 2023.01.12
"""


# import libraries
import cv2
import numpy as np
import mediapipe as mp
import math


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
    if delta_y < 100 and delta_x < 100:
        return -1
    if delta_x == 0:
        direction = delta_y / abs(delta_y)
    else: 
        slope = delta_y / delta_x
        if -1 < slope <= 1:
            direction = 2 * delta_x / abs(delta_x)
        else: 
            direction = 2 * delta_y / abs(delta_y)
    return direction+2

on = False
L1=0
L2=0
while True:
    ret, frame = cap.read()

    # process each frame
    frame = cv2.flip(frame, 1)

    # process frame
    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame)

    # draw the hand annotations on the frame
    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        # iterate through hands
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            x_list=[]
            y_list=[]

            for hand_landmark in hand_landmarks.landmark:
                x_list.append(hand_landmark.x)
                y_list.append(hand_landmark.y)

            index_finger_X = int(x_list[8] * screen_width)
            index_finger_Y = int(y_list[8] * screen_height)
            mid_finger_X = int(x_list[12] * screen_width)
            mid_finger_Y = int(y_list[12] * screen_height)

            finger_dis = math.hypot((index_finger_X-mid_finger_X), (index_finger_Y-mid_finger_Y))

            prev_direc = -1
            prev_x = 0
            prev_y = 0
            # whether termination
            if finger_dis < 60:
                direction = get_direction(prev_x, prev_y, (index_finger_X+mid_finger_X)/2, (index_finger_Y+mid_finger_Y)/2)
                if direction == prev_direc:
                    print(direction)
                    prev_direc=direction
            else:
                prev_direc=0

    # show each frame
    cv2.imshow("demo", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break



# release resources
cap.release()
cv2.destoryAllWindows()



