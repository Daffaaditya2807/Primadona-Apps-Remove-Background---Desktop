import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
    QMessageBox, QPushButton,QApplication, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from ui.widgets import ImageLabel, StyledButton
from ui.crop_dialog import CropDialog
from ui.background_dialog import BackgroundChangeDialog
from ui.enhance_dialog import PhotoEnhanceDialog
from utils.image_processor import ImageProcessor, REMBG_AVAILABLE

class MainWindow(QMainWindow):
    """Main window aplikasi"""

    def __init__(self):
        super().__init__()
        basedir = getattr(sys, '_MEIPASS', os.path.abspath("."))
        icon_path = os.path.join(basedir, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.original_pixmap = None
        self.result_pixmap = None
        self.setupUI()
        
        

    def setupUI(self):
        self.setWindowTitle("Primadona Apps - Hapus Background Foto")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #f0f0f0;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self._createTitle(main_layout)
        self._createContentArea(main_layout)
        self._createSaveButton(main_layout)
        main_layout.addStretch()

    def _createTitle(self, parent_layout):
        title = QLabel("Primadona Apps - Hapus Background Foto")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        parent_layout.addWidget(title)

    def _createContentArea(self, parent_layout):
        content_layout = QHBoxLayout()
        parent_layout.addLayout(content_layout)
        self._createBeforePanel(content_layout)
        self._createAfterPanel(content_layout)
        self._createControlPanel(content_layout)

    def _createBeforePanel(self, layout):
        panel = QVBoxLayout()
        layout.addLayout(panel)
        self.before_image = ImageLabel()
        panel.addWidget(self.before_image)
        label = QLabel("Sebelum")
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
        label.setAlignment(Qt.AlignCenter)
        panel.addWidget(label)

    def _createAfterPanel(self, layout):
        panel = QVBoxLayout()
        layout.addLayout(panel)
        self.after_image = ImageLabel()
        panel.addWidget(self.after_image)
        label = QLabel("Hasil / Sesudah")
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
        label.setAlignment(Qt.AlignCenter)
        panel.addWidget(label)

    def _createControlPanel(self, layout):
        panel = QVBoxLayout()
        panel.setSpacing(15)
        layout.addLayout(panel)

        self.add_photo_btn = StyledButton("Masukan Foto")
        self.add_photo_btn.clicked.connect(self.add_photo)
        panel.addWidget(self.add_photo_btn)

        self.process_btn = StyledButton("Proses Hapus Bg")
        self.process_btn.clicked.connect(self.process_background)
        self.process_btn.setEnabled(False)
        panel.addWidget(self.process_btn)

        self.crop_btn = StyledButton("Crop Gambar")
        self.crop_btn.clicked.connect(self.crop_image)
        self.crop_btn.setEnabled(False)
        panel.addWidget(self.crop_btn)

        self.change_bg_btn = StyledButton("Ubah Background")
        self.change_bg_btn.clicked.connect(self.change_background)
        self.change_bg_btn.setEnabled(False)
        panel.addWidget(self.change_bg_btn)
        
        self.enhance_btn = StyledButton("Perbaiki Foto")
        self.enhance_btn.clicked.connect(self.enhance_photo)
        self.enhance_btn.setEnabled(False)
        self.enhance_btn.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover { background-color: #8E44AD; }
            QPushButton:pressed { background-color: #7D3C98; }
            QPushButton:disabled { background-color: #AEB6BF; }
        """)
        panel.addWidget(self.enhance_btn)
        

        panel.addStretch()

    def _createSaveButton(self, layout):
        save_container = QHBoxLayout()
        save_container.addStretch()
        self.save_btn = QPushButton("Simpan Hasil Foto")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_result)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5DADE2;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 40px;
                border: none;
                border-radius: 5px;
                min-width: 250px;
            }
            QPushButton:hover { background-color: #3498DB; }
            QPushButton:pressed { background-color: #2874A6; }
            QPushButton:disabled { background-color: #AEB6BF; }
        """)
        save_container.addWidget(self.save_btn)
        save_container.addStretch()
        layout.addLayout(save_container)

    def add_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih Foto", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.original_pixmap = QPixmap(file_path)
            self.before_image.set_image(self.original_pixmap)
            self.after_image.clear()
            self.result_pixmap = None
            self.process_btn.setEnabled(True)
            self.crop_btn.setEnabled(True)  # Aktifkan crop button
            self.enhance_btn.setEnabled(True)
            self.change_bg_btn.setEnabled(False)
            self.save_btn.setEnabled(False)

    def process_background(self):
        if not self.original_pixmap:
            return
        if not REMBG_AVAILABLE:
            QMessageBox.warning(self, "Library Tidak Tersedia", "Library rembg tidak terinstall.\nInstall dengan:\npip install rembg")
            return
        try:
            self.setCursor(Qt.WaitCursor)
            QApplication.processEvents()
            self.result_pixmap = ImageProcessor.remove_background(self.original_pixmap)
            self.after_image.set_image(self.result_pixmap)
            self.change_bg_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.crop_btn.setEnabled(True)  # Tetap aktifkan crop button
            self.enhance_btn.setEnabled(True)
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.information(self, "Berhasil", "Background berhasil dihapus!")
        except Exception as e:
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(self, "Error", f"Gagal menghapus background:\n{str(e)}")

    # Update untuk main_window.py - ganti fungsi crop_image dengan ini:
    def crop_image(self):
        """Fungsi untuk crop gambar hasil remove background"""
        # Prioritas crop: result_pixmap (setelah remove bg) > original_pixmap
        pixmap_to_crop = self.result_pixmap if self.result_pixmap else self.original_pixmap
        
        if not pixmap_to_crop:
            QMessageBox.warning(self, "Peringatan", "Tidak ada gambar yang dapat di-crop!")
            return
        
        # Tentukan sumber gambar untuk informasi user
        source_info = "gambar hasil remove background" if self.result_pixmap else "gambar asli"
        
        # Buka dialog crop
        dialog = CropDialog(pixmap_to_crop, self)
        if dialog.exec_() == QDialog.Accepted:
            cropped_pixmap = dialog.get_cropped_pixmap()
            if cropped_pixmap:
                if self.result_pixmap:
                    # Jika crop dari hasil remove background, update result_pixmap
                    self.result_pixmap = cropped_pixmap
                    self.after_image.set_image(self.result_pixmap)
                    # Keep buttons enabled karena masih ada result
                    self.change_bg_btn.setEnabled(True)
                    self.enhance_btn.setEnabled(True)
                    self.save_btn.setEnabled(True)
                else:
                    # Jika crop dari original, update original_pixmap
                    self.original_pixmap = cropped_pixmap
                    self.before_image.set_image(self.original_pixmap)
                    # Reset hasil processing
                    self.after_image.clear()
                    self.result_pixmap = None
                    self.change_bg_btn.setEnabled(False)
                    self.enhance_btn.setEnabled(True)
                    self.save_btn.setEnabled(False)
                
                QMessageBox.information(self, "Berhasil", f"Berhasil crop {source_info}!")

    # Update untuk mengaktifkan button crop berdasarkan kondisi
    def update_crop_button_state(self):
        """Update state button crop berdasarkan kondisi gambar"""
        # Button crop aktif jika ada gambar original atau result
        has_croppable_image = self.original_pixmap is not None or self.result_pixmap is not None
        self.crop_btn.setEnabled(has_croppable_image)

    def change_background(self):
        """Fungsi untuk mengubah background"""
        if not self.result_pixmap:
            QMessageBox.warning(self, "Peringatan", "Lakukan proses hapus background terlebih dahulu!")
            return
        
        # Buka dialog change background
        dialog = BackgroundChangeDialog(self.result_pixmap, self)
        if dialog.exec_() == QDialog.Accepted:
            new_background_pixmap = dialog.get_result_pixmap()
            if new_background_pixmap:
                # Update result pixmap dengan background baru
                self.result_pixmap = new_background_pixmap
                self.after_image.set_image(self.result_pixmap)
                
                QMessageBox.information(self, "Berhasil", "Background berhasil diubah!")
    # Tambahkan fungsi enhance_photo:
    def enhance_photo(self):
        """Fungsi untuk memperbaiki foto"""
        # Prioritas enhance: result_pixmap > original_pixmap
        pixmap_to_enhance = self.result_pixmap if self.result_pixmap else self.original_pixmap
        
        if not pixmap_to_enhance:
            QMessageBox.warning(self, "Peringatan", "Tidak ada gambar yang dapat diperbaiki!")
            return
        
        # Tentukan sumber gambar untuk informasi user
        source_info = "gambar hasil editing" if self.result_pixmap else "gambar asli"
        
        # Buka dialog enhance
        dialog = PhotoEnhanceDialog(pixmap_to_enhance, self)
        if dialog.exec_() == QDialog.Accepted:
            enhanced_pixmap = dialog.get_enhanced_pixmap()
            if enhanced_pixmap:
                if self.result_pixmap:
                    # Jika enhance dari result, update result_pixmap
                    self.result_pixmap = enhanced_pixmap
                    self.after_image.set_image(self.result_pixmap)
                    # Keep all buttons enabled
                    self.change_bg_btn.setEnabled(True)
                    self.crop_btn.setEnabled(True)
                    self.enhance_btn.setEnabled(True)
                    self.save_btn.setEnabled(True)
                else:
                    # Jika enhance dari original, update original_pixmap
                    self.original_pixmap = enhanced_pixmap
                    self.before_image.set_image(self.original_pixmap)
                    # Enable relevant buttons
                    self.crop_btn.setEnabled(True)
                    self.enhance_btn.setEnabled(True)
                
                QMessageBox.information(self, "Berhasil", f"Berhasil memperbaiki {source_info}!")

    def save_result(self):
        if not self.result_pixmap:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan Hasil", "hasil_no_bg.png", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if file_path:
            self.result_pixmap.save(file_path, quality=100)
            QMessageBox.information(self, "Berhasil", f"Foto berhasil disimpan ke:\n{file_path}")
