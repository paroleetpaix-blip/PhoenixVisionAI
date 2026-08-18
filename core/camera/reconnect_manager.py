"""
========================================================
PHOENIX VISION AI

Reconnect Manager

Phoenix Security Technologies
========================================================
"""

import time

from core.camera.camera_status import CameraStatus


class ReconnectManager:

    def __init__(self):

        self.delay = 3

    def reconnect(self, camera):

        if camera.status != CameraStatus.OFFLINE:
            return False

        print(f"[Reconnect] Tentative : {camera.name}")

        camera.status = CameraStatus.CONNECTING

        time.sleep(self.delay)

        camera.set_online()

        camera.increase_reconnect()

        print(f"[Reconnect] Succès : {camera.name}")

        return True