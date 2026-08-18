"""
========================================================
PHOENIX VISION AI

Workspace Manager

Phoenix Security Technologies
========================================================
"""


from core.workspace.workspace import Workspace



class WorkspaceManager:


    def __init__(self):

        self.workspaces = {}



    def create_workspace(

        self,

        name,

        screen_id

    ):


        workspace = Workspace(

            name,

            screen_id

        )


        self.workspaces[workspace.uuid] = workspace


        return workspace



    def get_workspace(

        self,

        workspace_uuid

    ):


        return self.workspaces.get(

            workspace_uuid

        )



    def all(self):


        return list(

            self.workspaces.values()

        )



    def total(self):

        return len(self.workspaces)