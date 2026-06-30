# crop_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QRect
from ui.crop_widget import CropWidget


class CropDialog(QDialog):
    """Dialog untuk cropping gambar"""
    
    # Aspect ratios untuk berbagai ukuran foto
    ASPECT_RATIOS = {
        "Free (Manual)": None,
        "4x6 (2:3)": 4/6,
        "3x4 (3:4)": 3/4,
        "2x3 (2:3)": 2/3,
        "1x1 (Square)": 1/1
    }
    
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap
        self.cropped_pixmap = None
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("Crop Gambar")
        self.setModal(True)
        self.resize(700, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #1E293B;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 12px;
                color: #1E293B;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                selection-background-color: #4F46E5;
                selection-color: white;
                color: #1E293B;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Instruksi
        instruction = QLabel("Pilih ukuran crop dan klik-drag untuk memilih area yang ingin di-crop")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("font-size: 13px; color: #64748B; padding: 5px;")
        layout.addWidget(instruction)
        
        # Size selection
        size_layout = QHBoxLayout()
        size_label = QLabel("Ukuran Crop:")
        size_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #64748B;")
        size_layout.addWidget(size_label)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(list(self.ASPECT_RATIOS.keys()))
        self.size_combo.currentTextChanged.connect(self.on_size_changed)
        size_layout.addWidget(self.size_combo)
        
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # Crop widget
        self.crop_widget = CropWidget(self.pixmap)
        layout.addWidget(self.crop_widget)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 12px; color: #64748B; padding: 5px;")
        layout.addWidget(self.info_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self.reset_crop)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #DC2626; }
            QPushButton:pressed { background-color: #B91C1C; }
        """)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Batal")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E2E3E;
                color: #F3F4F6;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #3E3E52; }
            QPushButton:pressed { background-color: #1F1F2E; }
        """)
        button_layout.addWidget(cancel_btn)
        
        # Crop button
        crop_btn = QPushButton("Crop")
        crop_btn.setCursor(Qt.PointingHandCursor)
        crop_btn.clicked.connect(self.perform_crop)
        crop_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:pressed { background-color: #047857; }
        """)
        button_layout.addWidget(crop_btn)
        
        layout.addLayout(button_layout)
        
        # Set default
        self.on_size_changed("Free (Manual)")
    
    def on_size_changed(self, size_text):
        """Handle perubahan ukuran crop"""
        aspect_ratio = self.ASPECT_RATIOS.get(size_text)
        self.crop_widget.set_aspect_ratio(aspect_ratio)
        
        if aspect_ratio:
            self.info_label.setText(f"Mode: {size_text} - Aspect ratio akan dipertahankan")
        else:
            self.info_label.setText("Mode: Free crop - Anda dapat memilih area bebas")
    
    def reset_crop(self):
        """Reset crop selection"""
        self.crop_widget.crop_rect = QRect()
        self.crop_widget.update_display()
    
    def perform_crop(self):
        """Perform the actual crop operation"""
        crop_rect = self.crop_widget.get_crop_rect()
        
        if crop_rect.isNull() or crop_rect.width() < 5 or crop_rect.height() < 5:
            QMessageBox.warning(self, "Peringatan", "Pilih area yang ingin di-crop terlebih dahulu!\nArea crop minimal 5x5 pixel.")
            return
        
        # Pastikan crop rect dalam bounds pixmap
        pixmap_rect = QRect(0, 0, self.pixmap.width(), self.pixmap.height())
        crop_rect = crop_rect.intersected(pixmap_rect)
        
        if crop_rect.isEmpty():
            QMessageBox.warning(self, "Peringatan", "Area crop tidak valid!")
            return
        
        # Simpan hasil
        self.crop_rect = crop_rect
        self.cropped_pixmap = self.pixmap.copy(crop_rect)
        self.accept()
    
    def get_crop_result(self):
        """Return tuple hasil (cropped_pixmap, crop_rect)"""
        return self.cropped_pixmap, getattr(self, 'crop_rect', None)