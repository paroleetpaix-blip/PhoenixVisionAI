import cv2
from camera.camera import Camera

print("=" * 50)
print("PHOENIX VISION AI")
print("=" * 50)

camera = Camera()

if not camera.is_open():
    print("Impossible d'ouvrir la caméra.")
    exit()

while True:

    ret, frame = camera.read()

    if not ret:
        break

    cv2.putText(
        frame,
        "Phoenix Vision AI",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("Phoenix Vision AI", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
