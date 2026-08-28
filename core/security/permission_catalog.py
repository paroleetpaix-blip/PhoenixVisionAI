"""
========================================================
PHOENIX VISION AI

Enterprise Permission Catalog

Human-readable permission metadata.

Phoenix Security Technologies
========================================================
"""


PERMISSION_GROUPS = {

    "OPERATIONS": {
        "label":
            "Opérations",

        "permissions": {
            "history.view":
                "Consulter l'historique",

            "history.print":
                "Imprimer l'historique",

            "evidence.view":
                "Consulter les preuves",

            "evidence.print":
                "Imprimer les preuves",

            "evidence.export_video":
                "Exporter une vidéo de preuve",
        },
    },


    "ANPR": {
        "label":
            "LAPI / ANPR",

        "permissions": {
            "anpr.view":
                "Consulter les lectures LAPI",

            "anpr.search":
                "Rechercher une plaque",
        },
    },


    "WATCHLIST": {
        "label":
            "Surveillance",

        "permissions": {
            "watchlist.match":
                "Recevoir les correspondances",

            "watchlist.view":
                "Consulter la surveillance",

            "watchlist.propose":
                "Proposer une surveillance",

            "watchlist.approve_local":
                "Valider localement une surveillance",
        },
    },


    "REPORTS": {
        "label":
            "Rapports",

        "permissions": {
            "reports.view":
                "Consulter les rapports",

            "reports.generate":
                "Générer des rapports",

            "reports.print":
                "Imprimer les rapports",

            "reports.export_pdf":
                "Exporter les rapports PDF",
        },
    },


    "USERS": {
        "label":
            "Utilisateurs",

        "permissions": {
            "users.view":
                "Consulter les utilisateurs",

            "users.view_sensitive":
                "Consulter les données administratives sensibles",

            "users.edit":
                "Modifier un dossier utilisateur",

            "users.approve_request":
                "Approuver une demande de compte",

            "users.suspend":
                "Suspendre un compte",

            "users.disable":
                "Désactiver un compte",

            "users.reactivate":
                "Réactiver un compte",

            "users.change_role":
                "Modifier le rôle d'un utilisateur",

            "users.view_audit":
                "Consulter l'historique administratif d'un utilisateur",

            "users.print":
                "Imprimer une fiche utilisateur",
        },
    },


    "BACKUPS": {
        "label":
            "Sauvegardes",

        "permissions": {
            "backups.view":
                "Consulter les sauvegardes",

            "backups.create":
                "Créer une sauvegarde",

            "backups.verify":
                "Vérifier l'intégrité d'une sauvegarde",

            "backups.restore":
                "Préparer une restauration",

            "backups.migrate":
                "Migrer une sauvegarde",
        },
    },


    "SYSTEM": {
        "label":
            "Système",

        "permissions": {
            "system.view":
                "Consulter l'état système",

            "system.diagnostics":
                "Exécuter les diagnostics système",

            "system.database_check":
                "Vérifier l'intégrité des bases",
        },
    },


    "SETTINGS": {
        "label":
            "Paramètres",

        "permissions": {
            "settings.view":
                "Consulter les paramètres",

            "settings.view_installation":
                "Voir les informations d'installation",

            "settings.permissions.view_self":
                "Voir mes autorisations",

            "settings.permissions.view_matrix":
                "Voir la matrice des rôles",

            "settings.update_general":
                "Modifier les paramètres généraux",

            "settings.update_interface":
                "Modifier l'interface globale",

            "settings.update_operations":
                "Modifier les paramètres d'exploitation",

            "settings.update_anpr":
                "Modifier les paramètres LAPI",

            "settings.update_reports":
                "Modifier les paramètres Rapports",

            "settings.audit.view":
                "Consulter le journal des paramètres",
        },
    },

}


MANDATORY_SECURITY_RULES = [

    {
        "id":
            "authentication_required",

        "label":
            "Authentification obligatoire",

        "description":
            (
                "Toute utilisation de Phoenix Vision AI "
                "nécessite une session authentifiée."
            ),
    },

    {
        "id":
            "temporary_password_change",

        "label":
            "Mot de passe temporaire",

        "description":
            (
                "Un mot de passe temporaire doit être "
                "remplacé avant l'accès opérationnel."
            ),
    },

    {
        "id":
            "server_side_permissions",

        "label":
            "Contrôle serveur",

        "description":
            (
                "Les permissions sont vérifiées côté serveur "
                "et ne dépendent pas seulement de l'interface."
            ),
    },

    {
        "id":
            "human_validation",

        "label":
            "Validation humaine",

        "description":
            (
                "Phoenix Vision AI ne peut pas déclarer seul "
                "un véhicule officiellement recherché."
            ),
    },

    {
        "id":
            "restricted_admin_promotion",

        "label":
            "Promotion ADMIN renforcée",

        "description":
            (
                "Phoenix Vision AI n'autorise pas une promotion "
                "directe vers le rôle ADMIN. Cette opération "
                "est réservée à une procédure administrative "
                "renforcée de Phoenix Admin."
            ),
    },

    {
        "id":
            "restricted_evidence_exports",

        "label":
            "Exports contrôlés",

        "description":
            (
                "Les impressions et exports de preuves "
                "sont soumis aux permissions."
            ),
    },

]


def permission_catalog():

    result = {}

    for group in PERMISSION_GROUPS.values():

        result.update(
            group[
                "permissions"
            ]
        )

    return result


def permission_label(
    permission
):

    return permission_catalog().get(
        permission,
        permission,
    )


def public_permission_groups():

    return PERMISSION_GROUPS


def public_security_rules():

    return list(
        MANDATORY_SECURITY_RULES
    )
