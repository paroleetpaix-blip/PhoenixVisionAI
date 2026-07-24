"""
========================================================
PHOENIX VISION AI
utils.py

Fonctions utilitaires

Phoenix Security Technologies
========================================================
"""

from pathlib import Path
from core import constants


def print_banner():
    """Affiche la bannière officielle."""
    print(constants.BANNER)


def ensure_directories():
    """Crée automatiquement les dossiers nécessaires."""

    folders = [
        constants.OUTPUTS_FOLDER,
        constants.MODELS_FOLDER,
        constants.DATABASE_FOLDER,
        constants.ASSETS_FOLDER,
        constants.DOCS_FOLDER,
    ]

    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)


def file_exists(path):
    """Retourne True si le fichier existe."""
    return Path(path).is_file()


def folder_exists(path):
    """Retourne True si le dossier existe."""
    return Path(path).is_dir()