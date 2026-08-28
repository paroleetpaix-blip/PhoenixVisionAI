"""
Phoenix Backup operation locks.
"""

import threading


# Un seul processus de mutation Backup à la fois :
# création, migration, préparation Restore ou rétention.
backup_mutation_lock = threading.RLock()
