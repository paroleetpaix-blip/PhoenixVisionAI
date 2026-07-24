"""
========================================================
PHOENIX VISION AI

Video Source Manager

Gestion des sources vidéo

Phoenix Security Technologies
========================================================
"""


import cv2


class VideoSource:

    def __init__(self):

        self.capture = None


    def open(self, source):

        self.capture = cv2.VideoCapture(
            source
        )


        if not self.capture.isOpened():

            raise Exception(
                f"Source impossible : {source}"
            )


    def read(self):

        if self.capture:

            return self.capture.read()

        return False, None


    def release(self):

        if self.capture:

            self.capture.release()