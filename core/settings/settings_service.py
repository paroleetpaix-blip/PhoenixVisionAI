"""
========================================================
PHOENIX VISION AI

Enterprise Settings Service

Validation, defaults and controlled access.

Phoenix Security Technologies
========================================================
"""

from copy import deepcopy

from core.settings.settings_access import (
    can_update_setting,
)

from core.settings.settings_database import (
    SettingsDatabase,
    settings_database,
)

from core.settings.settings_defaults import (
    SETTING_DEFINITIONS,
    get_definition,
    public_definition,
    validate_setting_value,
)


class SettingsService:

    def __init__(
        self,
        database=None,
    ):

        self.database = (
            database
            or
            settings_database
        )


    # ==================================================
    # DEFAULT INITIALIZATION
    # ==================================================

    def initialize_defaults(
        self,
    ):

        created = 0
        existing = 0

        for (
            setting_key,
            definition
        ) in SETTING_DEFINITIONS.items():

            current = (
                self.database.get(
                    setting_key
                )
            )

            if current is not None:

                existing += 1
                continue

            value = deepcopy(
                definition[
                    "default"
                ]
            )

            value = (
                validate_setting_value(
                    setting_key,
                    value,
                )
            )

            self.database.set(

                setting_key,

                value,

                category=
                    definition[
                        "category"
                    ],

                actor=
                    "SYSTEM",

                actor_role=
                    "SYSTEM",

                data_type=
                    definition[
                        "data_type"
                    ],

                scope=
                    definition[
                        "scope"
                    ],

                source=
                    definition[
                        "source"
                    ],

                mutable=
                    definition[
                        "mutable"
                    ],

                description=
                    definition[
                        "description"
                    ],

                details={
                    "reason":
                        "DEFAULT_INITIALIZATION"
                },
            )

            created += 1

        return {
            "created":
                created,

            "existing":
                existing,

            "total":
                len(
                    SETTING_DEFINITIONS
                ),
        }


    # ==================================================
    # READ
    # ==================================================

    def get(
        self,
        setting_key,
    ):

        if (
            setting_key
            not in SETTING_DEFINITIONS
        ):

            raise KeyError(
                (
                    "Paramètre Phoenix inconnu : "
                    f"{setting_key}"
                )
            )

        setting = (
            self.database.get(
                setting_key
            )
        )

        if setting is None:

            self.initialize_defaults()

            setting = (
                self.database.get(
                    setting_key
                )
            )

        return setting


    def value(
        self,
        setting_key,
    ):

        return self.get(
            setting_key
        )[
            "value"
        ]


    def all(
        self,
    ):

        self.initialize_defaults()

        result = []

        for setting in (
            self.database.all()
        ):

            if (
                setting["key"]
                not in
                SETTING_DEFINITIONS
            ):

                continue

            item = deepcopy(
                setting
            )

            item[
                "definition"
            ] = (
                public_definition(
                    setting["key"]
                )
            )

            result.append(
                item
            )

        return result


    def by_category(
        self,
        category,
    ):

        category = str(
            category
            or
            ""
        ).strip().upper()

        return [
            setting
            for setting
            in self.all()
            if (
                setting[
                    "category"
                ]
                ==
                category
            )
        ]


    # ==================================================
    # UPDATE
    # ==================================================

    def update(
        self,
        setting_key,
        value,
        *,
        actor,
        actor_role,
        details=None,
    ):

        definition = (
            get_definition(
                setting_key
            )
        )

        if definition is None:

            raise KeyError(
                (
                    "Paramètre Phoenix inconnu : "
                    f"{setting_key}"
                )
            )

        if not definition[
            "mutable"
        ]:

            raise PermissionError(
                (
                    "Paramètre Phoenix "
                    "en lecture seule : "
                    f"{setting_key}"
                )
            )


        if not can_update_setting(
            actor_role,
            setting_key,
        ):

            raise PermissionError(
                (
                    "Rôle non autorisé à modifier "
                    "ce paramètre : "
                    f"{setting_key}"
                )
            )


        normalized_value = (
            validate_setting_value(
                setting_key,
                value,
            )
        )

        return self.database.set(

            setting_key,

            normalized_value,

            category=
                definition[
                    "category"
                ],

            actor=
                actor,

            actor_role=
                actor_role,

            data_type=
                definition[
                    "data_type"
                ],

            scope=
                definition[
                    "scope"
                ],

            source=
                "LOCAL",

            mutable=
                definition[
                    "mutable"
                ],

            description=
                definition[
                    "description"
                ],

            details=
                details,
        )


    # ==================================================
    # SYSTEM SYNCHRONIZATION
    # ==================================================

    def synchronize_system_values(
        self,
    ):

        changed = 0

        for (
            setting_key,
            definition
        ) in SETTING_DEFINITIONS.items():

            if (
                definition[
                    "source"
                ]
                !=
                "SYSTEM"
            ):

                continue

            value = deepcopy(
                definition[
                    "default"
                ]
            )

            value = (
                validate_setting_value(
                    setting_key,
                    value,
                )
            )

            current = (
                self.database.get(
                    setting_key
                )
            )

            if (
                current is not None
                and
                current[
                    "value"
                ]
                ==
                value
                and
                current[
                    "mutable"
                ]
                ==
                definition[
                    "mutable"
                ]
            ):

                continue

            result = (
                self.database.set(

                    setting_key,

                    value,

                    category=
                        definition[
                            "category"
                        ],

                    actor=
                        "SYSTEM",

                    actor_role=
                        "SYSTEM",

                    data_type=
                        definition[
                            "data_type"
                        ],

                    scope=
                        definition[
                            "scope"
                        ],

                    source=
                        "SYSTEM",

                    mutable=
                        definition[
                            "mutable"
                        ],

                    description=
                        definition[
                            "description"
                        ],

                    details={
                        "reason":
                            "SYSTEM_SYNCHRONIZATION"
                    },

                    force=True,
                )
            )

            if result[
                "changed"
            ]:

                changed += 1

        return {
            "changed":
                changed
        }


    # ==================================================
    # INTROSPECTION
    # ==================================================

    def definitions(
        self,
    ):

        return {
            key:
                public_definition(
                    key
                )
            for key
            in SETTING_DEFINITIONS
        }


settings_service = SettingsService()
