"""
========================================================
PHOENIX VISION AI

License Manager

Phoenix Security Technologies
========================================================
"""


class LicenseManager:

    def __init__(self):

        self.license_key = "COMMUNITY"

        self.edition = "Community"

        self.client = "LOCAL"



    def load(self):

        print(
            f"Licence : {self.edition}"
        )



    def info(self):

        return {

            "license": self.license_key,

            "edition": self.edition,

            "client": self.client

        }