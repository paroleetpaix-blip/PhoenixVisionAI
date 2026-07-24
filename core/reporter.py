"""
========================================================
PHOENIX VISION AI

reporter.py

Création des rapports d'analyse.

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
from core import config


class Reporter:

    def build(self, source, tracked_objects, statistics):

        now = datetime.now()

        report = {

            "project": config.APP_NAME,

            "version": config.VERSION,

            "company": "Phoenix Security Technologies",

            "analysis": {

                "source": source,

                "date": now.strftime("%Y-%m-%d"),

                "time": now.strftime("%H:%M:%S")

            },

            "objects": tracked_objects,

            "statistics": statistics

        }

        return report