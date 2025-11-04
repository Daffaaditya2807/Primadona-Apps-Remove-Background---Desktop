"""Script untuk membuat splash screen image"""
from PIL import Image, ImageDraw, ImageFont
import os

# Ukuran splash screen
width, height = 500, 300

# Buat image dengan gradient background
img = Image.new('RGB', (width, height), color='#2C3E50')
draw = ImageDraw.Draw(img)

# Tambah gradient effect (simulasi dengan rectangles)
for i in range(height):
    opacity = int(255 * (1 - i/height * 0.3))
    color = (44 + int(i/height * 30), 62 + int(i/height * 30), 80 + int(i/height * 30))
    draw.rectangle([(0, i), (width, i+1)], fill=color)

# Tambah border
border_color = '#3498DB'
border_width = 3
draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color, width=border_width)

# Tambah text
try:
    # Try to use a nice font
    title_font = ImageFont.truetype("arial.ttf", 32)
    subtitle_font = ImageFont.truetype("arial.ttf", 16)
    loading_font = ImageFont.truetype("arial.ttf", 14)
except:
    # Fallback to default font
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    loading_font = ImageFont.load_default()

# Title - Using anchor for better centering
title = "Primadona Apps"
draw.text((width//2, 80), title, fill='#ECF0F1', font=title_font, anchor='mm')

# Subtitle - Using anchor for better centering
subtitle = "Hapus Background Foto"
draw.text((width//2, 130), subtitle, fill='#BDC3C7', font=subtitle_font, anchor='mm')

# Progress bar background
progress_y = 200
progress_width = 300
progress_height = 8
progress_x = (width - progress_width) // 2
draw.rectangle(
    [(progress_x, progress_y), (progress_x + progress_width, progress_y + progress_height)],
    fill='#34495E',
    outline='#3498DB',
    width=1
)

# Loading text - Embed di image dengan perfect center
loading = "Loading..."
draw.text((width//2, 240), loading, fill='#3498DB', font=loading_font, anchor='mm')

# Save splash screen
output_path = os.path.join(os.path.dirname(__file__), 'splash.png')
img.save(output_path, 'PNG')
print(f"Splash screen created: {output_path}")
print(f"Size: {width}x{height}")
