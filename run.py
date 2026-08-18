"""
========================================================
PHOENIX VISION AI

Official Entry Point

Phoenix Security Technologies
========================================================
"""

from core.server.server import PhoenixServer
from core import runtime

server = PhoenixServer()

# Enregistrement des objets globaux
runtime.engine = server.engine

# Le StreamService sera enregistré après le démarrage
# (lorsqu'il existera dans PhoenixEngine)

server.start()

# Vérification
runtime.stream_service = getattr(
    server.engine,
    "stream_service",
    None
)

input("\nAppuyez sur Entrée pour arrêter le serveur...\n")