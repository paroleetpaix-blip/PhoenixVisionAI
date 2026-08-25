"""
Phoenix Vision AI — User lifecycle status.
"""

from datetime import (
    date,
    datetime,
)


PENDING = "PENDING"
APPROVED = "APPROVED"
ACTIVE = "ACTIVE"
SUSPENDED = "SUSPENDED"
DISABLED = "DISABLED"
EXPIRED = "EXPIRED"


VALID_USER_STATUSES = {
    PENDING,
    APPROVED,
    ACTIVE,
    SUSPENDED,
    DISABLED,
    EXPIRED,
}


def normalize_user_status(
    value,
    default=ACTIVE,
):

    normalized = str(
        value
        or
        ""
    ).strip().upper()

    if normalized in VALID_USER_STATUSES:

        return normalized

    return default


def _expiry_date(
    value,
):

    value = str(
        value
        or
        ""
    ).strip()

    if not value:

        return None

    try:

        parsed = datetime.fromisoformat(
            value
        )

        return parsed.date()

    except ValueError:

        try:

            return date.fromisoformat(
                value
            )

        except ValueError:

            return None


def account_is_expired(
    account_expiry,
):

    expiry = _expiry_date(
        account_expiry
    )

    if expiry is None:

        return False

    return (
        date.today()
        >
        expiry
    )


def derive_legacy_user_status(
    *,
    active=True,
    account_expiry="",
    must_change_password=False,
):

    if active is False:

        return DISABLED


    expiry = _expiry_date(
        account_expiry
    )

    if (
        expiry is not None
        and
        date.today() > expiry
    ):

        return EXPIRED


    if bool(
        must_change_password
    ):

        return APPROVED


    return ACTIVE
