import cv2
import mediapipe as mp
import random
import time

# MediaPipe Hands for finger tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Quiz data
quiz_questions = [
   {"question": "Apa itu HTML?", "choices": ["Bahasa Pemrograman", "Bahasa Markup", "Bahasa Mesin"], "answer": 1},
    {"question": "Apa ekstensi file untuk JavaScript?", "choices": [".js", ".java", ".jsx"], "answer": 0},
    {"question": "Apa fungsi utama dari CSS?", "choices": ["Membuat logika program", "Menyusun layout", "Mempercantik tampilan"], "answer": 2},
    {"question": "Apa itu loop dalam pemrograman?", "choices": ["Pernyataan bersyarat", "Pengulangan", "Array"], "answer": 1},
    {"question": "Apa simbol untuk operator penambahan di Python?", "choices": ["+", "-", "*"], "answer": 0},
    {"question": "Apa itu variabel?", "choices": ["Penyimpanan data", "Operasi matematika", "Fungsi"], "answer": 0},
    {"question": "Apa peran dari `if` dalam coding?", "choices": ["Melakukan pengulangan", "Membuat percabangan logika", "Menentukan variabel"], "answer": 1},
    {"question": "Apa itu array?", "choices": ["Tipe data tunggal", "Tipe data berganda", "Pengulangan"], "answer": 1},
    {"question": "Apa ekstensi file untuk Python?", "choices": [".py", ".java", ".cpp"], "answer": 0},
    {"question": "Apa fungsi utama dari Git?", "choices": ["Menghapus file", "Version control", "Membuat layout"], "answer": 1},
    {"question": "Apa itu IDE?", "choices": ["Tempat menyimpan data", "Editor kode", "Framework"], "answer": 1},
    {"question": "Apa itu `for` dalam coding?", "choices": ["Looping", "Variabel", "Pernyataan kondisi"], "answer": 0},
    {"question": "Apa fungsi `print()`?", "choices": ["Menghapus data", "Menampilkan output", "Menghentikan program"], "answer": 1},
    {"question": "Apa nama simbol untuk komentar di Python?", "choices": ["#", "//", "/*"], "answer": 0},
    {"question": "Apa itu fungsi dalam pemrograman?", "choices": ["Sebuah tipe data", "Kumpulan perintah", "Operator"], "answer": 1},
    {"question": "Apa itu debugging?", "choices": ["Memperbaiki error", "Membuat script", "Menjalankan aplikasi"], "answer": 0},
    {"question": "Apa itu database?", "choices": ["Tempat penyimpanan data", "Bahasa pemrograman", "Editor kode"], "answer": 0},
    {"question": "Apa itu API?", "choices": ["Aplikasi game", "Interface untuk program", "Bahasa pemrograman"], "answer": 1},
    {"question": "Apa ekstensi file untuk CSS?", "choices": [".css", ".html", ".js"], "answer": 0},
    {"question": "Apa itu framework?", "choices": ["Kerangka kerja", "Bahasa pemrograman", "Editor kode"], "answer": 0},
]

# Score tracking
score = 0
used_questions = []
current_question = None
last_click_time = 0  # Time of the last registered click
click_delay = 1.0  # Minimum delay between clicks in seconds
answered = False  # Flag to ensure only one answer per question
touch_distance_threshold = 15  # Adjusted maximum distance in pixels for fingers to be considered "touching"

# OpenCV setup
cap = cv2.VideoCapture(0)

# Game state variables
game_started = False
game_ended = False
restart_prompt = False

def draw_button(frame, text, position, color=(0, 255, 0)):
    """Draw a button on the frame."""
    x, y = position
    cv2.rectangle(frame, (x, y), (x + 200, y + 60), color, -1)
    cv2.putText(frame, text, (x + 20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for natural interaction
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Process the frame with MediaPipe Hands
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # Game Start Button
    if not game_started and not restart_prompt:
        draw_button(frame, "Start Game", (w // 2 - 100, h // 2 - 30), (0, 255, 0))
        draw_button(frame, "Exit", (w // 2 - 100, h // 2 + 50), (0, 0, 255))
        
        # Check if Start button is clicked
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Get index finger tip coordinates
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Check if the index finger is in the "Start Game" button area
                if w // 2 - 100 < index_x < w // 2 + 100 and h // 2 - 30 < index_y < h // 2 + 30:
                    game_started = True
                    break
                
                # Check if Exit button is clicked
                if w // 2 - 100 < index_x < w // 2 + 100 and h // 2 + 50 < index_y < h // 2 + 110:
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

    if game_started and not game_ended:
        # Pick a new question if all questions are used or current question is None
        if len(used_questions) == len(quiz_questions):
            used_questions = []
        if current_question is None or current_question in used_questions:
            while True:
                current_question = random.randint(0, len(quiz_questions) - 1)
                if current_question not in used_questions:
                    used_questions.append(current_question)
                    answered = False  # Reset answered flag for the new question
                    break

        question_data = quiz_questions[current_question]

        # Draw landmarks and handle interaction
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get index finger tip and thumb tip coordinates
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # Convert to pixel coordinates
                index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)

                # Calculate distance between index finger tip and thumb tip
                distance = ((index_x - thumb_x) ** 2 + (index_y - thumb_y) ** 2) ** 0.5

                # Highlight the tip of the index finger
                cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), -1)

                # Detect if finger is over a choice
                for i, choice in enumerate(question_data["choices"]):
                    choice_x1, choice_y1 = 50, 150 + i * 50
                    choice_x2, choice_y2 = 400, 200 + i * 50

                    if choice_x1 < index_x < choice_x2 and choice_y1 < index_y < choice_y2:
                        # Highlight the selected choice
                        cv2.rectangle(frame, (choice_x1, choice_y1), (choice_x2, choice_y2), (0, 255, 255), -1)

                        # Check for "click" gesture when fingers are touching
                        current_time = time.time()
                        if distance < touch_distance_threshold and not answered and (current_time - last_click_time > click_delay):
                            last_click_time = current_time
                            answered = True  # Mark question as answered
                            if i == question_data["answer"]:
                                score += 10
                                color = (0, 255, 0)
                                feedback = "Benar!"
                            else:
                                color = (0, 0, 255)
                                feedback = "Salah!"

                            # Display feedback briefly
                            cv2.rectangle(frame, (choice_x1, choice_y1), (choice_x2, choice_y2), color, -1)
                            cv2.putText(frame, feedback, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                            # Move to the next question after feedback
                            current_question = None  # Reset the question so the next question is selected

                            # Check if score reaches 100
                            if score >= 100:
                                game_ended = True
                                restart_prompt = True
                            break

        # Display the current question
        cv2.putText(frame, question_data["question"], (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the choices
        for i, choice in enumerate(question_data["choices"]):
            choice_text = f"{i + 1}. {choice}"
            x1, y1 = 50, 150 + i * 50
            x2, y2 = 400, 200 + i * 50

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(frame, choice_text, (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display the score
        cv2.putText(frame, f"Score: {score}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # End game prompt
    if restart_prompt:
        cv2.putText(frame, "Selamat! Anda mencapai skor 100!", (50, h // 2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        draw_button(frame, "Restart", (w // 2 - 100, h // 2), (0, 255, 0))
        draw_button(frame, "Exit", (w // 2 - 100, h // 2 + 70), (0, 0, 255))

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Check if Restart button is clicked
                if w // 2 - 100 < index_x < w // 2 + 100 and h // 2 < index_y < h // 2 + 60:
                    game_started = False
                    game_ended = False
                    restart_prompt = False
                    score = 0  # Reset score
                    used_questions = []  # Reset used questions

                # Check if Exit button is clicked
                if w // 2 - 100 < index_x < w // 2 + 100 and h // 2 + 70 < index_y < h // 2 + 130:
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

    # Show the frame
    cv2.imshow('Quiz Game', frame)

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()