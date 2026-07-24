"""
========================================================
PHOENIX VISION AI

Model Manager

Gestionnaire des modèles IA

Phoenix Security Technologies
========================================================
"""

from ai.backends.yolo_backend import YOLOBackend

class ModelManager:

    def __init__(self):

        self.current_model = None

        self.model_name = "Aucun modèle"

    
    def load(self, model_path):

        self.current_model = YOLOBackend()

        self.current_model.load(model_path)

        self.model_name = model_path

        print(f"Modèle chargé : {self.model_name}")

        return self.current_model
        
    def unload(self):

        self.current_model = None

        self.model_name = "Aucun modèle"


    def info(self):

        return {

            "model": self.model_name

        }