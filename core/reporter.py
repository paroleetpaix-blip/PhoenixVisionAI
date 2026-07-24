"""
========================================================
PHOENIX VISION AI
reporter.py

Création des rapports d'analyse.

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

from datetime import datetime
from core import config


class Reporter:

    def build(self, source, frames, statistics):
        """
        Génère un rapport d'analyse.
        """

        now = datetime.now()

        report = {

            "project": config.APP_NAME,

            "version": config.VERSION,

            "company": "Phoenix Security Technologies",

            "analysis": {

                "source": source,

                "date": now.strftime("%Y-%m-%d"),

                "time": now.strftime("%H:%M:%S"),

                "frames_processed": frames

            },

            "statistics": statistics

        }

        return report