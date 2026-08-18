"""
========================================================
PHOENIX VISION AI

Workspace Controller

Gestion des emplacements caméra dans un écran.

Phoenix Security Technologies
========================================================
"""


class WorkspaceController:


    def __init__(self, workspace):

        self.workspace = workspace

        self.slots = {}



    def create_layout(self, number_of_slots):

        for index in range(1, number_of_slots + 1):

            self.slots[index] = None



    def assign_camera(self, slot, camera):

        if slot not in self.slots:

            raise ValueError(
                "Slot inexistant"
            )


        self.slots[slot] = camera



    def remove_camera(self, slot):

        if slot in self.slots:

            self.slots[slot] = None



    def get_camera(self, slot):

        return self.slots.get(slot)



    def replace_camera(

        self,

        slot,

        new_camera

    ):

        self.assign_camera(

            slot,

            new_camera

        )



    def display_state(self):


        print()

        print(
            "========= WORKSPACE ========="
        )


        for slot, camera in self.slots.items():


            if camera:

                print(

                    f"SLOT {slot} : "

                    f"{camera.name}"

                )

            else:

                print(

                    f"SLOT {slot} : VIDE"

                )


        print()