"""
========================================================
PHOENIX VISION AI

Evidence Manager

Phoenix Security Technologies
========================================================
"""

from core.evidence.evidence import Evidence


class EvidenceManager:

    def __init__(self):

        self.evidences = []

    def create(

        self,

        vehicle_uuid,

        event_type,

        image_path

    ):

        evidence = Evidence(

            vehicle_uuid,

            event_type,

            image_path

        )

        self.evidences.append(evidence)

        return evidence

    def total(self):

        return len(self.evidences)

    def all(self):

        return self.evidences