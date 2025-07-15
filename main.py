import sys
from app import BackgroundRemoverApp

def main():
    """Entry point aplikasi"""
    print('Apps berjalan bous')
    app = BackgroundRemoverApp()
    sys.exit(app.run())  # ganti exit() dengan sys.exit()

if __name__ == '__main__':
    main()
