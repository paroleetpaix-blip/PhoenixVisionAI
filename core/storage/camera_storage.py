"""
========================================================
PHOENIX VISION AI

Camera Storage

Sauvegarde des caméras

Phoenix Security Technologies
========================================================
"""


from core.storage.database import Database



class CameraStorage:


    def __init__(self):

        self.database = Database()



    def save_cameras(self, cameras):

        data = []


        for camera in cameras:

            data.append(

                camera.to_dict()

            )


        self.database.save(

            "cameras.json",

            data

        )



    def load_cameras(self):

        return self.database.load(

            "cameras.json"

        )