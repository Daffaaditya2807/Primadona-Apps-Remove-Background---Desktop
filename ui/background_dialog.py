# background_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor
from ui.widgets import ColorButton

class BackgroundPreview(QLabel):
    """Widget untuk preview background yang dipilih"""
    
    def __init__(self, original_pixmap):
        super().__init__()
        self.original_pixmap = original_pixmap
        self.preview_pixmap = None
        self.setFixedSize(300, 320)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
        """)
        
        # Tampilkan gambar asli tanpa background
        self.update_preview(None)
    
    def update_preview(self, background_color):
        """Update preview dengan background color yang dipilih"""
        if not self.original_pixmap:
            return
        
        # Buat pixmap sementara seukuran gambar asli
        # Ini memastikan preview persis sama dengan hasil akhir
        temp_pixmap = QPixmap(self.original_pixmap.size())
        
        # Fill dengan warna background jika ada, jika tidak biarkan transparan
        if background_color:
            temp_pixmap.fill(QColor(background_color))
        else:
            temp_pixmap.fill(Qt.transparent)
            
        # Gambar original yang transparan di atas background
        painter = QPainter(temp_pixmap)
        painter.drawPixmap(0, 0, self.original_pixmap)
        painter.end()
        
        # Buat pixmap untuk background area preview agar tetap bersih
        preview_size = self.size()
        self.preview_pixmap = QPixmap(preview_size)
        
        # Fill dengan warna transparan/putih untuk area kosong
        self.preview_pixmap.fill(Qt.transparent)
        
        # Scale hasil komposisi
        scaled_result = temp_pixmap.scaled(
            preview_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        # Hitung posisi center
        x = (preview_size.width() - scaled_result.width()) // 2
        y = (preview_size.height() - scaled_result.height()) // 2
        
        # Gambar ke preview pixmap
        painter = QPainter(self.preview_pixmap)
        
        # Jika belum ada warna, beri efek checkerboard (opsional, tapi lebih baik)
        if not background_color:
            self._draw_checkerboard(painter, x, y, scaled_result.width(), scaled_result.height())
            
        painter.drawPixmap(x, y, scaled_result)
        painter.end()
        
        self.setPixmap(self.preview_pixmap)
        
    def _draw_checkerboard(self, painter, x, y, width, height):
        """Gambar pola checkerboard untuk merepresentasikan transparansi"""
        square_size = 10
        for i in range(x, x + width, square_size):
            for j in range(y, y + height, square_size):
                if ((i - x) // square_size + (j - y) // square_size) % 2 == 0:
                    painter.fillRect(i, j, min(square_size, x + width - i), min(square_size, y + height - j), QColor("#E5E7EB"))
                else:
                    painter.fillRect(i, j, min(square_size, x + width - i), min(square_size, y + height - j), QColor("#FFFFFF"))

class BackgroundChangeDialog(QDialog):
    """Dialog untuk mengubah background"""
    
    # Definisi warna background
    BACKGROUND_COLORS = {
        "Merah": "#E74C3C",
        "Kuning": "#F1C40F", 
        "Biru": "#3498DB",
        "Abu-abu": "#95A5A6"
    }
    
    def __init__(self, transparent_pixmap, parent=None):
        super().__init__(parent)
        self.transparent_pixmap = transparent_pixmap
        self.selected_color = None
        self.result_pixmap = None
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("Ubah Background")
        self.setModal(True)
        self.setFixedSize(500, 680)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #1E293B;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(24, 20, 24, 20)
        
        # Title
        title = QLabel("Pilih Warna Background")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 800;
                color: #1E293B;
                padding: 5px;
            }
        """)
        main_layout.addWidget(title)
        
        # Preview area
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(5)
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #64748B;")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_label)
        
        self.preview_widget = BackgroundPreview(self.transparent_pixmap)
        preview_layout.addWidget(self.preview_widget, 0, Qt.AlignCenter)
        main_layout.addLayout(preview_layout)
        
        # Controls area
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)
        
        color_label = QLabel("Pilih Warna:")
        color_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #64748B;")
        color_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(color_label)
        
        # Color buttons row
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(12)
        colors_layout.addStretch()
        for color_name, color_value in self.BACKGROUND_COLORS.items():
            color_btn = ColorButton(color_name, color_value)
            color_btn.clicked.connect(lambda checked, name=color_name, value=color_value: 
                                    self.on_color_selected(name, value))
            colors_layout.addWidget(color_btn)
        colors_layout.addStretch()
        controls_layout.addLayout(colors_layout)
        
        # Selected color info
        self.selected_info = QLabel("Belum ada warna yang dipilih")
        self.selected_info.setAlignment(Qt.AlignCenter)
        self.selected_info.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 12px;
                font-size: 12px;
                font-weight: 500;
                color: #64748B;
                min-width: 280px;
            }
        """)
        
        info_layout = QHBoxLayout()
        info_layout.addStretch()
        info_layout.addWidget(self.selected_info)
        info_layout.addStretch()
        controls_layout.addLayout(info_layout)
        
        main_layout.addLayout(controls_layout)
        main_layout.addSpacing(10)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self.reset_background)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                min-width: 90px;
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
                background-color: #F1F5F9;
                color: #334155;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                min-width: 90px;
            }
            QPushButton:hover { background-color: #E2E8F0; }
            QPushButton:pressed { background-color: #CBD5E1; }
        """)
        button_layout.addWidget(cancel_btn)
        
        # Apply button
        self.apply_btn = QPushButton("Terapkan")
        self.apply_btn.setCursor(Qt.PointingHandCursor)
        self.apply_btn.clicked.connect(self.apply_background)
        self.apply_btn.setEnabled(False)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                min-width: 90px;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:pressed { background-color: #047857; }
            QPushButton:disabled { background-color: #F8FAFC; color: #94A3B8; border: 1px solid #CBD5E1; }
        """)
        button_layout.addWidget(self.apply_btn)
        
        main_layout.addLayout(button_layout)
    
    def on_color_selected(self, color_name, color_value):
        """Handle pemilihan warna"""
        self.selected_color = color_value
        self.preview_widget.update_preview(color_value)
        self.selected_info.setText(f"Warna dipilih: {color_name}")
        self.selected_info.setStyleSheet(f"""
            QLabel {{
                background-color: {color_value};
                border: 2px solid #4F46E5;
                border-radius: 6px;
                padding: 12px;
                font-size: 12px;
                font-weight: bold;
                color: {'white' if color_name in ['Merah', 'Biru'] else '#1E293B'};
            }}
        """)
        self.apply_btn.setEnabled(True)
    
    def reset_background(self):
        """Reset pilihan background"""
        self.selected_color = None
        self.preview_widget.update_preview(None)
        self.selected_info.setText("Belum ada warna yang dipilih")
        self.selected_info.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 12px;
                font-size: 12px;
                font-weight: 500;
                color: #64748B;
            }
        """)
        self.apply_btn.setEnabled(False)
    
    def apply_background(self):
        """Terapkan background yang dipilih"""
        if not self.selected_color or not self.transparent_pixmap:
            return
        
        # Buat pixmap hasil dengan background baru
        result_size = self.transparent_pixmap.size()
        self.result_pixmap = QPixmap(result_size)
        
        # Fill dengan warna background
        self.result_pixmap.fill(QColor(self.selected_color))
        
        # Gambar gambar transparent di atas background
        painter = QPainter(self.result_pixmap)
        painter.drawPixmap(0, 0, self.transparent_pixmap)
        painter.end()
        
        self.accept()
    
    def get_result_pixmap(self):
        """Return hasil dengan background baru"""
        return self.result_pixmap