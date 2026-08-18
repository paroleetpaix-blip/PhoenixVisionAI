"""
========================================================
PHOENIX VISION AI

Camera Layout

Phoenix Security Technologies
========================================================
"""


class CameraLayout:

    LAYOUTS = {

        1: (1, 1),

        2: (1, 2),

        3: (2, 2),

        4: (2, 2),

        5: (2, 3),

        6: (2, 3),

        7: (3, 3),

        8: (3, 3),

        9: (3, 3),

        10: (3, 4),

        11: (3, 4),

        12: (3, 4),

        13: (4, 4),

        14: (4, 4),

        15: (4, 4),

        16: (4, 4)

    }

    @classmethod
    def get_layout(cls, total):

        return cls.LAYOUTS.get(total, (4, 4))