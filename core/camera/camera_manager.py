"""
========================================================
PHOENIX VISION AI

Camera Manager

Phoenix Security Technologies
========================================================
"""

from core.camera.camera import Camera


class CameraManager:

    def __init__(self):

        self.cameras = {}

        self.bootstrap()

    # ---------------------------------
    # Ajouter une caméra
    # ---------------------------------

    def add_camera(
        self,
        name,
        source,
        camera_type="RTSP"
    ):

        camera = Camera(
            name,
            source,
            camera_type
        )

        self.cameras[camera.uuid] = camera

        return camera

    # ---------------------------------
    # Supprimer une caméra
    # ---------------------------------

    def remove_camera(self, camera_uuid):

        if camera_uuid in self.cameras:

            del self.cameras[camera_uuid]

    # ---------------------------------
    # Rechercher une caméra
    # ---------------------------------

    def get_camera(self, camera_uuid):

        return self.cameras.get(camera_uuid)

    # ---------------------------------
    # Toutes les caméras
    # ---------------------------------

    def get_all(self):

        return list(self.cameras.values())

    # ---------------------------------
    # Nombre total
    # ---------------------------------

    def total(self):

        return len(self.cameras)

    # ---------------------------------
    # Caméras ONLINE
    # ---------------------------------

    def online(self):

        return [

            camera

            for camera in self.cameras.values()

            if camera.status.value == "ONLINE"

        ]

    # ---------------------------------
    # Recherche par nom
    # ---------------------------------

    def find_by_name(self, name):

        for camera in self.cameras.values():

            if camera.name == name:

                return camera

        return None

    def all(self):

        return list(
            self.cameras.values()
        )

        # ---------------------------------
    # Création automatique
    # des caméras Enterprise
    # ---------------------------------

    def bootstrap(self):

        default_video = "videos/route.mp4"

        for i in range(1, 10):

            name = f"CAM{i:02d}"

            self.add_camera(

                name,

                default_video,

                "VIDEO"

            )