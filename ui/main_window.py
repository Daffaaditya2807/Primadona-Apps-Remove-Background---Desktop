import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
    QMessageBox, QPushButton,QApplication, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from ui.widgets import ImageLabel, StyledButton
from ui.crop_dialog import CropDialog
from ui.background_dialog import BackgroundChangeDialog
from ui.print_dialog import PrintDialog
from utils.image_processor import remove_background, REMBG_AVAILABLE

class MainWindow(QMainWindow):
    """Main window aplikasi"""

    def __init__(self):
        super().__init__()
        basedir = getattr(sys, '_MEIPASS', os.path.abspath("."))
        icon_path = os.path.join(basedir, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.original_pixmap = None
        self.result_pixmap = None
        self.transparent_pixmap = None
        self.undo_stack = []
        self.redo_stack = []
        self.setupUI()
        
        

    def setupUI(self):
        self.setWindowTitle("Primadona Apps - Hapus Background Foto")
        self.setFixedSize(920, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8FAFC;
            }
            QWidget {
                color: #1E293B;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            }
            QLabel {
                color: #1E293B;
            }
            QDialog {
                background-color: #FFFFFF;
            }
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #1E293B;
            }
            QMessageBox QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #E2E8F0;
            }
            QPushButton:disabled {
                background-color: #E2E8F0;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(15)

        self._createTitle(main_layout)
        self._createTopControls(main_layout)
        self._createContentArea(main_layout)
        self._createBottomControls(main_layout)
        main_layout.addStretch()

    def _createTitle(self, parent_layout):
        title = QLabel("Primadona Apps - Hapus Background Foto")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1E293B; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        parent_layout.addWidget(title)

    def _createTopControls(self, parent_layout):
        top_controls = QHBoxLayout()
        
        self.undo_btn = StyledButton("↩ Undo", "secondary")
        self.undo_btn.setFixedSize(120, 38)
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)
        top_controls.addWidget(self.undo_btn)
        
        self.redo_btn = StyledButton("Redo ↪", "secondary")
        self.redo_btn.setFixedSize(120, 38)
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setEnabled(False)
        top_controls.addWidget(self.redo_btn)
        
        top_controls.addStretch()
        parent_layout.addLayout(top_controls)

    def save_state(self):
        state = {
            'original': QPixmap(self.original_pixmap) if self.original_pixmap else None,
            'result': QPixmap(self.result_pixmap) if self.result_pixmap else None,
            'transparent': QPixmap(self.transparent_pixmap) if getattr(self, 'transparent_pixmap', None) else None
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > 15:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        self.undo_btn.setEnabled(len(self.undo_stack) > 0)
        self.redo_btn.setEnabled(len(self.redo_stack) > 0)

    def undo(self):
        if not self.undo_stack:
            return
        
        current_state = {
            'original': QPixmap(self.original_pixmap) if self.original_pixmap else None,
            'result': QPixmap(self.result_pixmap) if self.result_pixmap else None,
            'transparent': QPixmap(self.transparent_pixmap) if getattr(self, 'transparent_pixmap', None) else None
        }
        self.redo_stack.append(current_state)
        
        state = self.undo_stack.pop()
        self.restore_state(state)
        self.update_undo_redo_buttons()

    def redo(self):
        if not self.redo_stack:
            return
            
        current_state = {
            'original': QPixmap(self.original_pixmap) if self.original_pixmap else None,
            'result': QPixmap(self.result_pixmap) if self.result_pixmap else None,
            'transparent': QPixmap(self.transparent_pixmap) if getattr(self, 'transparent_pixmap', None) else None
        }
        self.undo_stack.append(current_state)
        
        state = self.redo_stack.pop()
        self.restore_state(state)
        self.update_undo_redo_buttons()

    def restore_state(self, state):
        self.original_pixmap = state['original']
        self.result_pixmap = state['result']
        self.transparent_pixmap = state['transparent']
        
        if self.original_pixmap:
            self.before_image.set_image(self.original_pixmap)
        else:
            self.before_image.clear()
            
        if self.result_pixmap:
            self.after_image.set_image(self.result_pixmap)
        else:
            self.after_image.clear()
            
        has_original = self.original_pixmap is not None
        has_result = self.result_pixmap is not None
        has_transparent = self.transparent_pixmap is not None
        
        self.process_btn.setEnabled(has_original)
        self.crop_btn.setEnabled(has_original or has_result)
        self.change_bg_btn.setEnabled(has_transparent)
        self.save_btn.setEnabled(has_result)
        self.print_btn.setEnabled(has_result)

    def _createContentArea(self, parent_layout):
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        parent_layout.addLayout(content_layout)
        self._createBeforePanel(content_layout)
        self._createAfterPanel(content_layout)

    def _createBeforePanel(self, layout):
        panel = QVBoxLayout()
        panel.setAlignment(Qt.AlignCenter)
        layout.addLayout(panel)
        
        self.before_image = ImageLabel(360, 420)
        self.before_image.file_dropped.connect(self.load_image_path)
        panel.addWidget(self.before_image, 0, Qt.AlignCenter)
        
        panel.addSpacing(12)
        
        label = QLabel("Sebelum (Original)")
        label.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748B; padding: 5px;")
        label.setAlignment(Qt.AlignCenter)
        panel.addWidget(label)

    def _createAfterPanel(self, layout):
        panel = QVBoxLayout()
        panel.setAlignment(Qt.AlignCenter)
        layout.addLayout(panel)
        
        self.after_image = ImageLabel(360, 420)
        panel.addWidget(self.after_image, 0, Qt.AlignCenter)
        
        panel.addSpacing(12)
        
        label = QLabel("Hasil / Sesudah")
        label.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748B; padding: 5px;")
        label.setAlignment(Qt.AlignCenter)
        panel.addWidget(label)

    def _createBottomControls(self, parent_layout):
        # Row 1: Action/editing buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        actions_layout.addStretch()

        self.add_photo_btn = StyledButton("Masukan Foto", "secondary")
        self.add_photo_btn.clicked.connect(self.add_photo)
        actions_layout.addWidget(self.add_photo_btn)

        self.process_btn = StyledButton("Proses Hapus Bg", "primary")
        self.process_btn.clicked.connect(self.process_background)
        self.process_btn.setEnabled(False)
        actions_layout.addWidget(self.process_btn)

        self.crop_btn = StyledButton("Crop Gambar", "secondary")
        self.crop_btn.clicked.connect(self.crop_image)
        self.crop_btn.setEnabled(False)
        actions_layout.addWidget(self.crop_btn)

        self.change_bg_btn = StyledButton("Ubah Background", "secondary")
        self.change_bg_btn.clicked.connect(self.change_background)
        self.change_bg_btn.setEnabled(False)
        actions_layout.addWidget(self.change_bg_btn)

        actions_layout.addStretch()
        parent_layout.addLayout(actions_layout)

        parent_layout.addSpacing(10)

        # Row 2: Save button centered at the very bottom
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        self.save_btn = StyledButton("Simpan Hasil Foto", "success")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_result)
        self.save_btn.setStyleSheet(self.save_btn.styleSheet() + "\nQPushButton { min-width: 200px; font-size: 14px; }")
        save_layout.addWidget(self.save_btn)
        
        self.print_btn = StyledButton("Cetak (Print)", "primary")
        self.print_btn.setEnabled(False)
        self.print_btn.clicked.connect(self.print_result)
        self.print_btn.setStyleSheet(self.print_btn.styleSheet() + "\nQPushButton { min-width: 150px; font-size: 14px; }")
        save_layout.addWidget(self.print_btn)
        
        save_layout.addStretch()
        parent_layout.addLayout(save_layout)

    def load_image_path(self, file_path):
        if file_path:
            self.save_state()
            self.original_pixmap = QPixmap(file_path)
            self.before_image.set_image(self.original_pixmap)
            self.after_image.clear()
            self.result_pixmap = None
            self.process_btn.setEnabled(True)
            self.crop_btn.setEnabled(True)
            self.change_bg_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.print_btn.setEnabled(False)

    def add_photo(self):
        # Default ke folder Downloads
        import os
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih Foto", downloads_path, "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.load_image_path(file_path)

    def process_background(self):
        # Gunakan result_pixmap jika ada (foto terakhir yang diedit/dicrop), jika tidak gunakan original
        source_pixmap = self.result_pixmap if self.result_pixmap else self.original_pixmap
        
        if not source_pixmap:
            return
        if not REMBG_AVAILABLE:
            QMessageBox.warning(self, "Library Tidak Tersedia", "Library rembg tidak terinstall.")
            return
            
        # Tampilkan loading state
        self.process_btn.setText("⏳ Sedang Memproses...")
        self.process_btn.setEnabled(False)
        self.setCursor(Qt.WaitCursor)
        QApplication.processEvents() # Force UI refresh agar teks update
        
        try:
            self.save_state()
            self.transparent_pixmap = remove_background(source_pixmap)
            self.result_pixmap = QPixmap(self.transparent_pixmap)
            self.after_image.set_image(self.result_pixmap)
            
            # Kembalikan state button
            self.process_btn.setText("✨ Proses Hapus Bg")
            self.process_btn.setEnabled(True)
            self.change_bg_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.print_btn.setEnabled(True)
            self.crop_btn.setEnabled(True)
            self.setCursor(Qt.ArrowCursor)
        except Exception as e:
            self.process_btn.setText("✨ Proses Hapus Bg")
            self.process_btn.setEnabled(True)
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(self, "Error", "Gagal menghapus background")

    def crop_image(self):
        """Fungsi untuk crop gambar"""
        # Prioritas crop: result_pixmap (setelah remove bg) > original_pixmap
        pixmap_to_crop = self.result_pixmap if self.result_pixmap else self.original_pixmap

        if not pixmap_to_crop:
            QMessageBox.warning(self, "Peringatan", "Tidak ada gambar yang dapat di-crop!")
            return

        # Buka dialog crop
        dialog = CropDialog(pixmap_to_crop, self)
        if dialog.exec_() == QDialog.Accepted:
            cropped_pixmap, crop_rect = dialog.get_crop_result()
            if cropped_pixmap:
                self.save_state()
                # Selalu update result_pixmap dan tampilkan di after_image (Hasil/Sesudah)
                self.result_pixmap = cropped_pixmap
                self.after_image.set_image(self.result_pixmap)
                
                # Jika kita meng-crop gambar original (sebelum hapus bg)
                if pixmap_to_crop == self.original_pixmap:
                    # Update juga original_pixmap agar proses hapus bg berikutnya sinkron
                    self.original_pixmap = cropped_pixmap
                    self.before_image.set_image(self.original_pixmap)
                    self.transparent_pixmap = None
                else:
                    # Jika kita meng-crop hasil, crop juga transparent_pixmap jika ada
                    if hasattr(self, 'transparent_pixmap') and self.transparent_pixmap and crop_rect:
                        self.transparent_pixmap = self.transparent_pixmap.copy(crop_rect)
                
                # Aktifkan tombol save, print, dan crop
                self.save_btn.setEnabled(True)
                self.print_btn.setEnabled(True)
                self.crop_btn.setEnabled(True)
                
                # Tombol change background aktif jika kita punya transparent pixmap
                has_removed_bg = hasattr(self, 'transparent_pixmap') and self.transparent_pixmap is not None
                self.change_bg_btn.setEnabled(has_removed_bg)

    def change_background(self):
        """Fungsi untuk mengubah background"""
        if not self.result_pixmap:
            QMessageBox.warning(self, "Peringatan", "Lakukan proses hapus background terlebih dahulu!")
            return

        # Gunakan transparent_pixmap sebagai dasar ubah warna
        trans_pixmap = getattr(self, 'transparent_pixmap', None)
        if not trans_pixmap:
            trans_pixmap = self.result_pixmap

        # Buka dialog change background
        dialog = BackgroundChangeDialog(trans_pixmap, self)
        if dialog.exec_() == QDialog.Accepted:
            new_background_pixmap = dialog.get_result_pixmap()
            if new_background_pixmap:
                self.save_state()
                # Update result pixmap dengan background baru
                self.result_pixmap = new_background_pixmap
                self.after_image.set_image(self.result_pixmap)

    def save_result(self):
        if not self.result_pixmap:
            return
        # Default ke folder Downloads dengan nama file dinamis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"hasil_edit_{timestamp}.png"
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", default_filename)
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan Hasil", downloads_path, "PNG Files (*.png);;JPEG Files (*.jpg)")
        if file_path:
            self.result_pixmap.save(file_path, quality=100)

    def print_result(self):
        """Fungsi untuk mencetak foto"""
        if not self.result_pixmap:
            return
        
        dialog = PrintDialog(self.result_pixmap, self)
        dialog.exec_()
