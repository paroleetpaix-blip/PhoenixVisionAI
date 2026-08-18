"""
========================================================
PHOENIX VISION AI

Screen

Phoenix Security Technologies
========================================================
"""

import uuid


class Screen:

    def __init__(self, name):

        self.uuid = str(uuid.uuid4())

        self.name = name

        # 4 emplacements vidéo
        self.slots = [

            None,

            None,

            None,

            None

        ]

    def assign_camera(

        self,

        slot,

        camera

    ):

        if 0 <= slot < 4:

            self.slots[slot] = camera

    def remove_camera(

        self,

        slot

    ):

        if 0 <= slot < 4:

            self.slots[slot] = None

    def get_camera(

        self,

        slot

    ):

        if 0 <= slot < 4:

            return self.slots[slot]

        return None

    def get_slots(self):

        return self.slots

    def swap_camera(

        self,

        slot,

        new_camera

    ):

        if 0 <= slot < 4:

            self.slots[slot] = new_camera

    def to_dict(self):

        cameras = []

        for camera in self.slots:

            if camera is None:

                cameras.append(None)

            else:

                cameras.append(camera.name)

        return {

            "uuid": self.uuid,

            "name": self.name,

            "slots": cameras

        }