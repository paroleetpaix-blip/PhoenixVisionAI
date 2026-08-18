"""
========================================================
PHOENIX VISION AI

Line Manager

Gestion des lignes virtuelles de surveillance.

Phoenix Security Technologies
========================================================
"""

from core.lines.line import Line


class LineManager:

    def __init__(self):

        self.lines = []

    def add_line(
        self,
        name,
        x1,
        y1,
        x2,
        y2
    ):

        line = Line(
            name,
            x1,
            y1,
            x2,
            y2
        )

        self.lines.append(line)

        return line

    def get_lines(self):

        return self.lines

    def get_line(self, name):

        for line in self.lines:

            if line.name == name:
                return line

        return None

    def check_crossing(
        self,
        previous_point,
        current_point
    ):

        crossed_lines = []

        for line in self.lines:

            if line.crossed(
                previous_point,
                current_point
            ):

                crossed_lines.append(
                    line
                )

        return crossed_lines