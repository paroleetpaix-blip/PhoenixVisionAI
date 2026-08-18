"""
========================================================
PHOENIX VISION AI

Session Manager

Phoenix Security Technologies
========================================================
"""

import uuid


class SessionManager:

    def __init__(self):

        self.sessions = {}

    # ----------------------------
    # Création d'une session
    # ----------------------------

    def create(self, username, role):

        token = str(uuid.uuid4())

        self.sessions[token] = {

            "username": username,

            "role": role

        }

        return token

    # ----------------------------
    # Vérifier une session
    # ----------------------------

    def exists(self, token):

        return token in self.sessions

    # ----------------------------
    # Récupérer une session
    # ----------------------------

    def get(self, token):

        return self.sessions.get(token)

    # ----------------------------
    # Supprimer une session
    # ----------------------------

    def remove(self, token):

        if token in self.sessions:

            del self.sessions[token]


session_manager = SessionManager()