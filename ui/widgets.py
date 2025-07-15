from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageLabel(QLabel):
    def __init__(self, width=250, height=300):
        super().__init__()
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #d0d0d0;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
        """)

    def set_image(self, pixmap):
        if pixmap:
            scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)

class StyledButton(QPushButton):
    def __init__(self, text, primary=True):
        super().__init__(text)
        self.setPrimary(primary)
        self.setCursor(Qt.PointingHandCursor)

    def setPrimary(self, primary=True):
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #5DADE2;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 5px;
                    min-width: 200px;
                }
                QPushButton:hover { background-color: #3498DB; }
                QPushButton:pressed { background-color: #2874A6; }
                QPushButton:disabled { background-color: #AEB6BF; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 5px;
                    min-width: 200px;
                }
                QPushButton:hover { background-color: #C0392B; }
                QPushButton:pressed { background-color: #A93226; }
            """)
