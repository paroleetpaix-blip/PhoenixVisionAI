"""
========================================================
PHOENIX VISION AI

Enterprise Settings Defaults

Canonical definitions and validation rules.

Phoenix Security Technologies
========================================================
"""

from copy import deepcopy
from zoneinfo import ZoneInfo

from core import constants

from core.i18n.locale_registry import (
    DEFAULT_LOCALE,
    validate_selectable_locale,
)


# ======================================================
# CATEGORIES
# ======================================================

CATEGORY_GENERAL = "GENERAL"
CATEGORY_INTERFACE = "INTERFACE"
CATEGORY_OPERATIONS = "OPERATIONS"
CATEGORY_ANPR = "ANPR"
CATEGORY_REPORTS = "REPORTS"
CATEGORY_INSTALLATION = "INSTALLATION"


SUPPORTED_CATEGORIES = {
    CATEGORY_GENERAL,
    CATEGORY_INTERFACE,
    CATEGORY_OPERATIONS,
    CATEGORY_ANPR,
    CATEGORY_REPORTS,
    CATEGORY_INSTALLATION,
}


# ======================================================
# VALIDATION HELPERS
# ======================================================

def validate_string(
    value,
    *,
    minimum=0,
    maximum=200,
):

    if not isinstance(
        value,
        str,
    ):

        raise ValueError(
            "Une chaîne de caractères est requise."
        )

    cleaned = value.strip()

    if len(cleaned) < minimum:

        raise ValueError(
            (
                "La valeur doit contenir au moins "
                f"{minimum} caractère(s)."
            )
        )

    if len(cleaned) > maximum:

        raise ValueError(
            (
                "La valeur ne peut pas dépasser "
                f"{maximum} caractères."
            )
        )

    return cleaned


def validate_choice(
    value,
    choices,
):

    if value not in choices:

        raise ValueError(
            (
                "Valeur non autorisée. "
                "Valeurs possibles : "
                +
                ", ".join(
                    str(choice)
                    for choice
                    in choices
                )
            )
        )

    return value


def validate_boolean(
    value,
):

    if not isinstance(
        value,
        bool,
    ):

        raise ValueError(
            "Une valeur booléenne est requise."
        )

    return value


def validate_timezone(
    value,
):

    value = validate_string(
        value,
        minimum=1,
        maximum=100,
    )

    try:

        ZoneInfo(
            value
        )

    except Exception as error:

        raise ValueError(
            (
                "Fuseau horaire invalide : "
                f"{value}"
            )
        ) from error

    return value


def validate_country_code(
    value,
):

    value = validate_string(
        value,
        minimum=2,
        maximum=2,
    ).upper()

    if not value.isalpha():

        raise ValueError(
            (
                "Le code pays doit contenir "
                "exactement deux lettres."
            )
        )

    return value


def validate_report_sections(
    value,
):

    if not isinstance(
        value,
        list,
    ):

        raise ValueError(
            "La liste des sections est invalide."
        )

    allowed = {
        "summary",
        "vehicles",
        "events",
        "alerts",
        "anpr",
        "watchlist",
    }

    normalized = []

    for item in value:

        item = str(
            item
        ).strip().lower()

        if item not in allowed:

            raise ValueError(
                (
                    "Section de rapport "
                    f"non autorisée : {item}"
                )
            )

        if item not in normalized:

            normalized.append(
                item
            )

    if not normalized:

        raise ValueError(
            (
                "Au moins une section de rapport "
                "doit être sélectionnée."
            )
        )

    return normalized


# ======================================================
# DEFINITIONS
# ======================================================

SETTING_DEFINITIONS = {

    # --------------------------------------------------
    # GENERAL
    # --------------------------------------------------

    "general.site_name": {
        "category":
            CATEGORY_GENERAL,

        "default":
            "",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "LOCAL",

        "mutable":
            True,

        "description":
            "Nom local du site Phoenix.",

        "validator":
            lambda value:
                validate_string(
                    value,
                    minimum=0,
                    maximum=120,
                ),
    },


    "general.country_code": {
        "category":
            CATEGORY_GENERAL,

        "default":
            "CD",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            (
                "Code ISO simplifié du pays "
                "de l'installation."
            ),

        "validator":
            validate_country_code,
    },


    "general.city": {
        "category":
            CATEGORY_GENERAL,

        "default":
            "",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "LOCAL",

        "mutable":
            True,

        "description":
            "Ville du site Phoenix.",

        "validator":
            lambda value:
                validate_string(
                    value,
                    minimum=0,
                    maximum=120,
                ),
    },


    "general.timezone": {
        "category":
            CATEGORY_GENERAL,

        "default":
            "Africa/Kinshasa",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            (
                "Fuseau horaire utilisé par "
                "l'installation."
            ),

        "validator":
            validate_timezone,
    },


    # --------------------------------------------------
    # INTERFACE
    # --------------------------------------------------

    "interface.default_language": {
        "category":
            CATEGORY_INTERFACE,

        "default":
            DEFAULT_LOCALE,

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            (
                "Langue par défaut de "
                "l'interface Phoenix."
            ),

        "validator":
            validate_selectable_locale,
    },


    "interface.date_format": {
        "category":
            CATEGORY_INTERFACE,

        "default":
            "DD/MM/YYYY",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            "Format d'affichage des dates.",

        "validator":
            lambda value:
                validate_choice(
                    value,
                    (
                        "DD/MM/YYYY",
                        "YYYY-MM-DD",
                    ),
                ),
    },


    "interface.time_format": {
        "category":
            CATEGORY_INTERFACE,

        "default":
            "24h",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            "Format d'affichage de l'heure.",

        "validator":
            lambda value:
                validate_choice(
                    value,
                    (
                        "24h",
                        "12h",
                    ),
                ),
    },


    "interface.theme": {
        "category":
            CATEGORY_INTERFACE,

        "default":
            "dark",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            False,

        "description":
            (
                "Thème institutionnel actuel "
                "de Phoenix Vision AI."
            ),

        "validator":
            lambda value:
                validate_choice(
                    value,
                    (
                        "dark",
                    ),
                ),
    },


    # --------------------------------------------------
    # OPERATIONS
    # --------------------------------------------------

    "operations.confirm_sensitive_actions": {
        "category":
            CATEGORY_OPERATIONS,

        "default":
            True,

        "data_type":
            "boolean",

        "scope":
            "LOCAL",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            (
                "Confirmation obligatoire avant "
                "certaines opérations sensibles."
            ),

        "validator":
            validate_boolean,
    },


    # --------------------------------------------------
    # ANPR
    # --------------------------------------------------

    "anpr.review_uncertain_reads": {
        "category":
            CATEGORY_ANPR,

        "default":
            True,

        "data_type":
            "boolean",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            (
                "Envoyer les lectures LAPI "
                "incertaines vers une vérification "
                "humaine."
            ),

        "validator":
            validate_boolean,
    },


    "anpr.show_confidence": {
        "category":
            CATEGORY_ANPR,

        "default":
            True,

        "data_type":
            "boolean",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            (
                "Afficher le niveau de confiance "
                "des lectures LAPI."
            ),

        "validator":
            validate_boolean,
    },


    # --------------------------------------------------
    # REPORTS
    # --------------------------------------------------

    "reports.default_period": {
        "category":
            CATEGORY_REPORTS,

        "default":
            "today",

        "data_type":
            "string",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            (
                "Période sélectionnée par défaut "
                "dans la console Rapports."
            ),

        "validator":
            lambda value:
                validate_choice(
                    value,
                    (
                        "today",
                        "yesterday",
                        "week",
                        "previous_week",
                        "month",
                        "previous_month",
                        "quarter",
                        "semester",
                        "year",
                    ),
                ),
    },


    "reports.default_sections": {
        "category":
            CATEGORY_REPORTS,

        "default": [
            "summary",
            "vehicles",
            "events",
            "alerts",
            "anpr",
            "watchlist",
        ],

        "data_type":
            "list",

        "scope":
            "LOCAL",

        "source":
            "DEFAULT",

        "mutable":
            True,

        "description":
            (
                "Sections incluses par défaut "
                "dans un rapport."
            ),

        "validator":
            validate_report_sections,
    },


    "reports.paper_format": {
        "category":
            CATEGORY_REPORTS,

        "default":
            "A4",

        "data_type":
            "string",

        "scope":
            "SYSTEM",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            (
                "Format institutionnel des "
                "rapports Phoenix."
            ),

        "validator":
            lambda value:
                validate_choice(
                    value,
                    (
                        "A4",
                    ),
                ),
    },


    "reports.include_integrity": {
        "category":
            CATEGORY_REPORTS,

        "default":
            True,

        "data_type":
            "boolean",

        "scope":
            "SYSTEM",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            (
                "Inclure les informations "
                "d'intégrité dans les rapports."
            ),

        "validator":
            validate_boolean,
    },


    # --------------------------------------------------
    # INSTALLATION
    # --------------------------------------------------

    "installation.product_name": {
        "category":
            CATEGORY_INSTALLATION,

        "default":
            constants.APP_NAME,

        "data_type":
            "string",

        "scope":
            "SYSTEM",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            "Nom officiel du produit.",

        "validator":
            lambda value:
                validate_string(
                    value,
                    minimum=1,
                    maximum=120,
                ),
    },


    "installation.software_version": {
        "category":
            CATEGORY_INSTALLATION,

        "default":
            constants.VERSION,

        "data_type":
            "string",

        "scope":
            "SYSTEM",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            (
                "Version installée de "
                "Phoenix Vision AI."
            ),

        "validator":
            lambda value:
                validate_string(
                    value,
                    minimum=1,
                    maximum=80,
                ),
    },


    "installation.codename": {
        "category":
            CATEGORY_INSTALLATION,

        "default":
            constants.CODENAME,

        "data_type":
            "string",

        "scope":
            "SYSTEM",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            "Nom de génération Phoenix.",

        "validator":
            lambda value:
                validate_string(
                    value,
                    minimum=1,
                    maximum=80,
                ),
    },


    "installation.publisher": {
        "category":
            CATEGORY_INSTALLATION,

        "default":
            constants.COMPANY,

        "data_type":
            "string",

        "scope":
            "SYSTEM",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            "Éditeur officiel du logiciel.",

        "validator":
            lambda value:
                validate_string(
                    value,
                    minimum=1,
                    maximum=120,
                ),
    },


    "installation.license_name": {
        "category":
            CATEGORY_INSTALLATION,

        "default":
            constants.LICENSE,

        "data_type":
            "string",

        "scope":
            "SYSTEM",

        "source":
            "SYSTEM",

        "mutable":
            False,

        "description":
            "Nom de la licence logicielle.",

        "validator":
            lambda value:
                validate_string(
                    value,
                    minimum=1,
                    maximum=160,
                ),
    },

}


# ======================================================
# PUBLIC HELPERS
# ======================================================

def get_definition(
    setting_key,
):

    definition = (
        SETTING_DEFINITIONS.get(
            setting_key
        )
    )

    if definition is None:

        return None

    return deepcopy(
        definition
    )


def default_value(
    setting_key,
):

    definition = get_definition(
        setting_key
    )

    if definition is None:

        raise KeyError(
            (
                "Paramètre Phoenix inconnu : "
                f"{setting_key}"
            )
        )

    return deepcopy(
        definition[
            "default"
        ]
    )


def validate_setting_value(
    setting_key,
    value,
):

    definition = get_definition(
        setting_key
    )

    if definition is None:

        raise KeyError(
            (
                "Paramètre Phoenix inconnu : "
                f"{setting_key}"
            )
        )

    validator = definition.get(
        "validator"
    )

    if validator is None:

        return value

    return validator(
        value
    )


def public_definition(
    setting_key,
):

    definition = get_definition(
        setting_key
    )

    if definition is None:

        return None

    definition.pop(
        "validator",
        None,
    )

    return definition
