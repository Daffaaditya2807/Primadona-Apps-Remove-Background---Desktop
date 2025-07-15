# background_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGridLayout, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush

class ColorButton(QPushButton):
    """Button untuk memilih warna background"""
    
    def __init__(self, color_name, color_value, parent=None):
        super().__init__(parent)
        self.color_name = color_name
        self.color_value = color_value
        self.setFixedSize(80, 80)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_value};
                border: 3px solid #ccc;
                border-radius: 10px;
                font-weight: bold;
                color: {'white' if color_name in ['Merah', 'Biru'] else 'black'};
            }}
            QPushButton:hover {{
                border: 3px solid #3498DB;
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                border: 3px solid #2874A6;
            }}
        """)
        self.setText(color_name)
        self.setCursor(Qt.PointingHandCursor)

class BackgroundPreview(QLabel):
    """Widget untuk preview background yang dipilih"""
    
    def __init__(self, original_pixmap):
        super().__init__()
        self.original_pixmap = original_pixmap
        self.preview_pixmap = None
        self.setFixedSize(300, 350)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        # Tampilkan gambar asli tanpa background
        self.update_preview(None)
    
    def update_preview(self, background_color):
        """Update preview dengan background color yang dipilih"""
        if not self.original_pixmap:
            return
        
        # Buat pixmap baru untuk preview
        preview_size = self.size()
        self.preview_pixmap = QPixmap(preview_size)
        
        if background_color:
            self.preview_pixmap.fill(QColor(background_color))
        else:
            # Default transparent (checkerboard pattern)
            self.preview_pixmap.fill(QColor(255, 255, 255))
        
        # Scale gambar untuk preview
        scaled_original = self.original_pixmap.scaled(
            preview_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        # Hitung posisi center
        x = (preview_size.width() - scaled_original.width()) // 2
        y = (preview_size.height() - scaled_original.height()) // 2
        
        # Gambar ke preview pixmap
        painter = QPainter(self.preview_pixmap)
        painter.drawPixmap(x, y, scaled_original)
        painter.end()
        
        self.setPixmap(self.preview_pixmap)

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
        self.setFixedSize(550, 600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("Pilih Warna Background")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                padding: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # Content layout (preview + controls)
        content_layout = QHBoxLayout()
        
        # Preview area
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        preview_layout.addWidget(preview_label)
        
        self.preview_widget = BackgroundPreview(self.transparent_pixmap)
        preview_layout.addWidget(self.preview_widget)
        content_layout.addLayout(preview_layout)
        
        # Controls area
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        
        # Color selection
        color_label = QLabel("Pilih Warna:")
        color_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        controls_layout.addWidget(color_label)
        
        # Color buttons grid
        color_grid = QGridLayout()
        color_grid.setSpacing(10)
        
        row, col = 0, 0
        for color_name, color_value in self.BACKGROUND_COLORS.items():
            color_btn = ColorButton(color_name, color_value)
            color_btn.clicked.connect(lambda checked, name=color_name, value=color_value: 
                                    self.on_color_selected(name, value))
            color_grid.addWidget(color_btn, row, col)
            
            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1
        
        color_frame = QFrame()
        color_frame.setLayout(color_grid)
        controls_layout.addWidget(color_frame)
        
        # Selected color info
        self.selected_info = QLabel("Belum ada warna yang dipilih")
        self.selected_info.setAlignment(Qt.AlignCenter)
        self.selected_info.setStyleSheet("""
            QLabel {
                background-color: #ECF0F1;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                color: #34495E;
            }
        """)
        controls_layout.addWidget(self.selected_info)
        
        controls_layout.addStretch()
        content_layout.addLayout(controls_layout)
        
        main_layout.addLayout(content_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_background)
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
        self.apply_btn.clicked.connect(self.apply_background)
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
    
    def on_color_selected(self, color_name, color_value):
        """Handle pemilihan warna"""
        self.selected_color = color_value
        self.preview_widget.update_preview(color_value)
        self.selected_info.setText(f"Warna dipilih: {color_name}")
        self.selected_info.setStyleSheet(f"""
            QLabel {{
                background-color: {color_value};
                border: 2px solid #2C3E50;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                color: {'white' if color_name in ['Merah', 'Biru'] else 'black'};
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
                background-color: #ECF0F1;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                color: #34495E;
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