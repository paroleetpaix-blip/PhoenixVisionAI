"""
========================================================
PHOENIX VISION AI
tracker.py

Tracker Enterprise

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

import math


class Tracker:

    def __init__(self):

        self.next_id = 1

        self.tracks = []

        self.max_distance = 50


    def _center(self, bbox):

        x1, y1, x2, y2 = bbox

        return (
            (x1 + x2) / 2,
            (y1 + y2) / 2
        )


    def _distance(self, box1, box2):

        c1 = self._center(box1)

        c2 = self._center(box2)

        return math.sqrt(

            (c1[0] - c2[0]) ** 2 +

            (c1[1] - c2[1]) ** 2

        )


    def update(self, detections):

        updated_tracks = []


        for detection in detections:

            assigned = False


            for track in self.tracks:

                if (

                    track.label == detection.label

                    and

                    self._distance(

                        track.bbox,

                        detection.bbox

                    ) < self.max_distance

                ):

                    detection.id = track.id

                    detection.counted = track.counted

                    assigned = True

                    break


            if not assigned:

                detection.id = self.next_id

                self.next_id += 1


            updated_tracks.append(detection)


        self.tracks = updated_tracks

        return updated_tracks


    def reset(self):

        self.next_id = 1

        self.tracks = []