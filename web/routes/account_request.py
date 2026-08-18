"""
========================================================
PHOENIX VISION AI

Account Request Routes

Phoenix Security Technologies
========================================================
"""

from fastapi import (
    APIRouter,
    Form
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse
)

from datetime import datetime

from pathlib import Path

import json
import uuid


router = APIRouter()


DATA_FILE = Path(
    "data/account_requests.json"
)


def load_requests():

    if not DATA_FILE.exists():

        return []

    try:

        with DATA_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_requests(requests):

    DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with DATA_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            requests,
            file,
            ensure_ascii=False,
            indent=4
        )


@router.get(
    "/request-account",
    response_class=HTMLResponse
)
async def account_request_page():

    with open(

        "web/templates/account_request.html",

        "r",

        encoding="utf-8"

    ) as file:

        return file.read()


@router.post(
    "/api/account-request"
)
async def submit_account_request(

    nom: str = Form(...),

    postnom: str = Form(...),

    prenom: str = Form(...),

    sexe: str = Form(...),

    date_naissance: str = Form(...),

    email: str = Form(...),

    telephone: str = Form(...),

    organisation: str = Form(...),

    matricule: str = Form(""),

    departement: str = Form(...),

    fonction: str = Form(...),

    site_affectation: str = Form(...),

    responsable: str = Form(""),

    acces_demande: str = Form(...),

    motif: str = Form(...)

):

    requests = load_requests()


    normalized_email = (
        email
        .strip()
        .lower()
    )


    for existing in requests:

        if (

            existing.get(
                "email",
                ""
            ).lower()
            ==
            normalized_email

            and

            existing.get(
                "status"
            )
            ==
            "PENDING"

        ):

            return JSONResponse(

                status_code=409,

                content={

                    "success": False,

                    "message":
                        "Une demande est déjà en attente pour cet email."

                }

            )


    request_data = {

        "request_id":
            "REQ-"
            +
            uuid.uuid4()
            .hex[:10]
            .upper(),

        "nom":
            nom.strip(),

        "postnom":
            postnom.strip(),

        "prenom":
            prenom.strip(),

        "sexe":
            sexe.strip(),

        "date_naissance":
            date_naissance.strip(),

        "email":
            normalized_email,

        "telephone":
            telephone.strip(),

        "organisation":
            organisation.strip(),

        "matricule":
            matricule.strip(),

        "departement":
            departement.strip(),

        "fonction":
            fonction.strip(),

        "site_affectation":
            site_affectation.strip(),

        "responsable":
            responsable.strip(),

        "acces_demande":
            acces_demande.strip(),

        "motif":
            motif.strip(),

        "status":
            "PENDING",

        "created_at":
            datetime.now()
            .isoformat(
                timespec="seconds"
            ),

        "photo":
            None,

        "assigned_username":
            None,

        "role":
            None,

        "access_level":
            None,

        "account_expiry":
            None

    }


    requests.append(
        request_data
    )


    save_requests(
        requests
    )


    return {

        "success": True,

        "request_id":
            request_data[
                "request_id"
            ]

    }