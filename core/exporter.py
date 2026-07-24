"""
======================================================
PHOENIX VISION AI
Exporter
Version : 0.5.0
======================================================
"""

import json
import os


class Exporter:

    def __init__(self, output_folder="outputs"):

        self.output_folder = output_folder

        os.makedirs(self.output_folder, exist_ok=True)

    def export_json(self, filename, data):

        filepath = os.path.join(self.output_folder, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"✔ Rapport enregistré : {filepath}")