import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

# Import pyi_splash untuk kontrol splash screen
# Note: pyi_splash hanya tersedia saat aplikasi dijalankan via PyInstaller
try:
    import pyi_splash  # type: ignore[import-not-found]
    SPLASH_AVAILABLE = True
except ImportError:
    SPLASH_AVAILABLE = False

class BackgroundRemoverApp:
    """Main application class"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        self.window = MainWindow()

    def run(self):
        """Menjalankan aplikasi"""
        self.window.show()

        # Close splash screen setelah window muncul
        if SPLASH_AVAILABLE:
            pyi_splash.close()

        return self.app.exec_()
