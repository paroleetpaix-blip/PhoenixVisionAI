"""
============================================================
PHOENIX VISION AI

Enterprise Restore Service

Phoenix Security Technologies
============================================================
"""

import json

from pathlib import Path

from core import constants

from core.backups.backup_catalog import (
    backup_catalog,
)

from core.backups.backup_service import (
    backup_service,
)

from core.backups.backup_policy import (
    DATA_DIRECTORY,
    LEGACY_HISTORY_DATABASE,
    PROJECT_ROOT,
    USER_IMAGE_EXTENSIONS,
    USER_UPLOAD_DIRECTORY,
)


CONFIGURATION_TARGETS = {
    "configuration/cameras.json":
        DATA_DIRECTORY
        /
        "cameras.json",

    "configuration/config.json":
        DATA_DIRECTORY
        /
        "config.json",

    "configuration/workspaces.json":
        DATA_DIRECTORY
        /
        "workspaces.json",
}


SENSITIVE_TARGETS = {
    "sensitive/approved_users.json":
        DATA_DIRECTORY
        /
        "approved_users.json",

    "sensitive/account_requests.json":
        DATA_DIRECTORY
        /
        "account_requests.json",
}


class RestoreService:

    # ========================================================
    # TARGET RESOLUTION
    # ========================================================

    def _database_target(
        self,
        archive_path,
    ):

        relative = Path(
            archive_path
        )


        if (
            len(
                relative.parts
            )
            !=
            2
            or
            relative.parts[0]
            !=
            "databases"
        ):

            raise ValueError(
                "Chemin de base de sauvegarde invalide."
            )


        database_name = (
            relative.parts[1]
        )


        if (
            not database_name.endswith(
                ".db"
            )
            or
            Path(
                database_name
            ).name
            !=
            database_name
        ):

            raise ValueError(
                "Nom de base invalide."
            )


        if (
            database_name
            ==
            "vehicle_history.db"
        ):

            return (
                LEGACY_HISTORY_DATABASE
                .resolve()
            )


        return (
            DATA_DIRECTORY
            /
            database_name
        ).resolve()


    def _user_photo_target(
        self,
        archive_path,
    ):

        relative = Path(
            archive_path
        )


        prefix = (
            "sensitive",
            "user_photos",
        )


        if (
            len(
                relative.parts
            )
            <
            3
            or
            tuple(
                relative.parts[
                    :2
                ]
            )
            !=
            prefix
            or
            relative.is_absolute()
            or
            ".."
            in
            relative.parts
        ):

            raise ValueError(
                "Chemin de photo utilisateur invalide."
            )


        photo_relative = Path(
            *relative.parts[
                2:
            ]
        )


        if (
            photo_relative.suffix.lower()
            not in
            USER_IMAGE_EXTENSIONS
        ):

            raise ValueError(
                "Format de photo non autorisé."
            )


        root = (
            USER_UPLOAD_DIRECTORY
            .resolve()
        )

        target = (
            root
            /
            photo_relative
        ).resolve()


        try:

            target.relative_to(
                root
            )

        except ValueError:

            raise ValueError(
                "Destination de photo invalide."
            )


        return target


    def resolve_restore_target(
        self,
        entry,
    ):

        archive_path = str(
            entry.get(
                "archive_path"
            )
            or
            ""
        ).strip()

        category = str(
            entry.get(
                "category"
            )
            or
            ""
        ).strip()


        if not archive_path:

            raise ValueError(
                "Chemin d'archive absent."
            )


        relative = Path(
            archive_path
        )


        if (
            relative.is_absolute()
            or
            ".."
            in
            relative.parts
        ):

            raise ValueError(
                "Chemin d'archive invalide."
            )


        if category == "DATABASE":

            return (
                self._database_target(
                    archive_path
                )
            )


        if category == "CONFIGURATION":

            target = (
                CONFIGURATION_TARGETS
                .get(
                    archive_path
                )
            )

            if target is None:

                raise ValueError(
                    "Configuration non autorisée."
                )

            return target.resolve()


        if category == "SENSITIVE_AUTH":

            target = (
                SENSITIVE_TARGETS
                .get(
                    archive_path
                )
            )

            if target is None:

                raise ValueError(
                    "Donnée sensible non autorisée."
                )

            return target.resolve()


        if (
            category
            ==
            "SENSITIVE_USER_ASSET"
        ):

            return (
                self._user_photo_target(
                    archive_path
                )
            )


        raise ValueError(
            "Catégorie de restauration non autorisée."
        )


    # ========================================================
    # PREFLIGHT
    # ========================================================

    def preflight(
        self,
        backup_id,
    ):

        backup = (
            backup_catalog
            .get_backup(
                backup_id,
                verify_files=True,
            )
        )


        verification = (
            backup.get(
                "verification"
            )
            or
            {}
        )


        if not verification.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "NOT_RESTORABLE",

                "backup_id":
                    backup_id,

                "reason":
                    "BACKUP_INTEGRITY_INVALID",

                "verification":
                    verification,
            }


        backup_path = (
            backup_catalog
            ._backup_path(
                backup_id
            )
        )


        manifest_path = (
            backup_path
            /
            "manifest.json"
        )


        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )


        application = str(
            manifest.get(
                "application"
            )
            or
            ""
        )


        if (
            application
            !=
            getattr(
                constants,
                "APP_NAME",
                "Phoenix Vision AI",
            )
        ):

            return {
                "success":
                    False,

                "status":
                    "NOT_RESTORABLE",

                "backup_id":
                    backup_id,

                "reason":
                    "APPLICATION_MISMATCH",
            }


        files = manifest.get(
            "files",
            []
        )


        if not isinstance(
            files,
            list
        ):

            return {
                "success":
                    False,

                "status":
                    "NOT_RESTORABLE",

                "backup_id":
                    backup_id,

                "reason":
                    "MANIFEST_FILES_INVALID",
            }


        restore_plan = []


        try:

            for entry in files:

                target = (
                    self.resolve_restore_target(
                        entry
                    )
                )


                source = (
                    backup_path
                    /
                    str(
                        entry[
                            "archive_path"
                        ]
                    )
                ).resolve()


                source.relative_to(
                    backup_path.resolve()
                )


                restore_plan.append(
                    {
                        "archive_path":
                            entry[
                                "archive_path"
                            ],

                        "category":
                            entry[
                                "category"
                            ],

                        "sensitive":
                            bool(
                                entry.get(
                                    "sensitive"
                                )
                            ),

                        "source":
                            str(
                                source
                            ),

                        "target":
                            str(
                                target
                            ),

                        "target_exists":
                            target.exists(),
                    }
                )


        except (
            KeyError,
            ValueError,
        ) as error:

            return {
                "success":
                    False,

                "status":
                    "NOT_RESTORABLE",

                "backup_id":
                    backup_id,

                "reason":
                    "RESTORE_TARGET_INVALID",

                "message":
                    str(
                        error
                    ),
            }


        current_version = getattr(
            constants,
            "VERSION",
            "unknown",
        )

        backup_version = str(
            manifest.get(
                "application_version"
            )
            or
            "unknown"
        )


        return {
            "success":
                True,

            "status":
                "RESTORABLE",

            "backup_id":
                backup_id,

            "backup_version":
                backup_version,

            "current_version":
                current_version,

            "same_version":
                (
                    backup_version
                    ==
                    current_version
                ),

            "file_count":
                len(
                    restore_plan
                ),

            "database_count":
                sum(
                    item[
                        "category"
                    ]
                    ==
                    "DATABASE"

                    for item
                    in restore_plan
                ),

            "sensitive_count":
                sum(
                    item[
                        "sensitive"
                    ]

                    for item
                    in restore_plan
                ),

            "verification":
                {
                    "status":
                        verification.get(
                            "status"
                        ),

                    "files_valid":
                        verification.get(
                            "files_valid"
                        ),

                    "files_checked":
                        verification.get(
                            "files_checked"
                        ),

                    "databases_valid":
                        verification.get(
                            "databases_valid"
                        ),

                    "databases_checked":
                        verification.get(
                            "databases_checked"
                        ),
                },

            "restore_plan":
                restore_plan,

            "write_performed":
                False,
        }



    # ========================================================
    # PREPARE RESTORE
    # ========================================================

    def prepare_restore(
        self,
        backup_id,
        *,
        actor="LOCAL_ADMIN",
    ):

        preflight = (
            self.preflight(
                backup_id
            )
        )


        if not preflight.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "NOT_READY",

                "backup_id":
                    backup_id,

                "reason":
                    preflight.get(
                        "reason",
                        "PREFLIGHT_FAILED",
                    ),

                "write_performed":
                    False,
            }


        # Tant qu'aucun moteur de migration
        # de sauvegardes n'existe, seule la
        # même version Phoenix est restaurable.
        if not preflight.get(
            "same_version"
        ):

            return {
                "success":
                    False,

                "status":
                    "NOT_READY",

                "backup_id":
                    backup_id,

                "reason":
                    "VERSION_MISMATCH",

                "backup_version":
                    preflight.get(
                        "backup_version"
                    ),

                "current_version":
                    preflight.get(
                        "current_version"
                    ),

                "write_performed":
                    False,
            }


        # Sauvegarde automatique de l'état
        # courant AVANT toute restauration.
        safety_backup = (
            backup_service
            .create_backup(
                actor=
                    actor,

                backup_type=
                    "PRE_RESTORE",
            )
        )


        safety_backup_id = (
            safety_backup[
                "backup_id"
            ]
        )


        safety_catalog = (
            backup_catalog
            .get_backup(
                safety_backup_id,
                verify_files=True,
            )
        )


        safety_verification = (
            safety_catalog.get(
                "verification"
            )
            or
            {}
        )


        if not safety_verification.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "NOT_READY",

                "backup_id":
                    backup_id,

                "reason":
                    "PRE_RESTORE_BACKUP_INVALID",

                "pre_restore_backup_id":
                    safety_backup_id,

                "write_performed":
                    False,
            }


        return {
            "success":
                True,

            "status":
                "READY_TO_RESTORE",

            "backup_id":
                backup_id,

            "backup_version":
                preflight.get(
                    "backup_version"
                ),

            "current_version":
                preflight.get(
                    "current_version"
                ),

            "pre_restore_backup_id":
                safety_backup_id,

            "pre_restore_integrity":
                True,

            "pre_restore_files_valid":
                safety_verification.get(
                    "files_valid"
                ),

            "pre_restore_files_checked":
                safety_verification.get(
                    "files_checked"
                ),

            "pre_restore_databases_valid":
                safety_verification.get(
                    "databases_valid"
                ),

            "pre_restore_databases_checked":
                safety_verification.get(
                    "databases_checked"
                ),

            "restore_file_count":
                preflight.get(
                    "file_count"
                ),

            "restore_database_count":
                preflight.get(
                    "database_count"
                ),

            "restore_sensitive_count":
                preflight.get(
                    "sensitive_count"
                ),

            # Aucune donnée active n'est encore
            # remplacée à cette étape.
            "write_performed":
                False,

            "active_data_modified":
                False,
        }


restore_service = RestoreService()
