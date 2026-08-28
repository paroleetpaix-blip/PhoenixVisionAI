"""
============================================================
PHOENIX VISION AI

Automatic Backup Retention

Phoenix Security Technologies
============================================================

Rotation GFS des sauvegardes AUTOMATIC uniquement.

Les sauvegardes MANUAL, PRE_RESTORE, MIGRATED et les
sauvegardes invalides ne sont jamais supprimées ici.
"""

import shutil

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from core.backups.backup_automation_policy import (
    AUTOMATIC_BACKUP_TYPE,
    RETENTION_DAILY_DAYS,
    RETENTION_HOURLY_HOURS,
    RETENTION_MONTHLY_MONTHS,
    RETENTION_WEEKLY_WEEKS,
)

from core.backups.backup_catalog import (
    backup_catalog,
)

from core.backups.backup_service import (
    BACKUP_DIRECTORY,
)

from core.backups.restore_request import (
    IN_PROGRESS_PATH,
    PENDING_RESTORE_PATH,
    validate_backup_id,
)


class BackupRetentionService:

    def __init__(
        self,
        *,
        catalog=backup_catalog,
        backup_root=BACKUP_DIRECTORY,
        pending_path=PENDING_RESTORE_PATH,
        in_progress_path=IN_PROGRESS_PATH,
    ):

        self.catalog = catalog

        self.backup_root = Path(
            backup_root
        )

        self.pending_path = Path(
            pending_path
        )

        self.in_progress_path = Path(
            in_progress_path
        )


    # ========================================================
    # UTC
    # ========================================================

    @staticmethod
    def _utc_now():

        return datetime.now(
            timezone.utc
        )


    # ========================================================
    # DATE PARSER
    # ========================================================

    @staticmethod
    def _parse_datetime(
        value,
    ):

        value = str(
            value or ""
        ).strip()


        if not value:

            raise ValueError(
                "Date sauvegarde absente."
            )


        if value.endswith(
            "Z"
        ):

            value = (
                value[:-1]
                +
                "+00:00"
            )


        date = datetime.fromisoformat(
            value
        )


        if date.tzinfo is None:

            date = date.replace(
                tzinfo=timezone.utc
            )


        return date.astimezone(
            timezone.utc
        )


    # ========================================================
    # RESTORE GATE
    # ========================================================

    def restore_active(
        self,
    ):

        return (
            self.pending_path.exists()
            or
            self.pending_path.is_symlink()
            or
            self.in_progress_path.exists()
            or
            self.in_progress_path.is_symlink()
        )


    # ========================================================
    # DISCOVER AUTOMATIC BACKUPS
    # ========================================================

    def automatic_backups(
        self,
    ):

        root = self.backup_root.resolve()


        if not root.exists():

            return []


        if (
            not root.is_dir()
            or
            root.is_symlink()
        ):

            raise RuntimeError(
                "Répertoire Backup invalide."
            )


        backups = []


        for directory in root.iterdir():

            if (
                not directory.is_dir()
                or
                directory.is_symlink()
            ):

                continue


            try:

                backup_id = (
                    validate_backup_id(
                        directory.name
                    )
                )

            except Exception:

                continue


            try:

                item = (
                    self.catalog
                    .get_backup(
                        backup_id,
                        verify_files=False,
                    )
                )

            except Exception:

                # Backup invalide/inconnu :
                # ne jamais le supprimer automatiquement.
                continue


            if (
                item.get(
                    "status"
                )
                !=
                "AVAILABLE"
            ):

                continue


            if (
                str(
                    item.get(
                        "backup_type"
                    )
                    or
                    ""
                ).upper()
                !=
                AUTOMATIC_BACKUP_TYPE
            ):

                continue


            try:

                created_at = (
                    self._parse_datetime(
                        item.get(
                            "created_at"
                        )
                    )
                )

            except Exception:

                continue


            backups.append(
                {
                    **item,

                    "_created_at":
                        created_at,
                }
            )


        backups.sort(
            key=lambda item:
                item[
                    "_created_at"
                ],
            reverse=True,
        )


        return backups


    # ========================================================
    # RETENTION PLAN
    # ========================================================

    def plan(
        self,
        *,
        now=None,
    ):

        now = (
            now
            or
            self._utc_now()
        ).astimezone(
            timezone.utc
        )


        backups = (
            self.automatic_backups()
        )


        keep = set()

        delete = set()


        # Toujours conserver au minimum la plus récente.
        if backups:

            keep.add(
                backups[0][
                    "backup_id"
                ]
            )


        daily_seen = set()

        weekly_seen = set()

        monthly_seen = set()


        hourly_seconds = (
            RETENTION_HOURLY_HOURS
            *
            60
            *
            60
        )

        daily_seconds = (
            RETENTION_DAILY_DAYS
            *
            24
            *
            60
            *
            60
        )

        weekly_seconds = (
            RETENTION_WEEKLY_WEEKS
            *
            7
            *
            24
            *
            60
            *
            60
        )

        # Approximation volontaire uniquement pour la
        # limite de conservation. Les buckets restent
        # basés sur les vrais mois calendaires.
        monthly_seconds = (
            RETENTION_MONTHLY_MONTHS
            *
            31
            *
            24
            *
            60
            *
            60
        )


        for item in backups:

            backup_id = item[
                "backup_id"
            ]

            created_at = item[
                "_created_at"
            ]


            age = (
                now
                -
                created_at
            ).total_seconds()


            # Timestamp futur :
            # conserver par sécurité.
            if age < 0:

                keep.add(
                    backup_id
                )

                continue


            # 0 → 48 h :
            # toutes les sauvegardes.
            if age <= hourly_seconds:

                keep.add(
                    backup_id
                )

                continue


            # 48 h → 30 jours :
            # une par jour.
            if age <= daily_seconds:

                key = (
                    created_at.year,
                    created_at.month,
                    created_at.day,
                )


                if key not in daily_seen:

                    daily_seen.add(
                        key
                    )

                    keep.add(
                        backup_id
                    )

                else:

                    delete.add(
                        backup_id
                    )


                continue


            # 30 jours → 12 semaines :
            # une par semaine ISO.
            if age <= weekly_seconds:

                iso = created_at.isocalendar()

                key = (
                    iso.year,
                    iso.week,
                )


                if key not in weekly_seen:

                    weekly_seen.add(
                        key
                    )

                    keep.add(
                        backup_id
                    )

                else:

                    delete.add(
                        backup_id
                    )


                continue


            # 12 semaines → 12 mois :
            # une par mois.
            if age <= monthly_seconds:

                key = (
                    created_at.year,
                    created_at.month,
                )


                if key not in monthly_seen:

                    monthly_seen.add(
                        key
                    )

                    keep.add(
                        backup_id
                    )

                else:

                    delete.add(
                        backup_id
                    )


                continue


            # Plus ancien que la politique mensuelle.
            delete.add(
                backup_id
            )


        delete -= keep


        return {
            "success":
                True,

            "status":
                "RETENTION_PLANNED",

            "automatic_count":
                len(
                    backups
                ),

            "keep":
                sorted(
                    keep
                ),

            "delete":
                sorted(
                    delete
                ),

            "delete_count":
                len(
                    delete
                ),
        }


    # ========================================================
    # SAFE DELETE
    # ========================================================

    def _delete_backup(
        self,
        backup_id,
    ):

        backup_id = (
            validate_backup_id(
                backup_id
            )
        )


        if self.restore_active():

            raise RuntimeError(
                "Rétention interdite pendant Restore."
            )


        root = self.backup_root.resolve()

        directory = (
            root
            /
            backup_id
        ).resolve()


        if directory.parent != root:

            raise RuntimeError(
                "Chemin de suppression invalide."
            )


        if (
            not directory.is_dir()
            or
            directory.is_symlink()
        ):

            raise RuntimeError(
                "Backup à supprimer invalide."
            )


        # Vérification complète juste avant suppression.
        backup = (
            self.catalog
            .get_backup(
                backup_id,
                verify_files=True,
            )
        )


        if (
            backup.get(
                "status"
            )
            !=
            "AVAILABLE"
        ):

            raise RuntimeError(
                "Backup non disponible : suppression refusée."
            )


        if (
            str(
                backup.get(
                    "backup_type"
                )
                or
                ""
            ).upper()
            !=
            AUTOMATIC_BACKUP_TYPE
        ):

            raise RuntimeError(
                "Suppression réservée aux backups AUTOMATIC."
            )


        verification = (
            backup.get(
                "verification"
            )
            or
            {}
        )


        if (
            verification.get(
                "success"
            )
            is not True
        ):

            raise RuntimeError(
                "Backup non valide : suppression refusée."
            )


        # Recheck Restore juste avant l'écriture destructive.
        if self.restore_active():

            raise RuntimeError(
                "Restore détecté avant suppression."
            )


        shutil.rmtree(
            directory
        )


        return {
            "backup_id":
                backup_id,

            "deleted":
                True,
        }


    # ========================================================
    # APPLY
    # ========================================================

    def apply(
        self,
        *,
        now=None,
    ):

        if self.restore_active():

            return {
                "success":
                    False,

                "status":
                    "RETENTION_BLOCKED_BY_RESTORE",

                "deleted":
                    [],

                "skipped":
                    [],
            }


        plan = self.plan(
            now=now
        )


        deleted = []

        skipped = []


        for backup_id in plan[
            "delete"
        ]:

            try:

                self._delete_backup(
                    backup_id
                )

                deleted.append(
                    backup_id
                )


            except Exception as error:

                skipped.append(
                    {
                        "backup_id":
                            backup_id,

                        "error":
                            type(
                                error
                            ).__name__,

                        "message":
                            str(
                                error
                            ),
                    }
                )


        return {
            "success":
                True,

            "status":
                "RETENTION_APPLIED",

            "automatic_count":
                plan[
                    "automatic_count"
                ],

            "kept_count":
                len(
                    plan[
                        "keep"
                    ]
                ),

            "deleted":
                deleted,

            "deleted_count":
                len(
                    deleted
                ),

            "skipped":
                skipped,

            "skipped_count":
                len(
                    skipped
                ),
        }


backup_retention_service = (
    BackupRetentionService()
)
