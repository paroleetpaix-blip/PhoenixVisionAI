"""
============================================================
PHOENIX VISION AI

Enterprise Backup Policy

Phoenix Security Technologies
============================================================
"""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

DATA_DIRECTORY = (
    PROJECT_ROOT
    /
    "data"
)

USER_UPLOAD_DIRECTORY = (
    PROJECT_ROOT
    /
    "web"
    /
    "static"
    /
    "uploads"
    /
    "users"
)

LEGACY_HISTORY_DATABASE = (
    PROJECT_ROOT
    /
    "database"
    /
    "vehicle_history.db"
)


CONFIGURATION_FILES = (
    DATA_DIRECTORY
    /
    "cameras.json",

    DATA_DIRECTORY
    /
    "config.json",

    DATA_DIRECTORY
    /
    "workspaces.json",
)


SENSITIVE_FILES = (
    DATA_DIRECTORY
    /
    "approved_users.json",

    DATA_DIRECTORY
    /
    "account_requests.json",
)


USER_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


@dataclass(
    frozen=True
)
class BackupSource:

    source_path: Path

    archive_path: Path

    category: str

    sensitive: bool = False


def _file_is_inside(
    path,
    root,
):

    try:

        path.resolve().relative_to(
            root.resolve()
        )

        return True

    except ValueError:

        return False


def discover_database_sources():

    sources = []


    if DATA_DIRECTORY.is_dir():

        for path in sorted(
            DATA_DIRECTORY.glob(
                "*.db"
            )
        ):

            if not path.is_file():

                continue


            if path.is_symlink():

                continue


            if not _file_is_inside(
                path,
                DATA_DIRECTORY,
            ):

                continue


            sources.append(
                BackupSource(
                    source_path=
                        path,

                    archive_path=
                        Path(
                            "databases"
                        )
                        /
                        path.name,

                    category=
                        "DATABASE",

                    sensitive=
                        False,
                )
            )


    if (
        LEGACY_HISTORY_DATABASE
        .is_file()
        and
        not
        LEGACY_HISTORY_DATABASE
        .is_symlink()
    ):

        sources.append(
            BackupSource(
                source_path=
                    LEGACY_HISTORY_DATABASE,

                archive_path=
                    Path(
                        "databases"
                    )
                    /
                    "vehicle_history.db",

                category=
                    "DATABASE",

                sensitive=
                    False,
            )
        )


    return sources


def discover_configuration_sources():

    sources = []


    for path in CONFIGURATION_FILES:

        if (
            not path.is_file()
            or
            path.is_symlink()
        ):

            continue


        sources.append(
            BackupSource(
                source_path=
                    path,

                archive_path=
                    Path(
                        "configuration"
                    )
                    /
                    path.name,

                category=
                    "CONFIGURATION",

                sensitive=
                    False,
            )
        )


    return sources


def discover_sensitive_sources():

    sources = []


    for path in SENSITIVE_FILES:

        if (
            not path.is_file()
            or
            path.is_symlink()
        ):

            continue


        sources.append(
            BackupSource(
                source_path=
                    path,

                archive_path=
                    Path(
                        "sensitive"
                    )
                    /
                    path.name,

                category=
                    "SENSITIVE_AUTH",

                sensitive=
                    True,
            )
        )


    if USER_UPLOAD_DIRECTORY.is_dir():

        for path in sorted(
            USER_UPLOAD_DIRECTORY.rglob(
                "*"
            )
        ):

            if (
                not path.is_file()
                or
                path.is_symlink()
            ):

                continue


            if (
                path.suffix.lower()
                not in
                USER_IMAGE_EXTENSIONS
            ):

                continue


            if not _file_is_inside(
                path,
                USER_UPLOAD_DIRECTORY,
            ):

                continue


            relative_path = (
                path.resolve()
                .relative_to(
                    USER_UPLOAD_DIRECTORY
                    .resolve()
                )
            )


            sources.append(
                BackupSource(
                    source_path=
                        path,

                    archive_path=
                        Path(
                            "sensitive"
                        )
                        /
                        "user_photos"
                        /
                        relative_path,

                    category=
                        "SENSITIVE_USER_ASSET",

                    sensitive=
                        True,
                )
            )


    return sources


def discover_backup_sources():

    sources = (
        discover_database_sources()
        +
        discover_configuration_sources()
        +
        discover_sensitive_sources()
    )


    archive_paths = set()


    for source in sources:

        key = str(
            source.archive_path
        )


        if key in archive_paths:

            raise RuntimeError(
                "Destination de sauvegarde "
                f"dupliquée : {key}"
            )


        archive_paths.add(
            key
        )


    return sources
