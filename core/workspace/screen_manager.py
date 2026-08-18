"""
========================================================
PHOENIX VISION AI

Screen Manager

Phoenix Security Technologies
========================================================
"""

from core.workspace.screen import Screen


class ScreenManager:

    def __init__(self):

        self.screens = {}

    def create_screen(self, name):

        screen = Screen(name)

        self.screens[screen.uuid] = screen

        return screen

    def get_screen(self, screen_uuid):

        return self.screens.get(screen_uuid)

    def remove_screen(self, screen_uuid):

        if screen_uuid in self.screens:

            del self.screens[screen_uuid]

    def get_all(self):

        return list(self.screens.values())

    def total(self):

        return len(self.screens)