"""
============================================================
PHOENIX VISION AI

Backup Migration Registry

Phoenix Security Technologies
============================================================

Registre ordonné des migrations de sauvegardes.

Une migration doit être enregistrée explicitement.
Aucun saut de version implicite n'est autorisé.
"""


class BackupMigrationRegistry:

    def __init__(
        self,
    ):

        self._steps = {}


    # ========================================================
    # REGISTER
    # ========================================================

    def register(
        self,
        *,
        source_version,
        target_version,
        migration,
    ):

        source_version = str(
            source_version
            or
            ""
        ).strip()

        target_version = str(
            target_version
            or
            ""
        ).strip()


        if not source_version:

            raise ValueError(
                "Version source absente."
            )


        if not target_version:

            raise ValueError(
                "Version cible absente."
            )


        if source_version == target_version:

            raise ValueError(
                "Une migration doit changer de version."
            )


        if not callable(
            migration
        ):

            raise TypeError(
                "Migration non exécutable."
            )


        key = (
            source_version,
            target_version,
        )


        if key in self._steps:

            raise RuntimeError(
                "Migration déjà enregistrée : "
                +
                source_version
                +
                " -> "
                +
                target_version
            )


        self._steps[
            key
        ] = migration


    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        source_version,
        target_version,
    ):

        return self._steps.get(
            (
                str(
                    source_version
                ).strip(),

                str(
                    target_version
                ).strip(),
            )
        )


    # ========================================================
    # REGISTERED EDGES
    # ========================================================

    def edges(
        self,
    ):

        return sorted(
            self._steps.keys()
        )


    # ========================================================
    # FIND CHAIN
    # ========================================================

    def find_chain(
        self,
        *,
        source_version,
        target_version,
    ):

        source_version = str(
            source_version
            or
            ""
        ).strip()

        target_version = str(
            target_version
            or
            ""
        ).strip()


        if not source_version or not target_version:

            raise ValueError(
                "Versions de migration invalides."
            )


        if source_version == target_version:

            return []


        queue = [
            (
                source_version,
                [],
            )
        ]

        visited = {
            source_version
        }


        while queue:

            current_version, chain = (
                queue.pop(0)
            )


            next_steps = sorted(
                (
                    destination,
                    migration,
                )

                for (
                    origin,
                    destination
                ),
                migration
                in self._steps.items()

                if origin == current_version
            )


            for (
                destination,
                migration
            ) in next_steps:

                next_chain = (
                    chain
                    +
                    [
                        {
                            "source_version":
                                current_version,

                            "target_version":
                                destination,

                            "migration":
                                migration,
                        }
                    ]
                )


                if destination == target_version:

                    return next_chain


                if destination in visited:

                    continue


                visited.add(
                    destination
                )

                queue.append(
                    (
                        destination,
                        next_chain,
                    )
                )


        return None


backup_migration_registry = (
    BackupMigrationRegistry()
)
