import cv2


class VideoWriter:

    def __init__(self, path, fps, width, height):

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        self.writer = cv2.VideoWriter(
            path,
            fourcc,
            fps,
            (width, height)
        )

    def write(self, frame):

        self.writer.write(frame)

    def release(self):

        self.writer.release()