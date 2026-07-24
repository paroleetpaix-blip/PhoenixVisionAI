"""
========================================================
PHOENIX VISION AI

Tracker

Suivi des objets détectés.

Phoenix Security Technologies
========================================================
"""


class Tracker:


    def __init__(self):

        self.next_id = 1

        self.objects = []



    def update(self, detections):

        tracked = []


        for detection in detections:

            item = {

                "id": self.next_id,

                "label": detection.label,

                "confidence": detection.confidence,

                "bbox": detection.bbox

            }


            tracked.append(item)

            self.next_id += 1


        self.objects = tracked


        return tracked