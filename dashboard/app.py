"""
Phoenix Vision AI Desktop Launcher
"""

import sys

from PySide6.QtWidgets import QApplication

from dashboard.main_window import PhoenixMainWindow



def start_dashboard():

    app = QApplication(sys.argv)

    window = PhoenixMainWindow()

    window.show()

    sys.exit(
        app.exec()
    )



if __name__ == "__main__":

    start_dashboard()