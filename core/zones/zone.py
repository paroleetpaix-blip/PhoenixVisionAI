"""
========================================================
PHOENIX VISION AI

Zone

Phoenix Security Technologies
========================================================
"""


class Zone:

    def __init__(

        self,

        name,

        x1,

        y1,

        x2,

        y2

    ):

        self.name = name

        self.x1 = x1
        self.y1 = y1

        self.x2 = x2
        self.y2 = y2

    def contains(self, point):

        x, y = point

        return (

            self.x1 <= x <= self.x2

            and

            self.y1 <= y <= self.y2

        )

    def to_dict(self):

        return {

            "name": self.name,

            "x1": self.x1,

            "y1": self.y1,

            "x2": self.x2,

            "y2": self.y2

        }