import cv2
import serial
import serial.tools.list_ports
import time
import numpy as np
import os
import mediapipe as mp

GUI_AVAILABLE = os.environ.get('DISPLAY') is not None

def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'Arduino' in port.description or 'ACM' in port.device:
            return port.device
    return None

class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def detect_hand(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        output = frame.copy()
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    output, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                count = self.count_fingers(hand_landmarks)
                cv2.putText(output, f'Fingers: {count}', (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                
                return count, output, "Hand detected"
        
        return 0, output, "No hand detected"
    
    def count_fingers(self, landmarks):
        finger_tips = [8, 12, 16, 20]
        finger_mcps = [6, 10, 14, 18]
        thumb_tip = 4
        thumb_mcp = 2
        
        count = 0
        
        if landmarks.landmark[thumb_tip].x < landmarks.landmark[thumb_mcp].x:
            count += 1
        
        for tip, mcp in zip(finger_tips, finger_mcps):
            if landmarks.landmark[tip].y < landmarks.landmark[mcp].y:
                count += 1
        
        return count

detector = HandDetector()

port = find_arduino_port()
if port is None:
    print("No Arduino found. Please make sure it's connected.")
    exit()

print(f"Found Arduino on port: {port}")

try:
    arduino = serial.Serial(port, 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset
except serial.SerialException as e:
    print(f"Error opening port {port}: {e}")
    exit()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    arduino.close()
    exit()

current_led_states = [0] * 5
last_update_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        frame = cv2.flip(frame, 1)
        finger_count, processed_frame, status = detector.detect_hand(frame)
        
        print(f"\rStatus: {status} | Fingers: {finger_count}", end="", flush=True)
        
        try:
            new_led_states = [1 if i < finger_count else 0 for i in range(5)]
            
            current_time = time.time()
            if new_led_states != current_led_states or (current_time - last_update_time) > 0.5:
                arduino.write(b'L' + bytes(new_led_states))
                current_led_states = new_led_states
                last_update_time = current_time
                
        except serial.SerialException as e:
            print(f"\nError sending data to Arduino: {e}")
            break
        
        if GUI_AVAILABLE:
            cv2.imshow('Hand Detection', processed_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuitting...")
                arduino.write(b'L' + bytes([0] * 5))  # Turn off LEDs before exiting
                arduino.close()  # Close the serial connection
                cap.release()  # Release the webcam
                if GUI_AVAILABLE:
                    cv2.destroyAllWindows()  # Close any open windows
                exit()  # Exit the program

except KeyboardInterrupt:
    print("\nProgram terminated by user")

finally:
    # Turn off all LEDs before closing
    try:
        arduino.write(b'L' + bytes([0] * 5))
        time.sleep(0.1)
    except:
        pass
    
    cap.release()
    if GUI_AVAILABLE:
        cv2.destroyAllWindows()
    arduino.close()