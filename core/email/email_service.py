"""
========================================================
PHOENIX VISION AI

Email Service

Phoenix Security Technologies
========================================================
"""

import os
import smtplib

from email.message import EmailMessage


class PhoenixEmailService:

    def __init__(self):

        self.host = os.getenv(
            "PHOENIX_SMTP_HOST"
        )

        self.port = int(
            os.getenv(
                "PHOENIX_SMTP_PORT",
                "587"
            )
        )

        self.username = os.getenv(
            "PHOENIX_SMTP_USER"
        )

        self.password = os.getenv(
            "PHOENIX_SMTP_PASSWORD"
        )

        self.sender = os.getenv(
            "PHOENIX_SMTP_SENDER",
            self.username or ""
        )

        self.company_name = (
            "Phoenix Security Technologies"
        )

        self.product_name = (
            "Phoenix Vision AI"
        )


    # ====================================================
    # CONFIGURATION
    # ====================================================

    def is_configured(self):

        return all([

            self.host,

            self.port,

            self.username,

            self.password,

            self.sender

        ])


    # ====================================================
    # ENVOI
    # ====================================================

    def send_message(
        self,
        destination,
        subject,
        text_content,
        html_content=None
    ):

        if not self.is_configured():

            return {

                "success": False,

                "reason":
                    "SMTP_NOT_CONFIGURED"

            }


        message = EmailMessage()

        message["From"] = (
            self.sender
        )

        message["To"] = (
            destination
        )

        message["Subject"] = (
            subject
        )


        message.set_content(
            text_content
        )


        if html_content:

            message.add_alternative(

                html_content,

                subtype="html"

            )


        try:

            with smtplib.SMTP(

                self.host,

                self.port,

                timeout=20

            ) as smtp:

                smtp.ehlo()

                smtp.starttls()

                smtp.ehlo()

                smtp.login(

                    self.username,

                    self.password

                )

                smtp.send_message(
                    message
                )


            return {

                "success": True,

                "reason": None

            }


        except Exception as error:

            print(
                "[PHOENIX EMAIL ERROR]",
                error
            )


            return {

                "success": False,

                "reason":
                    "SMTP_SEND_FAILED"

            }


    # ====================================================
    # EMAIL D'ACTIVATION
    # ====================================================

    def send_account_activation(

        self,

        destination,

        first_name,

        username,

        temporary_password,

        role,

        organisation

    ):

        subject = (
            "Phoenix Vision AI — "
            "Votre compte a été activé"
        )


        text_content = f"""
Bonjour {first_name},

Votre demande d'accès à Phoenix Vision AI a été approuvée.

Organisation :
{organisation}

Identifiant Phoenix :
{username}

Mot de passe temporaire :
{temporary_password}

Rôle :
{role}

Lors de votre première connexion, Phoenix Vision AI vous demandera obligatoirement de remplacer ce mot de passe temporaire.

Ne communiquez jamais votre identifiant ou votre mot de passe à une autre personne.

Si vous n'êtes pas à l'origine de cette demande, contactez immédiatement votre administrateur.

Phoenix Security Technologies
Phoenix Vision AI

© 2026 Tous droits réservés.
""".strip()


        html_content = f"""
<!DOCTYPE html>

<html lang="fr">

<head>

<meta charset="UTF-8">

</head>

<body style="
    margin:0;
    padding:0;
    background:#02060d;
    font-family:Arial,Helvetica,sans-serif;
    color:#eef4fa;
">

<div style="
    width:100%;
    padding:35px 15px;
    box-sizing:border-box;
">

<div style="
    max-width:620px;
    margin:0 auto;
    background:#061522;
    border:1px solid #0a5d9f;
    border-radius:12px;
    overflow:hidden;
">


<div style="
    padding:28px 30px;
    background:#03101c;
    border-bottom:1px solid #10446d;
">

<div style="
    color:#078cff;
    font-size:13px;
    font-weight:bold;
    letter-spacing:2px;
">
PHOENIX VISION AI
</div>

<div style="
    margin-top:6px;
    color:#ffb400;
    font-size:11px;
">
Phoenix Security Technologies
</div>

</div>


<div style="
    padding:32px 30px;
">

<h2 style="
    margin:0 0 12px;
    color:#ffffff;
">
Compte approuvé
</h2>


<p style="
    color:#adb8c5;
    line-height:1.6;
">
Bonjour {first_name},
</p>


<p style="
    color:#adb8c5;
    line-height:1.6;
">
Votre demande d'accès à
<strong style="color:#ffffff;">
Phoenix Vision AI
</strong>
a été validée par un administrateur.
</p>


<div style="
    margin:25px 0;
    padding:20px;
    background:#020b16;
    border:1px solid #0c568f;
    border-radius:8px;
">


<div style="
    margin-bottom:15px;
">

<div style="
    color:#71869a;
    font-size:11px;
">
IDENTIFIANT PHOENIX
</div>

<div style="
    margin-top:5px;
    color:#19a0ff;
    font-size:19px;
    font-weight:bold;
    font-family:monospace;
">
{username}
</div>

</div>


<div style="
    margin-bottom:15px;
">

<div style="
    color:#71869a;
    font-size:11px;
">
MOT DE PASSE TEMPORAIRE
</div>

<div style="
    margin-top:5px;
    color:#ffffff;
    font-size:18px;
    font-weight:bold;
    font-family:monospace;
">
{temporary_password}
</div>

</div>


<div>

<div style="
    color:#71869a;
    font-size:11px;
">
RÔLE
</div>

<div style="
    margin-top:5px;
    color:#ffb400;
    font-size:13px;
">
{role}
</div>

</div>


</div>


<div style="
    padding:15px;
    background:rgba(255,180,0,.05);
    border:1px solid rgba(255,180,0,.35);
    border-radius:7px;
    color:#d5c49b;
    font-size:12px;
    line-height:1.6;
">

Pour votre sécurité, ce mot de passe est temporaire.
Vous devrez obligatoirement le remplacer lors de votre
première connexion.

</div>


<p style="
    margin-top:25px;
    color:#8190a0;
    font-size:11px;
    line-height:1.6;
">

Ne partagez jamais vos identifiants.
Si vous n'êtes pas à l'origine de cette demande,
contactez immédiatement votre administrateur.

</p>

</div>


<div style="
    padding:18px 30px;
    border-top:1px solid #10324e;
    background:#020a13;
    color:#677687;
    font-size:10px;
    text-align:center;
">

© 2026 Phoenix Security Technologies.
Tous droits réservés.

</div>

</div>

</div>

</body>

</html>
"""


        return self.send_message(

            destination=
                destination,

            subject=
                subject,

            text_content=
                text_content,

            html_content=
                html_content

        )


email_service = (
    PhoenixEmailService()
)