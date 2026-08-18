"""
========================================================
PHOENIX VISION AI

Stream Buffer

Phoenix Security Technologies
========================================================
"""


class StreamBuffer:

    def __init__(self):

        self.frame = None

        self.frame_number = 0

    def update(self, frame):

        self.frame = frame

        self.frame_number += 1

    def get_frame(self):

        return self.frame

    def get_frame_number(self):

        return self.frame_number

    def clear(self):

        self.frame = None

        self.frame_number = 0