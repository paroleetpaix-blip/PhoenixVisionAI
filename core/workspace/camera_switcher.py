"""
========================================================
PHOENIX VISION AI

Camera Switcher Enterprise

Phoenix Security Technologies
========================================================
"""


class CameraSwitcher:

    def __init__(self, camera_manager):

        self.camera_manager = camera_manager

    # --------------------------------------------------

    def switch(

        self,

        screen,

        slot,

        camera

    ):

        screen.assign_camera(

            slot,

            camera

        )

        return True

    # --------------------------------------------------

    def switch_by_name(

        self,

        screen,

        slot,

        camera_name

    ):

        camera = self.camera_manager.find_by_name(

            camera_name

        )

        if camera is None:

            return False

        screen.assign_camera(

            slot,

            camera

        )

        return True

    # --------------------------------------------------

    def switch_by_uuid(

        self,

        screen,

        slot,

        uuid

    ):

        for camera in self.camera_manager.get_all():

            if camera.uuid == uuid:

                screen.assign_camera(

                    slot,

                    camera

                )

                return True

        return False