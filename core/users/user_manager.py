"""
========================================================
PHOENIX VISION AI

User Manager

Phoenix Security Technologies
========================================================
"""

from core.users.user import User


class UserManager:

    def __init__(self):

        self.users = {}



    def create_user(

        self,

        username,

        password,

        role

    ):

        user = User(

            username,

            password,

            role

        )

        self.users[username] = user

        return user



    def get(

        self,

        username

    ):

        return self.users.get(username)



    def exists(

        self,

        username

    ):

        return username in self.users



    def remove(

        self,

        username

    ):

        if username in self.users:

            del self.users[username]



    def total(self):

        return len(self.users)



    def all(self):

        return list(

            self.users.values()

        )

    def authenticate(

        self,

        username,

        password

    ):

        user = self.get(username)

        if user is None:

            return None

        if user.password != password:

            return None

        return user