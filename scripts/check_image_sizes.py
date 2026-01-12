from PIL import Image
import os

folder = "static/payments/images"
for f in os.listdir(folder):
    if f.endswith('.webp'):
        path = os.path.join(folder, f)
        with Image.open(path) as img:
            size = os.path.getsize(path)
            print(f"{f}: {img.size[0]}x{img.size[1]} ({size/1024:.1f}KB)")
