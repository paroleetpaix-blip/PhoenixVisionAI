"""
============================================================
PHOENIX VISION AI

Enterprise System Health Service

Observation locale de l'installation Phoenix.
Aucun composant n'est démarré par ce service.

Phoenix Security Technologies
============================================================
"""

from __future__ import annotations

import os
import platform
import sqlite3
import sys
import time

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

import psutil

from core import constants
from core import runtime


STATUS_ONLINE = "EN_LIGNE"
STATUS_AVAILABLE = "DISPONIBLE"
STATUS_UNAVAILABLE = "INDISPONIBLE"

OVERALL_OPERATIONAL = "OPERATIONNEL"
OVERALL_ATTENTION = "ATTENTION"
OVERALL_UNAVAILABLE = "INDISPONIBLE"


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

DATA_DIRECTORY = (
    PROJECT_ROOT
    /
    "data"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    /
    "outputs"
)

VIDEOS_DIRECTORY = (
    PROJECT_ROOT
    /
    "videos"
)


def utc_now_iso():

    return (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )


def bytes_to_mb(
    value,
):

    return round(
        float(
            value
        )
        /
        (
            1024
            *
            1024
        ),
        2,
    )


def bytes_to_gb(
    value,
):

    return round(
        float(
            value
        )
        /
        (
            1024
            *
            1024
            *
            1024
        ),
        2,
    )


def percentage(
    value,
):

    return round(
        float(
            value
        ),
        1,
    )


def timestamp_iso(
    timestamp,
):

    try:

        return (
            datetime.fromtimestamp(
                float(
                    timestamp
                ),
                tz=timezone.utc,
            )
            .isoformat()
        )

    except (
        TypeError,
        ValueError,
        OSError,
    ):

        return None


class SystemHealthService:

    def __init__(
        self,
        *,
        project_root=PROJECT_ROOT,
    ):

        self.project_root = Path(
            project_root
        ).resolve()

        self.process = psutil.Process(
            os.getpid()
        )

        self.started_at = time.time()


    # ========================================================
    # MACHINE
    # ========================================================

    def machine_metrics(
        self,
    ):

        cpu_percent = psutil.cpu_percent(
            interval=0.1
        )

        memory = psutil.virtual_memory()

        disk = psutil.disk_usage(
            str(
                self.project_root
            )
        )

        boot_time = psutil.boot_time()


        return {
            "status":
                STATUS_ONLINE,

            "cpu": {
                "percent":
                    percentage(
                        cpu_percent
                    ),

                "logical_cores":
                    psutil.cpu_count(
                        logical=True
                    ),

                "physical_cores":
                    psutil.cpu_count(
                        logical=False
                    ),
            },

            "memory": {
                "percent":
                    percentage(
                        memory.percent
                    ),

                "total_gb":
                    bytes_to_gb(
                        memory.total
                    ),

                "used_gb":
                    bytes_to_gb(
                        memory.used
                    ),

                "available_gb":
                    bytes_to_gb(
                        memory.available
                    ),
            },

            "disk": {
                "percent":
                    percentage(
                        disk.percent
                    ),

                "total_gb":
                    bytes_to_gb(
                        disk.total
                    ),

                "used_gb":
                    bytes_to_gb(
                        disk.used
                    ),

                "free_gb":
                    bytes_to_gb(
                        disk.free
                    ),
            },

            "boot_time":
                timestamp_iso(
                    boot_time
                ),

            "uptime_seconds":
                max(
                    0,
                    int(
                        time.time()
                        -
                        boot_time
                    ),
                ),
        }


    # ========================================================
    # PROCESSUS PHOENIX
    # ========================================================

    def process_metrics(
        self,
    ):

        try:

            memory = (
                self.process
                .memory_info()
            )

            create_time = (
                self.process
                .create_time()
            )


            return {
                "status":
                    STATUS_ONLINE,

                "pid":
                    self.process.pid,

                "cpu_percent":
                    percentage(
                        self.process
                        .cpu_percent(
                            interval=0.0
                        )
                    ),

                "memory_rss_mb":
                    bytes_to_mb(
                        memory.rss
                    ),

                "threads":
                    self.process
                    .num_threads(),

                "started_at":
                    timestamp_iso(
                        create_time
                    ),

                "uptime_seconds":
                    max(
                        0,
                        int(
                            time.time()
                            -
                            create_time
                        ),
                    ),
            }

        except (
            psutil.Error,
            OSError,
        ) as error:

            return {
                "status":
                    STATUS_UNAVAILABLE,

                "error":
                    type(
                        error
                    ).__name__,
            }


    # ========================================================
    # RUNTIME PHOENIX
    # ========================================================

    def _runtime_component_status(
        self,
        component,
    ):

        if component is None:

            return {
                "status":
                    STATUS_AVAILABLE,

                "runtime_active":
                    False,
            }


        try:

            get_status = getattr(
                component,
                "get_status",
                None,
            )


            if callable(
                get_status
            ):

                raw_status = get_status()

            else:

                raw_status = getattr(
                    component,
                    "status",
                    None,
                )


            normalized = str(
                raw_status
                or
                ""
            ).strip().lower()


            active_values = {
                "actif",
                "active",
                "running",
                "online",
                "en ligne",
                "en_ligne",
                "started",
                "démarré",
                "demarre",
            }


            if normalized in active_values:

                status = STATUS_ONLINE
                active = True

            else:

                status = STATUS_AVAILABLE
                active = False


            return {
                "status":
                    status,

                "runtime_active":
                    active,

                "reported_status":
                    (
                        raw_status
                        if raw_status is not None
                        else
                        None
                    ),
            }


        except Exception as error:

            return {
                "status":
                    STATUS_UNAVAILABLE,

                "runtime_active":
                    False,

                "error":
                    type(
                        error
                    ).__name__,
            }


    def runtime_health(
        self,
    ):

        engine = getattr(
            runtime,
            "engine",
            None,
        )

        stream_service = getattr(
            runtime,
            "stream_service",
            None,
        )


        engine_health = (
            self._runtime_component_status(
                engine
            )
        )

        stream_health = (
            self._runtime_component_status(
                stream_service
            )
        )


        if (
            engine_health[
                "status"
            ] == STATUS_ONLINE
            and
            stream_service is not None
            and
            getattr(
                engine,
                "stream_service",
                None,
            )
            is stream_service
        ):

            stream_health = {
                **stream_health,

                "status":
                    STATUS_ONLINE,

                "runtime_active":
                    True,

                "attached_to_engine":
                    True,
            }


        return {
            "engine":
                engine_health,

            "stream_service":
                stream_health,
        }


    # ========================================================
    # COMPOSANTS PHOENIX
    # ========================================================

    def components_health(
        self,
    ):

        engine = getattr(
            runtime,
            "engine",
            None,
        )


        if engine is None:

            return {
                "status":
                    STATUS_AVAILABLE,

                "engine_active":
                    False,

                "components": {
                    "camera_manager": {
                        "status":
                            STATUS_AVAILABLE,

                        "loaded":
                            False,
                    },

                    "frame_hub": {
                        "status":
                            STATUS_AVAILABLE,

                        "loaded":
                            False,
                    },

                    "stream_service": {
                        "status":
                            STATUS_AVAILABLE,

                        "loaded":
                            False,
                    },

                    "detector": {
                        "status":
                            STATUS_AVAILABLE,

                        "loaded":
                            False,
                    },

                    "memory_manager": {
                        "status":
                            STATUS_AVAILABLE,

                        "loaded":
                            False,
                    },
                },
            }


        engine_health = (
            self._runtime_component_status(
                engine
            )
        )

        engine_online = (
            engine_health[
                "status"
            ]
            ==
            STATUS_ONLINE
        )


        components = {}


        for (
            key,
            attribute,
        ) in (
            (
                "camera_manager",
                "camera_manager",
            ),
            (
                "frame_hub",
                "frame_hub",
            ),
            (
                "stream_service",
                "stream_service",
            ),
            (
                "memory_manager",
                "memory_manager",
            ),
        ):

            component = getattr(
                engine,
                attribute,
                None,
            )


            if component is None:

                components[
                    key
                ] = {
                    "status":
                        STATUS_UNAVAILABLE,

                    "loaded":
                        False,
                }

            else:

                components[
                    key
                ] = {
                    "status":
                        (
                            STATUS_ONLINE
                            if engine_online
                            else
                            STATUS_AVAILABLE
                        ),

                    "loaded":
                        True,

                    "class":
                        component
                        .__class__
                        .__name__,
                }


        detector = getattr(
            engine,
            "detector",
            None,
        )


        if detector is None:

            components[
                "detector"
            ] = {
                "status":
                    STATUS_UNAVAILABLE,

                "loaded":
                    False,
            }

        else:

            model_loaded = bool(
                getattr(
                    detector,
                    "loaded",
                    False,
                )
            )


            components[
                "detector"
            ] = {
                "status":
                    (
                        STATUS_ONLINE
                        if model_loaded
                        else
                        STATUS_AVAILABLE
                    ),

                "loaded":
                    model_loaded,

                "class":
                    detector
                    .__class__
                    .__name__,
            }


        unavailable = sum(
            1
            for item
            in components.values()
            if item[
                "status"
            ]
            ==
            STATUS_UNAVAILABLE
        )


        online = sum(
            1
            for item
            in components.values()
            if item[
                "status"
            ]
            ==
            STATUS_ONLINE
        )


        if unavailable:

            status = STATUS_UNAVAILABLE

        elif engine_online:

            status = STATUS_ONLINE

        else:

            status = STATUS_AVAILABLE


        return {
            "status":
                status,

            "engine_active":
                engine_online,

            "online":
                online,

            "unavailable":
                unavailable,

            "components":
                components,
        }


    # ========================================================
    # RÉPERTOIRES
    # ========================================================

    def directory_health(
        self,
    ):

        directories = {
            "data":
                self.project_root
                /
                "data",

            "outputs":
                self.project_root
                /
                "outputs",

            "videos":
                self.project_root
                /
                "videos",
        }


        result = {}


        for name, path in directories.items():

            exists = path.is_dir()


            result[
                name
            ] = {
                "status":
                    (
                        STATUS_AVAILABLE
                        if exists
                        else
                        STATUS_UNAVAILABLE
                    ),

                "exists":
                    exists,

                "path":
                    str(
                        path.relative_to(
                            self.project_root
                        )
                    )
                    if exists
                    else
                    str(
                        path
                    ),
            }


        return result


    # ========================================================
    # BASES SQLITE
    # ========================================================

    def _database_health(
        self,
        path,
    ):

        try:

            stat = path.stat()

        except OSError as error:

            return {
                "name":
                    path.name,

                "status":
                    STATUS_UNAVAILABLE,

                "error":
                    type(
                        error
                    ).__name__,
            }


        try:

            uri = (
                "file:"
                +
                str(
                    path.resolve()
                )
                +
                "?mode=ro"
            )


            connection = sqlite3.connect(
                uri,
                uri=True,
                timeout=1.0,
            )


            try:

                schema_version = (
                    connection.execute(
                        "PRAGMA schema_version"
                    )
                    .fetchone()
                )


                table_count = (
                    connection.execute(
                        """
                        SELECT COUNT(*)
                        FROM sqlite_master
                        WHERE type = 'table'
                        """
                    )
                    .fetchone()
                )


            finally:

                connection.close()


            return {
                "name":
                    path.name,

                "status":
                    STATUS_ONLINE,

                "size_mb":
                    bytes_to_mb(
                        stat.st_size
                    ),

                "modified_at":
                    timestamp_iso(
                        stat.st_mtime
                    ),

                "schema_version":
                    (
                        schema_version[
                            0
                        ]
                        if schema_version
                        else
                        None
                    ),

                "tables":
                    (
                        table_count[
                            0
                        ]
                        if table_count
                        else
                        0
                    ),

                "integrity_check":
                    "NON_EXECUTE",
            }


        except sqlite3.Error as error:

            return {
                "name":
                    path.name,

                "status":
                    STATUS_UNAVAILABLE,

                "size_mb":
                    bytes_to_mb(
                        stat.st_size
                    ),

                "error":
                    type(
                        error
                    ).__name__,

                "integrity_check":
                    "NON_EXECUTE",
            }


    def databases_health(
        self,
    ):

        data_directory = (
            self.project_root
            /
            "data"
        )


        if not data_directory.is_dir():

            return {
                "status":
                    STATUS_UNAVAILABLE,

                "count":
                    0,

                "online":
                    0,

                "unavailable":
                    0,

                "databases":
                    [],
            }


        database_paths = sorted(
            data_directory.glob(
                "*.db"
            )
        )


        databases = [
            self._database_health(
                path
            )
            for path
            in database_paths
        ]


        online = sum(
            1
            for item
            in databases
            if item[
                "status"
            ] == STATUS_ONLINE
        )


        unavailable = (
            len(
                databases
            )
            -
            online
        )


        if not databases:

            status = STATUS_AVAILABLE

        elif unavailable:

            status = STATUS_UNAVAILABLE

        else:

            status = STATUS_ONLINE


        return {
            "status":
                status,

            "count":
                len(
                    databases
                ),

            "online":
                online,

            "unavailable":
                unavailable,

            "databases":
                databases,
        }


    # ========================================================
    # ENVIRONNEMENT
    # ========================================================

    def environment(
        self,
    ):

        return {
            "application":
                getattr(
                    constants,
                    "APP_NAME",
                    "Phoenix Vision AI",
                ),

            "version":
                getattr(
                    constants,
                    "VERSION",
                    "unknown",
                ),

            "codename":
                getattr(
                    constants,
                    "CODENAME",
                    None,
                ),

            "company":
                getattr(
                    constants,
                    "COMPANY",
                    "Phoenix Security Technologies",
                ),

            "python":
                platform.python_version(),

            "python_executable":
                sys.executable,

            "operating_system":
                platform.system(),

            "os_release":
                platform.release(),

            "architecture":
                platform.machine(),

            "hostname":
                platform.node(),

            "project_root":
                str(
                    self.project_root
                ),
        }


    # ========================================================
    # ÉTAT GLOBAL
    # ========================================================

    def overall_status(
        self,
        *,
        machine,
        databases,
        runtime_health,
        directories,
    ):

        critical_failure = False
        attention = False


        if databases[
            "status"
        ] == STATUS_UNAVAILABLE:

            critical_failure = True


        if directories[
            "data"
        ][
            "status"
        ] == STATUS_UNAVAILABLE:

            critical_failure = True


        if runtime_health[
            "engine"
        ][
            "status"
        ] == STATUS_UNAVAILABLE:

            attention = True


        if (
            machine[
                "memory"
            ][
                "percent"
            ]
            >=
            90
        ):

            attention = True


        if (
            machine[
                "disk"
            ][
                "percent"
            ]
            >=
            90
        ):

            attention = True


        if critical_failure:

            return OVERALL_UNAVAILABLE


        if attention:

            return OVERALL_ATTENTION


        return OVERALL_OPERATIONAL


    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ):

        machine = self.machine_metrics()

        process = self.process_metrics()

        runtime_health = self.runtime_health()

        components = self.components_health()

        directories = self.directory_health()

        databases = self.databases_health()

        environment = self.environment()


        overall = self.overall_status(
            machine=
                machine,

            databases=
                databases,

            runtime_health=
                runtime_health,

            directories=
                directories,
        )


        return {
            "success":
                True,

            "generated_at":
                utc_now_iso(),

            "overall_status":
                overall,

            "machine":
                machine,

            "process":
                process,

            "runtime":
                runtime_health,

            "components":
                components,

            "directories":
                directories,

            "databases":
                databases,

            "environment":
                environment,
        }


system_health_service = SystemHealthService()
