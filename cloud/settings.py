"""
========================================================
PHOENIX VISION AI

Cloud Settings

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

import os


# ========================================================
# AI SERVER
# ========================================================

SERVER_URL = (
    os.getenv(
        "PHOENIX_AI_SERVER_URL",
        ""
    )
    .strip()
    .rstrip("/")
)


# ========================================================
# API KEY
# Future authentication layer
# ========================================================

API_KEY = (
    os.getenv(
        "PHOENIX_AI_API_KEY",
        ""
    )
    .strip()
)


# ========================================================
# NETWORK TIMEOUT
# ========================================================

try:

    TIMEOUT = float(
        os.getenv(
            "PHOENIX_AI_TIMEOUT",
            "30"
        )
    )

except ValueError:

    TIMEOUT = 30.0


# ========================================================
# JPEG QUALITY
# ========================================================

try:

    JPEG_QUALITY = int(
        os.getenv(
            "PHOENIX_AI_JPEG_QUALITY",
            "90"
        )
    )

except ValueError:

    JPEG_QUALITY = 90


JPEG_QUALITY = max(
    50,
    min(
        JPEG_QUALITY,
        100
    )
)