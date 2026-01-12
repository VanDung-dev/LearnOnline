"""Resize payment logos to optimal size for web display."""
from PIL import Image
import os

folder = "static/payments/images"
TARGET_SIZE = 96  # 2x for retina (display at 48px)

for f in os.listdir(folder):
    if f.endswith('.webp'):
        path = os.path.join(folder, f)
        with Image.open(path) as img:
            old_size = img.size
            # Resize with high quality
            resized = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
            resized.save(path, 'WEBP', quality=85)
            new_size = os.path.getsize(path)
            print(f"✓ {f}: {old_size[0]}x{old_size[1]} → {TARGET_SIZE}x{TARGET_SIZE} ({new_size/1024:.1f}KB)")

print("\nAll logos resized successfully!")
