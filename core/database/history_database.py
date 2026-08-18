"""
========================================================
PHOENIX VISION AI

Vehicle History Database

Phoenix Security Technologies
========================================================
"""

import sqlite3


class HistoryDatabase:

    def __init__(self):

        self.connection = sqlite3.connect(
            "database/vehicle_history.db"
        )

        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS vehicle_history(

            uuid TEXT PRIMARY KEY,

            tracker_id INTEGER,

            label TEXT,

            plate TEXT,

            color TEXT,

            brand TEXT,

            model TEXT,

            first_seen TEXT,

            last_seen TEXT,

            total_frames INTEGER,

            max_speed REAL,

            direction TEXT,

            zone TEXT,

            threat_level TEXT,

            threat_score INTEGER,

            status TEXT,

            alerts INTEGER,

            crossings INTEGER,

            created_at TEXT

        )

        """)

        self.connection.commit()

    def save_vehicle(self, vehicle, memory):

        self.cursor.execute("""

        INSERT OR REPLACE INTO vehicle_history(

            uuid,

            tracker_id,

            label,

            plate,

            color,

            brand,

            model,

            first_seen,

            last_seen,

            total_frames,

            max_speed,

            direction,

            zone,

            threat_level,

            threat_score,

            status,

            alerts,

            crossings,

            created_at

        )

        VALUES(

            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?

        )

        """, (

            vehicle.uuid,

            vehicle.tracker_id,

            vehicle.label,

            vehicle.plate,

            vehicle.color,

            vehicle.brand,

            vehicle.model,

            str(memory.first_seen),

            str(memory.last_seen),

            memory.total_frames,

            memory.max_speed,

            vehicle.direction,

            vehicle.zone,

            vehicle.threat_level,

            vehicle.threat_score,

            vehicle.status,

            len(memory.alerts),

            len(vehicle.crossing_events),

            str(memory.first_seen)

        ))

        self.connection.commit()

    def total(self):

        self.cursor.execute(

            "SELECT COUNT(*) FROM vehicle_history"

        )

        return self.cursor.fetchone()[0]

    def find_by_uuid(self, uuid):

        self.cursor.execute(

            "SELECT * FROM vehicle_history WHERE uuid=?",

            (uuid,)

        )

        return self.cursor.fetchone()


    def find_by_plate(self, plate):

        self.cursor.execute(

            "SELECT * FROM vehicle_history WHERE plate=?",

            (plate,)

        )

        return self.cursor.fetchall()


    def find_by_color(self, color):

        self.cursor.execute(

            "SELECT * FROM vehicle_history WHERE color=?",

            (color,)

        )

        return self.cursor.fetchall()


    def find_by_brand(self, brand):

        self.cursor.execute(

            "SELECT * FROM vehicle_history WHERE brand=?",

            (brand,)

        )

        return self.cursor.fetchall()


    def find_by_model(self, model):

        self.cursor.execute(

            "SELECT * FROM vehicle_history WHERE model=?",

            (model,)

        )

        return self.cursor.fetchall()


    def find_by_threat(self, threat):

        self.cursor.execute(

            "SELECT * FROM vehicle_history WHERE threat_level=?",

            (threat,)

        )

        return self.cursor.fetchall()
