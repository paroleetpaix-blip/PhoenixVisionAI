"""
============================================================
PHOENIX VISION AI

Enterprise Backup Manifest

Phoenix Security Technologies
============================================================
"""

import hashlib
import json
import os

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from core import constants

from core.backups.backup_policy import (
    PROJECT_ROOT,
)


MANIFEST_SCHEMA_VERSION = 1


def utc_now_iso():

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            microsecond=0
        )
        .isoformat()
    )


def sha256_file(
    path,
    chunk_size=1024 * 1024,
):

    path = Path(
        path
    )

    digest = hashlib.sha256()


    with path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                chunk_size
            )

            if not chunk:

                break

            digest.update(
                chunk
            )


    return digest.hexdigest()


def project_relative_path(
    path,
):

    path = Path(
        path
    ).resolve()

    root = (
        PROJECT_ROOT
        .resolve()
    )


    try:

        return str(
            path.relative_to(
                root
            )
        )

    except ValueError:

        raise ValueError(
            "La source est située hors "
            "du projet Phoenix Vision AI."
        )


def build_manifest(
    *,
    backup_id,
    actor,
    backup_type,
    files,
):

    total_size = sum(
        int(
            item.get(
                "size_bytes",
                0,
            )
        )

        for item
        in files
    )


    category_counts = {}

    for item in files:

        category = str(
            item.get(
                "category"
            )
            or
            "UNKNOWN"
        )

        category_counts[
            category
        ] = (
            category_counts.get(
                category,
                0
            )
            +
            1
        )


    return {
        "schema_version":
            MANIFEST_SCHEMA_VERSION,

        "backup_id":
            str(
                backup_id
            ),

        "application":
            getattr(
                constants,
                "APP_NAME",
                "Phoenix Vision AI",
            ),

        "application_version":
            getattr(
                constants,
                "VERSION",
                "unknown",
            ),

        "created_at":
            utc_now_iso(),

        "backup_type":
            str(
                backup_type
            ).upper(),

        "actor":
            str(
                actor
                or
                "UNKNOWN"
            ),

        "status":
            "COMPLETE",

        "file_count":
            len(
                files
            ),

        "total_size_bytes":
            total_size,

        "category_counts":
            category_counts,

        "files":
            files,
    }


def manifest_bytes(
    manifest,
):

    payload = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )

    return (
        payload
        +
        "\n"
    ).encode(
        "utf-8"
    )


def write_manifest(
    backup_directory,
    manifest,
):

    backup_directory = Path(
        backup_directory
    )

    manifest_path = (
        backup_directory
        /
        "manifest.json"
    )

    digest_path = (
        backup_directory
        /
        "manifest.sha256"
    )


    payload = manifest_bytes(
        manifest
    )


    manifest_path.write_bytes(
        payload
    )

    os.chmod(
        manifest_path,
        0o600,
    )


    digest = hashlib.sha256(
        payload
    ).hexdigest()


    digest_path.write_text(
        digest
        +
        "\n",
        encoding="utf-8",
    )

    os.chmod(
        digest_path,
        0o600,
    )


    return {
        "manifest_path":
            manifest_path,

        "digest_path":
            digest_path,

        "manifest_sha256":
            digest,
    }


def verify_manifest_hash(
    backup_directory,
):

    backup_directory = Path(
        backup_directory
    )

    manifest_path = (
        backup_directory
        /
        "manifest.json"
    )

    digest_path = (
        backup_directory
        /
        "manifest.sha256"
    )


    if (
        not manifest_path.is_file()
        or
        not digest_path.is_file()
    ):

        return False


    expected = (
        digest_path
        .read_text(
            encoding="utf-8"
        )
        .strip()
        .lower()
    )

    actual = sha256_file(
        manifest_path
    )


    return (
        expected
        ==
        actual
    )
