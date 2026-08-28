"""
============================================================
PHOENIX VISION AI

Single Instance Startup Lock

Phoenix Security Technologies
============================================================

Ce module doit rester léger.

Il est chargé AVANT PhoenixServer / PhoenixEngine afin
d'empêcher plusieurs instances Phoenix d'ouvrir les mêmes
bases SQLite simultanément.
"""

import atexit
import json
import os
import socket

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

LOCK_PATH = (
    PROJECT_ROOT
    /
    "data"
    /
    "phoenix_runtime.lock"
)


class PhoenixAlreadyRunningError(
    RuntimeError
):
    pass


class PhoenixInstanceLock:

    def __init__(
        self,
        path=LOCK_PATH,
    ):

        self.path = Path(
            path
        )

        self._handle = None

        self._registered = False


    # ========================================================
    # PLATFORM LOCK
    # ========================================================

    def _lock_handle(
        self,
        handle,
    ):

        if os.name == "nt":

            import msvcrt


            handle.seek(
                0,
                os.SEEK_END,
            )


            if handle.tell() == 0:

                handle.write(
                    " "
                )

                handle.flush()


            handle.seek(
                0
            )


            try:

                msvcrt.locking(
                    handle.fileno(),
                    msvcrt.LK_NBLCK,
                    1,
                )

            except OSError as error:

                raise PhoenixAlreadyRunningError(
                    "Une autre instance Phoenix "
                    "est déjà active."
                ) from error


            return


        import fcntl


        try:

            fcntl.flock(
                handle.fileno(),
                fcntl.LOCK_EX
                |
                fcntl.LOCK_NB,
            )

        except OSError as error:

            raise PhoenixAlreadyRunningError(
                "Une autre instance Phoenix "
                "est déjà active."
            ) from error


    def _unlock_handle(
        self,
        handle,
    ):

        try:

            if os.name == "nt":

                import msvcrt

                handle.seek(
                    0
                )

                msvcrt.locking(
                    handle.fileno(),
                    msvcrt.LK_UNLCK,
                    1,
                )

                return


            import fcntl

            fcntl.flock(
                handle.fileno(),
                fcntl.LOCK_UN,
            )

        except Exception:

            pass


    # ========================================================
    # METADATA
    # ========================================================

    def _write_metadata(
        self,
        handle,
    ):

        payload = {
            "application":
                "Phoenix Vision AI",

            "pid":
                os.getpid(),

            "hostname":
                socket.gethostname(),

            "started_at":
                datetime.now(
                    timezone.utc
                )
                .replace(
                    microsecond=0
                )
                .isoformat(),
        }


        handle.seek(
            0
        )

        handle.truncate(
            0
        )

        json.dump(
            payload,
            handle,
            ensure_ascii=False,
            sort_keys=True,
        )

        handle.write(
            "\n"
        )

        handle.flush()


        try:

            os.fsync(
                handle.fileno()
            )

        except OSError:

            pass


    # ========================================================
    # PUBLIC API
    # ========================================================

    def acquire(
        self,
    ):

        if self._handle is not None:

            return True


        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        handle = self.path.open(
            "a+",
            encoding="utf-8",
        )


        try:

            self._lock_handle(
                handle
            )


            self._handle = handle


            self._write_metadata(
                handle
            )


            if not self._registered:

                atexit.register(
                    self.release
                )

                self._registered = True


            return True


        except Exception:

            try:

                handle.close()

            except Exception:

                pass


            raise


    def release(
        self,
    ):

        handle = self._handle


        if handle is None:

            return


        self._handle = None


        self._unlock_handle(
            handle
        )


        try:

            handle.close()

        except Exception:

            pass


    def acquired(
        self,
    ):

        return (
            self._handle
            is not None
        )


phoenix_instance_lock = (
    PhoenixInstanceLock()
)
