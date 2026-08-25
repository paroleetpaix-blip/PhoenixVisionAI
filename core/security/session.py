"""
========================================================
PHOENIX VISION AI

Session Manager

Phoenix Security Technologies
========================================================
"""

import uuid


def _enterprise_access_decision(
    username,
):

    try:

        from core.users_registry.user_service import (
            user_registry_service,
        )


        return (
            user_registry_service
            .access_decision(
                username
            )
        )


    except Exception as error:

        # Pendant le développement, une erreur du registre
        # ne doit pas détruire silencieusement toutes les
        # sessions du système.
        #
        # Le durcissement fail-closed sera décidé pour
        # l'architecture de production.

        print(
            "Phoenix User Registry "
            "session validation warning:",
            type(
                error
            ).__name__,
        )


        return None


class SessionManager:

    def __init__(
        self
    ):

        self.sessions = {}


    # ----------------------------------------------------
    # Création
    # ----------------------------------------------------

    def create(
        self,
        username,
        role
    ):

        token = str(
            uuid.uuid4()
        )


        self.sessions[
            token
        ] = {

            "username":
                username,

            "role":
                role

        }


        return token


    # ----------------------------------------------------
    # Existence
    # ----------------------------------------------------

    def exists(
        self,
        token
    ):

        return (
            self.get(
                token
            )
            is not None
        )


    # ----------------------------------------------------
    # Récupération + contrôle d'accès Enterprise
    # ----------------------------------------------------

    def get(
        self,
        token
    ):

        session = (
            self.sessions
            .get(
                token
            )
        )


        if session is None:

            return None


        username = (
            session.get(
                "username"
            )
        )


        decision = (
            _enterprise_access_decision(
                username
            )
        )


        if (
            decision is not None
            and
            decision.get(
                "known"
            )
            and
            not decision.get(
                "allowed"
            )
        ):

            # Révoque toutes les sessions de ce compte,
            # pas uniquement le token courant.
            self.remove_by_username(
                username
            )

            return None


        return session


    # ----------------------------------------------------
    # Suppression d'un token
    # ----------------------------------------------------

    def remove(
        self,
        token
    ):

        if token in self.sessions:

            del self.sessions[
                token
            ]


    # ----------------------------------------------------
    # Révocation globale d'un utilisateur
    # ----------------------------------------------------

    def remove_by_username(
        self,
        username
    ):

        normalized = str(
            username
            or
            ""
        ).strip().lower()


        if not normalized:

            return 0


        tokens = [

            token

            for token, session
            in self.sessions.items()

            if str(
                session.get(
                    "username"
                )
                or
                ""
            ).strip().lower()
            ==
            normalized

        ]


        for token in tokens:

            self.sessions.pop(
                token,
                None
            )


        return len(
            tokens
        )


    # ----------------------------------------------------
    # Nombre de sessions actives d'un compte
    # ----------------------------------------------------

    def count_by_username(
        self,
        username
    ):

        normalized = str(
            username
            or
            ""
        ).strip().lower()


        return sum(

            1

            for session
            in self.sessions.values()

            if str(
                session.get(
                    "username"
                )
                or
                ""
            ).strip().lower()
            ==
            normalized

        )


session_manager = SessionManager()
