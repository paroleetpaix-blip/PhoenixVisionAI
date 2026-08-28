"""
============================================================
PHOENIX VISION AI

Isolated Live Restore Transaction Executor

Phoenix Security Technologies
============================================================

Exécute le plan transactionnel UNIQUEMENT sur une copie
isolée de Phoenix.

L'installation réelle est explicitement interdite.
"""

import os
import shutil

from pathlib import Path

from core.backups.backup_manifest import (
    sha256_file,
)

from core.backups.backup_policy import (
    PROJECT_ROOT,
)

from core.backups.restore_flags import (
    LIVE_RESTORE_ENABLED,
)

from core.startup_lock import (
    phoenix_instance_lock,
)


class IsolatedTransactionExecutor:

    # ========================================================
    # SAFE PATH
    # ========================================================

    @staticmethod
    def _safe_child(
        root,
        relative,
    ):

        root = Path(
            root
        ).resolve()

        relative = Path(
            str(
                relative
                or
                ""
            )
        )


        if (
            not str(relative)
            or
            relative.is_absolute()
            or
            ".." in relative.parts
        ):

            raise RuntimeError(
                "Chemin transaction invalide."
            )


        candidate = (
            root
            /
            relative
        ).resolve()


        try:

            candidate.relative_to(
                root
            )

        except ValueError:

            raise RuntimeError(
                "Chemin transaction hors périmètre."
            )


        return candidate


    # ========================================================
    # ISOLATION
    # ========================================================

    @staticmethod
    def _validate_isolated_root(
        project_root,
    ):

        project_root = Path(
            project_root
        ).resolve()

        real_root = (
            PROJECT_ROOT
            .resolve()
        )


        if project_root == real_root:

            raise RuntimeError(
                "REAL_PROJECT_ROOT_FORBIDDEN"
            )


        try:

            real_root.relative_to(
                project_root
            )

        except ValueError:

            pass

        else:

            raise RuntimeError(
                "PARENT_OF_REAL_PROJECT_FORBIDDEN"
            )


        return project_root


    # ========================================================
    # FSYNC DIRECTORY
    # ========================================================

    @staticmethod
    def _fsync_directory(
        path,
    ):

        path = Path(
            path
        )


        flags = os.O_RDONLY

        if hasattr(
            os,
            "O_DIRECTORY",
        ):

            flags |= os.O_DIRECTORY


        try:

            descriptor = os.open(
                path,
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


    # ========================================================
    # ATOMIC COPY
    # ========================================================

    def _atomic_copy(
        self,
        source,
        target,
    ):

        source = Path(
            source
        )

        target = Path(
            target
        )


        if (
            not source.is_file()
            or
            source.is_symlink()
        ):

            raise RuntimeError(
                "Source transaction invalide."
            )


        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        if target.parent.is_symlink():

            raise RuntimeError(
                "Parent transaction symbolique interdit."
            )


        temporary = (
            target.parent
            /
            (
                "."
                +
                target.name
                +
                ".restore-tmp"
            )
        )


        if (
            temporary.exists()
            or
            temporary.is_symlink()
        ):

            raise RuntimeError(
                "Temporaire transaction déjà présent."
            )


        try:

            with source.open(
                "rb"
            ) as source_handle:

                with temporary.open(
                    "xb"
                ) as target_handle:

                    shutil.copyfileobj(
                        source_handle,
                        target_handle,
                        length=
                            1024
                            *
                            1024,
                    )

                    target_handle.flush()

                    os.fsync(
                        target_handle.fileno()
                    )


            os.chmod(
                temporary,
                0o600,
            )


            if (
                sha256_file(
                    source
                )
                !=
                sha256_file(
                    temporary
                )
            ):

                raise RuntimeError(
                    "SHA-256 transaction incohérent."
                )


            os.replace(
                temporary,
                target,
            )

            os.chmod(
                target,
                0o600,
            )

            self._fsync_directory(
                target.parent
            )


        finally:

            if temporary.exists():

                try:

                    temporary.unlink()

                except OSError:

                    pass


    # ========================================================
    # REMOVE
    # ========================================================

    def _remove_file(
        self,
        path,
    ):

        path = Path(
            path
        )


        if not (
            path.exists()
            or
            path.is_symlink()
        ):

            return


        if path.is_symlink():

            raise RuntimeError(
                "Suppression lien symbolique refusée."
            )


        if not path.is_file():

            raise RuntimeError(
                "Suppression cible non-fichier refusée."
            )


        path.unlink()

        self._fsync_directory(
            path.parent
        )


    # ========================================================
    # SIDECARS
    # ========================================================

    def _remove_sidecars(
        self,
        *,
        project_root,
        operation,
    ):

        for relative in operation.get(
            "sqlite_sidecars",
            [],
        ):

            sidecar = self._safe_child(
                project_root,
                relative,
            )

            self._remove_file(
                sidecar
            )


    # ========================================================
    # APPLY
    # ========================================================

    def _apply_operation(
        self,
        *,
        project_root,
        staging_directory,
        operation,
    ):

        action = operation[
            "action"
        ]


        if action == "KEEP":

            return


        target = self._safe_child(
            project_root,
            operation[
                "target"
            ],
        )


        # ====================================================
        # QUARANTINE
        # ====================================================

        if action == "QUARANTINE":

            if (
                not target.is_file()
                or
                target.is_symlink()
            ):

                raise RuntimeError(
                    "Cible QUARANTINE invalide."
                )


            quarantine = self._safe_child(
                staging_directory,
                operation[
                    "quarantine_target"
                ],
            )


            quarantine.parent.mkdir(
                parents=True,
                exist_ok=True,
            )


            if (
                quarantine.exists()
                or
                quarantine.is_symlink()
            ):

                raise RuntimeError(
                    "Quarantaine déjà occupée."
                )


            os.replace(
                target,
                quarantine,
            )

            self._fsync_directory(
                target.parent
            )

            self._fsync_directory(
                quarantine.parent
            )

            return


        # ====================================================
        # REPLACE / CREATE
        # ====================================================

        if action not in {
            "REPLACE",
            "CREATE",
        }:

            raise RuntimeError(
                "Action transaction non supportée."
            )


        restore_source = self._safe_child(
            staging_directory,
            operation[
                "restore_source"
            ],
        )


        self._remove_sidecars(
            project_root=
                project_root,

            operation=
                operation,
        )


        self._atomic_copy(
            restore_source,
            target,
        )


    # ========================================================
    # RESTORE SIDECARS FROM SNAPSHOT
    # ========================================================

    def _rollback_sidecars(
        self,
        *,
        project_root,
        snapshot_root,
        operation,
    ):

        for relative in operation.get(
            "sqlite_sidecars",
            [],
        ):

            target = self._safe_child(
                project_root,
                relative,
            )

            snapshot = self._safe_child(
                snapshot_root,
                relative,
            )


            if snapshot.is_file():

                self._atomic_copy(
                    snapshot,
                    target,
                )

            else:

                self._remove_file(
                    target
                )


    # ========================================================
    # ROLLBACK OPERATION
    # ========================================================

    def _rollback_operation(
        self,
        *,
        project_root,
        snapshot_root,
        operation,
    ):

        action = operation[
            "action"
        ]


        if action == "KEEP":

            return


        target = self._safe_child(
            project_root,
            operation[
                "target"
            ],
        )


        if action in {
            "REPLACE",
            "QUARANTINE",
        }:

            snapshot = self._safe_child(
                snapshot_root,
                operation[
                    "target"
                ],
            )


            if not snapshot.is_file():

                raise RuntimeError(
                    "Snapshot rollback absent."
                )


            self._atomic_copy(
                snapshot,
                target,
            )


        elif action == "CREATE":

            self._remove_file(
                target
            )


        else:

            raise RuntimeError(
                "Action rollback inconnue."
            )


        self._rollback_sidecars(
            project_root=
                project_root,

            snapshot_root=
                snapshot_root,

            operation=
                operation,
        )


    # ========================================================
    # VERIFY SUCCESS
    # ========================================================

    def _verify_success(
        self,
        *,
        project_root,
        staging_directory,
        transaction,
    ):

        checked = 0

        valid = 0


        for operation in transaction[
            "operations"
        ]:

            action = operation[
                "action"
            ]


            if action == "KEEP":

                continue


            checked += 1


            target = self._safe_child(
                project_root,
                operation[
                    "target"
                ],
            )


            if action == "QUARANTINE":

                quarantine = self._safe_child(
                    staging_directory,
                    operation[
                        "quarantine_target"
                    ],
                )


                if (
                    not target.exists()
                    and
                    quarantine.is_file()
                ):

                    valid += 1


                continue


            restore_source = self._safe_child(
                staging_directory,
                operation[
                    "restore_source"
                ],
            )


            if (
                target.is_file()
                and
                sha256_file(
                    target
                )
                ==
                sha256_file(
                    restore_source
                )
            ):

                sidecars_absent = all(
                    not self._safe_child(
                        project_root,
                        relative,
                    ).exists()

                    for relative
                    in operation.get(
                        "sqlite_sidecars",
                        [],
                    )
                )


                if sidecars_absent:

                    valid += 1


        return {
            "success":
                checked == valid,

            "status":
                (
                    "VALID"
                    if checked == valid
                    else
                    "INVALID"
                ),

            "checked":
                checked,

            "valid":
                valid,
        }


    # ========================================================
    # VERIFY ROLLBACK
    # ========================================================

    def _verify_rollback(
        self,
        *,
        project_root,
        snapshot_root,
        transaction,
    ):

        checked = 0

        valid = 0


        for operation in transaction[
            "operations"
        ]:

            action = operation[
                "action"
            ]


            if action == "KEEP":

                continue


            checked += 1


            target = self._safe_child(
                project_root,
                operation[
                    "target"
                ],
            )


            operation_valid = True


            if action in {
                "REPLACE",
                "QUARANTINE",
            }:

                snapshot = self._safe_child(
                    snapshot_root,
                    operation[
                        "target"
                    ],
                )


                operation_valid = (
                    snapshot.is_file()
                    and
                    target.is_file()
                    and
                    sha256_file(
                        snapshot
                    )
                    ==
                    sha256_file(
                        target
                    )
                )


            elif action == "CREATE":

                operation_valid = (
                    not target.exists()
                )


            else:

                operation_valid = False


            if operation_valid:

                for relative in operation.get(
                    "sqlite_sidecars",
                    [],
                ):

                    current = self._safe_child(
                        project_root,
                        relative,
                    )

                    previous = self._safe_child(
                        snapshot_root,
                        relative,
                    )


                    if previous.is_file():

                        if (
                            not current.is_file()
                            or
                            sha256_file(
                                current
                            )
                            !=
                            sha256_file(
                                previous
                            )
                        ):

                            operation_valid = False
                            break


                    elif current.exists():

                        operation_valid = False
                        break


            if operation_valid:

                valid += 1


        return {
            "success":
                checked == valid,

            "status":
                (
                    "VALID"
                    if checked == valid
                    else
                    "INVALID"
                ),

            "checked":
                checked,

            "valid":
                valid,
        }


    # ========================================================
    # EXECUTE ISOLATED
    # ========================================================

    def execute_isolated(
        self,
        *,
        project_root,
        transaction,
        snapshot,
        simulate_failure_after=None,
        simulate_rollback_failure_after=None,
        _live_authorized=False,
    ):

        if _live_authorized:

            project_root = Path(
                project_root
            ).resolve()


            if (
                project_root
                !=
                PROJECT_ROOT.resolve()
            ):

                raise RuntimeError(
                    "LIVE_PROJECT_ROOT_INVALID"
                )


            if not phoenix_instance_lock.acquired():

                raise RuntimeError(
                    "RESTORE_LIVE_LOCK_REQUIRED"
                )


            if not LIVE_RESTORE_ENABLED:

                raise RuntimeError(
                    "LIVE_RESTORE_DISABLED"
                )


        else:

            project_root = (
                self._validate_isolated_root(
                    project_root
                )
            )


        staging_directory = Path(
            transaction[
                "staging_directory"
            ]
        ).resolve()

        snapshot_root = Path(
            snapshot[
                "snapshot_directory"
            ]
        ).resolve()


        if not snapshot_root.is_dir():

            raise RuntimeError(
                "Snapshot transactionnel absent."
            )


        applied = []

        active_counter = 0


        try:

            for operation in transaction[
                "operations"
            ]:

                if not operation.get(
                    "active_write"
                ):

                    continue


                self._apply_operation(
                    project_root=
                        project_root,

                    staging_directory=
                        staging_directory,

                    operation=
                        operation,
                )


                applied.append(
                    operation
                )

                active_counter += 1


                if (
                    simulate_failure_after
                    is not None
                    and
                    active_counter
                    >=
                    int(
                        simulate_failure_after
                    )
                ):

                    raise RuntimeError(
                        "SIMULATED_TRANSACTION_FAILURE"
                    )


            verification = (
                self._verify_success(
                    project_root=
                        project_root,

                    staging_directory=
                        staging_directory,

                    transaction=
                        transaction,
                )
            )


            if not verification[
                "success"
            ]:

                raise RuntimeError(
                    "TRANSACTION_POSTCHECK_FAILED"
                )


            return {
                "success":
                    True,

                "status":
                    "ISOLATED_TRANSACTION_RESTORED",

                "safe_state":
                    True,

                "active_operations_applied":
                    len(
                        applied
                    ),

                "verification":
                    verification,

                "rollback_performed":
                    False,
            }


        except Exception as restore_error:

            rollback_counter = 0


            try:

                for operation in reversed(
                    applied
                ):

                    self._rollback_operation(
                        project_root=
                            project_root,

                        snapshot_root=
                            snapshot_root,

                        operation=
                            operation,
                    )


                    rollback_counter += 1


                    if (
                        simulate_rollback_failure_after
                        is not None
                        and
                        rollback_counter
                        >=
                        int(
                            simulate_rollback_failure_after
                        )
                    ):

                        raise RuntimeError(
                            "SIMULATED_TRANSACTION_ROLLBACK_FAILURE"
                        )


                verification = (
                    self._verify_rollback(
                        project_root=
                            project_root,

                        snapshot_root=
                            snapshot_root,

                        transaction=
                            transaction,
                    )
                )


                if not verification[
                    "success"
                ]:

                    raise RuntimeError(
                        "TRANSACTION_ROLLBACK_VERIFY_FAILED"
                    )


                return {
                    "success":
                        False,

                    "status":
                        "ISOLATED_TRANSACTION_ROLLED_BACK",

                    "safe_state":
                        True,

                    "restore_error":
                        str(
                            restore_error
                        ),

                    "rollback_performed":
                        True,

                    "rollback_verification":
                        verification,
                }


            except Exception as rollback_error:

                return {
                    "success":
                        False,

                    "status":
                        "ISOLATED_TRANSACTION_ROLLBACK_FAILED",

                    "safe_state":
                        False,

                    "restore_error":
                        str(
                            restore_error
                        ),

                    "rollback_error":
                        str(
                            rollback_error
                        ),

                    "rollback_performed":
                        True,
                }

    # ========================================================
    # EXECUTE LIVE
    # ========================================================

    def execute_live(
        self,
        *,
        transaction,
        snapshot,
    ):

        if not phoenix_instance_lock.acquired():

            raise RuntimeError(
                "RESTORE_LIVE_LOCK_REQUIRED"
            )


        if not LIVE_RESTORE_ENABLED:

            return {
                "success":
                    False,

                "status":
                    "LIVE_RESTORE_DISABLED",

                "safe_state":
                    True,

                "write_performed":
                    False,
            }


        return self.execute_isolated(
            project_root=
                PROJECT_ROOT,

            transaction=
                transaction,

            snapshot=
                snapshot,

            _live_authorized=
                True,
        )


isolated_transaction_executor = (
    IsolatedTransactionExecutor()
)
