"""
========================================================
PHOENIX VISION AI

Workspace Object

Phoenix Security Technologies
========================================================
"""


import uuid


class Workspace:


    def __init__(

        self,

        name,

        screen_id

    ):


        self.uuid = str(uuid.uuid4())

        self.name = name

        self.screen_id = screen_id

        self.cameras = []

        self.owner = None



    def add_camera(

        self,

        camera

    ):


        if camera not in self.cameras:

            self.cameras.append(camera)



    def remove_camera(

        self,

        camera

    ):


        if camera in self.cameras:

            self.cameras.remove(camera)



    def clear(self):

        self.cameras = []



    def camera_count(self):

        return len(self.cameras)

    def set_owner(

        self,

        user

    ):

        self.owner = user



    def to_dict(self):

        return {


            "uuid": self.uuid,

            "name": self.name,

            "owner":

                self.owner.username

                if self.owner

                else None,

            "screen_id": self.screen_id,

            "cameras": [

                camera.name

                for camera in self.cameras

            ]



        }