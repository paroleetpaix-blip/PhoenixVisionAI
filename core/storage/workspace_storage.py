"""
========================================================
PHOENIX VISION AI

Workspace Storage

Sauvegarde des écrans virtuels

Phoenix Security Technologies
========================================================
"""


from core.storage.database import Database



class WorkspaceStorage:


    def __init__(self):

        self.database = Database()



    def save_workspaces(self, workspaces):

        data = []


        for workspace in workspaces:

            data.append(

                workspace.to_dict()

            )


        self.database.save(

            "workspaces.json",

            data

        )



    def load_workspaces(self):

        return self.database.load(

            "workspaces.json"

        )