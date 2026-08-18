"""
========================================================
PHOENIX VISION AI

Database Manager

Stockage local JSON

Phoenix Security Technologies
========================================================
"""

import json
import os


class Database:


    def __init__(self, path="data"):

        self.path = path

        if not os.path.exists(self.path):

            os.makedirs(self.path)



    def save(
        self,
        filename,
        data
    ):

        file_path = os.path.join(
            self.path,
            filename
        )


        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                default=str
            )



    def load(
        self,
        filename
    ):

        file_path = os.path.join(
            self.path,
            filename
        )


        if not os.path.exists(file_path):

            return None


        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)