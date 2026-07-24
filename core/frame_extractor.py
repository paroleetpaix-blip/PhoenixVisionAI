"""
========================================================
PHOENIX VISION AI

Frame Extractor

Extraction des images vidéo

Phoenix Security Technologies
SDK v1.0 Enterprise
========================================================
"""

import cv2
import os


class FrameExtractor:

    def __init__(self, output_folder="frames"):

        self.output_folder = output_folder

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

    def extract(self, video_path, step=30):

        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():

            raise RuntimeError(
                f"Impossible d'ouvrir {video_path}"
            )

        frame_paths = []

        index = 0

        saved = 0

        while True:

            ret, frame = capture.read()

            if not ret:
                break

            if index % step == 0:

                filename = os.path.join(

                    self.output_folder,

                    f"frame_{saved:06d}.jpg"

                )

                cv2.imwrite(
                    filename,
                    frame
                )

                frame_paths.append(
                    filename
                )

                saved += 1

            index += 1

        capture.release()

        print(
            f"✓ {saved} images extraites."
        )

        return frame_paths