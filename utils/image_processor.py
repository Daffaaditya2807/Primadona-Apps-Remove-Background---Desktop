from PIL import Image
import io
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except Exception as e:
    REMBG_AVAILABLE = False
    print(f"Warning: rembg not available: {e}")

class ImageProcessor:
    @staticmethod
    def remove_background(input_image):
        if not REMBG_AVAILABLE:
            raise Exception("rembg library tidak terinstall")

        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        input_image.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data()))

        output_image = remove(pil_image)
        buffer = io.BytesIO()
        output_image.save(buffer, format='PNG')
        buffer.seek(0)

        result_pixmap = QPixmap()
        result_pixmap.loadFromData(buffer.read())
        return result_pixmap
