"""
========================================================
PHOENIX VISION AI

Line

Gestion d'une ligne virtuelle de surveillance.

Phoenix Security Technologies
========================================================
"""


class Line:

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

    def side(self, point):

        x, y = point

        value = (
            (self.x2 - self.x1) * (y - self.y1)
            - (self.y2 - self.y1) * (x - self.x1)
        )

        if value > 0:
            return 1

        if value < 0:
            return -1

        return 0

    def crossed(self, previous_point, current_point):

        previous_side = self.side(previous_point)
        current_side = self.side(current_point)

        if previous_side == 0 or current_side == 0:
            return False

        return previous_side != current_side

    def crossing_direction(
        self,
        previous_point,
        current_point
    ):

        previous_side = self.side(previous_point)
        current_side = self.side(current_point)

        if previous_side == 0 or current_side == 0:

            return None

        if previous_side == current_side:

            return None

        if previous_side < current_side:

            return "IN"

        return "OUT"

    def to_dict(self):

        return {
            "name": self.name,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2
        }