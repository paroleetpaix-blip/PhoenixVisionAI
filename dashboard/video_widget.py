"""
========================================================
PHOENIX VISION AI

Video Widget

Affichage du flux vidéo

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

import cv2

from PySide6.QtWidgets import QLabel

from PySide6.QtGui import QImage, QPixmap

from PySide6.QtCore import QTimer


class VideoWidget(QLabel):

    def __init__(self):

        super().__init__()

        self.setMinimumSize(
            800,
            450
        )

        self.capture = None


        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_frame
        )


    def open_video(self, path):

        self.capture = cv2.VideoCapture(
            path
        )


        if not self.capture.isOpened():

            raise Exception(
                f"Impossible d'ouvrir {path}"
            )


        self.timer.start(30)



    def update_frame(self):

        if self.capture is None:

            return


        ret, frame = self.capture.read()


        if not ret:

            self.timer.stop()

            return


        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        height, width, channel = frame.shape


        bytes_per_line = channel * width


        image = QImage(
            frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        )


        self.setPixmap(
            QPixmap.fromImage(image)
        )


    def close_video(self):

        self.timer.stop()


        if self.capture:

            self.capture.release()