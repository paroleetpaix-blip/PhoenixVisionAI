"""
========================================================
PHOENIX VISION AI

Config Manager

Gestion de configuration

Phoenix Security Technologies
========================================================
"""


from core.storage.database import Database



class ConfigManager:


    def __init__(self):

        self.database = Database()



    def save_config(
        self,
        config
    ):

        self.database.save(

            "config.json",

            config

        )



    def load_config(self):

        return self.database.load(

            "config.json"

        )