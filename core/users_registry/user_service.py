"""
============================================================
PHOENIX VISION AI

Enterprise User Registry Service

Authentication credentials remain stored separately.
Password hashes and salts never enter users.db.
============================================================
"""

from __future__ import annotations

import json

from pathlib import Path

from core.users_registry.user_database import (
    user_database,
    utc_timestamp,
)

from core.users_registry.user_status import (
    ACTIVE,
    APPROVED,
    DISABLED,
    EXPIRED,
    SUSPENDED,
    derive_legacy_user_status,
    account_is_expired,
)


from core.users_registry.user_access import (
    role_change_decision,
)


ACCOUNT_REQUESTS_PATH = Path(
    "data/account_requests.json"
)

APPROVED_USERS_PATH = Path(
    "data/approved_users.json"
)


SECRET_FIELDS = {
    "password_hash",
    "password_salt",
}


def _load_records(
    path,
):

    if not path.exists():

        return []


    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


    if isinstance(
        data,
        list,
    ):

        return [
            record
            for record
            in data
            if isinstance(
                record,
                dict,
            )
        ]


    if isinstance(
        data,
        dict,
    ):

        for key in (
            "users",
            "approved_users",
            "accounts",
            "requests",
            "account_requests",
        ):

            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return [
                    record
                    for record
                    in value
                    if isinstance(
                        record,
                        dict,
                    )
                ]


    return []


class UserRegistryError(
    Exception
):

    def __init__(
        self,
        code,
        message,
    ):

        super().__init__(
            message
        )

        self.code = code
        self.message = message



def _save_records(
    path,
    records,
):

    payload = records


    if path.exists():

        try:

            original = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )


            if isinstance(
                original,
                dict,
            ):

                for key in (
                    "users",
                    "approved_users",
                    "accounts",
                    "requests",
                    "account_requests",
                ):

                    if isinstance(
                        original.get(
                            key
                        ),
                        list,
                    ):

                        original[
                            key
                        ] = records

                        payload = original

                        break

        except (
            json.JSONDecodeError,
            OSError,
        ):

            pass


    temporary = (
        path.parent
        /
        (
            path.name
            +
            ".tmp"
        )
    )


    temporary.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        +
        "\n",
        encoding="utf-8",
    )


    temporary.replace(
        path
    )


def _display_name(
    record,
):

    parts = [
        str(
            record.get(
                "prenom"
            )
            or
            ""
        ).strip(),

        str(
            record.get(
                "postnom"
            )
            or
            ""
        ).strip(),

        str(
            record.get(
                "nom"
            )
            or
            ""
        ).strip(),
    ]


    value = " ".join(
        part
        for part
        in parts
        if part
    ).strip()


    return (
        value
        or
        str(
            record.get(
                "username"
            )
            or
            record.get(
                "assigned_username"
            )
            or
            ""
        ).strip()
    )


def _registry_record(
    account,
    request=None,
):

    request = (
        request
        if isinstance(
            request,
            dict,
        )
        else
        {}
    )


    account = (
        account
        if isinstance(
            account,
            dict,
        )
        else
        {}
    )


    merged = {
        **request,
        **account,
    }


    for secret in SECRET_FIELDS:

        merged.pop(
            secret,
            None,
        )


    status = derive_legacy_user_status(
        active=
            merged.get(
                "active",
                True,
            ),

        account_expiry=
            merged.get(
                "account_expiry",
                "",
            ),

        must_change_password=
            merged.get(
                "must_change_password",
                False,
            ),
    )


    return {
        "request_id":
            str(
                merged.get(
                    "request_id"
                )
                or
                ""
            ).strip(),

        "username":
            str(
                merged.get(
                    "username"
                )
                or
                merged.get(
                    "assigned_username"
                )
                or
                ""
            ).strip(),

        "display_name":
            _display_name(
                merged
            ),

        "nom":
            merged.get(
                "nom",
                "",
            ),

        "postnom":
            merged.get(
                "postnom",
                "",
            ),

        "prenom":
            merged.get(
                "prenom",
                "",
            ),

        "sexe":
            merged.get(
                "sexe",
                "",
            ),

        "date_naissance":
            merged.get(
                "date_naissance",
                "",
            ),

        "email":
            merged.get(
                "email",
                "",
            ),

        "telephone":
            merged.get(
                "telephone",
                "",
            ),

        "organisation":
            merged.get(
                "organisation",
                "",
            ),

        "matricule":
            merged.get(
                "matricule",
                "",
            ),

        "departement":
            merged.get(
                "departement",
                "",
            ),

        "fonction":
            merged.get(
                "fonction",
                "",
            ),

        "site_affectation":
            merged.get(
                "site_affectation",
                "",
            ),

        "responsable":
            merged.get(
                "responsable",
                "",
            ),

        "requested_access":
            request.get(
                "acces_demande",
                "",
            ),

        "request_reason":
            request.get(
                "motif",
                "",
            ),

        "role":
            str(
                merged.get(
                    "role"
                )
                or
                "OPERATOR"
            ).strip().upper(),

        "access_level":
            merged.get(
                "access_level",
                "",
            ),

        "status":
            status,

        "photo_url":
            merged.get(
                "photo",
                "",
            ),

        "account_expiry":
            merged.get(
                "account_expiry",
                "",
            ),

        "must_change_password":
            bool(
                merged.get(
                    "must_change_password",
                    False,
                )
            ),

        "approved_at":
            merged.get(
                "approved_at",
                "",
            ),

        "approved_by":
            merged.get(
                "approved_by",
                "",
            ),

        "account_created_at":
            merged.get(
                "created_at",
                "",
            ),

        "password_changed_at":
            merged.get(
                "password_changed_at",
                "",
            ),

        "last_login_at":
            "",

        "suspended_at":
            "",

        "suspended_by":
            "",

        "suspension_reason":
            "",

        "disabled_at":
            "",

        "disabled_by":
            "",

        "disable_reason":
            "",
    }


class UserRegistryService:

    def __init__(
        self,
        database=None,
    ):

        self.database = (
            database
            or
            user_database
        )


    def _requests(
        self,
    ):

        return _load_records(
            ACCOUNT_REQUESTS_PATH
        )


    def _accounts(
        self,
    ):

        return _load_records(
            APPROVED_USERS_PATH
        )


    def sync_approved_account(
        self,
        account,
        *,
        request=None,
        actor_username="SYSTEM",
        actor_role="SYSTEM",
        reason="Synchronisation du compte Phoenix",
    ):

        record = _registry_record(
            account,
            request,
        )


        if not record[
            "username"
        ]:

            raise ValueError(
                "Approved account has no username"
            )


        return (
            self.database
            .upsert_user(
                record,
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
            )
        )


    def sync_account_by_username(
        self,
        username,
        *,
        actor_username="SYSTEM",
        actor_role="SYSTEM",
    ):

        normalized = str(
            username
            or
            ""
        ).strip().lower()


        if not normalized:

            return None


        accounts = self._accounts()


        account = next(
            (
                item
                for item
                in accounts
                if str(
                    item.get(
                        "username"
                    )
                    or
                    ""
                ).strip().lower()
                ==
                normalized
            ),
            None,
        )


        if account is None:

            return None


        request_id = str(
            account.get(
                "request_id"
            )
            or
            ""
        ).strip()


        request = next(
            (
                item
                for item
                in self._requests()
                if str(
                    item.get(
                        "request_id"
                    )
                    or
                    ""
                ).strip()
                ==
                request_id
            ),
            {},
        )


        return self.sync_approved_account(
            account,
            request=
                request,
            actor_username=
                actor_username,
            actor_role=
                actor_role,
            reason=
                "Synchronisation automatique du compte",
        )


    def ensure_user(
        self,
        username,
        *,
        actor_username="SYSTEM",
        actor_role="SYSTEM",
    ):

        user = self.database.get_user(
            username
        )


        if user is not None:

            return user


        self.sync_account_by_username(
            username,
            actor_username=
                actor_username,
            actor_role=
                actor_role,
        )


        return self.database.get_user(
            username
        )


    def sync_legacy_accounts(
        self,
        *,
        actor_username="SYSTEM",
        actor_role="SYSTEM",
    ):

        requests = self._requests()

        accounts = self._accounts()


        requests_by_id = {
            str(
                request.get(
                    "request_id"
                )
                or
                ""
            ):
                request

            for request
            in requests

            if request.get(
                "request_id"
            )
        }


        results = []


        for account in accounts:

            request_id = str(
                account.get(
                    "request_id"
                )
                or
                ""
            ).strip()


            request = requests_by_id.get(
                request_id,
                {},
            )


            result = self.sync_approved_account(
                account,
                request=
                    request,
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    "Migration des comptes Phoenix existants",
            )


            results.append(
                result
            )


        return {
            "source_requests":
                len(
                    requests
                ),

            "source_accounts":
                len(
                    accounts
                ),

            "processed":
                len(
                    results
                ),

            "created":
                sum(
                    1
                    for item
                    in results
                    if item[
                        "action"
                    ]
                    ==
                    "CREATED"
                ),

            "updated":
                sum(
                    1
                    for item
                    in results
                    if item[
                        "action"
                    ]
                    ==
                    "UPDATED"
                ),

            "unchanged":
                sum(
                    1
                    for item
                    in results
                    if item[
                        "action"
                    ]
                    ==
                    "UNCHANGED"
                ),
        }


    def access_decision(
        self,
        username,
        *,
        persist_expiration=True,
    ):

        user = self.ensure_user(
            username,
            actor_username=
                "SYSTEM",
            actor_role=
                "SYSTEM",
        )


        # Compte absent du registre :
        # actuellement toléré pour les comptes legacy
        # nécessaires au développement.
        if user is None:

            return {
                "known":
                    False,

                "allowed":
                    True,

                "status":
                    "LEGACY",

                "code":
                    "LEGACY_ACCOUNT",
            }


        status = str(
            user.get(
                "status"
            )
            or
            ""
        ).strip().upper()


        if (
            account_is_expired(
                user.get(
                    "account_expiry"
                )
            )
        ):

            if (
                status
                !=
                EXPIRED
                and
                persist_expiration
            ):

                self.database.update_user_fields(
                    username,
                    {
                        "status":
                            EXPIRED,
                    },
                    action=
                        "ACCOUNT_EXPIRED",
                    actor_username=
                        "SYSTEM",
                    actor_role=
                        "SYSTEM",
                    reason=
                        "Expiration automatique "
                        "de l'autorisation du compte",
                )


            return {
                "known":
                    True,

                "allowed":
                    False,

                "status":
                    EXPIRED,

                "code":
                    "ACCOUNT_EXPIRED",
            }


        if status == SUSPENDED:

            return {
                "known":
                    True,

                "allowed":
                    False,

                "status":
                    SUSPENDED,

                "code":
                    "ACCOUNT_SUSPENDED",
            }


        if status == DISABLED:

            return {
                "known":
                    True,

                "allowed":
                    False,

                "status":
                    DISABLED,

                "code":
                    "ACCOUNT_DISABLED",
            }


        if status == EXPIRED:

            return {
                "known":
                    True,

                "allowed":
                    False,

                "status":
                    EXPIRED,

                "code":
                    "ACCOUNT_EXPIRED",
            }


        if status in {
            APPROVED,
            ACTIVE,
        }:

            return {
                "known":
                    True,

                "allowed":
                    True,

                "status":
                    status,

                "code":
                    "ACCESS_ALLOWED",
            }


        return {
            "known":
                True,

            "allowed":
                False,

            "status":
                status
                or
                "UNKNOWN",

            "code":
                "ACCOUNT_NOT_ACTIVE",
        }


    def record_login(
        self,
        username,
        *,
        actor_role,
    ):

        user = self.ensure_user(
            username,
            actor_username=
                username,
            actor_role=
                actor_role,
        )


        if user is None:

            return {
                "action":
                    "NOT_FOUND",
            }


        return (
            self.database
            .update_user_fields(
                username,
                {
                    "last_login_at":
                        utc_timestamp(),
                },
                action=
                    "LOGIN_SUCCESS",
                actor_username=
                    username,
                actor_role=
                    actor_role,
                reason=
                    "Connexion Phoenix réussie",
            )
        )


    def record_password_change(
        self,
        username,
        *,
        actor_role,
        changed_at=None,
    ):

        user = self.ensure_user(
            username,
            actor_username=
                username,
            actor_role=
                actor_role,
        )


        if user is None:

            return {
                "action":
                    "NOT_FOUND",
            }


        current_status = str(
            user.get(
                "status"
            )
            or
            ""
        ).strip().upper()


        protected_statuses = {
            SUSPENDED,
            DISABLED,
            EXPIRED,
        }


        if current_status in protected_statuses:

            next_status = (
                current_status
            )

        elif current_status in {
            APPROVED,
            ACTIVE,
        }:

            next_status = ACTIVE

        else:

            next_status = ACTIVE


        return (
            self.database
            .update_user_fields(
                username,
                {
                    "must_change_password":
                        False,

                    "password_changed_at":
                        changed_at
                        or
                        utc_timestamp(),

                    "status":
                        next_status,
                },
                action=
                    "PASSWORD_CHANGED",
                actor_username=
                    username,
                actor_role=
                    actor_role,
                reason=
                    (
                        "Mot de passe temporaire "
                        "remplacé par l'utilisateur"
                    ),
            )
        )


    def _update_source_account(
        self,
        username,
        changes,
    ):

        normalized = str(
            username
            or
            ""
        ).strip().lower()


        accounts = self._accounts()


        account = next(
            (
                item
                for item
                in accounts
                if str(
                    item.get(
                        "username"
                    )
                    or
                    ""
                ).strip().lower()
                ==
                normalized
            ),
            None,
        )


        if account is None:

            return False


        request_id = str(
            account.get(
                "request_id"
            )
            or
            ""
        ).strip()


        source_changes = {}


        for key, value in changes.items():

            if key == "photo_url":

                source_changes[
                    "photo"
                ] = value

            elif key in {
                "nom",
                "postnom",
                "prenom",
                "sexe",
                "date_naissance",
                "email",
                "telephone",
                "organisation",
                "matricule",
                "departement",
                "fonction",
                "site_affectation",
                "responsable",
                "account_expiry",
                "role",
            }:

                source_changes[
                    key
                ] = value


        account.update(
            source_changes
        )


        _save_records(
            APPROVED_USERS_PATH,
            accounts,
        )


        if request_id:

            requests = self._requests()

            changed = False


            for request in requests:

                if str(
                    request.get(
                        "request_id"
                    )
                    or
                    ""
                ).strip() != request_id:

                    continue


                request.update(
                    source_changes
                )

                if (
                    "role"
                    in
                    source_changes
                ):

                    request[
                        "role"
                    ] = source_changes[
                        "role"
                    ]


                changed = True

                break


            if changed:

                _save_records(
                    ACCOUNT_REQUESTS_PATH,
                    requests,
                )


        return True


    def update_profile(
        self,
        username,
        changes,
        *,
        actor_username,
        actor_role,
        reason="Mise à jour du dossier utilisateur",
    ):

        user = self.get_user(
            username
        )


        if user is None:

            raise UserRegistryError(
                "USER_NOT_FOUND",
                "Utilisateur introuvable.",
            )


        allowed = {
            "nom",
            "postnom",
            "prenom",
            "sexe",
            "date_naissance",
            "email",
            "telephone",
            "organisation",
            "matricule",
            "departement",
            "fonction",
            "site_affectation",
            "responsable",
            "account_expiry",
        }


        filtered = {
            key:
                value

            for key, value
            in changes.items()

            if key in allowed
        }


        if not filtered:

            raise UserRegistryError(
                "NO_EDITABLE_FIELDS",
                "Aucune information modifiable reçue.",
            )


        if "email" in filtered:

            filtered[
                "email"
            ] = str(
                filtered[
                    "email"
                ]
                or
                ""
            ).strip().lower()


        merged = {
            **user,
            **filtered,
        }


        filtered[
            "display_name"
        ] = _display_name(
            merged
        )


        self._update_source_account(
            username,
            filtered,
        )


        result = (
            self.database
            .update_user_fields(
                username,
                filtered,
                action=
                    "USER_PROFILE_UPDATED",
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
            )
        )


        return {
            "result":
                result,

            "user":
                self.get_user(
                    username
                ),
        }


    def suspend_user(
        self,
        username,
        *,
        actor_username,
        actor_role,
        reason,
    ):

        user = self.get_user(
            username
        )


        if user is None:

            raise UserRegistryError(
                "USER_NOT_FOUND",
                "Utilisateur introuvable.",
            )


        if (
            str(
                username
            ).strip().lower()
            ==
            str(
                actor_username
            ).strip().lower()
        ):

            raise UserRegistryError(
                "SELF_ACTION_RESTRICTED",
                "Vous ne pouvez pas suspendre votre propre compte.",
            )


        if str(
            user.get(
                "role"
            )
            or
            ""
        ).upper() == "ADMIN":

            raise UserRegistryError(
                "ADMIN_ACCOUNT_PROTECTED",
                (
                    "Un compte ADMIN ne peut pas être suspendu "
                    "depuis Phoenix Vision AI."
                ),
            )


        reason = str(
            reason
            or
            ""
        ).strip()


        if len(
            reason
        ) < 3:

            raise UserRegistryError(
                "REASON_REQUIRED",
                "Un motif de suspension est obligatoire.",
            )


        return (
            self.database
            .update_user_fields(
                username,
                {
                    "status":
                        SUSPENDED,

                    "suspended_at":
                        utc_timestamp(),

                    "suspended_by":
                        actor_username,

                    "suspension_reason":
                        reason,
                },
                action=
                    "ACCOUNT_SUSPENDED",
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
            )
        )


    def disable_user(
        self,
        username,
        *,
        actor_username,
        actor_role,
        reason,
    ):

        user = self.get_user(
            username
        )


        if user is None:

            raise UserRegistryError(
                "USER_NOT_FOUND",
                "Utilisateur introuvable.",
            )


        if (
            str(
                username
            ).strip().lower()
            ==
            str(
                actor_username
            ).strip().lower()
        ):

            raise UserRegistryError(
                "SELF_ACTION_RESTRICTED",
                "Vous ne pouvez pas désactiver votre propre compte.",
            )


        if str(
            user.get(
                "role"
            )
            or
            ""
        ).upper() == "ADMIN":

            raise UserRegistryError(
                "ADMIN_ACCOUNT_PROTECTED",
                (
                    "Un compte ADMIN ne peut pas être désactivé "
                    "depuis Phoenix Vision AI."
                ),
            )


        reason = str(
            reason
            or
            ""
        ).strip()


        if len(
            reason
        ) < 3:

            raise UserRegistryError(
                "REASON_REQUIRED",
                "Un motif de désactivation est obligatoire.",
            )


        return (
            self.database
            .update_user_fields(
                username,
                {
                    "status":
                        DISABLED,

                    "disabled_at":
                        utc_timestamp(),

                    "disabled_by":
                        actor_username,

                    "disable_reason":
                        reason,
                },
                action=
                    "ACCOUNT_DISABLED",
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
            )
        )


    def reactivate_user(
        self,
        username,
        *,
        actor_username,
        actor_role,
        reason,
    ):

        user = self.get_user(
            username
        )


        if user is None:

            raise UserRegistryError(
                "USER_NOT_FOUND",
                "Utilisateur introuvable.",
            )


        if str(
            user.get(
                "role"
            )
            or
            ""
        ).upper() == "ADMIN":

            raise UserRegistryError(
                "ADMIN_ACCOUNT_PROTECTED",
                (
                    "Un compte ADMIN ne peut pas être réactivé "
                    "depuis cette console."
                ),
            )


        if account_is_expired(
            user.get(
                "account_expiry"
            )
        ):

            raise UserRegistryError(
                "ACCOUNT_EXPIRED",
                (
                    "La date d'expiration doit être corrigée "
                    "avant de réactiver ce compte."
                ),
            )


        reason = str(
            reason
            or
            ""
        ).strip()


        if len(
            reason
        ) < 3:

            raise UserRegistryError(
                "REASON_REQUIRED",
                "Un motif de réactivation est obligatoire.",
            )


        next_status = (
            APPROVED
            if bool(
                user.get(
                    "must_change_password"
                )
            )
            else
            ACTIVE
        )


        return (
            self.database
            .update_user_fields(
                username,
                {
                    "status":
                        next_status,

                    "suspended_at":
                        "",

                    "suspended_by":
                        "",

                    "suspension_reason":
                        "",

                    "disabled_at":
                        "",

                    "disabled_by":
                        "",

                    "disable_reason":
                        "",
                },
                action=
                    "ACCOUNT_REACTIVATED",
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
            )
        )


    def change_role(
        self,
        username,
        requested_role,
        *,
        actor_username,
        actor_role,
        reason,
    ):

        user = self.get_user(
            username
        )


        if user is None:

            raise UserRegistryError(
                "USER_NOT_FOUND",
                "Utilisateur introuvable.",
            )


        if (
            str(
                username
            ).strip().lower()
            ==
            str(
                actor_username
            ).strip().lower()
        ):

            raise UserRegistryError(
                "SELF_ROLE_CHANGE_RESTRICTED",
                (
                    "Vous ne pouvez pas modifier "
                    "votre propre rôle."
                ),
            )


        decision = role_change_decision(
            actor_role,
            user.get(
                "role"
            ),
            requested_role,
        )


        if not decision.get(
            "allowed"
        ):

            raise UserRegistryError(
                decision.get(
                    "code",
                    "ROLE_CHANGE_DENIED",
                ),
                decision.get(
                    "message",
                    "Modification du rôle refusée.",
                ),
            )


        reason = str(
            reason
            or
            ""
        ).strip()


        if len(
            reason
        ) < 3:

            raise UserRegistryError(
                "REASON_REQUIRED",
                (
                    "Un motif de changement "
                    "de rôle est obligatoire."
                ),
            )


        next_role = str(
            requested_role
        ).strip().upper()


        self._update_source_account(
            username,
            {
                "role":
                    next_role,
            },
        )


        return (
            self.database
            .update_user_fields(
                username,
                {
                    "role":
                        next_role,
                },
                action=
                    "USER_ROLE_CHANGED",
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
                metadata={
                    "previous_role":
                        user.get(
                            "role"
                        ),

                    "new_role":
                        next_role,
                },
            )
        )


    def record_user_sheet_print(
        self,
        username,
        *,
        actor_username,
        actor_role,
    ):

        user = self.get_user(
            username
        )


        if user is None:

            raise UserRegistryError(
                "USER_NOT_FOUND",
                "Utilisateur introuvable.",
            )


        return (
            self.database
            .record_audit_event(
                username,
                action=
                    "USER_SHEET_PRINT_PREPARED",
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    (
                        "Préparation de la fiche "
                        "utilisateur officielle"
                    ),
                metadata={
                    "user_id":
                        user.get(
                            "user_id"
                        ),

                    "role":
                        user.get(
                            "role"
                        ),

                    "status":
                        user.get(
                            "status"
                        ),
                },
            )
        )


    def audit_for_user(
        self,
        username,
        *,
        limit=200,
    ):

        return (
            self.database
            .audit_events_for_user(
                username,
                limit=limit,
            )
        )


    def account_request_summary(
        self,
    ):

        requests = self._requests()


        statuses = {}


        for request in requests:

            status = str(
                request.get(
                    "status"
                )
                or
                "UNKNOWN"
            ).strip().upper()


            statuses[
                status
            ] = (
                statuses.get(
                    status,
                    0,
                )
                +
                1
            )


        pending = statuses.get(
            "PENDING",
            0,
        )


        approved = statuses.get(
            "APPROVED",
            0,
        )


        return {
            "total":
                len(
                    requests
                ),

            "pending":
                pending,

            "approved":
                approved,

            "other":
                (
                    len(
                        requests
                    )
                    -
                    pending
                    -
                    approved
                ),

            "statuses":
                statuses,
        }


    def list_users(
        self,
        *,
        limit=500,
    ):

        return self.database.list_users(
            limit=limit
        )


    def get_user(
        self,
        username,
    ):

        return self.database.get_user(
            username
        )


user_registry_service = (
    UserRegistryService()
)
