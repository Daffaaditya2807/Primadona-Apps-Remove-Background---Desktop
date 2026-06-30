from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal

class ImageLabel(QLabel):
    file_dropped = pyqtSignal(str)

    def __init__(self, width=250, height=300):
        super().__init__()
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)

    def set_image(self, pixmap):
        if pixmap:
            scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
        else:
            self.setPixmap(QPixmap())

    def paintEvent(self, event):
        if self.pixmap() and not self.pixmap().isNull():
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw card background
        painter.fillRect(self.rect(), QColor("#FFFFFF"))
        
        # Draw dashed border
        pen = QPen(QColor("#CBD5E1"), 2, Qt.DashLine)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(4, 4, -4, -4), 8, 8)
        
        # Draw drag and drop icon/text
        painter.setPen(QColor("#64748B"))
        font = painter.font()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        painter.setFont(font)
        
        # Draw simulated cloud icon arrow using lines
        cx = self.width() // 2
        cy = self.height() // 2 - 20
        painter.setPen(QPen(QColor("#4F46E5"), 2, Qt.SolidLine))
        painter.drawLine(cx, cy - 12, cx, cy + 8)
        painter.drawLine(cx, cy - 12, cx - 6, cy - 6)
        painter.drawLine(cx, cy - 12, cx + 6, cy - 6)
        # Cloud base arcs
        painter.drawArc(cx - 15, cy, 30, 16, 0 * 16, 180 * 16)
        
        # Text under icon
        painter.setPen(QColor("#64748B"))
        painter.drawText(self.rect().adjusted(10, self.height() // 2 + 10, -10, -10), 
                         Qt.AlignHCenter | Qt.AlignTop, 
                         "Seret foto ke sini\natau klik tombol")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    background-color: #F8FAFC;
                    border: 2px solid #4F46E5;
                    border-radius: 8px;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        self.update()

    def dropEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        self.update()
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.file_dropped.emit(file_path)
                break

class StyledButton(QPushButton):
    def __init__(self, text, style_type="primary"):
        super().__init__(text)
        if isinstance(style_type, bool):
            style_type = "primary" if style_type else "danger"
        self.setStyleType(style_type)
        self.setCursor(Qt.PointingHandCursor)

    def setStyleType(self, style_type="primary"):
        if style_type == "primary":
            # Modern Indigo Light Accent
            bg, hover, pressed, text_color = "#4F46E5", "#4338CA", "#3730A3", "white"
            border_style = "none"
        elif style_type == "success":
            # Modern Emerald Light Accent
            bg, hover, pressed, text_color = "#10B981", "#059669", "#047857", "white"
            border_style = "none"
        elif style_type == "danger":
            # Modern Red Light Accent
            bg, hover, pressed, text_color = "#EF4444", "#DC2626", "#B91C1C", "white"
            border_style = "none"
        else: # "secondary"
            # Modern Slate Outline style
            bg, hover, pressed, text_color = "#F1F5F9", "#E2E8F0", "#CBD5E1", "#334155"
            border_style = "1px solid #CBD5E1"
            
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                font-size: 13px;
                font-weight: bold;
                padding: 11px 22px;
                border: {border_style};
                border-radius: 6px;
                min-width: 140px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{ background-color: #F8FAFC; color: #94A3B8; border: 1px solid #E2E8F0; }}
        """)


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
                border: 3px solid #E2E8F0;
                border-radius: 10px;
                font-weight: bold;
                color: {'white' if color_name in ['Merah', 'Biru'] else '#1E293B'};
            }}
            QPushButton:hover {{
                border: 3px solid #4F46E5;
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                border: 3px solid #3730A3;
            }}
        """)
        self.setText(color_name)
        self.setCursor(Qt.PointingHandCursor)



