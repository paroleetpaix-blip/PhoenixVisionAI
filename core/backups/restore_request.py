"""
============================================================
PHOENIX VISION AI

Restore Request Store

Phoenix Security Technologies
============================================================
"""

import json
import os
import re
import secrets

from datetime import (
    datetime,
    timezone,
)

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

PENDING_RESTORE_PATH = (
    DATA_DIRECTORY
    /
    "restore_pending.json"
)

LAST_RESULT_PATH = (
    DATA_DIRECTORY
    /
    "restore_last_result.json"
)

IN_PROGRESS_PATH = (
    DATA_DIRECTORY
    /
    "restore_in_progress.json"
)


REQUEST_SCHEMA_VERSION = 1

BACKUP_ID_PATTERN = re.compile(
    r"^PHX-BKP-\d{8}-\d{6}-[A-F0-9]{6}$"
)

REQUEST_ID_PATTERN = re.compile(
    r"^PHX-RST-[A-F0-9]{16}$"
)


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


def validate_backup_id(
    value,
):

    value = str(
        value
        or
        ""
    ).strip()


    if not BACKUP_ID_PATTERN.fullmatch(
        value
    ):

        raise ValueError(
            "Référence de sauvegarde invalide."
        )


    return value


def validate_restore_request_payload(
    payload,
):

    if not isinstance(
        payload,
        dict,
    ):

        raise ValueError(
            "Demande Restore invalide."
        )


    if (
        payload.get(
            "schema_version"
        )
        !=
        REQUEST_SCHEMA_VERSION
    ):

        raise ValueError(
            "Version de demande Restore incompatible."
        )


    request_id = str(
        payload.get(
            "request_id"
        )
        or
        ""
    ).strip()


    if not REQUEST_ID_PATTERN.fullmatch(
        request_id
    ):

        raise ValueError(
            "Identifiant de demande Restore invalide."
        )


    backup_id = validate_backup_id(
        payload.get(
            "backup_id"
        )
    )

    pre_restore_backup_id = (
        validate_backup_id(
            payload.get(
                "pre_restore_backup_id"
            )
        )
    )


    if (
        backup_id
        ==
        pre_restore_backup_id
    ):

        raise ValueError(
            "Le backup source et le PRE_RESTORE "
            "doivent être distincts."
        )


    status = str(
        payload.get(
            "status"
        )
        or
        ""
    ).strip().upper()


    if status != "PENDING":

        raise ValueError(
            "État de demande Restore invalide."
        )


    actor = str(
        payload.get(
            "actor"
        )
        or
        ""
    ).strip()


    if not actor:

        raise ValueError(
            "Acteur Restore absent."
        )


    if len(actor) > 128:

        raise ValueError(
            "Acteur Restore trop long."
        )


    requested_at = str(
        payload.get(
            "requested_at"
        )
        or
        ""
    ).strip()


    if not requested_at:

        raise ValueError(
            "Date de demande Restore absente."
        )


    return {
        "schema_version":
            REQUEST_SCHEMA_VERSION,

        "request_id":
            request_id,

        "backup_id":
            backup_id,

        "pre_restore_backup_id":
            pre_restore_backup_id,

        "actor":
            actor,

        "requested_at":
            requested_at,

        "status":
            "PENDING",
    }


class RestoreRequestStore:

    def __init__(
        self,
        *,
        pending_path=PENDING_RESTORE_PATH,
        last_result_path=LAST_RESULT_PATH,
        in_progress_path=None,
    ):

        self.pending_path = Path(
            pending_path
        )

        self.last_result_path = Path(
            last_result_path
        )


        if in_progress_path is None:

            in_progress_path = (
                self.pending_path
                .with_name(
                    "restore_in_progress.json"
                )
            )


        self.in_progress_path = Path(
            in_progress_path
        )


    def _prepare_parent(
        self,
        path,
    ):

        parent = Path(
            path
        ).parent

        parent.mkdir(
            parents=True,
            exist_ok=True,
        )


    def _atomic_json_write(
        self,
        path,
        payload,
    ):

        path = Path(
            path
        )

        self._prepare_parent(
            path
        )


        if path.is_symlink():

            raise RuntimeError(
                "Un fichier Restore Phoenix "
                "ne peut pas être un lien symbolique."
            )


        temporary = (
            path.parent
            /
            (
                "."
                +
                path.name
                +
                "."
                +
                secrets.token_hex(
                    4
                )
                +
                ".tmp"
            )
        )


        try:

            with temporary.open(
                "x",
                encoding="utf-8",
            ) as handle:

                json.dump(
                    payload,
                    handle,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )

                handle.write(
                    "\n"
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )


            os.chmod(
                temporary,
                0o600,
            )

            os.replace(
                temporary,
                path,
            )

            os.chmod(
                path,
                0o600,
            )


        finally:

            if temporary.exists():

                try:

                    temporary.unlink()

                except OSError:

                    pass


    def has_pending(
        self,
    ):

        return (
            self.pending_path.exists()
            or
            self.pending_path.is_symlink()
        )


    def create_pending(
        self,
        *,
        backup_id,
        pre_restore_backup_id,
        actor,
    ):

        if self.has_pending():

            raise RuntimeError(
                "Une restauration Phoenix "
                "est déjà en attente."
            )


        payload = {
            "schema_version":
                REQUEST_SCHEMA_VERSION,

            "request_id":
                (
                    "PHX-RST-"
                    +
                    secrets.token_hex(
                        8
                    ).upper()
                ),

            "backup_id":
                validate_backup_id(
                    backup_id
                ),

            "pre_restore_backup_id":
                validate_backup_id(
                    pre_restore_backup_id
                ),

            "actor":
                str(
                    actor
                    or
                    ""
                ).strip(),

            "requested_at":
                utc_now_iso(),

            "status":
                "PENDING",
        }


        payload = (
            validate_restore_request_payload(
                payload
            )
        )


        self._atomic_json_write(
            self.pending_path,
            payload,
        )


        return dict(
            payload
        )


    def read_pending(
        self,
    ):

        if not self.has_pending():

            return None


        if self.pending_path.is_symlink():

            raise RuntimeError(
                "La demande Restore est "
                "un lien symbolique interdit."
            )


        if not self.pending_path.is_file():

            raise RuntimeError(
                "La demande Restore "
                "n'est pas un fichier valide."
            )


        try:

            payload = json.loads(
                self.pending_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception as error:

            raise RuntimeError(
                "Demande Restore illisible."
            ) from error


        return (
            validate_restore_request_payload(
                payload
            )
        )


    def remove_pending(
        self,
    ):

        if not self.has_pending():

            return


        if self.pending_path.is_symlink():

            raise RuntimeError(
                "Suppression refusée : "
                "pending Restore est un lien."
            )


        if not self.pending_path.is_file():

            raise RuntimeError(
                "Suppression refusée : "
                "pending Restore invalide."
            )


        self.pending_path.unlink()


    def has_in_progress(
        self,
    ):

        return (
            self.in_progress_path.exists()
            or
            self.in_progress_path.is_symlink()
        )


    def read_in_progress(
        self,
    ):

        if not self.has_in_progress():

            return None


        if self.in_progress_path.is_symlink():

            raise RuntimeError(
                "Restore IN_PROGRESS symbolique interdit."
            )


        if not self.in_progress_path.is_file():

            raise RuntimeError(
                "Restore IN_PROGRESS invalide."
            )


        try:

            payload = json.loads(
                self.in_progress_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception as error:

            raise RuntimeError(
                "Restore IN_PROGRESS illisible."
            ) from error


        return (
            validate_restore_request_payload(
                payload
            )
        )


    def _fsync_parent(
        self,
        path,
    ):

        parent = Path(
            path
        ).parent


        flags = os.O_RDONLY

        if hasattr(
            os,
            "O_DIRECTORY",
        ):

            flags |= os.O_DIRECTORY


        try:

            descriptor = os.open(
                str(
                    parent
                ),
                flags,
            )

        except OSError:

            return


        try:

            os.fsync(
                descriptor
            )

        finally:

            os.close(
                descriptor
            )


    def claim_pending(
        self,
    ):

        if self.has_in_progress():

            raise RuntimeError(
                "Une restauration Phoenix "
                "est déjà IN_PROGRESS."
            )


        request = self.read_pending()


        if request is None:

            return None


        if self.pending_path.is_symlink():

            raise RuntimeError(
                "Pending Restore symbolique interdit."
            )


        self._prepare_parent(
            self.in_progress_path
        )


        if (
            self.in_progress_path.exists()
            or
            self.in_progress_path.is_symlink()
        ):

            raise RuntimeError(
                "Restore IN_PROGRESS déjà présent."
            )


        os.replace(
            self.pending_path,
            self.in_progress_path,
        )

        os.chmod(
            self.in_progress_path,
            0o600,
        )

        self._fsync_parent(
            self.in_progress_path
        )


        return dict(
            request
        )


    def remove_in_progress(
        self,
    ):

        if not self.has_in_progress():

            return


        if self.in_progress_path.is_symlink():

            raise RuntimeError(
                "Suppression IN_PROGRESS symbolique refusée."
            )


        if not self.in_progress_path.is_file():

            raise RuntimeError(
                "Suppression IN_PROGRESS invalide."
            )


        self.in_progress_path.unlink()

        self._fsync_parent(
            self.in_progress_path
        )


    def write_result(
        self,
        *,
        request,
        status,
        success,
        details=None,
    ):

        request = dict(
            request
            or
            {}
        )


        payload = {
            "schema_version":
                REQUEST_SCHEMA_VERSION,

            "request_id":
                request.get(
                    "request_id"
                ),

            "backup_id":
                request.get(
                    "backup_id"
                ),

            "pre_restore_backup_id":
                request.get(
                    "pre_restore_backup_id"
                ),

            "actor":
                request.get(
                    "actor"
                ),

            "requested_at":
                request.get(
                    "requested_at"
                ),

            "completed_at":
                utc_now_iso(),

            "status":
                str(
                    status
                ),

            "success":
                bool(
                    success
                ),

            "details":
                (
                    details
                    if isinstance(
                        details,
                        dict,
                    )
                    else
                    {}
                ),
        }


        self._atomic_json_write(
            self.last_result_path,
            payload,
        )


        return dict(
            payload
        )


    def read_last_result(
        self,
    ):

        if not self.last_result_path.exists():

            return None


        if self.last_result_path.is_symlink():

            raise RuntimeError(
                "Le résultat Restore est "
                "un lien symbolique interdit."
            )


        if not self.last_result_path.is_file():

            raise RuntimeError(
                "Résultat Restore invalide."
            )


        payload = json.loads(
            self.last_result_path.read_text(
                encoding="utf-8"
            )
        )


        if not isinstance(
            payload,
            dict,
        ):

            raise RuntimeError(
                "Résultat Restore invalide."
            )


        return payload


restore_request_store = (
    RestoreRequestStore()
)
