"""
============================================================
PHOENIX VISION AI

Automatic Backup Scheduler

Phoenix Security Technologies
============================================================
"""

import json
import os
import threading
import time

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from core.backups.backup_automation_policy import (
    AUTOMATIC_BACKUPS_ENABLED,
    AUTOMATIC_BACKUP_INTERVAL_SECONDS,
    AUTOMATIC_BACKUP_TYPE,
    SCHEDULER_POLL_SECONDS,
)

from core.backups.backup_locks import (
    backup_mutation_lock,
)

from core.backups.backup_retention import (
    backup_retention_service,
)

from core.backups.backup_service import (
    backup_service,
)

from core.backups.restore_request import (
    IN_PROGRESS_PATH,
    PENDING_RESTORE_PATH,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

AUTOMATION_JOURNAL_PATH = (
    PROJECT_ROOT
    /
    "data"
    /
    "backup_automation_journal.jsonl"
)


class BackupScheduler:

    def __init__(
        self,
        *,
        service=backup_service,
        retention=backup_retention_service,
        journal_path=AUTOMATION_JOURNAL_PATH,
        pending_path=PENDING_RESTORE_PATH,
        in_progress_path=IN_PROGRESS_PATH,
        interval_seconds=AUTOMATIC_BACKUP_INTERVAL_SECONDS,
        poll_seconds=SCHEDULER_POLL_SECONDS,
    ):

        self.service = service

        self.retention = retention

        self.journal_path = Path(
            journal_path
        )

        self.pending_path = Path(
            pending_path
        )

        self.in_progress_path = Path(
            in_progress_path
        )

        self.interval_seconds = int(
            interval_seconds
        )

        self.poll_seconds = int(
            poll_seconds
        )

        self._stop_event = (
            threading.Event()
        )

        self._thread = None

        self._state_lock = (
            threading.RLock()
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
    # RESTORE
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
    # JOURNAL
    # ========================================================

    def _journal(
        self,
        event,
        **details,
    ):

        path = self.journal_path


        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            path.parent,
            0o700,
        )


        if path.is_symlink():

            raise RuntimeError(
                "Journal Backup symbolique interdit."
            )


        payload = {
            "timestamp":
                self._utc_now()
                .replace(
                    microsecond=0
                )
                .isoformat(),

            "event":
                str(
                    event
                ),

            **details,
        }


        with path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )

            handle.write(
                "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )


        os.chmod(
            path,
            0o600,
        )


    # ========================================================
    # LATEST AUTOMATIC
    # ========================================================

    def latest_automatic(
        self,
    ):

        backups = (
            self.retention
            .automatic_backups()
        )


        if not backups:

            return None


        return backups[0]


    # ========================================================
    # DUE
    # ========================================================

    def is_due(
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


        latest = (
            self.latest_automatic()
        )


        if latest is None:

            return True


        created_at = latest.get(
            "_created_at"
        )


        if created_at is None:

            return True


        age = (
            now
            -
            created_at
        ).total_seconds()


        # Timestamp futur :
        # ne pas créer en boucle.
        if age < 0:

            return False


        return (
            age
            >=
            self.interval_seconds
        )


    # ========================================================
    # RUN ONCE
    # ========================================================

    def run_once(
        self,
        *,
        actor="PHOENIX_AUTOMATION",
        now=None,
    ):

        if not AUTOMATIC_BACKUPS_ENABLED:

            return {
                "success":
                    True,

                "status":
                    "AUTOMATIC_BACKUPS_DISABLED",

                "backup_created":
                    False,
            }


        if self.restore_active():

            return {
                "success":
                    False,

                "status":
                    "AUTOMATION_BLOCKED_BY_RESTORE",

                "backup_created":
                    False,
            }


        if not self.is_due(
            now=now
        ):

            return {
                "success":
                    True,

                "status":
                    "AUTOMATIC_BACKUP_NOT_DUE",

                "backup_created":
                    False,
            }


        with backup_mutation_lock:

            # Recheck après acquisition du verrou.
            if self.restore_active():

                return {
                    "success":
                        False,

                    "status":
                        "AUTOMATION_BLOCKED_BY_RESTORE",

                    "backup_created":
                        False,
                }


            if not self.is_due(
                now=now
            ):

                return {
                    "success":
                        True,

                    "status":
                        "AUTOMATIC_BACKUP_NOT_DUE",

                    "backup_created":
                        False,
                }


            backup = (
                self.service
                .create_backup(
                    actor=
                        actor,

                    backup_type=
                        AUTOMATIC_BACKUP_TYPE,
                )
            )


            if (
                not isinstance(
                    backup,
                    dict,
                )
                or
                backup.get(
                    "success"
                )
                is not True
            ):

                self._journal(
                    "AUTOMATIC_BACKUP_FAILED",
                    result=
                        backup,
                )

                return {
                    "success":
                        False,

                    "status":
                        "AUTOMATIC_BACKUP_FAILED",

                    "backup_created":
                        False,

                    "backup":
                        backup,
                }


            self._journal(
                "AUTOMATIC_BACKUP_CREATED",
                backup_id=
                    backup.get(
                        "backup_id"
                    ),
            )


            retention = (
                self.retention
                .apply(
                    now=now
                )
            )


            self._journal(
                "BACKUP_RETENTION",
                status=
                    retention.get(
                        "status"
                    ),

                deleted=
                    retention.get(
                        "deleted",
                        [],
                    ),

                skipped=
                    retention.get(
                        "skipped",
                        [],
                    ),
            )


            return {
                "success":
                    True,

                "status":
                    "AUTOMATIC_BACKUP_CREATED",

                "backup_created":
                    True,

                "backup":
                    backup,

                "retention":
                    retention,
            }


    # ========================================================
    # LOOP
    # ========================================================

    def _loop(
        self,
    ):

        while not self._stop_event.is_set():

            try:

                self.run_once()

            except Exception as error:

                try:

                    self._journal(
                        "AUTOMATION_ERROR",
                        error=
                            type(
                                error
                            ).__name__,

                        message=
                            str(
                                error
                            ),
                    )

                except Exception:

                    pass


            self._stop_event.wait(
                self.poll_seconds
            )


    # ========================================================
    # START
    # ========================================================

    def start(
        self,
    ):

        with self._state_lock:

            if (
                self._thread is not None
                and
                self._thread.is_alive()
            ):

                return False


            self._stop_event.clear()


            self._thread = threading.Thread(
                target=
                    self._loop,

                name=
                    "PhoenixBackupScheduler",

                daemon=True,
            )


            self._thread.start()


            return True


    # ========================================================
    # STOP
    # ========================================================

    def stop(
        self,
        *,
        timeout=5.0,
    ):

        with self._state_lock:

            thread = self._thread


            if thread is None:

                return True


            self._stop_event.set()


        thread.join(
            timeout=
                float(
                    timeout
                )
        )


        stopped = (
            not thread.is_alive()
        )


        if stopped:

            with self._state_lock:

                self._thread = None


        return stopped


    # ========================================================
    # STATUS
    # ========================================================

    def status(
        self,
    ):

        thread = self._thread


        return {
            "enabled":
                AUTOMATIC_BACKUPS_ENABLED,

            "running":
                bool(
                    thread
                    and
                    thread.is_alive()
                ),

            "interval_seconds":
                self.interval_seconds,

            "poll_seconds":
                self.poll_seconds,

            "restore_blocked":
                self.restore_active(),
        }


backup_scheduler = (
    BackupScheduler()
)
