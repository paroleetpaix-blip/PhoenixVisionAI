"""
========================================================
PHOENIX VISION AI

Session Manager

Phoenix Security Technologies
========================================================
"""

from datetime import datetime


class SessionManager:

    def __init__(self):

        self.current_user = None

        self.login_time = None


    def login(self, user):

        self.current_user = user

        self.login_time = datetime.now()


    def logout(self):

        self.current_user = None

        self.login_time = None


    def is_logged(self):

        return self.current_user is not None


    def get_user(self):

        return self.current_user


    def get_workspace(self):

        if self.current_user:

            return self.current_user.workspace

        return None


    def info(self):

        if not self.current_user:

            return None

        return {

            "username": self.current_user.username,

            "role": self.current_user.role.value,

            "workspace":

                self.current_user.workspace.name

                if self.current_user.workspace

                else None,

            "login_time":

                str(self.login_time)

        }