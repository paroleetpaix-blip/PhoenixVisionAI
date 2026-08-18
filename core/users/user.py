"""
========================================================
PHOENIX VISION AI

User Object

Phoenix Security Technologies
========================================================
"""

import uuid

from datetime import datetime

from core.users.roles import UserRole

from core.users.permissions import PERMISSIONS


class User:

    def __init__(

        self,

        username,

        password,

        role=UserRole.OPERATOR

    ):

        self.uuid = str(uuid.uuid4())

        self.username = username

        self.password = password

        self.role = role

        self.permissions = PERMISSIONS[role.value]

        self.workspace = None

        self.last_login = None

        self.enabled = True



    def login(self):

        self.last_login = datetime.now()



    def assign_workspace(

        self,

        workspace

    ):

        self.workspace = workspace

        workspace.set_owner(self)



    def has_permission(

        self,

        permission

    ):

        if "ALL" in self.permissions:

            return True

        return permission in self.permissions



    def disable(self):

        self.enabled = False



    def enable(self):

        self.enabled = True



    def to_dict(self):

        return {

            "uuid": self.uuid,

            "username": self.username,

            "role": self.role.value,

            "workspace":

                self.workspace.name

                if self.workspace

                else None,

            "enabled": self.enabled,

            "last_login":

                str(self.last_login)

                if self.last_login

                else None

        }