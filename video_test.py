import cv2

video = cv2.VideoCapture("videos/route.mp4")

if not video.isOpened():
    print("Impossible d'ouvrir la vidéo.")
    exit()

while True:
    ret, frame = video.read()

    if not ret:
        print("Fin de la vidéo.")
        break

    cv2.putText(
        frame,
        "PHOENIX VISION AI",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Lecture video", frame)

    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
