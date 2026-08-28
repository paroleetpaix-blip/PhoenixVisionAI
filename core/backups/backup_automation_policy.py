"""
Phoenix Vision AI
Backup Automation Policy

Réglages centralisés des sauvegardes automatiques.
"""

AUTOMATIC_BACKUPS_ENABLED = True

AUTOMATIC_BACKUP_TYPE = "AUTOMATIC"

# Une nouvelle sauvegarde automatique au maximum chaque heure.
AUTOMATIC_BACKUP_INTERVAL_SECONDS = 60 * 60

# Le scheduler vérifie périodiquement sans créer
# systématiquement une sauvegarde.
SCHEDULER_POLL_SECONDS = 5 * 60


# ============================================================
# RETENTION GFS
# ============================================================

# Toutes les sauvegardes automatiques récentes.
RETENTION_HOURLY_HOURS = 48

# Ensuite : une sauvegarde représentative par jour.
RETENTION_DAILY_DAYS = 30

# Ensuite : une sauvegarde représentative par semaine.
RETENTION_WEEKLY_WEEKS = 12

# Ensuite : une sauvegarde représentative par mois.
RETENTION_MONTHLY_MONTHS = 12
