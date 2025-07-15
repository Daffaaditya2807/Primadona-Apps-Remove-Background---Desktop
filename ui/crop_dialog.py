# crop_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor

class CropWidget(QLabel):
    """Widget untuk menampilkan gambar dan menangani crop selection"""
    
    def __init__(self, pixmap):
        super().__init__()
        self.original_pixmap = pixmap
        self.scaled_pixmap = None
        self.crop_rect = QRect()
        self.start_point = None
        self.end_point = None
        self.is_cropping = False
        self.aspect_ratio = None  # Untuk fixed aspect ratio
        
        self.setMinimumSize(400, 300)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        
        # Scale pixmap untuk ditampilkan
        self.scale_and_display()
    
    def set_aspect_ratio(self, ratio):
        """Set fixed aspect ratio untuk crop"""
        self.aspect_ratio = ratio
        self.crop_rect = QRect()  # Reset crop rect
        self.update_display()
        
    def scale_and_display(self):
        """Scale pixmap sesuai ukuran widget"""
        if self.original_pixmap:
            self.scaled_pixmap = self.original_pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.update_display()
    
    def update_display(self):
        """Update tampilan dengan crop rectangle"""
        if self.scaled_pixmap:
            # Buat pixmap baru untuk menggambar crop rectangle
            display_pixmap = QPixmap(self.scaled_pixmap)
            painter = QPainter(display_pixmap)
            
            # Gambar crop rectangle jika ada
            if not self.crop_rect.isNull():
                pen = QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
                painter.setPen(pen)
                painter.drawRect(self.crop_rect)
                
                # Tambahkan overlay semi-transparent di luar crop area
                overlay = QPixmap(display_pixmap.size())
                overlay.fill(QColor(0, 0, 0, 100))  # Semi-transparent black
                
                overlay_painter = QPainter(overlay)
                overlay_painter.setCompositionMode(QPainter.CompositionMode_DestinationOut)
                overlay_painter.fillRect(self.crop_rect, QColor(0, 0, 0, 255))
                overlay_painter.end()
                
                painter.drawPixmap(0, 0, overlay)
            
            painter.end()
            self.setPixmap(display_pixmap)
    
    def get_pixmap_bounds(self):
        """Get bounds pixmap dalam widget"""
        if not self.scaled_pixmap:
            return QRect()
        
        widget_rect = self.rect()
        pixmap_rect = self.scaled_pixmap.rect()
        
        # Hitung offset untuk center alignment
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2
        
        return QRect(x_offset, y_offset, pixmap_rect.width(), pixmap_rect.height())
    
    def mousePressEvent(self, event):
        """Handle mouse press untuk mulai crop selection"""
        if event.button() == Qt.LeftButton and self.scaled_pixmap:
            pixmap_bounds = self.get_pixmap_bounds()
            
            # Pastikan click dalam bounds pixmap
            if pixmap_bounds.contains(event.pos()):
                self.start_point = event.pos()
                self.is_cropping = True
                self.crop_rect = QRect()
                # Force update untuk clear previous selection
                self.update_display()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move untuk update crop selection"""
        if self.is_cropping and self.start_point:
            pixmap_bounds = self.get_pixmap_bounds()
            
            # Batasi end point dalam pixmap bounds
            end_x = max(pixmap_bounds.left(), 
                       min(event.pos().x(), pixmap_bounds.right()))
            end_y = max(pixmap_bounds.top(), 
                       min(event.pos().y(), pixmap_bounds.bottom()))
            
            self.end_point = event.pos()
            
            # Hitung crop rectangle
            start_x = self.start_point.x() - pixmap_bounds.left()
            start_y = self.start_point.y() - pixmap_bounds.top()
            end_x = end_x - pixmap_bounds.left()
            end_y = end_y - pixmap_bounds.top()
            
            width = abs(end_x - start_x)
            height = abs(end_y - start_y)
            
            # Pastikan minimal size untuk menghindari division by zero
            min_size = 5
            if width < min_size:
                width = min_size
            if height < min_size:
                height = min_size
            
            # Apply aspect ratio constraint jika ada
            if self.aspect_ratio and height > 0:
                if width / height > self.aspect_ratio:
                    width = int(height * self.aspect_ratio)
                else:
                    height = int(width / self.aspect_ratio)
            
            # Hitung posisi berdasarkan start point dan arah drag
            left = start_x if end_x > start_x else start_x - width
            top = start_y if end_y > start_y else start_y - height
            
            # Pastikan crop rect dalam bounds
            left = max(0, min(left, pixmap_bounds.width() - width))
            top = max(0, min(top, pixmap_bounds.height() - height))
            
            # Pastikan width dan height tidak melebihi bounds
            width = min(width, pixmap_bounds.width() - left)
            height = min(height, pixmap_bounds.height() - top)
            
            self.crop_rect = QRect(left, top, width, height)
            self.update_display()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release untuk selesai crop selection"""
        if event.button() == Qt.LeftButton:
            self.is_cropping = False
    
    def get_crop_rect(self):
        """Return crop rectangle dalam koordinat pixmap asli"""
        if self.crop_rect.isNull() or not self.scaled_pixmap:
            return QRect()
        
        # Hitung scale factor
        scale_x = self.original_pixmap.width() / self.scaled_pixmap.width()
        scale_y = self.original_pixmap.height() / self.scaled_pixmap.height()
        
        # Convert ke koordinat pixmap asli
        return QRect(
            int(self.crop_rect.x() * scale_x),
            int(self.crop_rect.y() * scale_y),
            int(self.crop_rect.width() * scale_x),
            int(self.crop_rect.height() * scale_y)
        )
    
    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        self.scale_and_display()


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
        
        layout = QVBoxLayout(self)
        
        # Instruksi
        instruction = QLabel("Pilih ukuran crop dan klik-drag untuk memilih area yang ingin di-crop")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("font-size: 14px; color: #666; padding: 10px;")
        layout.addWidget(instruction)
        
        # Size selection
        size_layout = QHBoxLayout()
        size_label = QLabel("Ukuran Crop:")
        size_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        size_layout.addWidget(size_label)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(list(self.ASPECT_RATIOS.keys()))
        self.size_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 14px;
                min-width: 150px;
            }
        """)
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
        self.info_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        layout.addWidget(self.info_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_crop)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                min-width: 80px;
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
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #7F8C8D; }
            QPushButton:pressed { background-color: #6C7B7D; }
        """)
        button_layout.addWidget(cancel_btn)
        
        # Crop button
        crop_btn = QPushButton("Crop")
        crop_btn.clicked.connect(self.perform_crop)
        crop_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:pressed { background-color: #1E8449; }
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
        
        # Crop pixmap
        self.cropped_pixmap = self.pixmap.copy(crop_rect)
        self.accept()
    
    def get_cropped_pixmap(self):
        """Return hasil crop"""
        return self.cropped_pixmap