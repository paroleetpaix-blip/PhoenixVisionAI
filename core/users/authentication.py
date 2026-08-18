"""
========================================================
PHOENIX VISION AI

Authentication

Phoenix Security Technologies
========================================================
"""


class Authentication:


    def __init__(

        self,

        user_manager

    ):

        self.user_manager = user_manager



    def login(

        self,

        username,

        password

    ):

        user = self.user_manager.get(

            username

        )


        if user is None:

            return None


        if not user.enabled:

            return None


        if user.password != password:

            return None


        user.login()

        return user