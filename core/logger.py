"""
========================================================
PHOENIX VISION AI

logger.py

Système de journalisation

Phoenix Security Technologies
========================================================
"""

import logging
import os


class PhoenixLogger:

    def __init__(self):

        os.makedirs("logs", exist_ok=True)

        logging.basicConfig(

            filename="logs/phoenix.log",

            level=logging.INFO,

            format="%(asctime)s | %(levelname)s | %(message)s"

        )

        self.logger = logging.getLogger("Phoenix")


    def info(self, message):

        self.logger.info(message)


    def warning(self, message):

        self.logger.warning(message)


    def error(self, message):

        self.logger.error(message)