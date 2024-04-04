from queue import Queue

from deepface import DeepFace
import cv2

progress_queue = Queue()

def analize_emotions(videopath, video_label) -> float:
    cap = cv2.VideoCapture(videopath)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    positive_emotions_count = 0
    negative_emotions_count = 0

    # print("Analyzing emotions...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        info = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
        emotions = info[0]['emotion']
        
        positive_emotions = emotions['happy'] + emotions['surprise']
        negative_emotions = emotions['disgust'] + emotions['fear'] + emotions['neutral']

        positive_emotions_count += positive_emotions
        negative_emotions_count += negative_emotions

        progress_queue.put((current_frame / total_frames))
        
        if video_label == True:
            emotion_label = max(emotions, key=emotions.get)
            cv2.putText(frame, f"Emotion: {emotion_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            percentage = (current_frame / total_frames) * 100
            cv2.putText(frame, f"Progress: {percentage:.2f}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Emotion Detection", frame)

        # Esc to quit
        if cv2.waitKey(1) == 27:
            break

    total_emotions = positive_emotions_count + negative_emotions_count
    
    if total_emotions == 0:
        confidence = 0
    else:
        confidence = ((positive_emotions_count - negative_emotions_count) / total_emotions) * 100
        confidence = max(0, min(100, confidence))

    # print(f"Total de emociones positivas: {positive_emotions_count}")
    # print(f"Total de emociones negativas: {negative_emotions_count}")
    # print(f"Total de emociones: {total_emotions}")
    # print(f"Porcentaje de confianza para contratar: {confidence:.2f}%")

    cap.release()
    cv2.destroyAllWindows()

    return total_emotions, positive_emotions_count, negative_emotions_count, confidence