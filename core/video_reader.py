import cv2


class VideoReader:

    def __init__(self, path):

        self.path = path
        self.capture = None

    def open(self):

        self.capture = cv2.VideoCapture(self.path)

        if not self.capture.isOpened():
            raise Exception(f"Impossible d'ouvrir : {self.path}")

    def read(self):

        return self.capture.read()

    def release(self):

        if self.capture:
            self.capture.release()

    def fps(self):

        return int(self.capture.get(cv2.CAP_PROP_FPS))

    def width(self):

        return int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    def height(self):

        return int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))