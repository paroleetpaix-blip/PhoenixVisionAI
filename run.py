"""
========================================================
PHOENIX VISION AI

Official Entry Point

Phoenix Security Technologies
========================================================
"""

from core import runtime

from core.startup_lock import (
    PhoenixAlreadyRunningError,
    phoenix_instance_lock,
)


def main():

    # ====================================================
    # SINGLE INSTANCE GATE
    # ====================================================
    #
    # Doit être acquis AVANT RestoreBootstrap,
    # PhoenixServer et PhoenixEngine.
    # ====================================================

    try:

        phoenix_instance_lock.acquire()

    except PhoenixAlreadyRunningError:

        print()
        print(
            "✗ Phoenix Vision AI est déjà "
            "en cours d'exécution."
        )
        print(
            "  Une deuxième instance est "
            "interdite par sécurité."
        )
        print()

        return 2


    # ====================================================
    # OFFLINE RESTORE GATE
    # ====================================================
    #
    # Cette vérification doit obligatoirement avoir lieu
    # AVANT l'import de PhoenixServer / PhoenixEngine.
    #
    # Cela garantit qu'aucune base SQLite globale Phoenix
    # n'est ouverte avant le traitement d'une éventuelle
    # restauration.
    # ====================================================

    from core.backups.restore_bootstrap import (
        restore_bootstrap,
    )


    restore_bootstrap.startup_gate()


    # IMPORTANT :
    # import volontairement différé.
    #
    # Ne pas remonter cet import en haut du fichier.
    from core.server.server import (
        PhoenixServer,
    )


    server = PhoenixServer()


    # Enregistrement des objets globaux
    runtime.engine = server.engine


    # Le StreamService sera enregistré après
    # le démarrage lorsqu'il existera dans
    # PhoenixEngine.
    server.start()


    runtime.stream_service = getattr(
        server.engine,
        "stream_service",
        None,
    )


    # ====================================================
    # AUTOMATIC BACKUPS
    # ====================================================
    #
    # Le scheduler démarre seulement après le serveur :
    # - RestoreBootstrap a déjà autorisé le démarrage ;
    # - le verrou d'instance Phoenix est déjà acquis ;
    # - les services opérationnels sont initialisés.
    #
    # Il reste indépendant du moteur Vision AI :
    # aucune dépendance YOLO n'existe dans le scheduler.
    # ====================================================

    from core.backups.backup_scheduler import (
        backup_scheduler,
    )


    try:

        backup_scheduler.start()


        input(
            "\n"
            "Appuyez sur Entrée pour arrêter "
            "le serveur...\n"
        )


    finally:

        backup_scheduler.stop(
            timeout=10.0
        )


if __name__ == "__main__":

    raise SystemExit(
        main()
        or
        0
    )
