# enhance_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSlider, QGroupBox, QCheckBox, QProgressBar,
                             QMessageBox, QTabWidget, QWidget, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import io

class EnhanceWorker(QThread):
    """Worker thread untuk processing foto"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, pixmap, settings):
        super().__init__()
        self.pixmap = pixmap
        self.settings = settings
        
    def pixmap_to_cv2(self, pixmap):
        """Convert QPixmap ke OpenCV format"""
        # Convert QPixmap to QImage
        qimg = pixmap.toImage()
        
        # Convert QImage to PIL Image
        buffer = qimg.bits().asstring(qimg.byteCount())
        pil_img = Image.frombuffer("RGBA", (qimg.width(), qimg.height()), buffer, "raw", "BGRA", 0, 1)
        
        # Convert PIL to OpenCV
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGR)
        return cv_img
    
    def cv2_to_pixmap(self, cv_img):
        """Convert OpenCV ke QPixmap"""
        # Convert BGR to RGB
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(rgb_img)
        
        # Convert PIL to QPixmap
        buffer = io.BytesIO()
        pil_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        return pixmap
    
    def run(self):
        try:
            self.progress.emit(10)
            
            # Convert pixmap ke cv2
            img = self.pixmap_to_cv2(self.pixmap)
            self.progress.emit(20)
            
            # Apply enhancements berdasarkan settings
            if self.settings['sharpen']:
                img = self.sharpen_image(img)
                self.progress.emit(35)
            
            if self.settings['denoise']:
                img = self.denoise_image(img)
                self.progress.emit(50)
            
            if self.settings['enhance_contrast']:
                img = self.enhance_contrast(img)
                self.progress.emit(65)
            
            if self.settings['brightness'] != 0:
                img = self.adjust_brightness(img, self.settings['brightness'])
                self.progress.emit(80)
            
            if self.settings['auto_enhance']:
                img = self.auto_enhance(img)
                self.progress.emit(90)
            
            # Convert kembali ke pixmap
            result_pixmap = self.cv2_to_pixmap(img)
            self.progress.emit(100)
            
            self.finished.emit(result_pixmap)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def sharpen_image(self, img):
        """Sharpen gambar untuk mengurangi blur"""
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(img, -1, kernel)
        return sharpened
    
    def denoise_image(self, img):
        """Mengurangi noise pada gambar"""
        # Non-local means denoising
        denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        return denoised
    
    def enhance_contrast(self, img):
        """Meningkatkan kontras gambar"""
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        return enhanced
    
    def adjust_brightness(self, img, brightness):
        """Adjust brightness"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Adjust brightness
        v = cv2.add(v, brightness)
        v = np.clip(v, 0, 255)
        
        enhanced = cv2.merge([h, s, v])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_HSV2BGR)
        return enhanced
    
    def auto_enhance(self, img):
        """Auto enhancement menggunakan histogram equalization"""
        # Convert to YUV
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        
        # Equalize histogram pada Y channel
        yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        return enhanced

class PhotoEnhanceDialog(QDialog):
    """Dialog untuk memperbaiki foto"""
    
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.original_pixmap = pixmap
        self.enhanced_pixmap = None
        self.preview_pixmap = None
        self.worker = None
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("Perbaiki Foto")
        self.setModal(True)
        self.setFixedSize(700, 650)
        
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Perbaiki Foto - Hapus Blur, Buram & Rusak")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2C3E50; padding: 15px;")
        main_layout.addWidget(title)
        
        # Content layout
        content_layout = QHBoxLayout()
        
        # Preview area
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        preview_layout.addWidget(preview_label)
        
        self.preview_widget = QLabel()
        self.preview_widget.setFixedSize(300, 350)
        self.preview_widget.setAlignment(Qt.AlignCenter)
        self.preview_widget.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        # Set preview awal
        scaled_pixmap = self.original_pixmap.scaled(300, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_widget.setPixmap(scaled_pixmap)
        preview_layout.addWidget(self.preview_widget)
        
        content_layout.addLayout(preview_layout)
        
        # Controls area
        controls_layout = QVBoxLayout()
        
        # Tab widget untuk pengaturan
        tab_widget = QTabWidget()
        
        # Tab Basic Enhancement
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Quick fixes
        quick_group = QGroupBox("Perbaikan Cepat")
        quick_layout = QVBoxLayout(quick_group)
        
        self.sharpen_check = QCheckBox("Sharpen (Anti Blur)")
        self.sharpen_check.setChecked(True)
        self.sharpen_check.setStyleSheet("font-size: 12px; padding: 5px;")
        quick_layout.addWidget(self.sharpen_check)
        
        self.denoise_check = QCheckBox("Hapus Noise/Grain")
        self.denoise_check.setChecked(True)
        self.denoise_check.setStyleSheet("font-size: 12px; padding: 5px;")
        quick_layout.addWidget(self.denoise_check)
        
        self.contrast_check = QCheckBox("Tingkatkan Kontras")
        self.contrast_check.setChecked(True)
        self.contrast_check.setStyleSheet("font-size: 12px; padding: 5px;")
        quick_layout.addWidget(self.contrast_check)
        
        self.auto_enhance_check = QCheckBox("Auto Enhancement")
        self.auto_enhance_check.setChecked(False)
        self.auto_enhance_check.setStyleSheet("font-size: 12px; padding: 5px;")
        quick_layout.addWidget(self.auto_enhance_check)
        
        basic_layout.addWidget(quick_group)
        
        # Brightness adjustment
        brightness_group = QGroupBox("Kecerahan")
        brightness_layout = QVBoxLayout(brightness_group)
        
        brightness_label = QLabel("Adjustment:")
        brightness_layout.addWidget(brightness_label)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-50, 50)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_slider.setTickInterval(25)
        brightness_layout.addWidget(self.brightness_slider)
        
        brightness_value_layout = QHBoxLayout()
        brightness_value_layout.addWidget(QLabel("Gelap"))
        brightness_value_layout.addStretch()
        self.brightness_value = QLabel("0")
        self.brightness_value.setAlignment(Qt.AlignCenter)
        brightness_value_layout.addWidget(self.brightness_value)
        brightness_value_layout.addStretch()
        brightness_value_layout.addWidget(QLabel("Terang"))
        brightness_layout.addLayout(brightness_value_layout)
        
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_value.setText(str(v)))
        
        basic_layout.addWidget(brightness_group)
        basic_layout.addStretch()
        
        tab_widget.addTab(basic_tab, "Dasar")
        
        # Tab Advanced (placeholder for future features)
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        info_label = QLabel("Fitur Advanced:\n• Preset akan ditambahkan\n• Custom filter\n• Batch processing")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        advanced_layout.addWidget(info_label)
        advanced_layout.addStretch()
        
        tab_widget.addTab(advanced_tab, "Lanjutan")
        
        controls_layout.addWidget(tab_widget)
        content_layout.addLayout(controls_layout)
        main_layout.addLayout(content_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498DB;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Preview button
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.preview_enhancement)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #2980B9; }
            QPushButton:pressed { background-color: #1F618D; }
        """)
        button_layout.addWidget(preview_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_preview)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #C0392B; }
            QPushButton:pressed { background-color: #A93226; }
        """)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Batal")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #7F8C8D; }
            QPushButton:pressed { background-color: #6C7B7D; }
        """)
        button_layout.addWidget(cancel_btn)
        
        # Apply button
        self.apply_btn = QPushButton("Terapkan")
        self.apply_btn.clicked.connect(self.apply_enhancement)
        self.apply_btn.setEnabled(False)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:pressed { background-color: #1E8449; }
            QPushButton:disabled { background-color: #AEB6BF; }
        """)
        button_layout.addWidget(self.apply_btn)
        
        main_layout.addLayout(button_layout)
    
    def get_settings(self):
        """Get current enhancement settings"""
        return {
            'sharpen': self.sharpen_check.isChecked(),
            'denoise': self.denoise_check.isChecked(),
            'enhance_contrast': self.contrast_check.isChecked(),
            'auto_enhance': self.auto_enhance_check.isChecked(),
            'brightness': self.brightness_slider.value()
        }
    
    def preview_enhancement(self):
        """Preview enhancement"""
        if self.worker and self.worker.isRunning():
            return
        
        settings = self.get_settings()
        
        # Check if any enhancement is selected
        if not any([settings['sharpen'], settings['denoise'], 
                   settings['enhance_contrast'], settings['auto_enhance']]) and settings['brightness'] == 0:
            QMessageBox.information(self, "Info", "Pilih minimal satu jenis perbaikan untuk preview!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start worker thread
        self.worker = EnhanceWorker(self.original_pixmap, settings)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_preview_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_preview_finished(self, enhanced_pixmap):
        """Handle preview completion"""
        self.preview_pixmap = enhanced_pixmap
        
        # Update preview
        scaled_pixmap = enhanced_pixmap.scaled(300, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_widget.setPixmap(scaled_pixmap)
        
        self.progress_bar.setVisible(False)
        self.apply_btn.setEnabled(True)
        
        QMessageBox.information(self, "Preview", "Preview berhasil! Klik 'Terapkan' untuk menggunakan hasil ini.")
    
    def on_error(self, error_msg):
        """Handle error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Gagal memproses gambar:\n{error_msg}")
    
    def reset_preview(self):
        """Reset preview ke gambar original"""
        scaled_pixmap = self.original_pixmap.scaled(300, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_widget.setPixmap(scaled_pixmap)
        self.preview_pixmap = None
        self.apply_btn.setEnabled(False)
    
    def apply_enhancement(self):
        """Apply enhancement"""
        if self.preview_pixmap:
            self.enhanced_pixmap = self.preview_pixmap
            self.accept()
        else:
            QMessageBox.warning(self, "Peringatan", "Lakukan preview terlebih dahulu!")
    
    def get_enhanced_pixmap(self):
        """Return enhanced pixmap"""
        return self.enhanced_pixmap


# Update untuk main_window.py - tambahkan fungsi enhance_photo:
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

