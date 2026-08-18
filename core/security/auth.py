"""
========================================================
PHOENIX VISION AI

Authentication

Phoenix Security Technologies
========================================================
"""

from pathlib import Path

import hashlib
import hmac
import json


from core.security.users import (
    USERS
)


from core.security.session import (
    session_manager
)


APPROVED_USERS_FILE = Path(
    "data/approved_users.json"
)


def load_approved_users():

    if not APPROVED_USERS_FILE.exists():

        return []


    try:

        with APPROVED_USERS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )


    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def verify_hashed_password(
    password,
    user
):

    try:

        salt = bytes.fromhex(
            user[
                "password_salt"
            ]
        )


        expected_hash = bytes.fromhex(
            user[
                "password_hash"
            ]
        )

    except (
        KeyError,
        ValueError
    ):

        return False


    calculated_hash = (
        hashlib.pbkdf2_hmac(

            "sha256",

            password.encode(
                "utf-8"
            ),

            salt,

            210_000

        )
    )


    return hmac.compare_digest(
        calculated_hash,
        expected_hash
    )


def authenticate(
    username,
    password
):

    username = (
        username
        .strip()
        .lower()
    )


    # ====================================================
    # ADMIN / LEGACY ACCOUNT
    # ====================================================

    user = USERS.get(
        username
    )


    if user is not None:

        if (
            user.get(
                "password"
            )
            ==
            password
        ):

            token = (
                session_manager.create(

                    username,

                    user[
                        "role"
                    ]

                )
            )


            return {

                "username":
                    username,

                "role":
                    user[
                        "role"
                    ],

                "token":
                    token,

                "must_change_password":
                    False

            }


    # ====================================================
    # APPROVED ENTERPRISE USERS
    # ====================================================

    approved_users = (
        load_approved_users()
    )


    for approved_user in approved_users:

        if (

            approved_user.get(
                "username"
            )
            !=
            username

        ):

            continue


        if not approved_user.get(
            "active",
            False
        ):

            return None


        if not verify_hashed_password(
            password,
            approved_user
        ):

            return None


        token = (
            session_manager.create(

                username,

                approved_user.get(
                    "role",
                    "OPERATOR"
                )

            )
        )


        return {

            "username":
                username,

            "role":
                approved_user.get(
                    "role",
                    "OPERATOR"
                ),

            "token":
                token,

            "must_change_password":
                approved_user.get(
                    "must_change_password",
                    True
                )

        }


    return None