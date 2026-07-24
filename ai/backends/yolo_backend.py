"""
========================================================
PHOENIX VISION AI

YOLO Backend

Interface entre Phoenix Vision AI
et les modèles YOLO.

Phoenix Security Technologies
========================================================
"""

from core.detection import Detection

class YOLOBackend:


    def __init__(self):

        self.model = None

        self.name = "YOLO Backend"



    def load(self, model_path):

        """
        Chargement du modèle YOLO.
        
        Pour le moment :
        préparation de l'interface.
        """

        self.model = model_path

        print(
            f"{self.name} prêt : {model_path}"
        )



    def predict(self, source):

        """
        Lance une détection.

        Retourne une liste standardisée
        pour Phoenix Vision AI.
        """

        if self.model is None:

            raise RuntimeError(
                "Modèle YOLO non chargé."
            )


        # Simulation temporaire
        # remplacée par YOLO réel ensuite

        detections = [

            Detection(
                label="car",
                confidence=0.90,
                bbox=[100, 120, 300, 400]
            ),

            Detection(
                label="person",
                confidence=0.85,
                bbox=[200, 150, 260, 350]
            )

        ]


        return detections



    def unload(self):

        self.model = None

        print(
            "YOLO Backend arrêté."
        )