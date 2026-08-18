from core.intelligence.alert import Alert


class IntelligenceCenter:

    def __init__(self):

        self.alerts = []

    def analyze_vehicle(self, vehicle):

        if vehicle.threat_level == "HIGH":

            alert = Alert(

                vehicle.uuid,

                "HIGH",

                "Véhicule à surveiller"

            )

            self.alerts.append(alert)

            return alert

        if vehicle.threat_level == "CRITICAL":

            alert = Alert(

                vehicle.uuid,

                "CRITICAL",

                "Intervention immédiate"

            )

            self.alerts.append(alert)

            return alert

        return None

    def total_alerts(self):

        return len(self.alerts)

    def get_alerts(self):

        return self.alerts