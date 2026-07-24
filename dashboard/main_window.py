"""
========================================================
PHOENIX VISION AI

Main Window

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""


from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)


from dashboard.video_widget import VideoWidget
from dashboard.controller import DashboardController



class PhoenixMainWindow(QMainWindow):


    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "Phoenix Vision AI Enterprise"
        )


        self.resize(
            1280,
            720
        )


        central = QWidget()

        self.setCentralWidget(
            central
        )


        layout = QVBoxLayout()


        title = QLabel(
            "Phoenix Vision AI\n"
            "Enterprise Dashboard"
        )


        title.setStyleSheet(
            """
            font-size:24px;
            font-weight:bold;
            """
        )


        self.video = VideoWidget()


        layout.addWidget(title)

        layout.addWidget(
            self.video
        )


        central.setLayout(
            layout
        )


        # Test vidéo

        self.controller.start()

        self.controller = DashboardController()