import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

class BackgroundRemoverApp:
    """Main application class"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        self.window = MainWindow()

    def run(self):
        """Menjalankan aplikasi"""
        self.window.show()
        return self.app.exec_()
