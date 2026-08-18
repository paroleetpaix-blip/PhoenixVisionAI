"""
========================================================
PHOENIX VISION AI

Cloud Protocol

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from core.detection import Detection


class CloudProtocol:

    @staticmethod
    def parse_prediction(
        response
    ):

        if not isinstance(
            response,
            dict
        ):

            raise ValueError(
                "Réponse IA distante invalide."
            )


        detections = []


        items = response.get(
            "detections",
            []
        )


        if not isinstance(
            items,
            list
        ):

            raise ValueError(
                "Le champ detections doit être une liste."
            )


        for item in items:

            if not isinstance(
                item,
                dict
            ):

                continue


            label = item.get(
                "label"
            )


            confidence = item.get(
                "confidence"
            )


            bbox = item.get(
                "bbox"
            )


            if (
                label is None
                or
                confidence is None
                or
                bbox is None
            ):

                continue


            if not isinstance(
                bbox,
                (
                    list,
                    tuple
                )
            ):

                continue


            if len(bbox) != 4:

                continue


            try:

                confidence = float(
                    confidence
                )


                bbox = [
                    float(value)
                    for value in bbox
                ]

            except (
                TypeError,
                ValueError
            ):

                continue


            detection = Detection(

                label=str(
                    label
                ),

                confidence=confidence,

                bbox=bbox

            )


            detections.append(
                detection
            )


        return detections