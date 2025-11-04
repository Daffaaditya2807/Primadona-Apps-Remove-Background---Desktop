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
        
        # Untuk resize dan move functionality
        self.is_resizing = False
        self.is_moving = False
        self.resize_handle = None
        self.move_start_point = None
        self.handle_size = 8
        
        # Resize handles: 0=top-left, 1=top-right, 2=bottom-left, 3=bottom-right
        # 4=top, 5=bottom, 6=left, 7=right
        self.resize_handles = []
        
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
                
                # Gambar resize handles
                self.draw_resize_handles(painter)
            
            painter.end()
            self.setPixmap(display_pixmap)
    
    def draw_resize_handles(self, painter):
        """Gambar resize handles di sekitar crop rectangle"""
        if self.crop_rect.isNull():
            return
            
        self.resize_handles = []
        handle_size = self.handle_size
        
        # Warna handle
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        
        rect = self.crop_rect
        
        # Corner handles
        handles = [
            (rect.left() - handle_size//2, rect.top() - handle_size//2),      # top-left
            (rect.right() - handle_size//2, rect.top() - handle_size//2),     # top-right
            (rect.left() - handle_size//2, rect.bottom() - handle_size//2),   # bottom-left
            (rect.right() - handle_size//2, rect.bottom() - handle_size//2),  # bottom-right
            (rect.center().x() - handle_size//2, rect.top() - handle_size//2),    # top
            (rect.center().x() - handle_size//2, rect.bottom() - handle_size//2), # bottom
            (rect.left() - handle_size//2, rect.center().y() - handle_size//2),   # left
            (rect.right() - handle_size//2, rect.center().y() - handle_size//2)   # right
        ]
        
        for i, (x, y) in enumerate(handles):
            handle_rect = QRect(x, y, handle_size, handle_size)
            painter.drawRect(handle_rect)
            self.resize_handles.append(handle_rect)
    
    def get_handle_at_point(self, point):
        """Return handle index jika point berada di handle, -1 jika tidak"""
        for i, handle in enumerate(self.resize_handles):
            if handle.contains(point):
                return i
        return -1
    
    def get_cursor_for_handle(self, handle_index):
        """Return cursor yang sesuai untuk handle"""
        cursors = [
            Qt.SizeFDiagCursor,  # top-left
            Qt.SizeBDiagCursor,  # top-right
            Qt.SizeBDiagCursor,  # bottom-left
            Qt.SizeFDiagCursor,  # bottom-right
            Qt.SizeVerCursor,    # top
            Qt.SizeVerCursor,    # bottom
            Qt.SizeHorCursor,    # left
            Qt.SizeHorCursor     # right
        ]
        return cursors[handle_index] if 0 <= handle_index < len(cursors) else Qt.ArrowCursor
    
    def can_move_crop(self, point):
        """Check apakah point berada di dalam crop area untuk moving"""
        if self.crop_rect.isNull():
            return False
        return self.crop_rect.contains(point)
    
    def move_crop_rect(self, delta_x, delta_y):
        """Move crop rectangle dengan delta yang diberikan"""
        if self.crop_rect.isNull():
            return
            
        pixmap_bounds = self.get_pixmap_bounds()
        new_rect = self.crop_rect.translated(delta_x, delta_y)
        
        # Pastikan crop rect tetap dalam bounds
        if new_rect.left() < 0:
            new_rect.moveLeft(0)
        if new_rect.top() < 0:
            new_rect.moveTop(0)
        if new_rect.right() > pixmap_bounds.width():
            new_rect.moveRight(pixmap_bounds.width())
        if new_rect.bottom() > pixmap_bounds.height():
            new_rect.moveBottom(pixmap_bounds.height())
            
        self.crop_rect = new_rect
    
    def resize_crop_rect(self, handle_index, new_point):
        """Resize crop rectangle berdasarkan handle yang di-drag"""
        if self.crop_rect.isNull():
            return
            
        pixmap_bounds = self.get_pixmap_bounds()
        
        # Batasi new_point dalam pixmap bounds
        new_x = max(0, min(new_point.x(), pixmap_bounds.width()))
        new_y = max(0, min(new_point.y(), pixmap_bounds.height()))
        
        rect = self.crop_rect
        
        # Handle resize berdasarkan handle yang di-drag
        if handle_index == 0:  # top-left
            new_width = rect.right() - new_x
            new_height = rect.bottom() - new_y
            if self.aspect_ratio and new_height > 0:
                if new_width / new_height > self.aspect_ratio:
                    new_width = int(new_height * self.aspect_ratio)
                else:
                    new_height = int(new_width / self.aspect_ratio)
            self.crop_rect = QRect(rect.right() - new_width, rect.bottom() - new_height, new_width, new_height)
            
        elif handle_index == 1:  # top-right
            new_width = new_x - rect.left()
            new_height = rect.bottom() - new_y
            if self.aspect_ratio and new_height > 0:
                if new_width / new_height > self.aspect_ratio:
                    new_width = int(new_height * self.aspect_ratio)
                else:
                    new_height = int(new_width / self.aspect_ratio)
            self.crop_rect = QRect(rect.left(), rect.bottom() - new_height, new_width, new_height)
            
        elif handle_index == 2:  # bottom-left
            new_width = rect.right() - new_x
            new_height = new_y - rect.top()
            if self.aspect_ratio and new_height > 0:
                if new_width / new_height > self.aspect_ratio:
                    new_width = int(new_height * self.aspect_ratio)
                else:
                    new_height = int(new_width / self.aspect_ratio)
            self.crop_rect = QRect(rect.right() - new_width, rect.top(), new_width, new_height)
            
        elif handle_index == 3:  # bottom-right
            new_width = new_x - rect.left()
            new_height = new_y - rect.top()
            if self.aspect_ratio and new_height > 0:
                if new_width / new_height > self.aspect_ratio:
                    new_width = int(new_height * self.aspect_ratio)
                else:
                    new_height = int(new_width / self.aspect_ratio)
            self.crop_rect = QRect(rect.left(), rect.top(), new_width, new_height)
            
        elif handle_index == 4:  # top
            new_height = rect.bottom() - new_y
            if self.aspect_ratio:
                new_width = int(new_height * self.aspect_ratio)
                new_x = rect.center().x() - new_width // 2
                self.crop_rect = QRect(new_x, rect.bottom() - new_height, new_width, new_height)
            else:
                self.crop_rect = QRect(rect.left(), rect.bottom() - new_height, rect.width(), new_height)
                
        elif handle_index == 5:  # bottom
            new_height = new_y - rect.top()
            if self.aspect_ratio:
                new_width = int(new_height * self.aspect_ratio)
                new_x = rect.center().x() - new_width // 2
                self.crop_rect = QRect(new_x, rect.top(), new_width, new_height)
            else:
                self.crop_rect = QRect(rect.left(), rect.top(), rect.width(), new_height)
                
        elif handle_index == 6:  # left
            new_width = rect.right() - new_x
            if self.aspect_ratio:
                new_height = int(new_width / self.aspect_ratio)
                new_y = rect.center().y() - new_height // 2
                self.crop_rect = QRect(rect.right() - new_width, new_y, new_width, new_height)
            else:
                self.crop_rect = QRect(rect.right() - new_width, rect.top(), new_width, rect.height())
                
        elif handle_index == 7:  # right
            new_width = new_x - rect.left()
            if self.aspect_ratio:
                new_height = int(new_width / self.aspect_ratio)
                new_y = rect.center().y() - new_height // 2
                self.crop_rect = QRect(rect.left(), new_y, new_width, new_height)
            else:
                self.crop_rect = QRect(rect.left(), rect.top(), new_width, rect.height())
        
        # Pastikan minimal size
        min_size = 10
        if self.crop_rect.width() < min_size:
            self.crop_rect.setWidth(min_size)
        if self.crop_rect.height() < min_size:
            self.crop_rect.setHeight(min_size)
        
        # Pastikan dalam bounds
        if self.crop_rect.left() < 0:
            self.crop_rect.moveLeft(0)
        if self.crop_rect.top() < 0:
            self.crop_rect.moveTop(0)
        if self.crop_rect.right() > pixmap_bounds.width():
            self.crop_rect.moveRight(pixmap_bounds.width())
        if self.crop_rect.bottom() > pixmap_bounds.height():
            self.crop_rect.moveBottom(pixmap_bounds.height())
    
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
        """Handle mouse press untuk mulai crop selection atau adjustment"""
        if event.button() == Qt.LeftButton and self.scaled_pixmap:
            pixmap_bounds = self.get_pixmap_bounds()
            
            # Pastikan click dalam bounds pixmap
            if pixmap_bounds.contains(event.pos()):
                # Konversi ke koordinat pixmap
                pixmap_point = event.pos() - pixmap_bounds.topLeft()
                
                # Cek apakah click pada resize handle
                if not self.crop_rect.isNull():
                    handle_index = self.get_handle_at_point(pixmap_point)
                    if handle_index >= 0:
                        self.is_resizing = True
                        self.resize_handle = handle_index
                        self.setCursor(self.get_cursor_for_handle(handle_index))
                        return
                    
                    # Cek apakah click untuk move crop
                    if self.can_move_crop(pixmap_point):
                        self.is_moving = True
                        self.move_start_point = pixmap_point
                        self.setCursor(Qt.SizeAllCursor)
                        return
                
                # Mulai crop selection baru
                self.start_point = event.pos()
                self.is_cropping = True
                self.crop_rect = QRect()
                # Force update untuk clear previous selection
                self.update_display()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move untuk update crop selection atau adjustment"""
        pixmap_bounds = self.get_pixmap_bounds()
        
        if not pixmap_bounds.contains(event.pos()):
            self.setCursor(Qt.ArrowCursor)
            return
            
        pixmap_point = event.pos() - pixmap_bounds.topLeft()
        
        if self.is_resizing and self.resize_handle is not None:
            # Handle resize
            self.resize_crop_rect(self.resize_handle, pixmap_point)
            self.update_display()
            
        elif self.is_moving and self.move_start_point:
            # Handle move
            delta_x = pixmap_point.x() - self.move_start_point.x()
            delta_y = pixmap_point.y() - self.move_start_point.y()
            self.move_crop_rect(delta_x, delta_y)
            self.move_start_point = pixmap_point
            self.update_display()
            
        elif self.is_cropping and self.start_point:
            # Handle crop selection
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
            top = max(0, min(top, pixmap_bounds.height() - top))
            
            # Pastikan width dan height tidak melebihi bounds
            width = min(width, pixmap_bounds.width() - left)
            height = min(height, pixmap_bounds.height() - top)
            
            self.crop_rect = QRect(left, top, width, height)
            self.update_display()
            
        else:
            # Update cursor berdasarkan posisi mouse
            if not self.crop_rect.isNull():
                handle_index = self.get_handle_at_point(pixmap_point)
                if handle_index >= 0:
                    self.setCursor(self.get_cursor_for_handle(handle_index))
                elif self.can_move_crop(pixmap_point):
                    self.setCursor(Qt.SizeAllCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release untuk selesai crop selection atau adjustment"""
        if event.button() == Qt.LeftButton:
            self.is_cropping = False
            self.is_resizing = False
            self.is_moving = False
            self.resize_handle = None
            self.move_start_point = None
            self.setCursor(Qt.ArrowCursor)
    
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