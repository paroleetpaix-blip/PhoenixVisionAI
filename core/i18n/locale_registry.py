"""
========================================================
PHOENIX VISION AI

Locale Registry

Canonical language registry for Phoenix Vision AI.

Phoenix Security Technologies
========================================================
"""


DEFAULT_LOCALE = "fr"


LOCALES = {

    "fr": {
        "code":
            "fr",

        "name":
            "Français",

        "native_name":
            "Français",

        "default":
            True,

        "supported":
            True,

        "selectable":
            True,

        "status":
            "ACTIVE",
    },


    "en": {
        "code":
            "en",

        "name":
            "Anglais",

        "native_name":
            "English",

        "default":
            False,

        "supported":
            True,

        # La fondation i18n existe mais l'activation
        # dans l'interface globale attend la traduction
        # complète des écrans principaux.
        "selectable":
            False,

        "status":
            "PREPARED",
    },

}


def locale_codes():

    return tuple(
        LOCALES.keys()
    )


def get_locale(
    code,
):

    code = str(
        code
        or
        ""
    ).strip().lower()

    locale = LOCALES.get(
        code
    )

    if locale is None:

        return None

    return dict(
        locale
    )


def validate_locale(
    code,
):

    code = str(
        code
        or
        ""
    ).strip().lower()

    if code not in LOCALES:

        raise ValueError(
            (
                "Langue Phoenix Vision AI "
                f"non supportée : {code}"
            )
        )

    return code


def validate_selectable_locale(
    code,
):

    code = validate_locale(
        code
    )

    locale = LOCALES[
        code
    ]

    if not locale.get(
        "selectable",
        False,
    ):

        raise ValueError(
            (
                "Cette langue est préparée "
                "mais n'est pas encore activée "
                "dans Phoenix Vision AI : "
                f"{code}"
            )
        )

    return code


def public_locales():

    return [
        dict(
            locale
        )
        for locale
        in LOCALES.values()
    ]
