"""
========================================================
PHOENIX VISION AI

Vehicle Search Engine

Phoenix Security Technologies
========================================================
"""


class SearchEngine:

    def __init__(self, database):

        self.database = database


    def search_by_uuid(self, uuid):

        return self.database.find_by_uuid(uuid)


    def search_by_plate(self, plate):

        return self.database.find_by_plate(plate)


    def search_by_color(self, color):

        return self.database.find_by_color(color)


    def search_by_brand(self, brand):

        return self.database.find_by_brand(brand)


    def search_by_model(self, model):

        return self.database.find_by_model(model)


    def search_by_threat(self, level):

        return self.database.find_by_threat(level)