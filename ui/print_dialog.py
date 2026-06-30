from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QSpinBox, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

class PrintDialog(QDialog):
    """Dialog untuk mengatur dan mencetak foto ke kertas A4"""
    
    # Ukuran standar pasfoto dalam cm (Lebar x Tinggi)
    PHOTO_SIZES = {
        "2 x 3 cm": (2.0, 3.0),
        "3 x 4 cm": (3.0, 4.0),
        "4 x 6 cm": (4.0, 6.0),
        "5 x 7 cm (2R)": (5.0, 7.0),
        "Kustom (Seluruh Kertas)": (21.0, 29.7)
    }
    
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("Cetak Foto (Kertas A4)")
        self.setFixedSize(700, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #1E293B;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                color: #334155;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left Panel - Settings
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Pengaturan Cetak
        settings_group = QGroupBox("Pengaturan Cetak")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(15)
        
        # Ukuran Foto
        size_layout = QVBoxLayout()
        size_label = QLabel("Ukuran Foto:")
        size_label.setStyleSheet("font-weight: bold;")
        self.size_combo = QComboBox()
        self.size_combo.addItems(self.PHOTO_SIZES.keys())
        self.size_combo.setCurrentText("3 x 4 cm")
        self.size_combo.currentTextChanged.connect(self.update_preview)
        self.size_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                background: white;
            }
        """)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        settings_layout.addLayout(size_layout)
        
        # Jumlah Foto
        qty_layout = QVBoxLayout()
        qty_label = QLabel("Jumlah Foto:")
        qty_label.setStyleSheet("font-weight: bold;")
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 100)
        self.qty_spin.setValue(4)
        self.qty_spin.valueChanged.connect(self.update_preview)
        self.qty_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                background: white;
            }
        """)
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(self.qty_spin)
        settings_layout.addLayout(qty_layout)
        
        left_panel.addWidget(settings_group)
        left_panel.addStretch()
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        self.print_btn = QPushButton("Cetak Sekarang")
        self.print_btn.setCursor(Qt.PointingHandCursor)
        self.print_btn.clicked.connect(self.print_photo)
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #2563EB; }
            QPushButton:pressed { background-color: #1D4ED8; }
        """)
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        
        btn_layout.addWidget(self.print_btn)
        btn_layout.addWidget(cancel_btn)
        left_panel.addLayout(btn_layout)
        
        main_layout.addLayout(left_panel, 1)
        
        # Right Panel - Preview
        right_panel = QVBoxLayout()
        preview_label = QLabel("Preview Kertas A4:")
        preview_label.setStyleSheet("font-weight: bold; color: #64748B;")
        right_panel.addWidget(preview_label)
        
        self.preview_area = QLabel()
        self.preview_area.setAlignment(Qt.AlignCenter)
        self.preview_area.setStyleSheet("""
            QLabel {
                background-color: #E2E8F0;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }
        """)
        # Aspect ratio A4 (210 x 297 mm)
        self.preview_area.setFixedSize(350, 495) 
        right_panel.addWidget(self.preview_area)
        
        main_layout.addLayout(right_panel, 2)
        
        self.update_preview()
        
    def _generate_layout(self, painter, rect_width, rect_height, dpi):
        """Generate layout foto pada painter/kertas"""
        size_name = self.size_combo.currentText()
        w_cm, h_cm = self.PHOTO_SIZES[size_name]
        qty = self.qty_spin.value()
        
        # Konversi cm ke piksel berdasarkan DPI
        # 1 inch = 2.54 cm
        w_px = int((w_cm / 2.54) * dpi)
        h_px = int((h_cm / 2.54) * dpi)
        
        # Margin dan spacing
        margin = int((1.0 / 2.54) * dpi) # 1 cm margin
        spacing = int((0.5 / 2.54) * dpi) # 0.5 cm spacing
        
        # Hitung muat berapa kolom dan baris
        avail_w = rect_width - (2 * margin)
        avail_h = rect_height - (2 * margin)
        
        cols = max(1, (avail_w + spacing) // (w_px + spacing))
        
        # Scale pixmap ke ukuran yang diminta
        scaled_photo = self.pixmap.scaled(w_px, h_px, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        
        count = 0
        for i in range(qty):
            col = count % cols
            row = count // cols
            
            x = margin + col * (w_px + spacing)
            y = margin + row * (h_px + spacing)
            
            if y + h_px > rect_height - margin:
                # Tidak muat di satu halaman, hentikan atau butuh multi-page
                # Untuk sederhana, kita potong di halaman 1
                break
                
            # Gambar foto
            painter.drawPixmap(int(x), int(y), scaled_photo)
            
            # Gambar border tipis hitam untuk memudahkan pemotongan
            pen = painter.pen()
            painter.setPen(QColor("#000000"))
            painter.drawRect(int(x), int(y), w_px, h_px)
            painter.setPen(pen)
            
            count += 1
            
        return count

    def update_preview(self):
        """Update tampilan preview layout"""
        # Resolusi virtual untuk preview (DPI rendah agar tidak berat)
        preview_dpi = 50
        # A4 in cm = 21.0 x 29.7
        pw = int((21.0 / 2.54) * preview_dpi)
        ph = int((29.7 / 2.54) * preview_dpi)
        
        preview_img = QPixmap(pw, ph)
        preview_img.fill(Qt.white)
        
        painter = QPainter(preview_img)
        count = self._generate_layout(painter, pw, ph, preview_dpi)
        painter.end()
        
        # Scale preview image to fit the preview area
        scaled_preview = preview_img.scaled(
            self.preview_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview_area.setPixmap(scaled_preview)
        
        if count < self.qty_spin.value():
            self.print_btn.setToolTip("Peringatan: Jumlah foto melebihi kapasitas 1 halaman A4.")
        else:
            self.print_btn.setToolTip("")

    def print_photo(self):
        """Proses cetak ke printer fisik atau PDF"""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter()
            painter.begin(printer)
            
            # Area kertas yang bisa di-print
            rect = printer.pageRect()
            
            # Gunakan DPI printer untuk resolusi yang tajam
            dpi = printer.resolution()
            
            self._generate_layout(painter, rect.width(), rect.height(), dpi)
            
            painter.end()
            self.accept()
