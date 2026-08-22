"""
========================================================
PHOENIX VISION AI ENTERPRISE

Enterprise Report Service

Agrégation historique et persistante
des données opérationnelles réelles.

Phoenix Security Technologies
========================================================
"""

from datetime import (
    date,
    datetime,
    time
)

from core.database.history_database import (
    history_database
)

from core.events.event_database import (
    event_database
)

from core.intelligence.alert_database import (
    alert_database
)

from core.watchlist.watchlist_database import (
    watchlist_database
)

from core.reports.report_database import (
    report_database
)


class ReportService:

    COMPANY = (
        "Phoenix Security Technologies"
    )

    PRODUCT = (
        "Phoenix Vision AI Enterprise"
    )


    def __init__(
        self,
        report_store=None
    ):

        self.report_store = (
            report_store
            or
            report_database
        )


    @staticmethod
    def _normalize_bound(
        value,
        end_of_day=False
    ):

        if isinstance(
            value,
            datetime
        ):

            return value.isoformat()


        if isinstance(
            value,
            date
        ):

            target_time = (
                time.max
                if end_of_day
                else time.min
            )

            return datetime.combine(
                value,
                target_time
            ).isoformat()


        if value is None:

            return None


        text = str(
            value
        ).strip()


        if len(text) == 10:

            suffix = (
                "T23:59:59.999999"
                if end_of_day
                else
                "T00:00:00"
            )

            return (
                text
                +
                suffix
            )


        return text


    def resolve_period(
        self,
        start=None,
        end=None
    ):

        now = datetime.now()


        if (
            start is None
            and
            end is None
        ):

            start_value = (
                now.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                .isoformat()
            )

            end_value = (
                now.isoformat()
            )

            kind = "TODAY"


        else:

            if (
                start is None
                or
                end is None
            ):

                raise ValueError(
                    "start et end doivent être fournis ensemble."
                )


            start_value = (
                self._normalize_bound(
                    start,
                    end_of_day=False
                )
            )

            end_value = (
                self._normalize_bound(
                    end,
                    end_of_day=True
                )
            )

            kind = "CUSTOM"


        if start_value > end_value:

            raise ValueError(
                "La date de début doit être antérieure "
                "ou égale à la date de fin."
            )


        return {

            "kind":
                kind,

            "start":
                start_value,

            "end":
                end_value

        }


    def operational_snapshot(
        self,
        start=None,
        end=None,
        recent_limit=100
    ):

        period = (
            self.resolve_period(
                start,
                end
            )
        )


        start_value = (
            period["start"]
        )

        end_value = (
            period["end"]
        )


        recent_limit = max(
            1,
            min(
                int(
                    recent_limit
                ),
                500
            )
        )


        history_stats = (
            history_database
            .stats_between(
                start_value,
                end_value
            )
        )


        event_stats = (
            event_database
            .stats_between(
                start_value,
                end_value
            )
        )


        alert_stats = (
            alert_database
            .stats_between(
                start_value,
                end_value
            )
        )


        watchlist_stats = (
            watchlist_database
            .stats_between(
                start_value,
                end_value
            )
        )


        vehicles_recent = (
            history_database
            .between(
                start_value,
                end_value,
                limit=recent_limit
            )
        )


        anpr_recent = [

            record

            for record in vehicles_recent

            if str(
                record.get(
                    "plate"
                )
                or ""
            ).strip()

        ]


        events_recent = (
            event_database
            .between(
                start_value,
                end_value,
                limit=recent_limit
            )
        )


        alerts_recent = (
            alert_database
            .between(
                start_value,
                end_value,
                limit=recent_limit
            )
        )


        watchlist_recent = (
            watchlist_database
            .between(
                start_value,
                end_value,
                limit=recent_limit
            )
        )


        watchlist_audit = (
            watchlist_database
            .audit_between(
                start_value,
                end_value,
                limit=recent_limit
            )
        )


        anpr_stats = {

            "plates_detected":
                history_stats[
                    "plates_detected"
                ],

            "validated":
                history_stats[
                    "plates_validated"
                ],

            "to_review":
                history_stats[
                    "plates_to_review"
                ],

            "average_confidence":
                history_stats[
                    "average_plate_confidence"
                ]

        }


        return {

            "generated_snapshot_at":
                datetime.now()
                .isoformat(),

            "period":
                period,

            "summary": {

                "vehicles":
                    history_stats[
                        "vehicles"
                    ],

                "threat_vehicles":
                    history_stats[
                        "threats"
                    ],

                "plates_detected":
                    history_stats[
                        "plates_detected"
                    ],

                "plates_validated":
                    history_stats[
                        "plates_validated"
                    ],

                "plates_to_review":
                    history_stats[
                        "plates_to_review"
                    ],

                "average_plate_confidence":
                    history_stats[
                        "average_plate_confidence"
                    ],

                "events":
                    event_stats[
                        "total"
                    ],

                "events_warnings":
                    event_stats[
                        "warnings"
                    ],

                "events_critical":
                    event_stats[
                        "critical"
                    ],

                "alerts":
                    alert_stats[
                        "total"
                    ],

                "alerts_active_in_period":
                    alert_stats[
                        "active_in_period"
                    ],

                "alerts_open_at_end":
                    alert_stats[
                        "open_at_end"
                    ],

                "alerts_high":
                    alert_stats[
                        "high"
                    ],

                "alerts_critical":
                    alert_stats[
                        "critical"
                    ],

                "alerts_acknowledged":
                    alert_stats[
                        "acknowledged"
                    ],

                "alerts_resolved":
                    alert_stats[
                        "resolved"
                    ],

                "watchlist_created":
                    watchlist_stats[
                        "created"
                    ],

                "watchlist_approved":
                    watchlist_stats[
                        "approved"
                    ],

                "watchlist_pending_at_end":
                    watchlist_stats[
                        "pending_at_end"
                    ],

                "watchlist_active_in_period":
                    watchlist_stats[
                        "active_in_period"
                    ],

                "watchlist_matches":
                    watchlist_stats[
                        "matches"
                    ],

                "watchlist_expired":
                    watchlist_stats[
                        "expired"
                    ]

            },

            "data_coverage": {

                "vehicle_history": {

                    "storage":
                        "PERSISTENT",

                    "label":
                        "Historique persistant",

                    "source":
                        "database/vehicle_history.db"

                },

                "anpr": {

                    "storage":
                        "PERSISTENT",

                    "label":
                        "Données LAPI persistantes",

                    "source":
                        "database/vehicle_history.db"

                },

                "events": {

                    "storage":
                        "PERSISTENT",

                    "label":
                        "Événements persistants",

                    "source":
                        "data/events.db"

                },

                "alerts": {

                    "storage":
                        "PERSISTENT",

                    "label":
                        "Alertes persistantes",

                    "source":
                        "data/alerts.db"

                },

                "watchlist": {

                    "storage":
                        "PERSISTENT",

                    "label":
                        "Liste de surveillance persistante",

                    "source":
                        "data/watchlist.db"

                }

            },

            "history": {

                "stats":
                    history_stats,

                "recent":
                    vehicles_recent

            },

            "anpr": {

                "stats":
                    anpr_stats,

                "recent":
                    anpr_recent

            },

            "events": {

                "stats":
                    event_stats,

                "recent":
                    events_recent

            },

            "alerts": {

                "stats":
                    alert_stats,

                "recent":
                    alerts_recent

            },

            "watchlist": {

                "stats":
                    watchlist_stats,

                "recent":
                    watchlist_recent,

                "audit":
                    watchlist_audit

            }

        }


    def generate_operational_report(
        self,
        generated_by,
        generated_role,
        period_start=None,
        period_end=None,
        scope="LOCAL_SITE",
        filters=None,
        sections=None
    ):

        period = (
            self.resolve_period(
                period_start,
                period_end
            )
        )


        snapshot = (
            self.operational_snapshot(

                start=
                    period[
                        "start"
                    ],

                end=
                    period[
                        "end"
                    ]

            )
        )


        if sections is None:

            sections = [

                "summary",
                "vehicles",
                "events",
                "alerts",
                "anpr",
                "watchlist"

            ]


        return (
            self.report_store
            .create_report(

                report_type=
                    "OPERATIONAL",

                title=
                    "Rapport opérationnel Phoenix",

                snapshot=
                    snapshot,

                generated_by=
                    generated_by,

                generated_role=
                    generated_role,

                period_start=
                    period[
                        "start"
                    ],

                period_end=
                    period[
                        "end"
                    ],

                scope=
                    scope,

                filters=(
                    filters
                    or {}
                ),

                sections=
                    sections

            )
        )


report_service = (
    ReportService()
)
