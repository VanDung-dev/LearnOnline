"""
Utility functions for image processing.
"""
import os
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile


def convert_to_webp(image_field, quality=85):
    """
    Convert an uploaded image to WebP format.

    Args:
        image_field: Django ImageField or FieldFile instance
        quality: WebP compression quality (1-100, default 85)

    Returns:
        tuple: (new_filename, ContentFile) if conversion successful
        None: if no conversion needed or error occurred
    """
    if not image_field:
        return None

    try:
        # Get the original file extension
        original_name = image_field.name
        ext = os.path.splitext(original_name)[1].lower()

        # Skip if already WebP
        if ext == '.webp':
            return None

        # Only process supported image formats
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif']
        if ext not in supported_formats:
            return None

        # Open the image
        image_field.seek(0)
        img = Image.open(image_field)

        # Handle transparency for PNG and GIF
        if img.mode in ('RGBA', 'LA', 'P'):
            # Preserve transparency
            if img.mode == 'P':
                img = img.convert('RGBA')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Create output buffer
        output = BytesIO()

        # Save as WebP
        img.save(output, format='WEBP', quality=quality, optimize=True)
        output.seek(0)

        # Generate new filename with .webp extension
        new_filename = os.path.splitext(original_name)[0] + '.webp'

        # Create ContentFile
        content_file = ContentFile(output.read(), name=os.path.basename(new_filename))

        return (new_filename, content_file)

    except Exception as e:
        # Log error but don't break the upload
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"WebP conversion failed for {image_field.name}: {e}")
        return None
