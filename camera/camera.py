import cv2

class Camera:

    def __init__(self, camera_id=0):
        self.camera = cv2.VideoCapture(camera_id)

    def is_open(self):
        return self.camera.isOpened()

    def read(self):
        return self.camera.read()

    def release(self):
        self.camera.release()
        