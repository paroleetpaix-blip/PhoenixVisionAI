"""
============================================================
PHOENIX VISION AI

Live Restore Reconciliation

Phoenix Security Technologies
============================================================

Construit le plan exact des modifications qu'une restauration
LIVE devrait effectuer.

IMPORTANT
---------
Ce module ne modifie aucun fichier actif.
"""

import os
import re

from pathlib import Path

from core.backups.backup_manifest import (
    sha256_file,
)


SHA256_PATTERN = re.compile(
    r"^[a-fA-F0-9]{64}$"
)

USER_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


class LiveRestoreReconciliation:

    # ========================================================
    # SAFE RELATIVE PATH
    # ========================================================

    @staticmethod
    def _safe_relative(
        value,
    ):

        value = str(
            value
            or
            ""
        ).strip()

        relative = Path(
            value
        )


        if (
            not value
            or
            relative.is_absolute()
            or
            ".." in relative.parts
        ):

            raise RuntimeError(
                "Chemin Restore invalide."
            )


        return relative


    # ========================================================
    # USER ASSET SCAN
    # ========================================================

    def _scan_current_user_assets(
        self,
        *,
        project_root,
    ):

        project_root = Path(
            project_root
        ).resolve()

        uploads_root = (
            project_root
            /
            "web"
            /
            "static"
            /
            "uploads"
            /
            "users"
        ).resolve()


        try:

            uploads_root.relative_to(
                project_root
            )

        except ValueError:

            raise RuntimeError(
                "Répertoire utilisateurs "
                "hors projet Phoenix."
            )


        if not uploads_root.exists():

            return {
                "assets": [],
                "ignored": [],
            }


        if (
            not uploads_root.is_dir()
            or
            uploads_root.is_symlink()
        ):

            raise RuntimeError(
                "Répertoire utilisateurs invalide."
            )


        assets = []

        ignored = []


        for current_root, directories, files in os.walk(
            uploads_root,
            followlinks=False,
        ):

            current_root = Path(
                current_root
            )


            safe_directories = []

            for directory_name in directories:

                directory = (
                    current_root
                    /
                    directory_name
                )


                if directory.is_symlink():

                    raise RuntimeError(
                        "Lien symbolique interdit "
                        "dans les fichiers utilisateurs."
                    )


                safe_directories.append(
                    directory_name
                )


            directories[:] = (
                safe_directories
            )


            for filename in files:

                candidate = (
                    current_root
                    /
                    filename
                )


                if candidate.is_symlink():

                    raise RuntimeError(
                        "Fichier utilisateur symbolique interdit."
                    )


                if not candidate.is_file():

                    raise RuntimeError(
                        "Asset utilisateur invalide."
                    )


                candidate = candidate.resolve()


                try:

                    candidate.relative_to(
                        uploads_root
                    )

                except ValueError:

                    raise RuntimeError(
                        "Asset utilisateur "
                        "hors périmètre."
                    )


                relative = (
                    candidate.relative_to(
                        project_root
                    )
                )


                if (
                    candidate.suffix.lower()
                    in
                    USER_IMAGE_EXTENSIONS
                ):

                    assets.append(
                        candidate
                    )

                else:

                    ignored.append(
                        str(
                            relative
                        )
                    )


        assets.sort(
            key=lambda item:
                str(item)
        )

        ignored.sort()


        return {
            "assets":
                assets,

            "ignored":
                ignored,
        }


    # ========================================================
    # BUILD
    # ========================================================

    def build(
        self,
        *,
        project_root,
        backup_directory,
        manifest,
        target_resolver,
    ):

        project_root = Path(
            project_root
        ).resolve()

        backup_directory = Path(
            backup_directory
        ).resolve()


        files = manifest.get(
            "files"
        )


        if not isinstance(
            files,
            list,
        ):

            raise RuntimeError(
                "Manifest de réconciliation invalide."
            )


        actions = []

        target_keys = set()

        backup_user_targets = set()


        for entry in files:

            if not isinstance(
                entry,
                dict,
            ):

                raise RuntimeError(
                    "Entrée manifest invalide."
                )


            archive_relative = (
                self._safe_relative(
                    entry.get(
                        "archive_path"
                    )
                )
            )


            source = (
                backup_directory
                /
                archive_relative
            ).resolve()


            try:

                source.relative_to(
                    backup_directory
                )

            except ValueError:

                raise RuntimeError(
                    "Source backup hors périmètre."
                )


            if (
                not source.is_file()
                or
                source.is_symlink()
            ):

                raise RuntimeError(
                    "Source backup invalide."
                )


            expected_hash = str(
                entry.get(
                    "sha256"
                )
                or
                ""
            ).strip()


            if not SHA256_PATTERN.fullmatch(
                expected_hash
            ):

                raise RuntimeError(
                    "Empreinte SHA-256 manifest invalide."
                )


            try:

                expected_size = int(
                    entry.get(
                        "size_bytes"
                    )
                )

            except Exception as error:

                raise RuntimeError(
                    "Taille manifest invalide."
                ) from error


            if expected_size < 0:

                raise RuntimeError(
                    "Taille manifest invalide."
                )


            target = (
                target_resolver(
                    entry
                )
            ).resolve()


            try:

                relative_target = (
                    target.relative_to(
                        project_root
                    )
                )

            except ValueError:

                raise RuntimeError(
                    "Destination Restore "
                    "hors projet Phoenix."
                )


            target_key = str(
                target
            )


            if target_key in target_keys:

                raise RuntimeError(
                    "Destination Restore dupliquée."
                )


            target_keys.add(
                target_key
            )


            category = str(
                entry.get(
                    "category"
                )
                or
                ""
            )


            if (
                category
                ==
                "SENSITIVE_USER_ASSET"
            ):

                backup_user_targets.add(
                    target_key
                )


            # =================================================
            # CURRENT TARGET STATE
            # =================================================

            if (
                target.exists()
                or
                target.is_symlink()
            ):

                if target.is_symlink():

                    raise RuntimeError(
                        "Destination Restore "
                        "symbolique interdite."
                    )


                if not target.is_file():

                    raise RuntimeError(
                        "Destination Restore "
                        "existante invalide."
                    )


                current_size = (
                    target.stat()
                    .st_size
                )

                current_hash = (
                    sha256_file(
                        target
                    )
                )


                if (
                    current_size
                    ==
                    expected_size
                    and
                    current_hash.lower()
                    ==
                    expected_hash.lower()
                ):

                    action = "KEEP"

                else:

                    action = "REPLACE"


            else:

                current_size = None
                current_hash = None

                action = "CREATE"


            actions.append(
                {
                    "action":
                        action,

                    "category":
                        category,

                    "archive_path":
                        str(
                            archive_relative
                        ),

                    "target":
                        str(
                            relative_target
                        ),

                    "expected_size":
                        expected_size,

                    "expected_sha256":
                        expected_hash.lower(),

                    "current_size":
                        current_size,

                    "current_sha256":
                        current_hash,
                }
            )


        # ====================================================
        # VARIABLE USER ASSETS
        # ====================================================

        scan = (
            self._scan_current_user_assets(
                project_root=
                    project_root
            )
        )


        for asset in scan[
            "assets"
        ]:

            asset_key = str(
                asset.resolve()
            )


            if (
                asset_key
                in
                backup_user_targets
            ):

                continue


            relative_asset = (
                asset.relative_to(
                    project_root
                )
            )


            actions.append(
                {
                    "action":
                        "QUARANTINE",

                    "category":
                        "SENSITIVE_USER_ASSET",

                    "archive_path":
                        None,

                    "target":
                        str(
                            relative_asset
                        ),

                    "expected_size":
                        None,

                    "expected_sha256":
                        None,

                    "current_size":
                        asset.stat().st_size,

                    "current_sha256":
                        sha256_file(
                            asset
                        ),
                }
            )


        # ====================================================
        # COUNTS
        # ====================================================

        counts = {
            "KEEP": 0,
            "REPLACE": 0,
            "CREATE": 0,
            "QUARANTINE": 0,
        }


        for item in actions:

            action = item[
                "action"
            ]


            if action not in counts:

                raise RuntimeError(
                    "Action Restore inconnue."
                )


            counts[
                action
            ] += 1


        return {
            "status":
                "RECONCILIATION_READY",

            "actions":
                actions,

            "counts":
                counts,

            "backup_files":
                len(
                    files
                ),

            "total_actions":
                len(
                    actions
                ),

            "ignored_user_files":
                scan[
                    "ignored"
                ],

            "write_performed":
                False,

            "active_data_modified":
                False,
        }


live_restore_reconciliation = (
    LiveRestoreReconciliation()
)
