from PIL import Image
import io
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer

try:
    from rembg import remove
    REMBG_AVAILABLE = True
    REMBG_ERROR = None
except Exception as e:
    REMBG_AVAILABLE = False
    REMBG_ERROR = str(e)
    print(f"Warning: rembg not available: {e}")
    import traceback
    traceback.print_exc()

class ImageProcessor:
    @staticmethod
    def remove_background(input_image):
        if not REMBG_AVAILABLE:
            error_msg = "rembg library tidak terinstall"
            if REMBG_ERROR:
                error_msg += f"\nDetail error: {REMBG_ERROR}"
            raise Exception(error_msg)

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
